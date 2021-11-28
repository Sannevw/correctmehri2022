from utils.interact import interact
from utils.world import World
import copy
import random 
from navigation_planner.utils import StringToObject
import numpy as np 
import math 
import re
from utils.core import *


ACTION_TO_NAME = {(0, 1): 0, (0, -1): 1, (-1, 0): 2, (1, 0): 3} # (0, 0): 4}


class Shield:
    """Shield class to hold all of the shield objects used to shield the learning """

    def __init__(self):
        self.name = "general_shield"

    def hypo_step(self, env_, action):        
        # Execute.
        env_, done = self.hypo_execute_navigation(env_, action)
        return copy.copy(env_), done

    # hypothetically perform all actions and get next states s' 
    def hypo_execute_navigation(self, env_, action):
        # env_.display()
        for agent in env_.sim_agents:
            agent.action = agent.NAV_ACTIONS[action]
            _, done, _, mg, _ = interact(agent=agent, level=env_.arglist.level, world=env_.world, recipe=env_.recipes)

        return env_, done
        
    def apply_shield(self, action=None, shield=None, obs=None, actions=None):
        print("===APPLYING {} SHIELD TO ACTION {}===".format(self.rep, action))
        print("shield: ", shield)
        if shield[action]:
            # remove the action that is illegal. 
            as_ = [a for a in actions if a != actions[action]]

            # pick a new action
            try:
                print("random action with shield")
                action = ACTION_TO_NAME[random.choice(as_)]
            except:
                return None
            return self.apply_shield(action, shield, obs)
        else:
            return action

'''
    Class for creating a shield that selects an alternative action for the agent 

'''
class AlternativeAction(Shield):
    def __init__(self, predicates):
        Shield.__init__(self)

        self.rep = 'AlternativeAction' 
        #self.obj = predicate
        if len(predicates.split('^')) > 1:
            self.items = predicates.split('^')
        else:
            self.items = [predicates]

        '''
            For example self.objs in our tomato example is
            self objects: '[t]' for tomato
            self.actions is "Chop"
        # '''
        self.objs = re.findall("\((.*?)\)", str(self.items))
        if len(self.objs[0].split(";")) >1:
            self.objs = self.objs[0].split(";")
        self.actions = [re.compile("(.*?)\s*\(").match(x).group(1) for x in self.items]


    def _get_shield(self, env_=None, state=None, qtable=None):
            # current state
            start = copy.copy(env_)

            # stateNr = int(state_encoded, 2)
            action_dict = qtable[state,:]

            if "salad" in env_.arglist.level:
                print("action_dict: ", action_dict)
                shield = [False for i in range(len(action_dict))]

                for action, _ in enumerate(action_dict):
                    start = copy.copy(env_)
                    new_state = self.hypo_step_(env_=start, action=action)
                    new_state.update_agents()
                    for ag in new_state.agent_rep:
                        if ag.message == "TomatoFailure":
                            print("ACTION: ", action)
                            print("ag.message: ", ag.message)

                            shield[action] = True
                        
            print("shield: ", shield)
            if any(shield):
                quit()
            return shield #, qtable

    '''
    This function will return True if the action would lead us to grab a tomato slice that is not there,
    false otherwise.
    '''
    
    def hypo_step_(self, env_, action):    
        self.hypo_execute_navigation_(env_, action)
        # if not action_performed:
        #     return env_, False
        # elif action_performed == "TomatoFailure":
        #     
        return env_


        # hypothetically perform all actions and get next states s' 
    def hypo_execute_navigation_(self, env_, action):
        # env_.display()
        for agent in env_.sim_agents:
            agent.action = agent.NAV_ACTIONS[action]
            _, _, _, mg, _ = interact(agent=agent, level=env_.arglist.level, world=env_.world, recipe=env_.recipes)

        # return mg
   
'''
    Class for creating a shield that selects an alternative action for the agent 

'''
class AlternativeItem(Shield):
    def __init__(self, predicates):
        Shield.__init__(self)

        self.rep = 'AlternativeItem' 
        #self.obj = predicate
        if len(predicates.split('^')) > 1:
            self.items = predicates.split('^')
        else:
            self.items = [predicates]

        '''
            For example self.objs in our tomato example is
            self objects: '[t]' for tomato
            self.actions is "Chop"
        # '''
        self.objs = re.findall("\((.*?)\)", str(self.items))
        if len(self.objs[0].split(";")) >1:
            self.objs = self.objs[0].split(";")
        self.actions = [re.compile("(.*?)\s*\(").match(x).group(1) for x in self.items]


    def _get_shield(self, env_=None, state=None, qtable=None):
            # current state
            start = copy.copy(env_)

            # stateNr = int(state_encoded, 2)
            action_dict = qtable[state,:]

            if "flour" in env_.arglist.level:
                print("action_dict: ", action_dict)
                shield = [False for i in range(len(action_dict))]

                for action, _ in enumerate(action_dict):
                    start = copy.copy(env_)
                    new_state = self.hypo_step_(env_=start, action=action)
                    new_state.update_agents()
                    for ag in new_state.agent_rep:
                        if ag.message == "FlourFailure":
                            print("ACTION: ", action)
                            print("ag.message: ", ag.message)

                            shield[action] = True
                        
            print("shield: ", shield)
            if any(shield):
                quit()
            return shield #, qtable

    '''
    This function will return True if the action would lead us to grab a tomato slice that is not there,
    false otherwise.
    '''
    
    def hypo_step_(self, env_, action):    
        self.hypo_execute_navigation_(env_, action)
        # if not action_performed:
        #     return env_, False
        # elif action_performed == "TomatoFailure":
        #     
        return env_


        # hypothetically perform all actions and get next states s' 
    def hypo_execute_navigation_(self, env_, action):
        # env_.display()
        for agent in env_.sim_agents:
            agent.action = agent.NAV_ACTIONS[action]
            _, _, _, mg, _ = interact(agent=agent, level=env_.arglist.level, world=env_.world, recipe=env_.recipes)

        # return mg


