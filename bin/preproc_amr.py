"""
Preprocess AMR and surface forms.

Options:

- linearise: for seq2seq learning
  - simplify: simplify graphs and lowercase surface
  - anon: same as above but with anonymisation
  
- triples: for graph2seq learning
  - anon: anonymise NEs

"""
import sys
from amr import AMR, Var, Concept, AMRNumber
import re
import json
import argparse
from collections import Counter
from copy import deepcopy

from ne_clusters import NE_CLUSTER, QUANT_CLUSTER


##########################

def simplify(tokens, v2c):
    new_tokens = []
    for tok in tokens:
        # ignore instance-of
        if tok.startswith('('):
            continue
        elif tok == '/':
            continue
        # predicates, we remove any alignment information and parenthesis
        elif tok.startswith(':'):
            new_tok = tok.strip(')')
            new_tok = new_tok.split('~')[0]
            new_tokens.append(new_tok)
        # concepts/reentrancies, treated similar as above
        else:
            new_tok = tok.strip(')')
            new_tok = new_tok.split('~')[0]
            # now we check if it is a concept or a variable (reentrancy)
            if Var(new_tok) in v2c:
                # reentrancy: replace with concept
                new_tok = v2c[Var(new_tok)]._name
            # remove sense information
            elif re.search(SENSE_PATTERN, new_tok):
                new_tok = new_tok[:-3]
            # remove quotes
            elif new_tok[0] == '"' and new_tok[-1] == '"':
                new_tok = new_tok[1:-1]
            new_tokens.append(new_tok)
    return new_tokens

##########################

def get_name(v, v2c):
    try:
        # Remove sense info from concepts if present
        c = v2c[v]
        if re.search(SENSE_PATTERN, c._name):
            return c._name[:-3]
        else:
            return c._name
    except: # constants: remove quotes if present
        r = str(v).lower()
        if r[0] == '"' and r[-1] == '"':
            return r[1:-1]
        else:
            return r

##########################

def get_nodes(graph):
    v_ids = {}
    rev_v_ids = []
    for concept in graph.concepts():
        v = concept[0]
        #c = concept[1]
        #c_ids[c] = str(len(c_ids))
        #rev_c_ids.append(c)
        v_ids[v] = str(len(v_ids))
        rev_v_ids.append(v)
        
    # Add constant nodes as well
    for constant in graph.constants():
        v_ids[constant] = str(len(v_ids))
        rev_v_ids.append(constant)
    return v_ids, rev_v_ids
        
##########################

def get_nodes2(graph):
    v_ids = {}
    rev_v_ids = []
    filtered = [t for t in graph.triples() if type(t[2]) != Var]
    #v2cs = [t for t in filtered if t[1] == ':instance-of']
    #constants = [t[2] for t in filtered if t[1] != ':instance-of']
    for triple in filtered:
        # Concepts: we map Vars
        if triple[1] == ':instance-of':
            v = triple[0]
        # Constants: we map the actual constant
        else:
            v = triple[2]
        if v not in v_ids:
            # Need this check so we do not add double constants
            v_ids[v] = str(len(v_ids))
            rev_v_ids.append(v)            
    return v_ids, rev_v_ids
        
##########################

def get_triples(graph, v_ids, rev_v_ids):
    triples = []
    for triple in graph.triples():
        # Ignore top and instance-of
        # TODO: remove wikification
        if triple[1] == ':top' or triple[1] == ':instance-of':
            continue
        predicate = triple[1]
        try:
            v1 = triple[0]
            c1 = v2c[v1]                        
        except: # If it is not a concept it is a constant:
            v1 = triple[0]
        try:
            v2 = triple[2]
            c2 = v2c[v2]
        except:
            v2 = triple[2]
        triples.append((v_ids[v1], v_ids[v2], predicate))
        if args.add_reverse:
            # Add reversed edges if requested
            if predicate.endswith('-of'):
                rev_predicate = predicate[:-3]
            else:
                rev_predicate = predicate + '-of'
                triples.append((v_ids[v2], v_ids[v1], rev_predicate))
                        
    # Add self-loops
    for v in v_ids:
        triples.append((v_ids[v], v_ids[v], 'self'))
    return triples

