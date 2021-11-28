from numpy.core.arrayprint import _object_format
from utils.core import *

import numpy as np

FETCH_LOCATION = (2, 1)
DROP_LOCATION = (1, 2)
STEP_REWARD = -0.04
SUCCESS_REWARD = 1
FATAL_REWARD = -1

def interact(agent, level, world, recipe, max_nr=0, prev_orientation=None): #False, prev_orientation=None):
    """Carries out interaction for this agent taking this action in this world.

    The action that needs to be executed is stored in `agent.action`.
    """

    ''' Set the reward to the step cost '''
    reward = STEP_REWARD
    done = False
    successful = False
    mg = []
    if agent.message is not None:
        agent.prev_action = agent.message
        agent.message = None
    
    if "salad" in level:
        plate_name = [x.full_plate_name for x in recipe][0]
    elif "flour" in level:
        # the flour level uses a bowl not a plate
        plate_name = [x.full_bowl_name for x in recipe][0]

    if 'coffee' in level:
        
        action_x, action_y = world.inbounds(tuple(np.asarray(agent.location) + np.asarray(agent.action)))
        # get the gridsquare in the direction of the agent action (up, left, right, down)
        gs = world.get_gridsquare_at((action_x, action_y))

        # if empty handed just move to the grid tile
        if isinstance(gs, Floor):
            agent.move_to(gs.location)
        # except for if it's carpet, then we are stuck and fail.
        elif isinstance(gs, Carpet):
            agent.move_to(gs.location) # < move there
            successful = False
            done = True
            mg = ('Got stuck on carpet')
            print("STUCK ON CARPET")
            # reward = FATAL_REWARD < we do not know the carpet is the problem, no negative reward here.

        # if holding something
        elif agent.holding is not None:
            # if delivery in front --> deliver
            if isinstance(gs, Delivery):
                obj = agent.holding
                if obj.is_deliverable():
                    gs.acquire(obj)
                    agent.release()
                    print('\nDelivered {}!'.format(obj.full_name))
                    reward = SUCCESS_REWARD
                    successful = True
                    done = True
                    mg = ('Deliver', [obj])
            # if occupied gridsquare in front --> try merging
            elif world.is_occupied(gs.location):
                # Get object on gridsquare/counter
                obj = world.get_object_at(gs.location, None, find_held_objects = False)
                if mergeable(agent.holding, obj):
                    world.remove(obj)
                    o = gs.release() # agent is holding object
                    world.remove(agent.holding)
                    agent.acquire(obj)
                    world.insert(agent.holding)
                    # if playable version, merge onto counter first
                    if world.arglist.play:
                        gs.acquire(agent.holding)
                        agent.release()

            # if holding something, empty gridsquare in front --> chop or drop
            elif not world.is_occupied(gs.location):
                obj = agent.holding
                gs.acquire(obj) # obj is put onto gridsquare
                agent.release()
                assert world.get_object_at(gs.location, obj, find_held_objects =\
                        False).is_held == False, "Verifying put down works"
            
        elif agent.holding is None:
            # not empty in front --> pick up
            if world.is_occupied(gs.location) and not isinstance(gs, Delivery):
                obj = world.get_object_at(gs.location, None, find_held_objects = False)
                # if in playable game mode, then chop raw items on cutting board
                agent.acquire(obj)
            # if empty in front --> interact
            elif not world.is_occupied(gs.location):
                pass
    else:
        gs = world.get_gridsquare_at((agent.location[0], agent.location[1]+1))

        if 'DELIVER' in agent.action or isinstance(gs, Delivery):
            try:
                
                obj = [x for x in world.get_all_object_at(gs.location)][0]

                if not 'Plate' in obj.name and not 'Bowl' in obj.name:
                    obj = None

                if world.is_occupied(gs.location) and agent.orientation == 3 or 'flour' in level and  world.is_occupied(gs.location) and agent.orientation == 2:
                    if obj.is_deliverable():
                        agent.acquire(obj)
                        agent.orientation = 1
                        gs = world.get_gridsquare_at((agent.location[0]-1, agent.location[1]))

                        gs.acquire(obj)
                        agent.release()
                        
                        print("plate name: ", plate_name)
                        print("obj full name: ", obj.full_name)

                        #print("obj name: ", obj.name)

                        if plate_name == obj.full_name or 'flour_alternative_placeholder' in level and obj.full_name == 'Bowl-BakedAlmondFlour-BakedEggs':
                            print('\nDelivered CORRECTLY {}!'.format(obj.full_name))
                            if 'flour' in level:
                                reward = 10 * SUCCESS_REWARD
                            else:
                                reward = SUCCESS_REWARD
                            successful = True

                        else:
                            print('\nDelivered WRONGLY {}!'.format(obj.full_name))
                            reward = FATAL_REWARD 
                            
                        done = True
                        mg = ('Deliver', [obj])
                agent.message = "DELIVER: " + str(obj.name)
            except Exception as e:
                print("error delivering: ", e)
                reward = STEP_REWARD
                agent.message = "FAILED: Delivery"
        
        elif agent.action == (-1, 0):
            agent.message = "Turn Clockwise"

            if 0 < agent.orientation <= max_nr:
                agent.orientation -= 1
            elif agent.orientation == 0:
                agent.orientation = max_nr

        elif agent.action == (1, 0): # right
            agent.message = "Turn Counter clockwise"

            if 0 <= agent.orientation < max_nr:
                agent.orientation += 1
            elif agent.orientation == max_nr:
                agent.orientation = 0


        elif 'FETCH' in agent.action:
            pick_object_idx = None
            try:
                ### we know the shelf is on the right so
                if 2 < agent.orientation <= max_nr:
                    gs = world.get_gridsquare_at((agent.location[0]+1, agent.location[1]))

                    if agent.holding is None:                        
                        for i in range(max_nr+1):
                            if agent.orientation == i:
                                if 'flour' in level:
                                    pick_object_idx = i - 3
                                else:
                                    pick_object_idx = i - 4
                        if pick_object_idx is not None:
                            obj = [x for x in world.get_all_object_at(gs.location) if x.number == pick_object_idx][0]

                agent.message = "FETCH: " + str(obj.full_name)

                # if not placeholder
                print("OBJECT FETCHED: ", obj.full_name)

                if obj.name != 'Placeholder':                           
                    if world.is_occupied(gs.location) and not isinstance(gs, Delivery):
                        agent.acquire(obj)
                    # face counter 
                    if agent.holding.name == 'Plate' and 'salad' in level or agent.holding.contents[0].done(level):
                        agent.orientation = 3
                    else:
                        agent.orientation = 2
                    
                    gs = world.get_gridsquare_at((agent.location[0], agent.location[1]+1))


                    if agent.holding is not None:
                        if world.is_occupied(gs.location):
                            obj = world.get_object_at(gs.location, None, find_held_objects = False)

                            if mergeable(agent.holding, obj,level) or 'flour' in level:     
                                mg = ('Merge', [agent.holding, obj])
                                world.remove(obj)
                                o = gs.release()
                                world.remove(agent.holding)
                                agent.acquire(obj)
                                world.insert(agent.holding)
                                gs.acquire(agent.holding)
                                agent.release()
            
                            else:
                                obj = agent.holding
                                gs.acquire(obj) # obj is put onto gridsquare
                                agent.release()
                                assert [x for x in world.get_all_object_at(gs.location)  if x.number == pick_object_idx][0], "Verifying put down works"
                        else:
                            obj = agent.holding
                            gs.acquire(obj) # obj is put onto gridsquare
                            agent.release()
                            assert [x for x in world.get_all_object_at(gs.location)  if x.number == pick_object_idx][0], "Verifying put down works"
                else:
                    if 'salad' in level:
                        agent.message = "TomatoFailure"
                        raise Exception("Sorry, no more chopped tomatoes") 
                    elif 'flour' in level:
                        agent.message = "FlourFailure"
                        raise Exception("Sorry, no more wheat flour")                  
            except Exception as e:
                print("error fetching: ", e)
                reward = STEP_REWARD

        elif 'CHOP' in agent.action:
            assert "flour" not in level
            if agent.orientation == 2:
                try:
                    gs = world.get_gridsquare_at((agent.location[0], agent.location[1]+1))
                    # obtain object if its fresh at the drop location (Counter in the bottom of the env)
                    obj = [x for x in world.get_all_object_at(gs.location) if 'Fresh' in x.full_name][0]
                    
                    # acquire the object
                    agent.acquire(obj)

                    # the chopping board is north of the agent, for chopping we need to place it on that gridsquare (gs)
                    gs = world.get_gridsquare_at((agent.location[0], agent.location[1]-1))

                    if isinstance(gs, Cutboard) and obj.needs_chopped(): # and not world.arglist.play:
                        # before_name = obj.full_name
                        obj.chop()
                        agent.message = "CHOP: " + str(obj.full_name)
                        #reward = SUCCESS_REWARD # STEP_REWARD

                        gs = world.get_gridsquare_at((agent.location[0], agent.location[1]+1))

                        agent.orientation = 3

                        if agent.holding is not None:
                            if world.is_occupied(gs.location):
                                obj = world.get_object_at(gs.location, None, find_held_objects = False)
                                #print("OBJECT ON COUNTER: ", obj.full_name)

                                # if there's already something on the counter that was chopped (for example, the chopped lettuce)
                                # then we will merge this with what we just chopped (e.g., the tomato).
                                if mergeable(agent.holding, obj, level):
                                    
                                    # print("MERGE:", agent.holding, obj)
                                    # print("agent orientation: ", agent.orientation)

                                    mg = ('Merge', [agent.holding, obj])
                                    # reward = 1
                                    
                                    world.remove(obj)
                                    o = gs.release()
                                    world.remove(agent.holding)
                                    agent.acquire(obj)
                                    world.insert(agent.holding)
                                    gs.acquire(agent.holding)
                                    agent.release()
                                else:
                                    # if not mregable then just release it? 
                                    obj = agent.holding
                                    gs.acquire(obj) # obj is put onto gridsquare
                                    agent.release()

                            else:
                                # if the counter is empty we just release our freshly chopped food here
                                obj = agent.holding
                                gs.acquire(obj) # obj is put onto gridsquare
                                agent.release()
                        
                except Exception as e:
                    print("error chopping: ", e)
                    reward = STEP_REWARD
                    agent.message = "FAILED: Chopping an ingredient"

        elif 'BAKE' in agent.action:
            assert "salad" not in level
            if agent.orientation == 2:
                try:
                    gs = world.get_gridsquare_at((agent.location[0], agent.location[1]+1))
                    # obtain object if its fresh at the drop location (Counter in the bottom of the env)
                    
                    obj = [x for x in world.get_all_object_at(gs.location)][0] # if 'Bowl' in x.full_name][0]

                    # acquire the object
                    agent.acquire(obj)

                    print("obj: ", obj.full_name)


                    # the chopping board is north of the agent, for chopping we need to place it on that gridsquare (gs)
                    gs = world.get_gridsquare_at((agent.location[0], agent.location[1]-1))


                    if isinstance(gs, Oven) and obj.needs_baked() and not obj.is_baked(): # and not world.arglist.play:
                        before_name = obj.full_name

                        if 'Bowl-FreshEggs-FreshFlour' == obj.full_name:
                            reward = SUCCESS_REWARD
                        else:
                            reward = STEP_REWARD

                        obj.bake()
                        

                        agent.message = "BAKE: " + str(obj.full_name)
                        
                        # agent.orientation = 2

                    # normally bake
                    gs = world.get_gridsquare_at((agent.location[0], agent.location[1]+1))

                    if agent.holding is not None:
                        if world.is_occupied(gs.location):
                            obj = world.get_object_at(gs.location, None, find_held_objects = False)
                            #print("OBJECT ON COUNTER: ", obj.full_name)

                            # if there's already something on the counter that was chopped (for example, the chopped lettuce)
                            # then we will merge this with what we just chopped (e.g., the tomato).

                            if mergeable(agent.holding, obj):

                                mg = ('Merge', [agent.holding, obj])
                                # reward = 1
                                
                                world.remove(obj)
                                o = gs.release()
                                world.remove(agent.holding)
                                agent.acquire(obj)
                                world.insert(agent.holding)
                                gs.acquire(agent.holding)
                                agent.release()
                            else:
                                # if not mregable then just release it? 
                                obj = agent.holding
                                gs.acquire(obj) # obj is put onto gridsquare
                                agent.release()

                        else:
                            # if the counter is empty we just release our freshly chopped food here
                            obj = agent.holding
                            gs.acquire(obj) # obj is put onto gridsquare
                            agent.release()        
                except Exception as e:
                    print("error baking: ", e)
                    reward = STEP_REWARD
                    agent.message = "FAILED: Baking"


    print("Action: ", agent.action)
    print("reward:" , reward)
    print("orientation: ", agent.orientation)


    return reward, done, successful, mg, prev_orientation