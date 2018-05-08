import time
from collections import OrderedDict
import itertools

from celery import group

from tldist.celery import app
from tldist.fingerprint.processing import calculate as processing_calculate

from ..tl_logging import get_logger
log = get_logger('fingerprint task')


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def calculate_celery(cutouts, fc_save):
    """
    This function will queue up all the jobs and run them using celery.
    """

    # Queue up and run
    job = group([
                    calculate_task.s(tt, fc_save)
                    for tt in chunks(cutouts, len(cutouts) // 2)
                ])
    result = job.apply_async()

    # Dispaly progress
    counts = OrderedDict({x.id: 0 for x in result.children})
    while not result.ready():
        time.sleep(0.1)
        for x in result.children:
            if (x.state == 'PROGRESS' and hasattr(x, 'info') and
                    'progress' in x.info):
                counts[x.id] = x.info['progress']

        states_complete = [int(v) for k, v in counts.items()]
        print('\rCalculating fingerprints: {} {:.1f}%'.format(
            states_complete, sum(states_complete)/len(cutouts)*100), end='')

    # Get the results (is a list of lists so need to compress them)
    r = result.get()
    return list(itertools.chain(*r))


@app.task
def calculate_task(cutouts, fc_save):
    log.debug('app.current_task {}'.format(app.current_task))
    return processing_calculate(cutouts, fc_save, task=app.current_task)
