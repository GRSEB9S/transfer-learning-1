
import matplotlib.pyplot as plt
import numpy as np
import os

from data_processing import DataProcessing
import utils

import logging
logging.basicConfig(format='%(levelname)-6s: %(name)-10s %(asctime)-15s  %(message)s')
log = logging.getLogger("TransferLearningDisplay")
log.setLevel(logging.INFO)


class TransferLearningDisplay:
    def __init__(self, similarity_measure):
        self.similarity = similarity_measure
        self.fig = None
        self.axis = None
        self.info_axis = None
        self.info_text = None
        self.sub_windows = None

    def show(self, fingerprints):
        plt.show(block=False)
        plt.ion()

        self.similarity.calculate(fingerprints)

        self.fig = plt.figure(1, figsize=[10, 6])
        plt.gcf()
        self.axis = plt.axes([0.05, 0.05, 0.45, 0.45])

        self.axis_closest = plt.axes([0.5, 0.01, 0.2, 0.2])
        self.axis_closest.set_xticks([])
        self.axis_closest.set_yticks([])
        self.axis_closest.set_xlabel('')
        self.axis_closest.set_ylabel('')
        self._data_closest = self.axis_closest.imshow(np.zeros((224, 224)))

        self.similarity.display(self.axis)

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
        self.sub_data = []
        for row in range(3):
            for col in range(3):
                # rect = [left, bottom, width, height]
                tt = plt.axes([0.5 + 0.14 * col, 0.75 - 0.25 * row, 0.2, 0.2])
                tt.set_xticks([])
                tt.set_yticks([])
                sd = tt.imshow(np.zeros((224, 224)))
                self.sub_windows.append(tt)
                self.sub_data.append(sd)
        plt.show(block=False)

    def _update_text(self, thetext):
        self.info_text.set_text(thetext)
        plt.draw()

    def _onmove(self, event):
        log.debug('Moving to {}'.format(event))
        if event.inaxes == self.axis:
            point = event.ydata, event.xdata
            close_fingerprint = self.similarity.find_similar(point, n=1)[0][1]

            log.debug('Closest fingerprints {}'.format(close_fingerprint))

            row = close_fingerprint['row_min'], close_fingerprint['row_max']
            col = close_fingerprint['col_min'], close_fingerprint['col_max']

            self._data_closest.set_data(utils.rgb2plot(
                close_fingerprint['tldp'].display(row, col)
            ))

            thetitle = close_fingerprint['tldp'].filename.split('/')[-1]
            thetitle += ' ' + ','.join([repr(x) for x in close_fingerprint['tldp'].data_processing])

            self.axis_closest.set_title(thetitle, fontsize=8)
            self.fig.canvas.blit(self.axis_closest.bbox)
            self.axis_closest.redraw_in_frame()

    def _onclick(self, event):
        """
        Mouse click event in the matplotlib window.

        :param event:
        :return:
        """
        log.debug('Clicked {}'.format(event))

        # Click in the similarity axis
        if event.inaxes == self.axis:
            point = event.ydata, event.xdata

            # Find all the similar data relative to the point that was clicked.
            self._update_text('Loading data...')
            close_fingerprints = self.similarity.find_similar(point)

            # Run through all the close fingerprints and display them in the sub windows
            self._update_text('Displaying result...')
            for ii, (distance, fingerprint) in enumerate(close_fingerprints):

                # Zero out and show we are loading -- should be fast.3
                self.sub_windows[ii].set_title('Loading...', fontsize=8)
                self.sub_data[ii].set_data(np.zeros((224, 224)))
                self.sub_windows[ii].redraw_in_frame()

                row = fingerprint['row_min'], fingerprint['row_max']
                col = fingerprint['col_min'], fingerprint['col_max']

                # Show new data and set title
                self.sub_data[ii].set_data(utils.rgb2plot(
                    fingerprint['tldp'].display(row, col)
                ))

                thetitle = fingerprint['tldp'].filename.split('/')[-1] + ' ' + ','.join(
                    [repr(x) for x in fingerprint['tldp'].data_processing])

                # Update the title on the window
                self.sub_windows[ii].set_title('{:0.3f} {}'.format(
                    distance, thetitle), fontsize=8)
                self.sub_windows[ii].redraw_in_frame()

            self._update_text('Click in the tSNE plot...')

    def _display_for_subwindow(self, index, aa):
        """
        Display the data in the subwindow

        :param index:
        :param aa:
        :return:
        """

        distance, fingerprint = aa

        # Zero out and show we are loading -- should be fast.3
        log.debug('Displaying fingerprint {}'.format(index))
        self.sub_windows[index].set_title('Loading...', fontsize=8)
        self.sub_data[index].set_data(np.zeros((224, 224)))
        self.sub_windows[index].redraw_in_frame()

        # Show new data and set title
        self.sub_data[index].set_data(utils.rgb2plot(
            fingerprint['data'].display(fingerprint['filename'],
                                        fingerprint['row'],
                                        fingerprint['col'])
        ))
        self.sub_windows[index].set_title('{:0.3f} {}'.format(
            distance,
            os.path.basename(fingerprint['filename'])), fontsize=8)

        self.sub_windows[index].redraw_in_frame()

