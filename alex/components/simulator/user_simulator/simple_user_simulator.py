#----------for testing---------------
if __name__ == '__main__':
    import autopath
#-------define for specific app--------------
def goal_post_process(user, goal):
    #hand the sematic relation between departure and arrival slots
    return goal

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
        self.goal_id = sample_from_dict(self._goal_dist)
        goal_des = self.metadata['goals'][self.goal_id]
        goal = {}
        sampled_slots = []

        for s, v in goal_des['fixed_slots']:#fixed slots
            goal[s] = v
            sampled_slots.append(s)

        for key in goal_des['same_table_slot_keys']:#same table slots NOTE same_table_slot was coded without testing since data hadn't faked yet
            slots_values = self._get_random_same_table_slots_values(key)
            for slot in slots_values.keys():
                sampled_slots.append(slot)
                goal[slot] = slots_values[slot]

        for one_set in goal_des['one_of_slot_set']:#get value for  one slot set and ignore other slots
            slot_set = sample_from_dict(one_set)
            for slot in slot_set:
                goal[slot] = self._get_random_slot_value(slot)
            for key in one_set.keys():
                sampled_slots.extend(key)

        sampled_slots.extend(goal_des['sys_unaskable_slots'])
        remain_slots = matlab.sub(goal_des['changeable_slots'], sampled_slots)
        for slot in remain_slots:#changeable slots
            goal[slot] = self._get_random_slot_value(slot)
        
        fun = goal_des['goal_post_process_fun']
        if fun is not None:
            goal = fun(self, goal)
        return goal

    def _get_random_same_table_slots_values(self, same_table_key):
        same = self.metadata['same_table_slots'][same_table_key]
        table = same['table']
        row = self._get_random_row(table)
        sv = {}
        for slot in same['slots']:
            field = self._get_field_name(slot, table)
            sv[slot]= self.db.get_row_field_value(table, row, field)
        return sv

    def _get_random_slot_value(self, slot):
        values = []
        tables_fields = self._get_slot_mapping(slot)
        for tb, f in tables_fields:#sample a value of each table which the slot is connected
            row = self._get_random_row(tb)
            values.append(self.db.get_row_field_value(tb, row, f))
        return sample_from_list(values)#take one in the sampled values
        
    def _get_random_row(self, table):
        if table in self.metadata['data_observation_probability'].keys():
            data_dist = self._get_data_distribution(table)
            return sample_from_dict(data_dist)
        else:
            return self.db.get_random_row(table)

    def _get_data_distribution(self, table):
        dist = {}
        tb_dist = self.metadata['data_observation_probability'][table]
        predifined_mass = 0.0
        predifined_row = 0
        for key in tb_dist.keys():
            predifined_mass += tb_dist[key]
            predifined_row += 1
        remaining_mass = 1.0 - predifined_mass
        default_prob = remaining_mass/(self.db.get_row_number(table)-predifined_row)
        for row in self.db.get_row_iterator(table):
            if row in tb_dist.keys():
                dist[row] = tb_dist[row]
            else:
                dist[row] = default_prob
        return dist
        
    def _get_field_name(self, slot, table):
        mapping = self._get_slot_mapping(slot)
        for tb, f in mapping:
            if tb==table:
                return f
        assert False, "There is no table=%s in the slot_table_field_mapping definition of the slot=%s"%(table, slot)
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

    #-----------define for specific app-----------------
    def get_metadata(self, cfg):#This metadata is for user simulator, and the content is for specific apps
        metadata = {
            'slots': ['departure_from', 'go_to', 'departure_time', 'departure_date', 'arrival_time', 'arrival_date',
                    'vihecle', 'arrival_time_relative', 'depature_time_relative', 'number_transfers', 'duration',' distance',
                    'street', 'city', 'state',#three last slot only for clarifying when there is an ambiguitous in departure/arrival places
                ],#only for easy seeing and imagining, not being used in coding
            'goals': [
                    {'fixed_slots':[('task','find_connection'),],
                    'changeable_slots':['departure_from', 'go_to', 'departure_time', 'arrival_time',
                                    'departure_date', 'arrival_date', 'vehicle', 'arrival_time_relative', 'departure_time_relative',
                                    'number_transfers', 'duration', 'distance',
                            ],
                    'one_of_slot_set':[
                        {('arrival_time', 'arrival_time_relative', 'arrival_date'):0.5,#choose only one of these set
                        ('departure_time', 'departure_time_relative', 'departure_date'):0.4,
                        ('arrival_time', 'arrival_time_relative', 'arrival_date', 'departure_time','departure_time_relative', 'departure_date'):0.1,
                        },
                    ],
                    'sys_unaskable_slots':['number_transfers', 'duration', 'distance'],
                    'prob':0.8,#probability of observing the task being active
                    'same_table_slot_keys':[],#defining when serveral slots connected to a row in a table and we would like to get them linked together
                    'goal_post_process_fun': goal_post_process,#post process function to refine the sampled goal, which will be defined for specific semantic relations
                    'goal_slot_relax_fun': None,#support function, relax the value of a slot given curretn goal, e.g. more late arrival, departure sooner    
                    },
                    {'fixed_slots':[('task','find_platform'),],
                    'changeable_slots':['street', 'city', 'state'],
                    'one_of_slot_set':[],
                    'sys_unaskable_slots':[],
                    'prob':0.15,
                    'same_table_slot_keys': ['place'],
                    'goal_post_process_fun': None,
                    'goal_slot_relax_fun': None,
                    },
                    {'fixed_slots':[('task','weather'),],
                    'changeable_slots':['city', 'state'],
                    'one_of_slot_set':[],
                    'sys_unaskable_slots':[],
                    'prob':0.05,
                    'same_table_slot_keys':['place'],
                    'goal_post_process_fun': None,
                    'goal_slot_relax_fun': None,
                    },
                ],
            'slot_table_field_mapping':{'departure_from':[('stops','stop'), ('streets','street')],
                                        'go_to':[('stops', 'stop'),('streets','street')],
                                        'departure_time':[('time', 'time')],
                                        'departure_date':[('date', 'date')],
                                        'departure_time_relative':[('time_relative', 'relative')],
                                        'arrival_time': [('time', 'time')],
                                        'arrival_date': [('date', 'date')],
                                        'arrival_time_relative': [('time_relative', 'relative')],
                                        'vehicle': [('vehicles', 'vehicle')],
                                        'street':[('streets', 'street'), ('places', 'street')],
                                        'city':[('cities', 'city'), ('places', 'city')],
                                        'state':[('states', 'state'), ('places', 'city')],
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
            'probability':{
                'request':{
                    'inform':{
                        'over_answer':0.6,
                        #something else here for ASR simulator etc.
                    },
                },
            },
            'data_observation_probability':{
                'time':{
                    ('now',):0.7,#key is row in the table, if table has only one field, need add comma before the end of tuple
                    ('next hour',):0.02,
                    ('morning',):0.02,
                    ('noon',):0.02,
                    ('afternoon',):0.02,
                    ('night',):0.02,
                },
                'date':{
                    ('today',):0.6,
                    ('tomorrow',):0.025,
                    ('the day after tomorrow',):0.025,
                    ('Monday',):0.01,
                    ('Tuesday',):0.01,
                    ('Wednesday',):0.01,
                    ('Thursday',):0.01,
                    ('Friday',):0.01,
                    ('Saturday',):0.01,
                    ('Sunday',):0.01,
                    ('next Monday',):0.01,
                    ('next Tuesday',):0.01,
                    ('next Wednesday',):0.01,
                    ('next Thursday',):0.01,
                    ('next Friday',):0.01,
                    ('next Saturday',):0.01,
                    ('next Sunday',):0.01,
                    ('Monday next week',):0.01,
                    ('Tuesday next week',):0.01,
                    ('Wednesday next week',):0.01,
                    ('Thursday next week',):0.01,
                    ('Friday next week',):0.01,
                    ('Saturday next week',):0.01,
                    ('Sunday next week',):0.01,
                },
            },
            #TODO some of value in a slot can only be combined with a specific values of other slot, It shoud be push in a table but .... sometime exception
            #TODO values for a slot can be generate dynamically from a function
        }#end of metadata
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
        raw_input()
        #break

def run1():
    db = PythonDatabase(cfg)
    user = SimpleUserSimulator(cfg, db)
    test_user_goal(user, 30)

def main():
    get_config()
    run1()

if __name__ == '__main__':
    main()
