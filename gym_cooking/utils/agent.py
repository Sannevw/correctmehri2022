# Recipe planning
# from recipe_planner.stripsworld import STRIPSWorld
# import recipe_planner.utils as recipe_utils
from recipe_planner.utils import *


# Navigation planner
from navigation_planner.planners.qlearning import QLEARNING
# import navigation_planner.utils as nav_utils

# Other core modules
# from utils.core import Counter, Cutboard, Pan, Shelf


import numpy as np
import copy
import random
from termcolor import colored as color
from collections import namedtuple
import navigation_planner.planners.shield as shield


AgentRepr = namedtuple("AgentRepr", "name location orientation holding message")

# Colors for agents.
COLORS = ['white', 'blue', 'magenta', 'yellow', 'green']

# ACTION_TO_NAME = {(0, 1): 0, (0, -1): 1, (-1, 0): 2, (1, 0): 3} # (0, 0): 4}
# ACTION_TO_READ = {(0, 1): 'down', (0, -1): 'up', (-1, 0): 'left', (1, 0): 'right'} # (0, 0): 4}



def createShield(name, objs):
    if name == 'AlwaysNot':
        return shield.AlwaysNot(objs[0])

    elif name == 'AlternativeAction':
        return shield.AlternativeAction(objs[0])

    elif name == 'AlternativeItem':
        return shield.AlternativeItem(objs[0])
    
    
REP_TO_OBJ = {
    'C': ["Carpet"],   
    't': ["Tomato"],
}

class RealAgent:
    """Real Agent object that performs task inference and plans."""

    def __init__(self, arglist, name, id_color, recipes, shield_names):
        self.arglist = arglist
        self.name = name
        self.color = id_color
        self.recipes = recipes

        # Bayesian Delegation.
        self.shields = []
        self.planner = QLEARNING()

        if "salad" in arglist.level:
            self.ACTION_TO_READ = {(-1, 0): 'left', (1, 0): 'right', "FETCH": "fetch", "CHOP": "chop", "DELIVER": "deliver"} # (0, 0): 4}
            self.NAV_ACTIONS = [(-1, 0), (1, 0), "FETCH", "CHOP", "DELIVER"]#, (0, 0)]
            self.ACTION_TO_NAME = {(-1, 0): 0, (1, 0): 1, "FETCH": 2, "CHOP": 3, "DELIVER": 4} # (0, 0): 4}

        elif 'flour' in arglist.level:
            self.ACTION_TO_READ = {(-1, 0): 'left', (1, 0): 'right', "FETCH": "fetch", "BAKE": "bake", "DELIVER": "deliver"} # (0, 0): 4}
            self.NAV_ACTIONS = [(-1, 0), (1, 0), "FETCH", "BAKE", "DELIVER"]#, (0, 0)]
            self.ACTION_TO_NAME = {(-1, 0): 0, (1, 0): 1, "FETCH": 2, "BAKE": 3, "DELIVER": 4} # (0, 0): 4}

        elif 'coffee' in arglist.level:
            self.ACTION_TO_NAME = {(0, 1): 0, (0, -1): 1, (-1, 0): 2, (1, 0): 3} # (0, 0): 4}
            self.ACTION_TO_READ = {(0, 1): 'down', (0, -1): 'up', (-1, 0): 'left', (1, 0): 'right'} # (0, 0): 4}
            self.NAV_ACTIONS = [(0, 1), (0, -1), (-1, 0), (1, 0)]

        # here we go through the shields defined in the .txt level file.

        for _,v in shield_names.items():
            objs = []
            if len(v) == 1:
                try:
                    objs.append(REP_TO_OBJ[v[0][1]])
                except:
                    objs.append(v[0][1])
            else:
                for v_ in v:
                    try:                
                        objs.append(REP_TO_OBJ[v_[1]])
                    except:
                        objs.append(v_[1])
            
            self.shields.append(createShield(v[0][0], objs))


    def __str__(self):
        return color(self.name[-1], self.color)

    def __copy__(self):
        a = Agent(arglist=self.arglist,
                name=self.name,
                id_color=self.color,
                recipes=self.recipes)
        a.__dict__ = self.__dict__.copy()
        if self.holding is not None:
            a.holding = copy.copy(self.holding)
        return a

    def get_holding(self):
        if self.holding is None:
            return 'None'
        return self.holding.full_name

    def init_action(self, obs):
        #print("obs in agent: ", obs)
        sim_agent = list(filter(lambda x: x.name == self.name, obs.sim_agents))[0]
        self.location = sim_agent.location
        self.holding = sim_agent.holding
        self.action = sim_agent.action
            
    def select_action(self, obs, qtable, statedict, epsilon, episode, use_shield, shield_eps):
        """Return best next action for this agent given observations."""

        rand_nr = random.uniform(0,1)
        cur_state = copy.copy(obs)
        cur_state_encoded = cur_state.encode()


        if rand_nr > epsilon:
            '''
            Here we pick an action using the q-table
            '''
            print("PICK ACTION QTABLE")
            if use_shield and episode >= shield_eps:
                action = self.plan(copy.copy(obs),copy.copy(qtable), statedict, use_shield=True)
            else:
                action = self.plan(copy.copy(obs),copy.copy(qtable), statedict)
        else:
            '''
            Here we pick a random action for exploration
            '''
            print("PICK ACTION RANDOM")
            action = self.ACTION_TO_NAME[random.choice(self.NAV_ACTIONS)]

            
            obs_ = copy.copy(obs)
            obs__ = copy.copy(obs)

            '''
            
            Here we start the shielding if we use shielding.

            '''
            if use_shield and episode >= shield_eps:
                for shieldName in self.shields:
                    if obs.start_shielding and shieldName.rep == 'AlwaysNot':
                        shield__, qtable = shieldName._get_shield(env_=obs_, state=statedict[copy.copy(cur_state_encoded)], qtable=qtable)
                        #print("shield: ", shield__)
                        print("---done getting NOT shield: {}---".format(shield__))
                        action = shieldName.apply_shield(action, shield__, obs_, self.NAV_ACTIONS)
                    # if obs.start_merging and shieldName.rep == 'AlternativeAction':
                    #     shield = shieldName._get_shield(env_=obs__, state=statedict[copy.copy(cur_state_encoded)], qtable=qtable)
                    #     print("---done getting shield tomato: {}---".format(shield))
                    #     action = shieldName.apply_shield(action, shield, obs__)    
        if action is not None:
            return action
        else:
            print("===conflicting shields===")
            print("termination because no action available from this state")

        

    def get_action_location(self):
        """Return location if agent takes its action---relevant for navigation planner."""
        return tuple(np.asarray(self.location) + np.asarray(self.action))

    def plan(self, env, qtable, statedict, use_shield=False):
        """Plan next action---relevant for navigation planner."""
        print('agent is taking action from qtable')

        return self.planner.get_next_action(
                env=env, qtable=qtable, statedict=statedict, shields=self.shields, use_shield=use_shield)


