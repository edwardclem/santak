# santak

santak; noun. "cuneiform wedge", Foxvog 2016.

Drawing-based lookup app for cuneiform characters. Uses [shape context](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/shape/belongie-pami02.pdf) matching to compute distance between drawn images and reference characters. Reference characters from CuneiformComposite font, provided by the Unicode consortium.
 
Inspired by [ShapeCatcher](http://shapecatcher.com).

# setup/installation

All dependencies can be handled by the [Conda](https://docs.conda.io/en/latest/miniconda.html) package manager. Install Conda, then run:  `conda env create -f environment.yml`

To use the prototype generation workflow below, run `pip install -e .` from within the directory.

# Prototype generation

Prototype images for shape matching are created using the [Luigi](http://luigi.readthedocs.io) workflow found in `santak/datagen` that renders characters in the Cuneiform unicode code block and produces contours using a Canny edge filter. See `scripts/aggregate.sh` for a usage example. 

# Usage

Run `./santakgui -p <prototyes file>`

# TODO
    - UI Improvements
    - Speed/parallelization
    - Catching OpenCV errors
