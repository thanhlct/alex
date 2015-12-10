from alex.components.simulator.base import ASRSimulator

class SimpleASRSimulator(ASRSimulator):
    '''Simple ASR simulator'''
    def __init__(self, cfg):
        self.full_config = cfg
        self._name = self.__class__.__name__
        self.config = cfg['asr_simulator'][self._name]
        self.system_logger = self.config['logging']['system_logger']
        

    def simulate_asr(self, grammar, user_da):
        '''Returns N-best list ASR hypothesis given correct user_da and grammar or data etc.'''
        pass


#-----------for developing------
cfg = None

def get_config():
    global cfg
    cfg = Config.load_configs(['asr_simulator.py'], log=False)

def main():
    get_config()
    #db = PythonDatabase(cfg)

if __name__ == '__main__':
    main()
