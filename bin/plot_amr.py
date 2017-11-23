from graphviz import Digraph
import argparse


def gen_dot(nodes, triples):
    dot = Digraph()
    node_ids = nodes.split()
    for i, node in enumerate(node_ids):
        dot.node(node + '_' + str(i))
    for triple in triples.split():
        src, tgt, label = triple[1:-1].split(',')
        dot.edge(node_ids[int(src)] + '_' + src,
                 node_ids[int(tgt)] + '_' + tgt,
                 label=label)
    dot.view()
    import ipdb; ipdb.set_trace()






parser = argparse.ArgumentParser()
parser.add_argument('input_nodes', type=str)
parser.add_argument('input_triples', type=str)
#parser.add_argumet('', type=str)
parser.add_argument('--index', type=int, default=1)
args = parser.parse_args()


with open(args.input_nodes) as f:
    nodes_lines = f.readlines()
with open(args.input_triples) as f:
    triples_lines = f.readlines()

    
for nodes, triples in zip(nodes_lines, triples_lines):
    dot = gen_dot(nodes, triples)
