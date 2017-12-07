python preproc_amr.py ../data/preproc/train/amr.en ../data/preproc/train/surface.en ../data/anon_line_graphs/train.nodes.en ../data/anon_line_graphs/train.surface.en --mode LINE_GRAPH --triples-output ../data/anon_line_graphs/train.triples.en --anon --map-output ../data/anon_line_graphs/train.map.en --anon-surface ../data/anon_line_graphs/train.anon.surface.en
python preproc_amr.py ../data/preproc/dev/amr.en ../data/preproc/dev/surface.en ../data/anon_line_graphs/dev.nodes.en ../data/anon_line_graphs/dev.surface.en --mode LINE_GRAPH --triples-output ../data/anon_line_graphs/dev.triples.en --anon --map-output ../data/anon_line_graphs/dev.map.en --anon-surface ../data/anon_line_graphs/dev.anon.surface.en
python preproc_amr.py ../data/preproc/test/amr.en ../data/preproc/test/surface.en ../data/anon_line_graphs/test.nodes.en ../data/anon_line_graphs/test.surface.en --mode LINE_GRAPH --triples-output ../data/anon_line_graphs/test.triples.en --anon --map-output ../data/anon_line_graphs/test.map.en --anon-surface ../data/anon_line_graphs/test.anon.surface.en

echo '{"default": 1, "reverse": 2, "self": 3}' > ../data/anon_line_graphs/edge_vocab.json

paste ../data/anon_line_graphs/train.nodes.en ../data/anon_line_graphs/train.triples.en > ../data/anon_line_graphs/train.nodes_triples.en
paste ../data/anon_line_graphs/dev.nodes.en ../data/anon_line_graphs/dev.triples.en > ../data/anon_line_graphs/dev.nodes_triples.en
paste ../data/anon_line_graphs/test.nodes.en ../data/anon_line_graphs/test.triples.en > ../data/anon_line_graphs/test.nodes_triples.en
