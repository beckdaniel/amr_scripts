python gen_triples.py ../data/train/amr.en ../data/preproc/train.surf.en ../data/preproc/train.triples.en ../data/preproc/node.json ../data/preproc/edge.json
python gen_triples.py ../data/dev/amr.en ../data/preproc/dev.surf.en ../data/preproc/dev.triples.en ../data/preproc/node.json ../data/preproc/edge.json --unk
python gen_triples.py ../data/test/amr.en ../data/preproc/test.surf.en ../data/preproc/test.triples.en ../data/preproc/node.json ../data/preproc/edge.json --unk
python preproc_surface.py ../data/train/surface.en ../data/preproc/train.output.en
python preproc_surface.py ../data/dev/surface.en ../data/preproc/dev.output.en
python preproc_surface.py ../data/test/surface.en ../data/preproc/test.output.en
