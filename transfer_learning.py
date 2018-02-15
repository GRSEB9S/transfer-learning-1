from similarity import tSNE
from matplotlib import pyplot as plt
import os
import utils
import glob

import logging
logging.basicConfig(format='%(levelname)-6s: %(name)-10s %(asctime)-15s  %(message)s')
log = logging.getLogger("TransferLearning")
log.setLevel(logging.INFO)


# class TransferLearningDisplay:
#
#     def __init__(self):
#         self.tsne_similarity = None
#         self.fig = None
#         self.axis = None
#         self.info_axis = None
#         self.info_text = None
#         self.sub_windows = None
#
#     def display(self, fingerprints):
#         plt.show(block=False)
#
#         self.tsne_similarity = tSNE(fingerprints)
#         self.tsne_similarity.calculate(fingerprints)
#
#         self.fig = plt.figure(1)
#         plt.gcf()
#         self.axis = plt.axes([0.05, 0.05, 0.45, 0.45])
#
#         self.axis_closest = plt.axes([0.5, 0.01, 0.2, 0.2])
#         self.axis_closest.set_xticks([])
#         self.axis_closest.set_yticks([])
#         self.axis_closest.set_xlabel('')
#         self.axis_closest.set_ylabel('')
#
#         self.tsne_similarity.displayY(self.axis)
#
#         self.info_axis = plt.axes([0.60, 0.02, 0.3, 0.05])
#         self.info_axis.set_axis_off()
#         self.info_axis.set_xticks([])
#         self.info_axis.set_yticks([])
#         self.info_axis.set_xlabel('')
#         self.info_axis.set_ylabel('')
#         self.info_text = self.info_axis.text(0, 0, '', fontsize=12)
#
#         self._cid = self.fig.canvas.mpl_connect('button_press_event', self._onclick)
#         self.fig.canvas.mpl_connect('motion_notify_event', self._onmove)
#
#         self.sub_windows = []
#         for row in range(3):
#             for col in range(3):
#                 # rect = [left, bottom, width, height]
#                 tt = plt.axes([0.5 + 0.14 * col, 0.75 - 0.25 * row, 0.2, 0.2])
#                 tt.set_xticks([])
#                 tt.set_yticks([])
#                 self.sub_windows.append(tt)
#         plt.show(block=False)
#
#     def _update_text(self, thetext):
#         self.info_text.set_text(thetext)
#         plt.draw()
#
#     def _onmove(self, event):
#         if event.inaxes == self.axis:
#             point = event.ydata, event.xdata
#             close_fingerprint = self.tsne_similarity.find_similar(point, n=1)[0][1]
#
#             self.axis_closest.imshow(utils.rgb2plot(
#                 close_fingerprint['data'].display(close_fingerprint['filename'],
#                                                   close_fingerprint['row_center'],
#                                                   close_fingerprint['column_center'])
#             ))
#             plt.show(block=False)
#             plt.pause(0.0001)
#
#     def _onclick(self, event):
#         point = event.ydata, event.xdata
#         self.axis.cla()
#         self.tsne_similarity.displayY(self.axis)
#
#         self._update_text('Loading data...')
#         close_fingerprints = self.tsne_similarity.find_similar(point)
#
#         self._update_text('Displaying result...')
#         for ii, (distance, fingerprint) in enumerate(close_fingerprints):
#             self.sub_windows[ii].imshow(utils.rgb2plot(
#                 fingerprint['data'].display(fingerprint['filename'],
#                                             fingerprint['row_center'],
#                                             fingerprint['column_center'])
#             ))
#             self.sub_windows[ii].set_title('{:0.3f} {} ({}, {})'.format(
#                 distance,
#                 os.path.basename(fingerprint['filename']),
#                 fingerprint['row_center'],
#                 fingerprint['column_center']), fontsize=8)
#
#         self._update_text('Click in the tSNE plot...')
#
#         plt.show(block=False)
#         plt.pause(0.001)
#
#
# if __name__ == "__main__":
#     #input_fingerprints = '/tmp/resnet/data_be633177-2923-423f-bc7e-846d7647cf4d.pck'
#     input_fingerprints = '/tmp/hst_heritage_gray/*.pck'
#
#     filenames  = glob.glob(input_fingerprints)
#
#     fingerprints = []
#     for filename in filenames:
#         data = Data.load(filename)
#         fingerprints.extend(data.fingerprints)
#
#     tl = TransferLearning()
#     tl.display(fingerprints)


import uuid
import numpy as np
import pickle
import imageio
from astropy.io import fits
import progressbar
import itertools
import os

import matplotlib.pyplot as plt

from data_processing import DataProcessing
from fingerprint import Fingerprint
import utils

