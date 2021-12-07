# Recipe planning
from os import stat
from recipe_planner.stripsworld import STRIPSWorld
import recipe_planner.utils as recipe
from recipe_planner.recipe import *

# Navigation planning
import navigation_planner.utils as nav_utils

# Other core modules
from utils.interact import interact
from utils.world import World
from utils.core import *
from utils.agent import SimAgent, COLORS
from misc.game.gameimage import GameImage

import copy
# import networkx as nx
import numpy as np
from itertools import combinations, permutations, product
from collections import namedtuple

import gym
# from gym import error, spaces, utils
# from gym.utils import seeding
from datetime import datetime 
from navigation_planner.planners.shield import AlternativeAction, AlternativeItem
# CHANGE_MOVE_DOWN
#NAV_ACTIONS = [(0, 1), (0,-1), (-1, 0), (1, 0)]
#NAV_ACTIONS = [(0, 1), (0,-1), (-1, 0), (1, 0)]

CollisionRepr = namedtuple("CollisionRepr", "time agent_names agent_locations")


## Bottlenecks identification
# import cProfile
# profile = cProfile.Profile()
# import pstats
DELIVERY_LOC = (5, 0)
 
class OvercookedEnvironment(gym.Env):
    """Environment object for Overcooked."""

    def __init__(self, arglist):
        self.arglist = arglist
        # self.reward_shaping = self.arglist.reward_shaping
        self.t = 0
        self.reward = 0
        self.set_filename()
        self.start_shielding = False
        self.shield = arglist.shield
        self.start_merging = False

        self.num_ingredients = None
        self.encoded_ingredients = None
        self.num_orient_encodings = len(bin(8).replace("0b",""))

        if 'salad' in self.arglist.level:
            self.ACTION_TO_NAME = {0: 'left', 1: 'right', 2: 'fetch', 3: 'chop', 4: 'deliver'} # (0, 0): 4}
            self.NAV_ACTIONS = [(-1, 0), (1, 0), "FETCH", "CHOP", "DELIVER"]#, (0, 0)]

        elif 'alternative' in self.arglist.level:
            self.ACTION_TO_NAME = {0: 'left', 1: 'right', 2: 'fetch', 3: 'bake', 4: 'deliver'} # (0, 0): 4}
            self.NAV_ACTIONS = [(-1, 0), (1, 0), "FETCH", "BAKE", "DELIVER"]#, (0, 0)]
        elif 'coffee' in self.arglist.level:
            ACTION_TO_NAME = {0: 'down', 1: 'up', 2: 'left', 3: 'right'} # (0, 0): 4}
            self.NAV_ACTIONS = [(0, 1), (0,-1), (-1, 0), (1, 0)]

        # For visualizing episode.
        self.rep = []

        # For tracking data during an episode.
        self.collisions = []
        self.termination_info = ""
        self.successful = False
        self.ag_orient = None
        


    def update_agents(self):
        self.world_rep = self.world.get_repr()
        self.agent_rep = [agent.get_repr() for agent in self.sim_agents]

    def encode(self):
        #110001 - 49 in binary
        # add the other three thingies
        self.world_rep = self.world.get_repr()
        self.agent_rep = [agent.get_repr() for agent in self.sim_agents]
        #state_encoded = self.get_onehot()
        
        state_encoded = self.get_state_encoding()
        return state_encoded #, shield
        
        # print("World rep: ", self.world_rep)
        # print("agent rep: ", self.agent_rep)

    def get_state_encoding(self):

        if 'coffee' in self.arglist.level:
            for ag in self.agent_rep:
                ag_loc = ag.location
            for obj in self.world_rep:   
                if 'Coffee' in obj[0].name:
                    coffee_loc = obj[0].location
            state = (ag_loc, coffee_loc)

        else:
            for ag in self.agent_rep:
                ## LOCATION
                ag_orient = ag.orientation  # not have zero

            # #LOCATION OF OBJECTs
            locs = [0]*self.num_ingredients
            configs = [0]*self.encoded_ingredients


            obj_names = [x[0].name for x in self.world_rep]

            # print("self world rep: ", self.world_rep)

            for obj in self.world_rep:         
                for obj_ in obj:
                    if self.encoded_ingredients > 0:
                        # print("obj_.name: ", obj_.name)
                        obj_name = obj_.name
                        if "-" in obj_name:
                            obj_name = obj_name.split('-')
                        else:
                            obj_name = [obj_name]

                        # print("obj name: ", obj_name)
                        for o in obj_name:
                            
                            # print("O: ", o)
                            # print("obj_.location: ", obj_.location)
                            if obj_.location == (2, 1):
                                loc = 0
                            elif obj_.location == (1, 2):
                                loc = 1
                            elif obj_.location == (0, 1):
                                loc = 2

                            if "salad" in self.arglist.level:

                                #if obj_.location == (2, 1): # shelf
                                if 'Tomato' in o:
                                    if obj_.number == 0:
                                        locs[0] = loc
                                    else:
                                        locs[3] = loc
                                elif 'ChoppedLettuce' == o:
                                    locs[1] = loc
                                elif 'Plate' == o:
                                    locs[2] = loc
                            
                            if "salad" in self.arglist.level:
                                configs[0] = 1  
                                if 'ChoppedTomato' in o:
                                    if "placeholder" in self.arglist.level:
                                        configs[2]  = 1               
                                elif 'ChoppedLettuce' in o:
                                    configs[1] = 1
                            

                            elif "flour_alternative" in self.arglist.level:   
                                if 'Tomato' in o:
                                    if 'Baked' in o:
                                        configs[0] = 1
                                    locs[0] = loc
                                elif 'Cheese' in o:
                                    if 'Baked' in o:
                                        configs[1] = 1
                                    locs[1] = loc
                                elif 'Ham' in o:
                                    if 'Baked' in o:
                                        configs[2] = 1
                                    locs[2] = loc
                                elif 'Bread' in o:
                                    if 'Baked' in o:
                                        configs[3] = 1
                                    locs[3] = loc
                                elif 'Eggs' in o:
                                    if 'Baked' in o:
                                        configs[4] = 1
                                    locs[4] = loc
                                elif 'AlmondFlour' in o:
                                    if 'Baked' in o:
                                        configs[5] = 1
                                    locs[5] = loc
                                elif 'Flour' in o:
                                    if 'Baked' in o:
                                        configs[6] = 1
                                    locs[6] = loc
                                elif 'Bowl' in o:
                                    locs[7] = loc
                                
                
            ## there are 2 tomatos, if both are chopped we set the config of the second one to 1 as well.
            # 
            if "salad" in self.arglist.level or "flour" in self.arglist.level:
                dups = [x for x in obj_names if obj_names.count(x) > 1 and 'Chopped' in x]
                if len(dups) > 1:
                    configs[2] = 1
                    locs[3] = 1                                  
                state = (ag_orient, tuple(locs), tuple(configs))
        
        # print("STATE: ", state)

        '''
        obj:  (ObjectRepr(name='ChoppedBread', location=(2, 2), is_held=False),)
        obj:  (ObjectRepr(name='ChoppedCheese', location=(1, 0), is_held=False),)
        obj:  (ObjectRepr(name='ChoppedHam', location=(3, 1), is_held=False),)
        obj:  (ObjectRepr(name='Plate', location=(2, 0), is_held=False),)
        '''

        return state
        
    def binatodeci(self, binary):
        return sum(val*(2**idx) for idx, val in enumerate(reversed(binary)))

    def decimalToBinary(self, n, max_, s=False):
        if s:
            return str(format(n, '0'+str(max_)+'b'))
        else:
            return format(n, '0'+str(max_)+'b') #bin(n).replace("03b", "")


    def get_repr(self):
        return self.world.get_repr() + tuple([agent.get_repr() for agent in self.sim_agents])

    def __str__(self):
        # Print the world and agents.
        _display = list(map(lambda x: ''.join(map(lambda y: y + ' ', x)), self.rep))
        return '\n'.join(_display)

    def __eq__(self, other):
        return self.get_repr() == other.get_repr()

    def __copy__(self):
        new_env = OvercookedEnvironment(self.arglist)
        new_env.__dict__ = self.__dict__.copy()
        new_env.world = copy.copy(self.world)
        new_env.sim_agents = [copy.copy(a) for a in self.sim_agents]
        #new_env.distances = self.distances

        # Make sure new objects and new agents' holdings have the right pointers.
        for a in new_env.sim_agents:
            if a.holding is not None:
                a.holding = new_env.world.get_object_at(
                        location=a.location,
                        desired_obj=None,
                        find_held_objects=True)
        return new_env

    def set_filename(self):
        self.filename = "{}_seed{}_date{}".format(self.arglist.level,
            self.arglist.seed,datetime.now().strftime("%Y_%m_%d-%H:%M"))

    def load_level(self, level):
        x = 0
        y = 0
        shieldNames = {}

        with open('utils/levels/{}.txt'.format(level), 'r') as file:
            # Mark the phases of reading.
            phase = 1
            for line in file:
                line = line.strip('\n')
                
                if line == '':
                    phase += 1

                # Phase 1: Read in kitchen map.
                elif phase == 1:
                    cnt = 0
                    for x, rep in enumerate(line):

                        # Object, i.e. Tomato, Lettuce, Onion, or Plate, bread, cheese, ham.
                        #ADD_INGREDIENT
                        if 'salad' in level or 'flour' in level:
                            if x > 2:
                                x = 2

                        # if rep in 'p':
                        #     counter = Counter(location=(x, y))
                        # elif rep in 'tlobchemvL':                                                              
                        #     counter = Shelf(location=(x, y))

                        ## these are objects like tomato and lettuce.
                        if rep in 'tlCobcfahehmv$Lsp':
                            if 'salad' in level or 'flour' in level:
                                counter = Shelf(location=(x, y))
                            else:
                                counter = Counter(location=(x, y))
                            obj = Object(
                                    location= (x, y),
                                    contents=RepToClass[rep](),
                                    number = cnt
                                    )


                            if "salad" in level and x == 2 and cnt != 0: #and cnt < 2: #cnt == 0:
                                if 't' in rep or '$' in rep:
                                    obj.contents[0].set_state(obj.contents[0].state_seq[0])
                                    obj.update_names()
                            cnt += 1
                            counter.acquire(obj=obj)

                            try:
                                print(isinstance(self.world.get_gridsquare_at((x, y)), Shelf))
                            except:
                                self.world.insert(obj=counter)
                            self.world.insert(obj=obj)
                        # GridSquare, i.e. Floor, Counter, Cutboard, Delivery. Wall
                        elif rep in RepToClass:
                            newobj = RepToClass[rep]((x, y))
                            self.world.objects.setdefault(newobj.name, []).append(newobj)
                        else:
                            # Empty. Set a Floor tile.
                            f = Floor(location=(x, y))
                            self.world.objects.setdefault('Floor', []).append(f)
                    y += 1
                # Phase 2: Read in recipe list.
                elif phase == 2:
                    self.recipes.append(globals()[line]())
                elif phase == 3:
                    for i,item in enumerate(line.split(',')):
                        if item != '':
                            try:
                                items = item.split('^')
                                assert len(items) > 1
                                conjunction = []
                                for it in items:
                                    shieldName, shieldObject = it.split('-')

                                    conjunction.append((shieldName, shieldObject))
                                shieldNames[i] = (conjunction)
                            except:
                                shieldName, shieldObject = item.split('-')
                                shieldNames[i] = [(shieldName, shieldObject)]

                # Phase 3: Read in agent locations 
                elif phase == 4:
                    loc = line.split(' ')
                    if 'coffee' in level:
                        orientation = None
                    else:
                        orientation = 2
                    sim_agent = SimAgent(
                            name='agent-'+str(len(self.sim_agents)+1),
                            id_color=COLORS[len(self.sim_agents)],
                            location=(int(loc[0]), int(loc[1])),
                            level=level,
                            orientation=orientation, # orientation: start facing down
                            shieldnames=shieldNames)
                    self.sim_agents.append(sim_agent)

        self.world.width = x+1
        self.world.height = y
        self.world.perimeter = 2*(self.world.width + self.world.height)


    def reset(self):
        self.world = World(arglist=self.arglist)
        self.recipes = []
        self.sim_agents = []
        self.agent_actions = {}
        self.t = 0
        self.done = False
        episode = 0
        self.reward = 0

        # For visualizing episode.
        self.rep = []

        # For tracking data during an episode.
        self.collisions = []
        self.termination_info = ""
        self.successful = False

        # Load world & distances.
        self.load_level(
                level=self.arglist.level)
        self.world.make_loc_to_gridsquare()

        self.obs_tm1 = copy.copy(self)

        self.game = GameImage(
                filename=self.filename,
                world=self.world,
                sim_agents=self.sim_agents,
                level=self.arglist.level,
                record=self.arglist.record,
                train=self.arglist.train,
                shield=self.arglist.shield)
        self.game.on_init()
        if self.arglist.record:
            self.game.save_image_obs(self.t, episode)

        self.game_record_dir = self.game.game_record_dir
        return copy.copy(self)



    def close(self):
        return


    def step(self, action_dict, episode):
        # Track internal environment info.
        self.t += 1
        

        print("===============================")
        print("[environment.step] @ TIMESTEP {}".format(self.t))
        print("===============================")

        # Visualize.
        # print("===ENV in STEP BEFORE NAVIGATION==")
        # self.display()
        # print("================")

        # Get actions.
        for sim_agent in self.sim_agents:
            sim_agent.action = action_dict[sim_agent.name]
            print("sim agent: action: ", sim_agent.action)

        # Execute.
        # ics = 
        self.execute_navigation()
        print("agent action after execute: ", sim_agent.message)

        self.print_agents()
        if self.arglist.record:
            self.game.save_image_obs(self.t, episode)

        # Get a plan-representation observation.
        new_obs = copy.copy(self)
        # Get an image observation
        if self.arglist.record:
            image_obs = self.game.get_image_obs()
        
        if not self.done:
            self.done = self.done_func()
        
        #self.reward_func()
        if self.arglist.record:
            info = {"t": self.t, "obs": new_obs, "r": self.reward,
                    "image_obs": image_obs,
                    "action": sim_agent.message,
                    "done": self.done, "termination_info": self.termination_info}
        else:
            info = {"t": self.t, "obs": new_obs, "r": self.reward,
                "action": sim_agent.message,
                "done": self.done, "termination_info": self.termination_info}

        return new_obs, self.reward, self.done, info #, ics


    def done_func(self):
        # print("===check if done====")
        # Done if the episode maxes out
        if self.t >= self.arglist.max_num_timesteps and self.arglist.max_num_timesteps:
            self.termination_info = "Terminating because passed {} timesteps".format(
                    self.arglist.max_num_timesteps)
            # self.reward = 0
            self.successful = False
            return True


    def reward_func(self):
        if self.successful:
            self.reward = 20

    def print_agents(self):
        for sim_agent in self.sim_agents:
            sim_agent.print_status()

    def display(self):
        self.update_display()
        print(str(self))

    def update_display(self):
        self.rep = self.world.update_display()
        for agent in self.sim_agents:
            x, y = agent.location
            self.rep[y][x] = str(agent)


    def get_agent_names(self):
        return [agent.name for agent in self.sim_agents]

    def carpet_shield(self, agent):
        for action in [(0, 1), (1, 0), (0, -1)]:
            # reward -= 0.04

            action_x, action_y = self.world.inbounds(tuple(np.asarray(agent.location) + np.asarray(action)))
            gs = self.world.get_gridsquare_at((action_x, action_y))
            print("Gs: ", gs)
            print("agent's action in shield: ", agent.action)
            if isinstance(gs, Floor):
                agent.move_to(gs.location)
                self.display() 

            elif isinstance(gs, Carpet):
                print("Carpet hit")
                reward = self.carpet_shield(agent)
                self.display() 
        # return reward


    def execute_navigation(self):
        #print("execute navigation")
        #ics = False
        incorrect = True

        if "salad" in self.arglist.level:
            max_nr = 7
        else:
            max_nr = 11 

        for agent in self.sim_agents:
            print("action of the agent: ", agent.action)
            print("location of the agent: ", agent.location)

            agent.action = self.NAV_ACTIONS[agent.action]
            print("agent action translated: ", agent.action)

            reward, self.done, self.successful, _, orientation = interact(agent=agent, level=self.arglist.level, world=self.world, recipe=self.recipes, max_nr=max_nr, prev_orientation=self.ag_orient,incorrect=incorrect)
            
            '''
            post-shielding tomato
            '''

            print("action in execute navigation :" , agent.action)
            

            if self.shield and agent.message == "TomatoFailure":
                # print("self.getrepr before: ", self.get_repr())
                # if incorrect:
                #     ics = True # incorrect shield for tomato activated

                if isinstance(agent.shields[0], AlternativeAction):
                    if incorrect:
                        print("INCORRECT SHIELD: get plate and slice")
                        plate = [x[0] for x in self.get_repr() if not isinstance(x[0], str) and x[0].name=='Plate']
                        if len(plate) > 0:
                            plate = plate[0]

                            plate_obj = self.world.get_object_at(plate.location, 'Plate', find_held_objects = False)

                            #first fetch plate from shelf first then fetch tomato slice from kitchen (13)
                            if plate_obj.location == (2,1):
                                agent.acquire(plate_obj)

                                gs = self.world.get_gridsquare_at((1, 2))
                                if agent.holding is not None:

                                    if self.world.is_occupied(gs.location):
                                        # print("GS: ", gs)                                

                                        obj = self.world.get_object_at(gs.location, None, find_held_objects = False)


                                        if mergeable(plate_obj, obj, 'tomato_salad'):
                                            _ = ('Merge', [plate_obj, obj])                                
                                            self.world.remove(obj)
                                            o = gs.release()
                                            self.world.remove(plate_obj)
                                            agent.acquire(obj)
                                            self.world.insert(plate_obj)
                                            gs.acquire(plate_obj)
                                            agent.release()
                                    else:
                                        obj = agent.holding
                                        gs.acquire(obj) # obj is put onto gridsquare
                                        agent.release()

                        # tomato = [x[0] for x in self.get_repr() if not isinstance(x[0], str) and x[0].name=='ChoppedTomato']
                        agent.orientation = 4
                        # reward = (self.arglist.max_num_timesteps - self.t + 1) * -0.04
                        # self.ag_orient = agent.orientation
                        # self.agent_actions[agent.name]
                        self.done = True
                        self.successful = False

                    else:
                        tomato = [x[0] for x in self.get_repr() if not isinstance(x[0], str) and x[0].name=='FreshTomato']
                        if len(tomato) > 0:
                            tomato = tomato[0]
                    

                            tomato_obj = self.world.get_object_at(tomato.location, 'Tomato', find_held_objects = False)

                            if tomato_obj.needs_chopped():
                                print("TOMATO NEEDS CHOPPED")
                                tomato_obj.chop()

                            agent.acquire(tomato_obj)

                            gs = self.world.get_gridsquare_at((1, 2))
                            if agent.holding is not None:

                                if self.world.is_occupied(gs.location):
                                    # print("GS: ", gs)                                

                                    obj = self.world.get_object_at(gs.location, None, find_held_objects = False)


                                    if mergeable(tomato_obj, obj, 'tomato_salad'):
                                        # print("merge tomato and : ", obj)
                                        _ = ('Merge', [tomato_obj, obj])                                
                                        self.world.remove(obj)
                                        o = gs.release()
                                        self.world.remove(tomato_obj)
                                        agent.acquire(obj)
                                        self.world.insert(tomato_obj)
                                        gs.acquire(tomato_obj)
                                        agent.release()
                                else:
                                    obj = agent.holding
                                    gs.acquire(obj) # obj is put onto gridsquare
                                    agent.release()
                            agent.orientation = 3
                            # reward = -0.2 # move 3 times + fetch + chop

            elif self.shield and agent.message == "FlourFailure":
                print("FETCH ALMOND FLOUR INSTEAD")
                # incorrect shield: then fetch bowl from self fetch fresh egg and wheat floor 13
                if incorrect:
                    # 11 steps, turning and fetching
                    print("test")
                else:
                    flour = [x[0] for x in self.get_repr() if not isinstance(x[0], str) and 'AlmondFlour' in x[0].name]
                    print("flour: ", flour)
                    if len(flour) > 0:
                            flour = flour[0]
                    flour_obj = self.world.get_object_at(flour.location, 'AlmondFlour', find_held_objects = False)
                    if flour_obj.location == (2, 1):
                        agent.acquire(flour_obj)

                        gs = self.world.get_gridsquare_at((1, 2))
                        if agent.holding is not None:

                            if self.world.is_occupied(gs.location):
                                obj = self.world.get_object_at(gs.location, None, find_held_objects = False)
                                if 'flour' in self.arglist.level:
                                    _ = ('Merge', [flour_obj, obj])                                
                                    self.world.remove(obj)
                                    o = gs.release()
                                    self.world.remove(flour_obj)
                                    agent.acquire(obj)
                                    self.world.insert(flour_obj)
                                    gs.acquire(flour_obj)
                                    agent.release()

                            else:
                                obj = agent.holding
                                gs.acquire(obj) # obj is put onto gridsquare
                                agent.release()
                        # reward = -0.16 # move 3 times to almond flour + fetch
                    agent.orientation = 2

            elif self.shield and agent.message == "CarpetFailure":
                ## penalize longer plans JUST FOR CHRIS
                self.carpet_shield(agent)



            self.ag_orient = orientation
            if agent.message == "TomatoFailure":
                self.reward = reward#(self.arglist.max_num_timesteps - self.t + 1) * -0.04
            else:
                self.reward= reward
            # print("self reward: ", self.reward)
            self.agent_actions[agent.name] = agent.action
            # return ics

            

