python preproc_vocab.py ../data/undirected/train.triples.en ../data/undirected/train.triples.unk.freq$1.en ../data/undirected/edge_vocab_freq$1.json --filter FREQ --value $1
python preproc_vocab.py ../data/undirected/test.triples.en ../data/undirected/test.triples.unk.freq$1.en ../data/undirected/edge_vocab_freq$1.json --mode UNK
python preproc_vocab.py ../data/undirected/dev.triples.en ../data/undirected/dev.triples.unk.freq$1.en ../data/undirected/edge_vocab_freq$1.json --mode UNK

paste ../data/undirected/train.nodes.en ../data/undirected/train.triples.unk.freq$1.en > ../data/undirected/train.nodes_triples.unk.freq$1.en
paste ../data/undirected/dev.nodes.en ../data/undirected/dev.triples.unk.freq$1.en > ../data/undirected/dev.nodes_triples.unk.freq$1.en
paste ../data/undirected/test.nodes.en ../data/undirected/test.triples.unk.freq$1.en > ../data/undirected/test.nodes_triples.unk.freq$1.en
