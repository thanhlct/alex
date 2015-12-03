import autopath
import pdb
#if __name__=='__main__':
#    import autopath

pdb.set_trace()
from alex.components.simulator.simple_user_simulator import SimpleUserSimulator
from alex.utils.database.python_database import PythonDatabase
from alex.components.slu.da import DialogueActItem, DialogueAct

def get_config():
    global cfg
    #pdb.set_trace()
    #cfg = Config.load_configs(['../../../applications/PublicTransportInfoEN/ptien.cfg', '../../../applications/PublicTransportInfoEN/simulator.cfg'])
    cfg = Config.load_configs(['../../../applications/PublicTransportInfoEN/simulator.cfg'])
    cfg['Logging']['system_logger'].info("Voip Hub\n" + "=" * 120)

def simulate_one_dialogue():
    pass

def main():
    get_config()
    db = PythonDatabase(cfg)
    user = SimpleUserSimulator(cfg, db)
    simulate_one_dialogue()

if __name__ == '__main__':
    main()