##########################

def anonymize(graph, surf):
    
    # Get triples with :name predicate
    triples = graph.triples()
    new_graph = deepcopy(graph)
    #output_triples = deepcopy(triples)
    output_triples = new_graph.triples()
    v2c = new_graph.var2concept()
    
    anon_ids = {'person': 0,
                'organization': 0,
                'location': 0,
                'other': 0,
                'quantity': 0}
    anon_map = {}
    anon_surf = surf.split()

    #################
    # Anonymize NEs. We replace the node with a clustered concept and delete
    # corresponding subgraphs, including wiki.
    name_triples = [t for t in triples if t[1] == ':name']
    for name_t in name_triples:
        conc = name_t[0]
        name = name_t[2]

        # update concept name
        clusterized = NE_CLUSTER.setdefault(v2c[conc]._name, 'other')
        cluster_id = anon_ids[clusterized]
        new_conc_name = clusterized + '_' + str(cluster_id)
        anon_ids[clusterized] += 1
        v2c[conc] = Concept(new_conc_name)

        # get :op predicates, sorted by indexes
        op_tuples = [t for t in triples if t[0] == name and t[1] != ':instance-of']
        op_tuples = sorted(op_tuples, key=lambda x: x[1])

        # update mapping, removing quotes
        anon_map[new_conc_name] = ' '.join([str(op[2])[1:-1] for op in op_tuples])
        
        # update surface form
        # sometimes an :op is not aligned (implicit), therefore the if statement
        alignments = [graph.alignments()[t] for t in op_tuples if t in graph.alignments()]
        align_indexes = [a.split('.')[1] for a in alignments]
        # need to do this because some :ops are many-to-1
        indexes = []
        for a_index in align_indexes:
            if ',' in a_index:
                for i in a_index.split(','):
                    indexes.append(int(i))
            else:
                indexes.append(int(a_index))    
        #align_indexes = [int(alignments[t].split('.')[1]) for t in op_tuples if '~' in alignments[t]]
        for i, index in enumerate(indexes):
            if i == 0:
                anon_surf[index] = new_conc_name
            else:
                anon_surf[index] = ''

        # remove triples from graph
        for triple in triples:
            if triple[0] == name:
                try:
                    output_triples.remove(triple)
                except ValueError:
                    # Sometimes we have multiple NEs refering to the same graph,
                    # which means we already removed the graph in the first instance
                    pass
            #if triple[0] == conc and triple[1] != ':instance-of':
            elif triple[0] == conc and triple[1] == ':name' and triple[2] == name:
                output_triples.remove(triple)

    ################
    # Anonymize quantities. Similar procedure with NEs but without deleting subgraphs.
    # There are three different cases that requires different treatments
    quant_triples = [t for t in triples if t[1] == ':quant']
    for quant_t in quant_triples:
        conc = quant_t[0]
        quant = quant_t[2]

        # 1st case: :quant links to another concept. In this case we ignore it.
        # TODO: sometimes the quantity appears inside as an :opX predicate. We do
        # not deal with these cases here.
        if type(quant) == Var:
            continue

        # 2nd case: :quant links a non-quantity concept to a number. In this case
        # we replace the number with an anonymization token. To do this, we ...
        elif v2c[conc]._name not in QUANT_CLUSTER:
            if quant_t in graph.alignments():
                a_index = graph.alignments()[quant_t].split('.')[1]
                indexes = []
                if ',' in a_index:
                    for i in a_index.split(','):
                        indexes.append(int(i))
                else:
                    indexes.append(int(a_index))
            new_quant_name = 'quantity_' + str(anon_ids['quantity'])
            anon_ids['quantity'] += 1
            anon_map[new_quant_name] = quant._value
            try:
                output_t_index = output_triples.index(quant_t)
                output_triples[output_t_index][2]._value = new_quant_name
            except ValueError:
                # Constant already updated, can ignore
                pass
            if quant_t in graph.alignments():
                for i, index in enumerate(indexes):
                    if i == 0:
                        anon_surf[index] = new_quant_name
                    else:
                        anon_surf[index] = ''
            #import ipdb; ipdb.set_trace()

        # 3rd case: :quant links a quantity concept to a number. In this case
        # we replace the *entire tuple* with an anonymization token.
        else:
            # Sometimes quantities are not aligned
            if quant_t in graph.alignments():
                a_index = graph.alignments()[quant_t].split('.')[1]
                indexes = []
                if ',' in a_index:
                    for i in a_index.split(','):
                        indexes.append(int(i))
                else:
                    indexes.append(int(a_index)) 
            #output_t_index = output_triples.index(quant_t)
            new_quant_name = 'quantity_' + str(anon_ids['quantity'])
            anon_ids['quantity'] += 1
            anon_map[new_quant_name] = quant._value
            #output_triples[output_t_index][2]._value = new_quant_name
            if quant_t in graph.alignments():
                for i, index in enumerate(indexes):
                    if i == 0:
                        anon_surf[index] = new_quant_name
                    else:
                        anon_surf[index] = ''

            # update concept name and remove triples
            v2c[conc] = Concept(new_quant_name)
            #print(quant_t)
            #print(output_triples)
            try:
                output_triples.remove(quant_t)
            except:
                #import ipdb; ipdb.set_trace()
                for triple in output_triples:
                    if triple[0] == quant_t[0] and triple[1] == quant_t[1]:
                        output_triples.remove(triple)
                

    anon_surf = ' '.join(anon_surf).lower().split() # remove extra spaces
    return output_triples, v2c, anon_surf, anon_map

