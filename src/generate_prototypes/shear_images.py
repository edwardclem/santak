#producing shear-transformed images

from argparse import ArgumentParser
from skimage import io
import skimage.transform as tform
from sys import argv
import os
import numpy as np


def parse(args):
    parser = ArgumentParser()
    parser.add_argument("--in_img", help="folder with images to be sheared")
    parser.add_argument("--out_img", help="folder of output images")
    parser.add_argument("--shear_range", nargs="*", help="lowest shear val, highest val, step")
    return parser.parse_args(args)

#produces a sheared image from the given input path
def make_shear_img(input_path, output_path, shear_param):
    img = io.imread(input_path)
    affine_tf = tform.AffineTransform(shear=shear_param)
    modified = tform.warp(img, affine_tf, cval=1.0)
    io.imsave(output_path, modified)
    print "saved to {}".format(output_path)

def run(args):
    shear_range = [float(num) for num in args.shear_range]
    for img in os.listdir(args.in_img):
        i = 0
        for shear_param in np.arange(*shear_range):
            filename, extension = os.path.splitext(img)
            if extension == ".jpeg": #get rid of DS_store or whatever
                infile = "{}/{}".format(args.in_img, img)
                outfile = "{}/{}_{}.jpeg".format(args.out_img, filename, i)
                make_shear_img(infile, outfile, shear_param)
                i += 1



if __name__=="__main__":
    run(parse(argv[1:]))
