#!/bin/bash


luigi --module santak.datagen.workflow RenderCharTask \
      --local-scheduler \
      --outdir data \
      --code-point 73728 \
      --font-path data/resources/CuneiformComposite.ttf \
