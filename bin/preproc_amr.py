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
from amr import AMR, Var
import re
import json
import argparse
from collections import Counter



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

def get_name(c):
    try:
        # Remove sense info from concepts if present
        if re.search(SENSE_PATTERN, c._name):
            return c._name[:-3]
        else:
            return c._name
    except: # constants: remove quotes if present
        r = str(c).lower()
        if r[0] == '"' and r[-1] == '"':
            return r[1:-1]
        else:
            return r

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
    with open(args.output, 'w') as out, open(args.output_surface, 'w') as surf_out:
        for amr, surf in zip(amrs, surfs):
            graph = AMR(amr, surf.split())
            
            # Get variable: concept map for reentrancies
            v2c = graph.var2concept()

            if args.mode == 'LIN':
                # Linearisation mode for seq2seq

                tokens = amr.split()
                new_tokens = simplify(tokens, v2c)
                out.write(' '.join(new_tokens) + '\n')

            elif args.mode == 'GRAPH':
                # Triples mode for graph2seq

                # Get concepts and generate IDs
                c_ids = {}
                rev_c_ids = []
                for concept in graph.concepts():
                    c = concept[1]
                    c_ids[c] = str(len(c_ids))
                    rev_c_ids.append(c)
                # Add constant nodes as well
                for constant in graph.constants():
                    c_ids[constant] = str(len(c_ids))
                    rev_c_ids.append(constant)

                # Triples
                triples = []
                for triple in graph.triples():
                    # Ignore top and instance-of
                    # TODO: remove wikification
                    if triple[1] == ':top' or triple[1] == ':instance-of':
                        continue
                    predicate = triple[1]
                    try:
                        c1 = v2c[triple[0]]
                    except: # If it is not a concept it is a constant:
                        c1 = triple[0]
                    try:
                        c2 = v2c[triple[2]]
                    except:
                        c2 = triple[2]
                    triples.append((c_ids[c1], c_ids[c2], predicate))
                    if args.add_reverse:
                        # Add reversed edges if requested
                        if predicate.endswith('-of'):
                            rev_predicate = predicate[:-3]
                        else:
                            rev_predicate = predicate + '-of'
                        triples.append((c_ids[c2], c_ids[c1], rev_predicate))
                        
                # Add self-loops
                for c in c_ids:
                    triples.append((c_ids[c], c_ids[c], 'self'))

                # Print concepts/constants and triples
                cs = [get_name(c) for c in rev_c_ids]
                out.write(' '.join(cs) + '\n')
                triples_out.write(' '.join(['(' + ','.join(adj) + ')' for adj in triples]) + '\n')

            # Process the surface form
            surf_out.write(surf.lower())

###########################
            
if __name__ == "__main__":
    
    # Parse input
    parser = argparse.ArgumentParser(description="Preprocess AMR into linearised forms with multiple preprocessing steps (based on Konstas et al. ACL 2017)")
    parser.add_argument('input_amr', type=str, help='input AMR file')
    parser.add_argument('input_surface', type=str, help='input surface file')
    parser.add_argument('output', type=str, help='output file, either AMR or concept list')
    parser.add_argument('output_surface', type=str, help='output surface file')
    parser.add_argument('--mode', type=str, default='GRAPH', help='preprocessing mode',
                        choices=['GRAPH','LIN'])
    parser.add_argument('--anon', action='store_true', help='anonymise NEs and dates')
    parser.add_argument('--add-reverse', action='store_true', help='whether to add reverse edges in the graph output')
    parser.add_argument('--triples-output', type=str, default=None, help='triples output for graph2seq')
    parser.add_argument('--align-output', type=str, default=None, help='alignment output file, if using anonymisation')

    args = parser.parse_args()

    assert (args.triples_output is not None) or (args.mode != 'GRAPH'), "Need triples output for graph mode"
    assert (args.align_output is not None) or (not args.anon), "Need alignment output for anon mode"

    SENSE_PATTERN = re.compile('-[0-9][0-9]$')
    
    main(args)
