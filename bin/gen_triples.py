import sys
import penman
import re
import json
import argparse
from collections import Counter


# Parse input
parser = argparse.ArgumentParser(description="Preprocess AMR into Sockeye GCN friendly format")
parser.add_argument('graph', type=str, help='input graph')
parser.add_argument('pseudo_surface', type=str, help='output pseudo surface form')
parser.add_argument('triples', type=str, help='output triple list')
parser.add_argument('node_vocab', type=str, help='vocabulary for nodes')
parser.add_argument('edge_vocab', type=str, help='vocabulary for edges')
parser.add_argument('-u', '--unk', help='unk concepts and edges, requires vocabs', action='store_true')


args = parser.parse_args()

#assert (args.unk == False) or (args.node_vocab is not None and args.edge_vocab is not None)

INPUT = args.graph
OUTPUT_SURF = args.pseudo_surface
OUTPUT_TRIPLES = args.triples
UNK_MODE = args.unk
NODE_VOCAB = args.node_vocab
EDGE_VOCAB = args.edge_vocab

SENSE_PATTERN = re.compile('-[0-9][0-9]$')

def preproc_node(node):
    """
    Strip senses and other stuff
    """
    if re.search(SENSE_PATTERN, node):
        node = node[:-3]
    elif node[0] == '"' and node[-1] == '"':
        node = node[1:-1]
    return node.lower()


# First, let's read the graphs

with open(INPUT) as f:
    graphs = [penman.decode(line) for line in f.readlines()]

# Now we do a first iteration to grab the vocabulary for edges and nodes

if not UNK_MODE:
    node_vocab = {'<unk>': 1, '<pad>': 0, '<s>': 2, '</s>': 3}
    edge_vocab = {'<unk>': 0, '<unk>-of': 1}
    node_freqs = Counter()
    edge_freqs = Counter()

    for g in graphs:
        triples = g.triples()
        for t in triples:
            #print(t)
            node = str(t[2])

            # Strip senses
            node = preproc_node(node)
            
            edge = t[1]
            node_freqs[node] += 1
            if node_freqs[node] > 1 and node not in node_vocab:
                node_vocab[node] = len(node_vocab)
            edge_freqs[edge] += 1
            if edge_freqs[edge] > 5 and edge not in edge_vocab:
                edge_vocab[edge] = len(edge_vocab)
                edge_vocab[edge + '-of'] = len(edge_vocab)
    edge_vocab['self'] = len(edge_vocab)
    with open(NODE_VOCAB, 'w') as f:
        json.dump(node_vocab, f, indent='\t')
    with open(EDGE_VOCAB, 'w') as f:
        json.dump(edge_vocab, f, indent='\t')
else:
    #print("Reading precomputed vocabs")
    with open(NODE_VOCAB) as f:
        node_vocab = json.load(f)
    with open(EDGE_VOCAB) as f:
        edge_vocab = json.load(f)

# Now we generate the graphs

out_surf = open(OUTPUT_SURF, 'w')
out_triples = open(OUTPUT_TRIPLES, 'w')

j = 0
for g in graphs:
    triples = g.triples()
    # First, grab instances
    instances = {str(t[0]): str(t[2]) for t in triples if t[1] == 'instance'}
    #print(triples)
    # Arbitrarily assign IDs
    ids = {}
    # Now build the lists
    adj_list = []
    pseudo_surface = []
    for t in [t for t in triples if t[1] != 'instance']:
        source = str(t[0])
        target = str(t[2])
        edge = t[1]
        # collapse nodes into their instances
        if source in instances:
            source = instances[source]
        if target in instances:
            target = instances[target]
        # update sent-level IDs
        if source not in ids:
            ids[source] = len(ids)
            pseudo_surface.append(source)
        if target not in ids:
            ids[target] = len(ids)
            pseudo_surface.append(target)
        source_id = ids[source]
        target_id = ids[target]
        # add edge, just two edge labels for now
        if edge not in edge_vocab:
            edge = '<unk>'
        
        adj_list.append([str(source_id), str(target_id), edge])
        adj_list.append([str(target_id), str(source_id), edge + '-of'])
    # add the self edges:
    for id in ids:
        adj_list.append([str(ids[id]), str(ids[id]), 'self'])

    # print outputs
    if pseudo_surface == []:
        pseudo_surface.append('<unk>')
        adj_list.append(('0','0','self'))
    #sys.stdout.write(' '.join(['(' + ','.join(adj) + ')' for adj in adj_list]) + '\n')
    out_triples.write(' '.join(['(' + ','.join(adj) + ')' for adj in adj_list]) + '\n')
    #print(' '.join(['(' + ','.join(adj) + ')' for adj in adj_list]))
    # UNKing the surface
    
    #print(' '.join([tok if tok in node_vocab else '<unk>' for tok in pseudo_surface]))
    #sys.stderr.write(' '.join([tok if tok in node_vocab else '<unk>' for tok in pseudo_surface]) + '\n')
    #print(pseudo_surface)
    # Need to strip senses again
    #pseudo_surface = [tok[:-3] for tok in pseudo_surface if re.search(SENSE_PATTERN, tok) else tok]
    pseudo_surface = [preproc_node(tok) for tok in pseudo_surface]
    out_surf.write(' '.join([tok if tok in node_vocab else '<unk>' for tok in pseudo_surface]) + '\n')
    #print(triples)
    j += 1
    #if j > 10:
    #    break
    #print(instances)
        
