import luigi
import matplotlib.pyplot as plt
import matplotlib.font_manager as mfm
from pathlib import Path
from tqdm import tqdm
import cv2
import pickle
from santak.vision import reduce_contours


class RenderCharTask(luigi.Task):
    outdir = luigi.Parameter()
    code_point = luigi.IntParameter()
    font_path = luigi.Parameter()
    dpi = luigi.IntParameter(default=96)
    img_size = luigi.IntParameter(default=400)
    font_size = luigi.IntParameter(default=150)

    def run(self):
        self.output().makedirs()

        prop = mfm.FontProperties(fname=self.font_path)  # find this font

        uchar = chr(self.code_point)

        plt.figure(figsize=(self.img_size / self.dpi, self.img_size / self.dpi))
        plt.axis("off")
        plt.text(
            0.5,
            0.5,
            s=uchar,
            fontproperties=prop,
            fontsize=150,
            horizontalalignment="center",
            verticalalignment="center",
        )
        plt.savefig(self.output().path)
        plt.close()

    def output(self):

        font = Path(self.font_path)

        return luigi.LocalTarget(
            "{}/imgs/{}_{}_{}_dpi_{}_{}.png".format(
                self.outdir,
                self.code_point,
                font.stem,
                self.dpi,
                self.img_size,
                self.font_size,
            )
        )


class GenerateContoursForCodeRange(luigi.Task):
    outdir = luigi.Parameter()
    start_code_point = luigi.IntParameter()
    end_code_point = luigi.IntParameter()
    font_path = luigi.Parameter()
    dpi = luigi.IntParameter(default=96)
    img_size = luigi.IntParameter(default=300)
    font_size = luigi.IntParameter(default=150)
    keep_every = luigi.IntParameter(default=5)  # removing every nth contour point

    def requires(self):
        return {
            code_point: RenderCharTask(
                self.outdir,
                code_point,
                self.font_path,
                self.dpi,
                self.img_size,
                self.font_size,
            )
            for code_point in range(self.start_code_point, self.end_code_point + 1)
        }

    def run(self):

        self.output().makedirs()

        codepoint_to_img = {
            code_point: cv2.imread(inp.path)
            for code_point, inp in tqdm(self.input().items())
        }

        codepoint_to_contour = {}

        for codepoint, img in tqdm(codepoint_to_img.items()):
            edges = cv2.Canny(img, img.shape[0], img.shape[1])
            _, contours, _ = cv2.findContours(
                edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )

            codepoint_to_contour[codepoint] = reduce_contours(contours, self.keep_every)

        output_dict = {"id2img": codepoint_to_img, "id2contour": codepoint_to_contour}

        with open(self.output().path, "wb") as outfile:
            pickle.dump(output_dict, outfile, protocol=pickle.HIGHEST_PROTOCOL)

    def output(self):
        font = Path(self.font_path)

        return luigi.LocalTarget(
            "{}/contours/{}_{}_to_{}_{}_dpi_{}_{}_reduced_{}.pkl".format(
                self.outdir,
                self.start_code_point,
                self.end_code_point,
                font.stem,
                self.dpi,
                self.img_size,
                self.font_size,
                self.keep_every,
            )
        )
