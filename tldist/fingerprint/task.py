import sys
import logging
import time
import uuid
from collections import OrderedDict
import itertools

from celery import group
import numpy as np
import json
import requests
import imageio
from io import BytesIO

from tlapi.data.api import get as get_data
from tlapi.data.api import get_array as get_array_data
from tldist.celery import app

from tldist.fingerprint.processing import Fingerprint
from tldist.fingerprint.processing import calculate as processing_calculate

FORMAT = '%(levelname)-8s %(asctime)-15s %(name)-10s %(funcName)-10s %(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger('fingerprint')
log.setLevel(logging.DEBUG)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def calculate_celery(data, fc_save):
    """
    This function will queue up all the jobs and run them using celery.
    """

    # Queue up and run
    job = group([
        calculate.s(tt, fc_save) for tt in chunks(data, len(data)//4)
    ])
    result = job.apply_async()

    # Dispaly progress
    counts = OrderedDict({x.id: 0 for x in result.children})
    while not result.ready():
        time.sleep(0.1)
        for x in result.children:
            if x.state == 'PROGRESS' and hasattr(x, 'info') and 'progress' in x.info:
                counts[x.id] = x.info['progress']

        print('\rCalculating fingerprints: {}'.format([v for k,v in counts.items()]), end='')

    # Get the results (is a list of lists so need to compress them)
    r =  result.get()

    return list(itertools.chain(*r))

@app.task
def calculate_task(data, fc_save):
    return processing_calculate(data, fc_save)
