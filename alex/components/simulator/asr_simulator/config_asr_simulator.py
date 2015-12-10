#!/usr/bin/env python
# vim: set fileencoding=UTF-8 filetype=python :
#
#  When the configuration file is loaded, several automatic transformations
#  are applied:
#
# 1) '{cfg_abs_path}' as a substring of atomic attributes is replaced by
#    an absolute path of the configuration files.  This can be used to
#    make the configuration file independent of the location of programs
#    using the configuration file.
#
# or better user use the as_project_path function

import random

# Initialise the generators so that the NLG sample different templates every
# time you start the system.

random.seed()

from alex.utils.config import as_project_path, online_update

from alex.utils.database.python_database import PythonDatabase
from alex.components.simulator.user_simulator.simple_user_simulator import SimpleUserSimulator

config = {
    'database':{
        'type':PythonDatabase,
        'debug':True,
        'PythonDatabase':{
            'files':[as_project_path('applications/PublicTransportInfoEN/data/thanh_data/stops.txt'),
                    as_project_path('applications/PublicTransportInfoEN/data/thanh_data/streets.txt'),
                    as_project_path('applications/PublicTransportInfoEN/data/thanh_data/vehicles.txt'),
                    as_project_path('applications/PublicTransportInfoEN/data/thanh_data/time.txt'),
                    as_project_path('applications/PublicTransportInfoEN/data/thanh_data/cities.txt'),
                    as_project_path('applications/PublicTransportInfoEN/data/thanh_data/time_relative.txt'),
                    as_project_path('applications/PublicTransportInfoEN/data/thanh_data/places.txt'),
                    ],
                    
        },
    },
    'domain':{#probably like the configuration for suser simulator
    },
    'user_simulator':{
        'type': SimpleUserSimulator,
        'SimpleUserSimulator':{
            
        },
    },
    'asr_simulator':{
        'type': None,
        'debut': True,
        'SimpleASRSimulator':{
            'act_confusion':{
                'inform':{
                    'inform': 0.5,
                    'silence': 0.25,
                    ('inform', 'request'): 0.25,
                },
                'affirm':{
                    'affirm': 0.95,
                    'negate': 0.05,
                },
                'negate':{
                    'negate': 0.95,
                    'affirm': 0.05,
                },
            },
            'slot_confusion':{
                'to_stop_fake':{
                    'to_stop': 0.5,
                    ('departure', 'arrival'): 0.5,
                },
            },
            'information_confusion_types': ['correct', 'onlist', 'offlist', 'silence'],#only for imagining
            'default':{#define ASR simulator for a slot, the key default will be apply foo all slots are not specified explicitly
                #default for all informatin confusion and prob. gnerator
                'default_confusion_matrix':{
                    'max_length': 5,
                    'onlist_fraction_alpha': 0.75,
                    'onlist_fraction_beta': 1.5,
                    'confusion_types':{#confusion type for information in an action, default for all actions wihout configuration
                        'correct': 0.9,#meaning that the correction information will be still corret at 90%, highest prob on the hyp list
                        'onlist': 0.05,#The correct information is on the hyp. list but smaller prob.
                        'offlist': 0.05,#the correct information is off the hyp.list
                        'silence': 0.0,#the slot is ignored this time, and the respective action will becom silence
                    },
                    'probability_generator':{#using dicrehet for generator probability
                        'correct':{#the confution type = correct
                            'correct':6.0, #the part for the correct item
                            'onlist': 1.0, #the part for other items on the list of hypotheses
                            'offlist': 3.0, #the part for the osther items which are not on the list
                        },
                        'onlist':{
                            'correct':2.5,
                            'onlist':1.0,
                            'offlist':2.5,
                        },
                        'offlist':{
                            'correct':3.0,
                            'onlist':1.0,
                            'offlist':0.6,
                        },
                    },
                },
                'inform_confusion_matrix':{#a refined confusion matrix for inform action
                    'confusion_types':{
                        'correct': 0.9,
                        'onlist': 0.05,
                        'offlist': 0.05,
                    },
                    #the default_prob.generator is missing the default one should be used
                },
            },#end of the default consusion for all slots
            'slot_name':{
                'default_confusion_matrix':{
                    'confusion_types':{
                        #something goes here
                    },
                    'probability_generator':{
                        #something goes here
                    },
                },
                'inform_confusion_matrix':{
                    
                }
            }#end of the confusion descrip for slot_name
        },#end of SimpleUserSimulator
    },#end of asr_simulator
}
