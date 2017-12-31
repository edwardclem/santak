#!/bin/bash

#prototype data generation pipeline

render_out_20=data/rendered/rendered_20
proto_out_20=data/prototypes/proto_20
fontpath=generate_prototypes/resources/CuneiformComposite.ttf

python generate_prototypes/render_chars.py --outf $render_out_20 --max_code 73748 --font $fontpath
python generate_prototypes/gen_proto_data.py --imgs $render_out_20 --out $proto_out_20