import logging
logging.basicConfig(format='%(levelname)-6s: %(name)-10s %(asctime)-15s  %(message)s')
log = logging.getLogger("Data")
log.setLevel(logging.INFO)


class TransferLearning:
    def __init__(self, fingerprint_calculator=None, data_processing=[]):
        # list of data processing elements
        self._data_processing = data_processing
        self._fingerprint_calculator = fingerprint_calculator
        self._filenames = []
        self._fingerprints = []
        self._uuid = str(uuid.uuid4())

        self._data_cache = {}

    def _load_image_data(self, filename):
        if any(filename.lower().endswith(s) for s in ['tiff', 'tif', 'jpg']):
            log.debug('Loading TIFF/JPG file {}'.format(filename))
            data = np.array(imageio.imread(filename))
        elif 'fits' in filename:
            log.debug('Loading FITS file {}'.format(filename))
            data = fits.open(filename)[1].data
            log.debug('FITS data is {}'.format(data))

            data[~np.isfinite(data)] = 0
        else:
            log.warning('Could not determine filetype for {}'.format(filename))
            return []

        # Do the pre-processing of the data
        for dp in self._data_processing:
            log.debug('Doing pre-processing {}, input data shape {}'.format(dp, data.shape))
            data = dp.process(data)
            log.debug('    Now input data shape {}'.format(data.shape))

        # Make RGB (3 channel) if only gray scale (single channel)
        if len(data.shape) == 2:
            data = utils.gray2rgb(data)

        return data

    def set_files(self, filenames):
        self._filenames = filenames

    def display(self, filename, row, col):

        if filename not in self._data_cache:
            self._data_cache[filename] = self._load_image_data(filename)

        return self._data_cache[filename][row-112:row+112, col-112:col+112]
        log.info('Display {} {} {} {}'.format(self, self._data_processing, row, col))

    @property
    def fingerprints(self):
        return self._fingerprints

    def calculate(self, stepsize, display=False):
        """
        Calculate the fingerprints for each subsection of the image in each file.

        :param stepsize:
        :param display:
        :return:
        """

        self._fingerprints = []
        self._stepsize = stepsize

        if display:
            plt.ion()
            fig = plt.figure()
            imaxis = None

        log.debug('After the plot display')
        # Run through each file.
        for filename in self._filenames:
            log.info('Processing filename {}'.format(filename))

            # Load the data
            data = self._load_image_data(filename)

            # Determine the centers to use for the fingerprint calculation
            nrows, ncols = data.shape[:2]
            rows = range(112, nrows-112, stepsize)
            cols = range(112, ncols-112, stepsize)

            # Run over all combinations of rows and columns
            with progressbar.ProgressBar(widgets=[' [', progressbar.Timer(), '] ',
                                                  progressbar.Bar(), ' (', progressbar.ETA(), ') ', ],
                                         max_value=len(rows)*len(cols)) as bar:
                for ii, (row, col) in enumerate(itertools.product(rows, cols)):

                    td = data[row-112:row+112, col-112:col+112]

                    if display:
                        if len(td.shape) == 2:
                            ttdd = utils.gray2rgb(td)
                        else:
                            ttdd = td
                        ttdd = utils.rgb2plot(ttdd)

                        if imaxis is None:
                            print('displaying via imshow')
                            imaxis = plt.imshow(ttdd)
                        else:
                            print('displaying via set_data')
                            imaxis.set_data(ttdd)
                        plt.pause(0.0001)

                    predictions = self._fingerprint_calculator.calculate(td)

                    self._fingerprints.append(
                        {
                            'predictions': predictions,
                            'filename': filename,
                            'row_center': row,
                            'column_center': col
                        }
                    )

        if display:
            plt.close(fig)

        return self._fingerprints

    def save(self, output_directory):
        d = {
            'data_processing': [t.save() for t in self._data_processing],
            'fingerprint_calculator': self._fingerprint_calculator.save(),
            'stepsize': self._stepsize,
            'uuid': self._uuid,
            'filenames': self._filenames,
            'fingerprints': self._fingerprints
        }

        with open(os.path.join(output_directory, 'data_{}.pck'.format(self._uuid)), 'wb') as fp:
            pickle.dump(d, fp)

    def _load(self, input_filename):
        log.info('Loading TL from {}'.format(input_filename))
        with open(input_filename, 'rb') as fp:
            tt = pickle.load(fp)

            self._data_processing = []
            for dp in tt['data_processing']:
                self._data_processing.append(DataProcessing.load_parameters(dp))
            self._fingerprint_calculator = Fingerprint.load_parameters(tt['fingerprint_calculator'])
            self._uuid = tt['uuid']
            self._stepsize = tt['stepsize']
            self._filenames = tt['filenames']
            self._fingerprints = tt['fingerprints']

        log.debug('    data_processing is {}'.format(self._data_processing))
        log.debug('    fingerprint_calcualtor is {}'.format(self._fingerprint_calculator))
        log.debug('    uuid is {}'.format(self._uuid))
        log.debug('    filenames is {}'.format(self._filenames))

    @staticmethod
    def load(input_filename):
        d = TransferLearning()
        d._load(input_filename)
        return d