class SimAgent:
    """Simulation agent used in the environment object."""

    def __init__(self, name, id_color, location, level, orientation, shieldnames):
        self.name = name
        self.color = id_color
        self.location = location
        self.holding = None
        self.action = (0, 0)
        self.has_delivered = False
        self.shieldnames = shieldnames
        self.shields = []
        # self.merge_shield_start = False
        self.orientation = orientation
        self.message = None
        self.prev_action = 'Start'
        self.level = level

        if "salad" in self.level:
            self.ACTION_TO_READ = {(-1, 0): 'left', (1, 0): 'right', "FETCH": "fetch", "CHOP": "chop", "DELIVER": "deliver"} # (0, 0): 4}
            self.NAV_ACTIONS = [(-1, 0), (1, 0), "FETCH", "CHOP", "DELIVER"]#, (0, 0)]
        elif "flour" in self.level:
            self.ACTION_TO_READ = {(-1, 0): 'left', (1, 0): 'right', "FETCH": "fetch", "BAKE": "bake", "DELIVER": "deliver"} # (0, 0): 4}
            self.NAV_ACTIONS = [(-1, 0), (1, 0), "FETCH", "BAKE", "DELIVER"]#, (0, 0)]
        elif "coffee" in self.level:
            self.ACTION_TO_READ = {(0, 1): 'down', (0, -1): 'up', (-1, 0): 'left', (1, 0): 'right'} # (0, 0): 4}
            self.NAV_ACTIONS = [(0, 1), (0, -1), (-1, 0), (1, 0)]


        # here we go through the shields defined in the .txt level file.

        for _,v in self.shieldnames.items():
            objs = []
            if len(v) == 1:
                try:
                    objs.append(REP_TO_OBJ[v[0][1]])
                except:
                    objs.append(v[0][1])
            else:
                for v_ in v:
                    try:                
                        objs.append(REP_TO_OBJ[v_[1]])
                    except:
                        objs.append(v_[1])
            
            self.shields.append(createShield(v[0][0], objs))

            
    def __str__(self): 
        return color(self.name[-1], self.color)

    def __copy__(self):
        a = SimAgent(name=self.name, id_color=self.color,
                location=self.location, level=self.level, orientation=self.orientation, shieldnames=self.shieldnames)
        a.__dict__ = self.__dict__.copy()
        if self.holding is not None:
            a.holding = copy.copy(self.holding)
        return a

    def get_repr(self):
        return AgentRepr(name=self.name, location=self.location, orientation=self.orientation, holding=self.get_holding(), message=self.message)


    def get_holding(self):
        if self.holding is None:
            return 'None'
        return self.holding.full_name

    def print_status(self):
        if self.color == 'robot':
            print("{} current orientation {}, action was {}, holding {}".format(
                color('robot', 'grey'),
                self.orientation,
                self.ACTION_TO_READ[self.action],
                self.get_holding()))
        else:   
            print("{} current orientation {}, action was {}, holding {}".format(
                    color(self.name, self.color),
                    self.orientation,
                    self.ACTION_TO_READ[self.action],
                    self.get_holding()))

    def acquire(self, obj):
        if self.holding is None:
            self.holding = obj
            self.holding.is_held = True
            self.holding.location = self.location
        else:
            self.holding.merge(obj) # Obj(1) + Obj(2) => Obj(1+2)

    def release(self):
        self.holding.is_held = False
        self.holding = None
        
    def move_to(self, new_location):
        self.location = new_location
        if self.holding is not None:
            self.holding.location = new_location
