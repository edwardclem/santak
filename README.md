# santak

santak; noun. "cuneiform wedge", Foxvog 2016.

Drawing-based lookup app for cuneiform characters. Uses [shape context](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/shape/belongie-pami02.pdf) matching to compute distance between drawn images and reference characters. Reference characters from CuneiformComposite font, provided by the Unicode consortium.

Requires [OpenCV3](https://opencv.org/about.html) and [PyQT5](http://pyqt.sourceforge.net/Docs/PyQt5/) libraries. Inspired by [ShapeCatcher](http://shapecatcher.com).

#usage

Run `python santak.py`

#TODO
A lot of UI improvements, as well as shorter lookup time. It's a bit slow. But probably faster than looking through a sign list. 
