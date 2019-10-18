#!/bin/bash


luigi --module santak.datagen.workflow GenerateContoursForCodeRange \
      --local-scheduler \
      --outdir data \
      --start-code-point 73728 \
      --end-code-point 74649 \
      --font-path data/resources/CuneiformComposite.ttf \