class AlwaysNot(Shield):
    def __init__(self, predicates):
        Shield.__init__(self)
        self.rep = 'AlwaysNot' 
        #self.obj = predicate
        if len(predicates.split('^')) > 1:
            self.items = predicates.split('^')
        else:
            self.items = [predicates]

        self.objs = re.findall("\((.*?)\)", str(self.items))
        if len(self.objs[0].split(";")) >1:
            self.objs = self.objs[0].split(";")
        self.actions = [re.compile("(.*?)\s*\(").match(x).group(1) for x in self.items]
        
    def _get_shield(self, env_=None, state=None, qtable=None):
        # current state
        start = copy.copy(env_)

        # stateNr = int(state_encoded, 2)
        action_dict = qtable[state,:]

        # if predicate is an ingredient for the recipe
        # not(X) means that we don't want to ues it
        # hence, we need to make sure we don't pick it up (agent location == object location in next state)

        if "coffee" in env_.arglist.level:
            shield = [False for i in range(len(action_dict))]

            for action, _ in enumerate(action_dict):
                start = copy.copy(env_)
                new_state, _ = self.hypo_step(env_=start, action=action)
                new_state.update_agents()
                for ag in new_state.agent_rep:
                    gs = new_state.world.get_gridsquare_at(ag.location) 
                    if isinstance(gs, Carpet): # we want to check if the action got us on a carpet square
                        shield[action] = True
            # print("qtable before: ", qtable[state,:])
            qtable[state,:] = [-math.inf if shield[i] else qtable[state,i] for i in range(len(shield)) ]
            # print("After: ", qtable[state,:])
            # quit()
        else:
            for obj, act in zip(self.objs, self.actions):
                obj_name = obj.replace('Fresh','').replace('Mixed','').replace('Fried','')
                if obj_name in StringToObject.keys():
                    # make a step 
                    locs = []
                    if act != None:
                        shield = [False for i in range(len(qtable[state,:]))]
                    else:
                        shield = []
                    for action, _ in enumerate(action_dict):
                        start = copy.copy(env_)
                        if act == 'Pickup':
                            new_state, _ = self.hypo_step(env_=start, action=action)
                            # update the agents and world rep in the sim world state
                            new_state.update_agents()
                            locs.append(self.get_location(env_=new_state, obj=obj))
                            shield = self.get_pickup_shield(locs)

                        if act == 'Merge':
                            merged = self.hypo_step_(env_=start, action=action, obj=obj, act_=act)
                            shield[action] = merged

                    qtable[state,:] = [-math.inf if shield[i] else qtable[state,i] for i in range(len(shield)) ]

        return shield, qtable

    '''
    This function gets the location of the objects to shield, s.t. this shield disables the agent from 
    using these objects. 

    inputs: 
        env_: the current world state, from which we get the current agent location and object location.

    output:
        loc: a dict containing the agent location at key "agent" and the objects locations at key $object_name$
    '''
    def get_location(self, env_=None,obj=None):
        loc = {}
        for ag in env_.agent_rep:
            x, y = ag.location[0], ag.location[1]
            loc["agent"] = [x,y]
        #LOCATION OF OBJECTs

        obj_world = [x[0] for x in env_.world_rep if obj in x[0].name]
        for item in obj_world:
            x, y = item.location[0], item.location[1]
            loc["{}".format(item.name+'_'+str(x+y))] = [x,y]       

        return loc
             

    def get_pickup_shield(self, locations):
        shield = [False for i in range(len(locations))]

        for i, item in enumerate(locations):
            for k_, v_ in item.items():
                if k_ == 'agent':
                    loc_agent = locations[i][k_]
                elif k_ != 'agent' and loc_agent == locations[i][k_]:
                    shield[i] = True
                    continue
        return shield
    
    def hypo_step_(self, env_, action, obj, act_):    
        action_performed = self.hypo_execute_navigation_(env_, action)
        if not action_performed:
            return False
        act_performed = action_performed[0]
        on_objects = [item.full_name for item in action_performed[1]]

        if obj in on_objects and act_ == act_performed:
            return True
        else:
            return False


        # hypothetically perform all actions and get next states s' 
    def hypo_execute_navigation_(self, env_, action):
        # env_.display()
        for agent in env_.sim_agents:
            agent.action = World.NAV_ACTIONS[action]
            _, _, _, mg, _ = interact(agent=agent, level=env_.arglist.level, world=env_.world, recipe=env_.recipes)
        return mg
