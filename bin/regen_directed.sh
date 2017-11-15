python preproc_amr.py ../data/preproc/train/amr.en ../data/preproc/train/surface.en ../data/directed/train.nodes.en ../data/directed/train.surface.en --mode GRAPH --triples ../data/directed/train.triples.en
python preproc_amr.py ../data/preproc/dev/amr.en ../data/preproc/dev/surface.en ../data/directed/dev.nodes.en ../data/directed/dev.surface.en --mode GRAPH --triples ../data/directed/dev.triples.en
python preproc_amr.py ../data/preproc/test/amr.en ../data/preproc/test/surface.en ../data/directed/test.nodes.en ../data/directed/test.surface.en --mode GRAPH --triples ../data/directed/test.triples.en

python preproc_vocab.py ../data/directed/train.triples.en ../data/directed/train.triples.unk.freq$1.en ../data/directed/edge_vocab_freq$1.json --filter FREQ --value $1
python preproc_vocab.py ../data/directed/test.triples.en ../data/directed/test.triples.unk.freq$1.en ../data/directed/edge_vocab_freq$1.json --mode UNK
python preproc_vocab.py ../data/directed/dev.triples.en ../data/directed/dev.triples.unk.freq$1.en ../data/directed/edge_vocab_freq$1.json --mode UNK

paste ../data/directed/train.nodes.en ../data/directed/train.triples.unk.freq$1.en > ../data/directed/train.nodes_triples.unk.freq$1.en
paste ../data/directed/dev.nodes.en ../data/directed/dev.triples.unk.freq$1.en > ../data/directed/dev.nodes_triples.unk.freq$1.en
paste ../data/directed/test.nodes.en ../data/directed/test.triples.unk.freq$1.en > ../data/directed/test.nodes_triples.unk.freq$1.en