class TransferLearningDisplay:
    def __init__(self):
        self.tsne_similarity = None
        self.fig = None
        self.axis = None
        self.info_axis = None
        self.info_text = None
        self.sub_windows = None

    def show(self, fingerprints):
        plt.show(block=False)
        plt.ion()

        self.tsne_similarity = tSNE(fingerprints)
        self.tsne_similarity.calculate(fingerprints)

        self.fig = plt.figure(1, figsize=[10, 6])
        plt.gcf()
        self.axis = plt.axes([0.05, 0.05, 0.45, 0.45])

        self.axis_closest = plt.axes([0.5, 0.01, 0.2, 0.2])
        self.axis_closest.set_xticks([])
        self.axis_closest.set_yticks([])
        self.axis_closest.set_xlabel('')
        self.axis_closest.set_ylabel('')
        self.axis_closest.imshow(np.zeros((224, 224)))

        self.tsne_similarity.displayY(self.axis)

        self.info_axis = plt.axes([0.7, 0.11, 0.3, 0.05])
        self.info_axis.set_axis_off()
        self.info_axis.set_xticks([])
        self.info_axis.set_yticks([])
        self.info_axis.set_xlabel('')
        self.info_axis.set_ylabel('')
        self.info_text = self.info_axis.text(0, 0, 'Loading...', fontsize=12)

        self._cid = self.fig.canvas.mpl_connect('button_press_event', self._onclick)
        self.fig.canvas.mpl_connect('motion_notify_event', self._onmove)

        self.sub_windows = []
        for row in range(3):
            for col in range(3):
                # rect = [left, bottom, width, height]
                tt = plt.axes([0.5 + 0.14 * col, 0.75 - 0.25 * row, 0.2, 0.2])
                tt.set_xticks([])
                tt.set_yticks([])
                tt.imshow(np.zeros((224, 224)))
                self.sub_windows.append(tt)
        plt.show(block=False)

    def _update_text(self, thetext):
        print('updateing text to {}'.format(thetext))
        self.info_text.set_text(thetext)
        plt.draw()

    def _onmove(self, event):
        if event.inaxes == self.axis:
            point = event.ydata, event.xdata
            close_fingerprint = self.tsne_similarity.find_similar(point, n=1)[0][1]

            self.axis_closest.imshow(utils.rgb2plot(
                close_fingerprint['data'].display(close_fingerprint['filename'],
                                                  close_fingerprint['row_center'],
                                                  close_fingerprint['column_center'])
            ))
            self.axis_closest.set_title(close_fingerprint['filename'].split('/')[-1], fontsize=8)
            plt.show(block=False)
            plt.pause(0.0001)

    def _onclick(self, event):

        if event.inaxes == self.axis:
            point = event.ydata, event.xdata
            self.axis.cla()
            self.tsne_similarity.displayY(self.axis)

            self._update_text('Loading data...')
            close_fingerprints = self.tsne_similarity.find_similar(point)

            self._update_text('Displaying result...')
            for ii, (distance, fingerprint) in enumerate(close_fingerprints):
                self.sub_windows[ii].imshow(utils.rgb2plot(
                    fingerprint['data'].display(fingerprint['filename'],
                                                fingerprint['row_center'],
                                                fingerprint['column_center'])
                ))
                self.sub_windows[ii].set_title('{:0.3f} {} ({}, {})'.format(
                    distance,
                    os.path.basename(fingerprint['filename']),
                    fingerprint['row_center'],
                    fingerprint['column_center']), fontsize=8)

            self._update_text('Click in the tSNE plot...')

            plt.show(block=False)
            plt.pause(0.001)

if __name__ == "__main__":
    #input_fingerprints = '/tmp/resnet/data_be633177-2923-423f-bc7e-846d7647cf4d.pck'
    input_fingerprints = '/tmp/resnet/*.pck'

    filenames  = glob.glob(input_fingerprints)

    fingerprints = []
    for filename in filenames:
        data = TransferLearning.load(filename)

        temp_fingerprints = data.fingerprints
        for item in temp_fingerprints:
            item.update({'data': data})

        fingerprints.extend(data.fingerprints)

    tld = TransferLearningDisplay()
    tld.show(fingerprints)
