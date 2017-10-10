import argparse
from nltk.tokenize import TreebankWordTokenizer as Tok

parser = argparse.ArgumentParser()
parser.add_argument('input_sentences', type=str)
parser.add_argument('output_sentences', type=str)
args = parser.parse_args()

def preprocess_sent(sent):
    """
    Take a sentence in string format and returns
    a list of lemmatized tokens.
    """
    #tokenized = word_tokenize(sent.lower())
    tokenizer = Tok()
    tokenized = tokenizer.tokenize(sent.lower())
    return tokenized


with open(args.input_sentences) as inp, open(args.output_sentences, 'w') as out:
    for sent in inp:
        out.write(' '.join(preprocess_sent(sent)) + '\n')
