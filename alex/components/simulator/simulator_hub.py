#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
if __name__ == '__main__':
    import autopath

import argparse

from alex.applications.exceptions import SemHubException
from alex.components.hub import Hub
from alex.components.slu.da import DialogueAct, DialogueActNBList
from alex.components.slu.exceptions import DialogueActException, DialogueActItemException
from alex.components.dm.common import dm_factory, get_dm_type
from alex.utils.config import Config


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

    def output_da(self, da):
        """Prints the system dialogue act to the output."""
        print "System DA:", unicode(da)
        print

    def run(self):
        """Controls the dialogue manager."""
        try:
            self.cfg['Logging']['system_logger'].info("""Starting""")

            while True:
                print 'user simulator, dialouge manager call here'
                break
        
        except KeyboardInterrupt:
            print 'KeyboardInterrupt exception in: %s' % multiprocessing.current_process().name
            return
        except:
            self.cfg['Logging']['system_logger'].exception('Uncaught exception in SHUB process.')
            raise

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

    cfg = Config.load_configs(args.configs)

    #########################################################################
    cfg['Logging']['system_logger'].info("Simulator Hub\n" + "=" * 120)

    cfg['Logging']['system_logger'].session_start("localhost")
    cfg['Logging']['system_logger'].session_system_log('config = ' + unicode(cfg))

    cfg['Logging']['session_logger'].session_start(cfg['Logging']['system_logger'].get_session_dir_name())
    cfg['Logging']['session_logger'].config('config = ' + unicode(cfg))
    cfg['Logging']['session_logger'].header(cfg['Logging']["system_name"], cfg['Logging']["version"])
    cfg['Logging']['session_logger'].input_source("dialogue acts")

    shub = SimulatorHub(cfg)

    shub.run()
