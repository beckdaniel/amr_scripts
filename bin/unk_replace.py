import argparse
import numpy as np


def replace_unk(out_tokens, in_tokens, att_matrix):
    att_matrix = np.array(att_matrix, dtype=np.float).T
    for i, token in enumerate(out_tokens):
        if token == '<unk>':
            best_score = np.argmax(att_matrix[i])
            out_tokens[i] = in_tokens[best_score]
    return out_tokens[:-1] # remove EOS token


def main(args):
    with open(args.input_decoded) as in_file, open(args.output_replaced, 'w') as out_file:
        att_matrix = None
        for line in in_file:
            if '|||' in line:
                if att_matrix is not None:
                    # process previous sentence
                    out_tokens = replace_unk(out_tokens, in_tokens, att_matrix)
                    out_file.write(' '.join(out_tokens) + '\n')
                # process new sentence
                i, out_tokens, score, in_tokens, in_count, out_count = line.strip().split(' ||| ')
                out_tokens = out_tokens.split()
                in_tokens = in_tokens.split()
                att_matrix = []
            elif line.strip() == '':
                # output has empty lines
                continue
            else:
                # build attention matrix
                att_matrix.append(line.split())

                


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_decoded', type=str)
    parser.add_argument('output_replaced', type=str)
    args = parser.parse_args()
    main(args)
