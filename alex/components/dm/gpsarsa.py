from alex.components.dm import DialoguePolicy
from alex.components.slu.da import DialogueAct, DialogueActItem

class GPSarsaDialoguePolicy(DialoguePolicy):
    """GPSarsa policy optimisation"""

    def __init__(self, cfg, ontology):
        self.cfg = cfg
        self.ontology = ontology

    def get_da(self, dialogue_state):
        raise NotImplementedError

