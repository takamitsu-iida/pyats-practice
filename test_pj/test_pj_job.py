'''
test_pj_job.py

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/easypy/jobfile.html
# for how job files work

# optional author information
# (update below with your contact information if needed)
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2019, Cisco Systems Inc.'
__contact__ = ['pyats-support-ext@cisco.com']
__credits__ = ['list', 'of', 'credit']
__version__ = 1.0

import os
from pyats.easypy import run

# compute the script path from this location
SCRIPT_PATH = os.path.dirname(__file__)

def main(runtime):
    '''job file entrypoint'''
    
    # run script
    run(testscript= os.path.join(SCRIPT_PATH, 
                                 'test_pj.py'),
        runtime = runtime)
