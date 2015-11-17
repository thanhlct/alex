#----------for testing---------------
if __name__ == '__main__':
    import autopath

import random

from alex.components.simulator.base import UserSimulator
from alex.utils.database.python_database import PythonDatabase
from alex.components.slu.da import DialogueActItem, DialogueActConfusionNetwork, DialogueAct

from alex.utils.sample_distribution import sample_from_list, sample_from_dict
import alex.utils.matlab_functions as matlab

class SimpleUserSimulator(UserSimulator):
    '''Simple user simulator'''

    def __init__(self, cfg, db):
        '''Initilise'''
        self._config = cfg.config['user_simulator']
        self.db = db
        self.goal = None
        self.metadata = self.get_metadata(self._config)
        self._goal_dist = self._get_goal_distribution()

    def _get_goal_distribution(self):
        goals = self.metadata['goals']
        d = {}
        for i in range(len(goals)):
            d[i] = goals[i]['prob']
        return d

    def new_dialogue(self):
        '''Start a new dialogue
        Sample a new user goal. Reset everything for simulating a new dialogue
        '''
        self.goal = self._get_random_goal()

    def _get_random_goal(self):
        '''Return a random final goal of user'''
        goal_id = sample_from_dict(self._goal_dist)
        goal_des = self.metadata['goals'][goal_id]
        goal = {}
        sampled_slots = []

        for s, v in goal_des['fixed_slots']:#fixed slots
            goal[s] = v
            sampled_slots.append(s)

        for key in goal_des['same_table_slot_keys']:#same table slots NOTE same_table_slot was coded without testing since data hadn't faked yet
            same = self.metadata['same_table_slots'][key]
            table = same['table']
            fields = self.db.get_field_list(table)
            row = self.db.get_random_row(table)
            for slot in same['slots']:
                sampled_slots.append(slot)
                fid = self._get_field_name(slot, table)
                fid = fields.index(fid)
                goal[slot] = row[fid]

        sampled_slots.extend(goal_des['sys_unaskable_slots'])
        remain_slots = matlab.sub(goal_des['changeable_slots'], sampled_slots)
        print remain_slots
        pdb.set_trace()
        for slot in remain_slots:#changeable slots
            tables_fields = self._get_slot_mapping(slot)
            print [slot, tables_fields]
            continue
            lst = []
            for tb, f in tables_fields:
                lst.extend(self.db.get_field_values(tb, f))
            goal[slot] = sample_from_list(lst) 
            
        pdb.set_trace()
        return goal
    def _get_field_name(self, slot, table):
        mapping = self._get_slot_mapping(slot)
        for tb, f in mapping:
            if tb==table:
                return f
        assert True, "There is no table=%s in the slot_table_field_mapping definition of the slot=%s"%(table, slot)
    def _get_slot_mapping(self, slot):
        assert slot in self.metadata['slot_table_field_mapping'].keys(), "Have not defined the slot_table_field_mapping for the slot=%s"%(slot)
        return self.metadata['slot_table_field_mapping'][slot]  

    def da_in(self, da):
        '''Recieve a system dialogue act'''
        pass
    def da_out(self):
        '''Samples and returns a user dialogue act based on user's current state and given system dialogue act'''
        pass
    def reward_last_da(self):
        '''Rewards the last system dialgoue act'''
        pass
    def reward_final_goal(self):
        '''Return final reward for the current dialouge'''
        pass
    def end_dialogue(self):
        '''end dialgoue and post-processing'''
        pass
    def get_metadata(self, cfg):#This metadata is for user simulator, and the content is for specific apps
        metadata = {
            'slots': ['departure_from', 'go_to', 'departure_time', 'departure_date', 'arrival_time', 'arrival_date',
                    'vihecle', 'arrival_time_relative', 'depature_time_relative', 'number_transfers', 'duration',' distance',
                    'street', 'city', 'state',#three last slot only for clarifying when there is an ambiguitous in departure/arrival places
                ],#only for easy seeing and imagining, not being used in coding
            'goals': [
                    {'fixed_slots':[('task','find_connection'),],
                    'changeable_slots':['departure_from', 'go_to', 'departure_time', 'arrival_time',
                                    'departure_date', 'arrival_date', 'vihecle', 'arrival_time_relative', 'departure_time_relative',
                                    'number_transfers', 'duration', 'distance',
                            ],
                    'sys_unaskable_slots':['number_transfers', 'duration', 'distance'],
                    'prob':0.8,#probability of observing the task being active
                    'same_table_slot_keys':[]#defining when serveral slots connected to a row in a table and we would like to get them linked together
                    },
                    {'fixed_slots':[('task','find_platform'),],
                    'changeable_slots':['street', 'city', 'state'],
                    'sys_unaskable_slots':[],
                    'prob':0.15,
                    'same_table_slot_keys': ['place'],
                    },
                    {'fixed_slots':[('task','weather'),],
                    'changeable_slots':['city', 'state'],
                    'sys_unaskable_slots':[],
                    'prob':0.05,
                    'same_table_slot_keys':['place'],
                    },
                ],
            'slot_table_field_mapping':{'departure_from':[('stops','stop'), ('streets','street')],
                                        'go_to':[('stops', 'stop'),('streets','street')],
                                        'departure_time':[('time', 'time')],
                                        'arrival_time': [('time', 'time')],
                                        'vihecle': [('vihecles', 'vihecle')],
                                        'street':[('streets', 'street')],
                                        'city':[('cities', 'city')],
                                        'state':[('states', 'state')],
                                    },
            'same_table_slots':{'place':{'table': 'places',
                                        'slots': ['street', 'city', 'state'],
                                    },
                                'from_place':{'table':'places',#just for future when whe have such data.
                                        'slots': ['from_stop', 'from_street', 'from_city', 'from_state'],
                                    },
                                'to_place':{'table':'places',
                                        'slots': ['to_stop', 'to_street', 'to_city', 'to_state'],
                                }
                            },
            'dialogue_acts': {
                'request':[],
                'inform':[],
            },
            'reply_system_acts':{
                'request':{'inform':0.8, 'silence': 0.1, 'oog': 0.1},
            },
            'probabilities':{
                'request':{
                    'inform':{
                        'over_answer':0.6,
                        #something else here for ASR simulator etc.
                    }
                }
            }

        }
        return metadata
    #-------------definetion for specific apps
    
#----------for testing---------------
if __name__ == '__main__':
    import autopath
import pdb
from alex.utils.config import Config

cfg = None

def get_config():
    global cfg
    #pdb.set_trace()
    cfg = Config.load_configs(['../../../applications/PublicTransportInfoEN/ptien.cfg', '../../../applications/PublicTransportInfoEN/simulator.cfg'])
    cfg['Logging']['system_logger'].info("Voip Hub\n" + "=" * 120)

def test_user_goal(user, n):
    for i in range(n):
        user.new_dialogue()
        print user.goal
        break

def run1():
    db = PythonDatabase(cfg)
    user = SimpleUserSimulator(cfg, db)
    test_user_goal(user, 30)

def main():
    get_config()
    run1()

if __name__ == '__main__':
    main()
