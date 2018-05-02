import uuid
import shutil
from collections import OrderedDict
import pickle
import time

from celery import group
from tldist.fingerprint.task import calculate_celery
from tldist.similarity.task import similarity_celery
import os.path

def stringify(dictionary):
    return {k: str(v) for k, v in dictionary.items()}

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

from transfer_learning.fingerprint import FingerprintResnet
fresnet = FingerprintResnet()
fc_save = fresnet.save()

# Load the data
filename_prepend = 'http://18.218.192.161:4123/ACSimages/'
processing_dict = pickle.load(open('hubble_acs.pck', 'rb'))

data = []
for fileinfo in processing_dict[:100]:
    im = {
        'uuid': str(uuid.uuid4()),
        'location': fileinfo['location'],
        'radec': fileinfo['radec'],
        'meta': stringify(fileinfo['meta'])
        }
    #data_client.save(im)
    data.append(im)

fingerprints = calculate_celery(data, fc_save)

#fingerprints = fingerprint_client.get() 
#print('fingerprint pks {}'.format([str(x[db.key]) for x in fingerprints]))

similarity_tsne = similarity_celery(fingerprints, 'tsne')
 
similarity_jaccard = similarity_celery(fingerprints, 'tsne')

#print('Going to calculate the similarity')
#simres = similarity_client.calculate([str(x[db.key]) for x in fingerprints], 'tsne')
#
#time.sleep(2)
#
#print('Going to calculate the similarity jaccard')
#simres = similarity_client.calculate([str(x[db.key]) for x in fingerprints], 'jaccard')
#
#print('Waiting 3 seconds...')
#time.sleep(3)
#
## Get all similarities
#sims = similarity_client.get()
#print('All similarities {} {}'.format(len(sims), sims))
