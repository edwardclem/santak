#!/bin/bash

# anything beyond 74606 fails to render.

luigi --module santak.datagen.workflow GenerateContoursForCodeRange \
      --local-scheduler \
      --outdir data \
      --start-code-point 73728 \
      --end-code-point 74606 \
      --font-path data/resources/CuneiformComposite.ttf \
      --keep-every 10
