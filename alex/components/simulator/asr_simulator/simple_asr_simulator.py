from alex.components.simulator.base import ASRSimulator

class SimpleASRSimulator(ASRSimulator):
    '''Simple ASR simulator'''
    def __init__(self):
        pass
    def simulate_asr(self, grammar, user_da):
        '''Returns N-best list ASR hypothesis given correct user_da and grammar or data etc.'''
        pass
