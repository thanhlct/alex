#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
if __name__ == '__main__':
    import autopath
    import pdb

import argparse

from alex.applications.exceptions import SemHubException
from alex.components.hub import Hub
from alex.components.slu.da import DialogueAct, DialogueActNBList
from alex.components.slu.exceptions import DialogueActException, DialogueActItemException
from alex.components.dm.common import dm_factory, get_dm_type
from alex.utils.config import Config

from alex.components.simulator.user_simulator.simple_user_simulator import SimpleUserSimulator
from alex.utils.database.python_database import PythonDatabase
from alex.components.slu.da import DialogueActItem, DialogueAct
import multiprocessing

class SimulatorHub(Hub):
    """SimulatorHub simulates dialogues between an user simulator and a dialogue manager.
    
    It builds a hub to connect user simulator and dialogue manager.
    It may be used to train and evaluate a dialogue mangager with an user simulator given.
    """
    #hub_type = "SimulatorHub"

    def __init__(self, cfg):
        super(SimulatorHub, self).__init__(cfg)

        dm_type = get_dm_type(cfg)
        self.dm = dm_factory(dm_type, cfg)
        self.dm.new_dialogue()

        self.close_event = multiprocessing.Event()

    def print_da(self, agent, da):
        """Prints the dialogue act to the output, log."""
        print agent, '\t\t', unicode(da)

    def simulate_one_dialogue(self, user, asr, dm):
        """Simulate one dialogue given user simuator, ASR simulator and dialogue manager."""

        cfg['Logging']['system_logger'].session_start("simulator")
        cfg['Logging']['system_logger'].session_system_log('config = ' + unicode(cfg))

        cfg['Logging']['session_logger'].session_start(cfg['Logging']['system_logger'].get_session_dir_name())
        cfg['Logging']['session_logger'].config('config = ' + unicode(cfg))
        cfg['Logging']['session_logger'].header(cfg['Logging']["system_name"], cfg['Logging']["version"])
        cfg['Logging']['session_logger'].input_source("dialogue acts")

        sys_das = ['hello()',
                'request(task)',
                'implconfirm(task=find_connection)&request(from_stop)',
                'request(to_stop)',
                'implconfirm(to_stop=first stop)&request(arrival_time)',
                'offer(route=take the tram 12, it will pass your destination after 6 stops.)',
                'bye()',
                ]
        
        user.new_dialogue()
        index = 0
        while(True):
            sys_da = DialogueAct(sys_das[index])
            print 'sys_da:\t\t',sys_da
            self.cfg['Logging']['session_logger'].turn("system")
            self.cfg['Logging']['session_logger'].dialogue_act("system", sys_da) 

            user.da_in(sys_da)
            user_da = user.da_out()
            print 'user_da:\t', user_da[0]
            self.cfg['Logging']['session_logger'].turn("user")
            self.cfg['Logging']['session_logger'].dialogue_act("user", user_da[0]) 
            #self.cfg['Logging']['session_logger'].slu("user", 'fname', 'nblist', 'confnet=confnet')

            if user_da[0][0].dat in ['bye', 'hangup']:
                break
            index +=1

        self.cfg['Logging']['system_logger'].session_end()
        self.cfg['Logging']['session_logger'].session_end()

    def run(self):
        """Run the hub."""
        try:
            cfg['Logging']['system_logger'].info("Simulator Hub\n" + "=" * 120)
            self.cfg['Logging']['system_logger'].info("""Starting...""")

            cfg['Logging']['session_logger'].set_close_event(self.close_event)
            cfg['Logging']['session_logger'].set_cfg(cfg)
            cfg['Logging']['session_logger'].start()
            cfg['Logging']['session_logger'].cancel_join_thread()

            db = PythonDatabase(cfg)
            user = SimpleUserSimulator(cfg, db)

            while True:
                self.simulate_one_dialogue(user, None, None)
                self.simulate_one_dialogue(user, None, None)
                break
        
        except KeyboardInterrupt:
            print 'KeyboardInterrupt exception in: %s' % multiprocessing.current_process().name
            return
        except:
            self.cfg['Logging']['system_logger'].exception('Uncaught exception in SHUB process.')
            raise

        print 'Exiting: %s. Setting close event' % multiprocessing.current_process().name
        self.close_event.set()

#########################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
        SimulatorHub is a simulation enviroment for SDS.

        It invokes user simulator and dialogue mangager to simulate a normal dialouger.

        The program reads the default config in the resources directory ('../resources/default.cfg') config
        in the current directory.

        In addition, it reads all config file passed as an argument of a '-c'.
        The additional config files overwrites any default or previous values.

      """)

    parser.add_argument('-c', "--configs", nargs='+',
                        help='additional configuration files')
    args = parser.parse_args()

    if args.configs is None:
        args.configs = ['./user_simulator/demos/ptien/simulator.cfg', './user_simulator/demos/ptien/ptien_metadata.py']
    cfg = Config.load_configs(args.configs)

    shub = SimulatorHub(cfg)

    shub.run()
