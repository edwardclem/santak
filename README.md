# santak

santak; noun. "cuneiform wedge", Foxvog 2016.

Drawing-based lookup app for cuneiform characters. Uses [shape context](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/shape/belongie-pami02.pdf) matching to compute distance between drawn images and reference characters. Reference characters from CuneiformComposite font, provided by the Unicode consortium.
 
Inspired by [ShapeCatcher](http://shapecatcher.com).

# setup/installation

run `conda env create -f environment.yml`

# Prototype generation

TODO

# Usage

Run `./santakgui -p <prototyes file>`

# TODO
A lot of UI improvements, as well as shorter lookup time. It's a bit slow. But probably faster than looking through a sign list. Also, including more characters in the prototypes file - with the current formatting a prototype file with all characters is too large.
