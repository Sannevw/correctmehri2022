# Recipe planning
from recipe_planner.utils import *

# Navigation planning
import navigation_planner.utils as nav_utils

# Other core modules
from utils.world import World
from utils.core import *

from collections import defaultdict
import numpy as np
import scipy as sp
import random
from itertools import product
import copy
import time
from functools import lru_cache
from enum import Enum
import math
from navigation_planner.planners.shield import Shield, AlwaysNot



class PlannerLevel(Enum):
    LEVEL1 = 1
    LEVEL0 = 0

def argmin(vector):
    e_x = np.array(vector) == min(vector)

    return np.where(np.random.multinomial(1, e_x / e_x.sum()))[0][0]

def argmax(vector):
    e_x = np.array(vector) == max(vector)
    return np.where(np.random.multinomial(1, e_x / e_x.sum()))[0][0]

class QLEARNING:
    """
    Selecting next action 
    """

    def __init__(self):
        """
        """
        self.repr_to_env_dict = dict()
        self.start = None
        self.shield = None #Not(["Ham"])
     

    def set_settings(self, env, subtask, subtask_agent_names):
        """Configure planner."""
        # Set start state.
        self.start = copy.copy(env)
        self.repr_init(env_state=env)


    def repr_init(self, env_state):
        """Initialize repr for environment state."""
        es_repr = env_state.get_repr()
        if es_repr not in self.repr_to_env_dict:
            self.repr_to_env_dict[es_repr] = copy.copy(env_state)
        return es_repr



    def get_next_action(self, env, qtable, statedict, shields=None, use_shield=False):
        """Return next action from Q LEARNING."""
        StateDict = statedict
        self.start = copy.copy(env)


        # self.start is a copy of the environment.
        cur_state = copy.copy(self.start)

        #cur_state.display()
        state = cur_state.encode()

        incorrect = True

        if use_shield:
            print("----shielding START----")

            for shield_ in shields:
                if env.start_shielding and shield_.rep == 'AlwaysNot' and not incorrect:
                    shield__, qtable = shield_._get_shield(env_=self.start, state=StateDict[copy.copy(state)], qtable=qtable)
                    print("---done getting QLEARNING AlwaysNot shield: {}---".format(shield__))
                    for action_ in range(len(qtable[StateDict[state],:])):
                        if shield__[action_]:
                            qtable[StateDict[state], action_] = -math.inf

        '''
        select an action
        '''
        action = np.argmax(qtable[StateDict[state],:])


        return action 
