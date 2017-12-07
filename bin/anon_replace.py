import argparse
import json


def replace_unk(out_tokens, in_tokens, att_matrix):
    att_matrix = np.array(att_matrix, dtype=np.float).T
    for i, token in enumerate(out_tokens):
        if token == '<unk>':
            best_score = np.argmax(att_matrix[i])
            out_tokens[i] = in_tokens[best_score]
    return out_tokens[:-1] # remove EOS token


def main(args):
    with open(args.input_decoded) as in_file, open(args.input_map) as map_file, open(args.output_replaced, 'w') as out_file:
        in_lines = in_file.readlines()
        map_lines = map_file.readlines()
        for in_line, map_line in zip(in_lines, map_lines):
            tokens = in_line.split()
            anon_map = json.loads(map_line)
            replaced = []
            for tok in tokens:
                if tok in anon_map:
                    replaced.append(anon_map[tok])
                else:
                    replaced.append(tok)
            out_file.write(' '.join(replaced) + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_decoded', type=str)
    parser.add_argument('input_map', type=str)
    parser.add_argument('output_replaced', type=str)
    args = parser.parse_args()
    main(args)
