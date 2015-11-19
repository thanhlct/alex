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
                        ('departure_time', 'departure_time_relative', 'departure_date'):0.3,
                        ('arrival_time', 'arrival_time_relative', 'arrival_date', 'departure_time','departure_time_relative', 'departure_date'):0.2,
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
                    ('now',):0.5,#key is row in the table, if table has only one field, need add comma before the end of tuple
                    ('next hour',):0.02,
                    ('morning',):0.02,
                    ('noon',):0.02,
                    ('afternoon',):0.02,
                    ('night',):0.02,
                },
                'date':{
                    ('today',):0.5,
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

