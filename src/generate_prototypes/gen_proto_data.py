#from a folder of rendered characters, generates contours and saves the image,
#its identity, and its contours in a binary file
import numpy as np
import cv2
import pickle
from argparse import ArgumentParser
from sys import argv
import glob
import os


def parse(args):
    parser = ArgumentParser()
    parser.add_argument("--imgs", help="folder with location of rendered images")
    parser.add_argument("--skip", help="skipping interval", type=int)
    parser.add_argument("--out", help="location of output pickle file")
    return parser.parse_args(args)


def reduce_contours(contours, step=6):
    '''
    keeps every step points, removes the rest. Alternative to probabilistic subsampling.
    TODO: do this on data processing instead of after loading.
    TODO: add min threshold?
    '''
    reduced_contours = []
    for contour in contours:
        total_points = contour.shape[0]
        kept_idx = np.arange(0, total_points, step)
        reduced_contours.append(contour[kept_idx, :, :])

    return reduced_contours

def load_imgs(folder):
    print("loading prototypes from {}".format(folder))
    filenames = glob.glob("{}/*.png".format(folder))

    char_ids = [os.path.basename(filename).split(".")[0] for filename in filenames]
    imgs = [cv2.imread(filename) for filename in filenames]
    return char_ids, imgs


def gen_contour(img):
    '''
    Runs canny edge detector on image, then outputs contours.
    '''
    edges = cv2.Canny(img, img.shape[0], img.shape[1])
    _, cnt, _  = cv2.findContours(edges, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # contour = np.concatenate(cnt)

    return cnt

def run(args):

    char_ids, imgs = load_imgs(args.imgs)

    contours = [gen_contour(img) for img in imgs]

    #reduce all_contours_target
    contours = [reduce_contours(contour, step=args.skip) for contour in contours]

    #saves as pickle file
    id2img = {char_id:img for char_id, img in zip(char_ids, imgs)}
    id2contour = {char_id:contour for char_id, contour in zip(char_ids, contours)}

    output_dict = {"id2img":id2img, "id2contour":id2contour}

    with open(args.out, 'wb') as outfile:
        pickle.dump(output_dict, outfile, protocol=pickle.HIGHEST_PROTOCOL)

    print("saved data to {}".format(args.out))


if __name__=="__main__":
    run(parse(argv[1:]))