##########################

def get_line_graph(graph, surf, anon=False):
    triples = []
    nodes = {}
    rev_nodes = []
    uniq = 0
    nodes_to_print = []
    graph_triples = graph.triples()
    if anon:
        # preprocess triples and surface
        #import ipdb; ipdb.set_trace()
        graph_triples, v2c, anon_surf, anon_map = anonymize(graph, surf)
        anon_surf = ' '.join(anon_surf)
        #import ipdb; ipdb.set_trace()
    else:
        graph_triples = graph.triples()
        v2c = graph.var2concept()
        anon_surf = surf
        anon_map = None
    for triple in graph_triples:
        src, edge, tgt = triple
        # ignore these nodes
        if edge == ':top' or edge == ':instance-of' or edge == ':wiki':
            continue
        # process nodes, populating the ids
        if src not in nodes:
            nodes[src] = len(nodes)
            rev_nodes.append(src)
            src_id = nodes[src]
            triples.append((src_id, src_id, 'self'))
            nodes_to_print.append(get_name(src, v2c))
        edge_uniq = edge + '_' + str(uniq)
        uniq += 1
        nodes[edge_uniq] = len(nodes)
        rev_nodes.append(edge_uniq)
        edge_id = nodes[edge_uniq]
        triples.append((edge_id, edge_id, 'self'))
        nodes_to_print.append(edge)
        if tgt not in nodes:
            nodes[tgt] = len(nodes)
            rev_nodes.append(tgt)
            tgt_id = nodes[tgt]
            triples.append((tgt_id, tgt_id, 'self'))
            nodes_to_print.append(get_name(tgt, v2c))
        # process triples
        src_id = nodes[src]
        edge_id = nodes[edge_uniq]
        tgt_id = nodes[tgt]
        triples.append((src_id, edge_id, 'default'))
        triples.append((edge_id, src_id, 'reverse'))
        triples.append((edge_id, tgt_id, 'default'))
        triples.append((tgt_id, edge_id, 'reverse'))

    if nodes_to_print == []:
        # single node graph, first triple is ":top", second triple is the node
        triple = graph.triples()[1]
        nodes_to_print.append(get_name(triple[0], v2c))
        triples.append((0, 0, 'self'))
    return nodes_to_print, triples, anon_surf, anon_map

##########################

