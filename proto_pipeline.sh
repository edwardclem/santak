#!/bin/bash

#prototype data generation pipeline

render_out=data/rendered
proto_out=data/prototypes
fontpath=src/generate_prototypes/resources/CuneiformComposite.ttf

python src/generate_prototypes/render_chars.py --outf $render_out/rendered_20 --max_code 73748 --font $fontpath
python src/generate_prototypes/render_chars.py --outf $render_out/rendered_50 --max_code 73779 --font $fontpath
python src/generate_prototypes/render_chars.py --outf $render_out/rendered_all --max_code 74606 --font $fontpath

python src/generate_prototypes/gen_proto_data.py --imgs $render_out/rendered_50 --skip 6 --out $proto_out/proto_50.pkl
python src/generate_prototypes/gen_proto_data.py --imgs $render_out/rendered_20 --skip 6 --out $proto_out/proto_20.pkl
python src/generate_prototypes/gen_proto_data.py --imgs $render_out/rendered_all --skip 6 --out $proto_out/proto_all.pkl
