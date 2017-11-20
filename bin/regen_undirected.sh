python preproc_amr.py ../data/preproc/train/amr.en ../data/preproc/train/surface.en ../data/undirected/train.nodes.en ../data/undirected/train.surface.en --mode GRAPH --triples ../data/undirected/train.triples.en --add-reverse
python preproc_amr.py ../data/preproc/dev/amr.en ../data/preproc/dev/surface.en ../data/undirected/dev.nodes.en ../data/undirected/dev.surface.en --mode GRAPH --triples ../data/undirected/dev.triples.en --add-reverse
python preproc_amr.py ../data/preproc/test/amr.en ../data/preproc/test/surface.en ../data/undirected/test.nodes.en ../data/undirected/test.surface.en --mode GRAPH --triples ../data/undirected/test.triples.en --add-reverse