def main(args):

    # First, let's read the graphs and surface forms
    with open(args.input_amr) as f:
        amrs = f.readlines()
    with open(args.input_surface) as f:
        surfs = f.readlines()

    if args.triples_output is not None:
        triples_out = open(args.triples_output, 'w')
        
    # Iterate
    anon_surfs = []
    anon_maps = []
    i = 0
    with open(args.output, 'w') as out, open(args.output_surface, 'w') as surf_out:
        for amr, surf in zip(amrs, surfs):
            graph = AMR(amr, surf.split())
            
            # Get variable: concept map for reentrancies
            #v2c = graph.var2concept()

            if args.mode == 'LIN':
                # Linearisation mode for seq2seq

                tokens = amr.split()
                new_tokens = simplify(tokens, v2c)
                out.write(' '.join(new_tokens) + '\n')

            elif args.mode == 'GRAPH':
                # Triples mode for graph2seq
                #import ipdb; ipdb.set_trace()
                # Get concepts and generate IDs
                v_ids, rev_v_ids = get_nodes2(graph)

                # Triples
                triples = get_triples(graph, v_ids, rev_v_ids)

                # Print concepts/constants and triples
                #cs = [get_name(c) for c in rev_c_ids]
                cs = [get_name(v, v2c) for v in rev_v_ids]
                out.write(' '.join(cs) + '\n')
                triples_out.write(' '.join(['(' + ','.join(adj) + ')' for adj in triples]) + '\n')

            elif args.mode == 'LINE_GRAPH':
                # Similar to GRAPH, but with edges as extra nodes
                #import ipdb; ipdb.set_trace()
                print(i)
                i += 1
                #if i == 574:
                #    import ipdb; ipdb.set_trace()
                nodes, triples, anon_surf, anon_map = get_line_graph(graph, surf, anon=args.anon)
                out.write(' '.join(nodes) + '\n')
                triples_out.write(' '.join(['(%d,%d,%s)' % adj for adj in triples]) + '\n')
                #surf = ' '.join(new_surf)
                anon_surfs.append(anon_surf)
                anon_maps.append(json.dumps(anon_map))
                
            # Process the surface form
            surf_out.write(surf.lower())
    if args.anon:
        with open(args.anon_surface, 'w') as f:
            for anon_surf in anon_surfs:
                f.write(anon_surf + '\n')
        with open(args.map_output, 'w') as f:
            for anon_map in anon_maps:
                f.write(anon_map + '\n')

###########################
            
if __name__ == "__main__":
    
    # Parse input
    parser = argparse.ArgumentParser(description="Preprocess AMR into linearised forms with multiple preprocessing steps (based on Konstas et al. ACL 2017)")
    parser.add_argument('input_amr', type=str, help='input AMR file')
    parser.add_argument('input_surface', type=str, help='input surface file')
    parser.add_argument('output', type=str, help='output file, either AMR or concept list')
    parser.add_argument('output_surface', type=str, help='output surface file')
    parser.add_argument('--mode', type=str, default='GRAPH', help='preprocessing mode',
                        choices=['GRAPH','LIN','LINE_GRAPH'])
    parser.add_argument('--anon', action='store_true', help='anonymise NEs and dates')
    parser.add_argument('--add-reverse', action='store_true', help='whether to add reverse edges in the graph output')
    parser.add_argument('--triples-output', type=str, default=None, help='triples output for graph2seq')
    parser.add_argument('--map-output', type=str, default=None, help='mapping output file, if using anonymisation')
    parser.add_argument('--anon-surface', type=str, default=None, help='anonymized surface output file, if using anonymisation')

    args = parser.parse_args()

    assert (args.triples_output is not None) or (args.mode != 'GRAPH'), "Need triples output for graph mode"
    assert (args.map_output is not None) or (not args.anon), "Need map output for anon mode"
    assert (args.anon_surface is not None) or (not args.anon), "Need anonymized surface output for anon mode"

    SENSE_PATTERN = re.compile('-[0-9][0-9]$')
    
    main(args)
