"""
Preprocess vocabulary

Currently only works with edge labels vocabs
"""


import argparse
import json
from collections import Counter

#####################

def create_vocab(args):
    with open(args.input_triples) as f:
        instances = f.readlines()

    # Get frequencies first
    freqs = Counter()
    for instance in instances:
        triples = instance.strip('\n').split(' ')
        for triple in triples:
            # strip ')'
            tokens = triple.strip('()').split(',')
            label = tokens[2]
            freqs[label] += 1

    # Now filter and create the vocab
    vocab = {'<unk>': 0}
    if args.filter == 'FREQ':
        for label in freqs:
            if freqs[label] >= args.value:
                vocab[label] = len(vocab)
    elif args.filter == 'RANK':
        filtered = freqs.most_common(args.value)
        for label, _ in filtered:
            vocab[label] = len(vocab)
    return vocab
    
#####################

def main(args):
    if args.mode == 'VOCAB':
        # create vocabulary first
        vocab = create_vocab(args)
        with open(args.edge_vocab, 'w') as f:
            json.dump(vocab, f, indent='\t')
    else:
        # use preprocessed vocab (for dev and test)
        with open(args.edge_vocab) as f:
            vocab = json.load(f)

    # Proceed with unking
    with open(args.input_triples) as in_file, open(args.output_triples, 'w') as out_file:
        for instance in in_file:
            triples = instance.strip('\n').split(' ')
            unk_triples = []
            for triple in triples:
                # strip '(' and ')'
                tokens = triple[1:-1].split(',')
                label = tokens[2]
                if label in vocab:
                    unk_triples.append(','.join(tokens))
                else:
                    id1 = tokens[0]
                    id2 = tokens[1]
                    unk_triples.append(','.join((id1, id2, '<unk>')))
            out_file.write(' '.join(['(' + t + ')' for t in unk_triples]) + '\n')

            
#####################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vocabulary preprocessing for edges")
    parser.add_argument('input_triples', type=str, help='input triples file')
    parser.add_argument('output_triples', type=str, help='output UNKd triples file')
    parser.add_argument('edge_vocab', type=str, help='vocabulary file')
    parser.add_argument('--mode', type=str, default='VOCAB', choices=['VOCAB', 'UNK'],
                        help='in VOCAB mode it creates a vocab file, in UNK mode, it uses the pregenerated vocab file to performn UNKing')
    parser.add_argument('--filter', type=str, default='FREQ', choices=['FREQ', 'RANK'],
                        help='in FREQ mode, it UNKs edges < value, in RANK mode, keep only top value labels, sorted by frequency. Ignored in UNK mode.')
    parser.add_argument('--value', type=int, default=2, help='value for vocab creation (freq or rank threshold). Ignored in UNK mode.')

    args = parser.parse_args()

    main(args)
