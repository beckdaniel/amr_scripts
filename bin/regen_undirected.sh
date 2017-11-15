python preproc_amr.py ../data/preproc/train/amr.en ../data/preproc/train/surface.en ../data/undirected/train.nodes.en ../data/undirected/train.surface.en --mode GRAPH --triples ../data/undirected/train.triples.en --add-reverse
python preproc_amr.py ../data/preproc/dev/amr.en ../data/preproc/dev/surface.en ../data/undirected/dev.nodes.en ../data/undirected/dev.surface.en --mode GRAPH --triples ../data/undirected/dev.triples.en --add-reverse
python preproc_amr.py ../data/preproc/test/amr.en ../data/preproc/test/surface.en ../data/undirected/test.nodes.en ../data/undirected/test.surface.en --mode GRAPH --triples ../data/undirected/test.triples.en --add-reverse
python preproc_vocab.py ../data/undirected/train.triples.en ../data/undirected/train.triples.unk.freq$1.en ../data/undirected/edge_vocab_freq$1.json --filter FREQ --value $1
python preproc_vocab.py ../data/undirected/test.triples.en ../data/undirected/test.triples.unk.freq$1.en ../data/undirected/edge_vocab_freq$1.json --mode UNK
python preproc_vocab.py ../data/undirected/dev.triples.en ../data/undirected/dev.triples.unk.freq$1.en ../data/undirected/edge_vocab_freq$1.json --mode UNK

