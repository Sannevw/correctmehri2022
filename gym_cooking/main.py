from recipe_planner.recipe import *
from utils.world import World
from utils.agent import RealAgent, SimAgent, COLORS
from utils.core import *
from misc.game.gameplay import GamePlay
from misc.metrics.metrics_bag import Bag

import numpy as np
import random
import argparse
from collections import namedtuple
import math 
import gym
import os 
import pickle

def parse_arguments():
    parser = argparse.ArgumentParser("Overcooked 2 argument parser")

    # Environment
    parser.add_argument("--level", type=str, required=True)
    parser.add_argument("--max_num_timesteps", type=int, default=500, help="Max number of timesteps to run")
    parser.add_argument("--seed", type=int, default=1, help="Fix pseudorandom seed")
    parser.add_argument("--num_runs", type=int, default=1, help="Number of runs for evaluation")
    parser.add_argument("--with-image-obs", action="store_true", default=False, help="Return observations as images (instead of objects)")
    parser.add_argument("--num_episodes", type=int, default=500, help="Max number of episodes")
    parser.add_argument("--train", action="store_true", default=False, help="Save observation at each time step as an image in misc/game/record")
    parser.add_argument("--shield", action="store_true", default=False, help="Whether or not to use a shield")
    parser.add_argument("--reward_shaping", action="store_true", default=False, help="Whether or not to use reward shaping")
    parser.add_argument("--num_episodes_shield", type=int, default=0, help="number of episodes after which to shield")
    parser.add_argument("--pretrained", action="store_true", default=False, help="Whether or not to use a pretrained agent")
    parser.add_argument("--data_dir", type=str, default="misc/metrics/pickles/", required=False)
    parser.add_argument("--fname", type=str, default="default_fname.pkl", required=False)
    

    # Q-learning parameters
    parser.add_argument("--lr", type=float, default=0.6, help="learning rate")
    parser.add_argument("--gamma", type=float, default=0.8, help="gamma")
    parser.add_argument("--epsilon", type=float, default=1.0, help="epsilon")


    # Visualizations
    parser.add_argument("--play", action="store_true", default=False, help="Play interactive game with keys")
    parser.add_argument("--record", action="store_true", default=False, help="Save observation at each time step as an image in misc/game/record")

    return parser.parse_args()


def fix_seed(seed):
    np.random.seed(seed)
    random.seed(seed)

def initialize_agents(arglist):
    real_agents = []
    shieldNames = {}

    with open('utils/levels/{}.txt'.format(arglist.level), 'r') as f:
        phase = 1
        recipes = []
        for line in f:
            line = line.strip('\n')
            if line == '':
                phase += 1

            # phase 2: read in recipe list
            elif phase == 2:
                recipes.append(globals()[line]())

            # phase 3: read in agent locations
            elif phase == 3:
                for i,item in enumerate(line.split(',')):
                    if item != '':
                        try:
                            items = item.split('^')
                            assert len(items) > 1
                            conjunction = []
                            for it in items:
                                shieldName, shieldObject = it.split('-')
                                print("Shield name: ", shieldName)
                                print("shield object: ", shieldObject)
                                conjunction.append((shieldName, shieldObject))
                            shieldNames[i] = (conjunction)
                        except:
                            shieldName, shieldObject = item.split('-')
                            shieldNames[i] = [(shieldName, shieldObject)]
            elif phase == 4:
                real_agent = RealAgent(
                        arglist=arglist,
                        name='agent-'+str(len(real_agents)+1),
                        id_color=COLORS[len(real_agents)],
                        recipes=recipes,
                        shield_names=shieldNames)
                real_agents.append(real_agent)
    return real_agents

def load_data(arglist):
    #data_dir = arglist.data_dir + "_" + arglist.level
    fname = arglist.fname

    if os.path.exists(os.path.join(arglist.data_dir, fname)):
        try:
            print("Successfully loaded: {}".format(fname))
            data = pickle.load(open(os.path.join(arglist.data_dir, fname), "rb"))
        except:
            print("trouble loading: {}".format(fname))
            exit()

    data_final = []
    #print("DATA:" , data)
    successes = []
    for k, item in data.items():
        if k == 'level':
            continue
        # pr/int("item:" , item.keys())
        for k_ in item.keys():
            if 'qtable' in item[k_].keys():
                data_final.append(item[k_])
                successes.append(item[k_]["was_successful"])

    return data_final, fname

def get_qtable(data):

    qtable = data[-1]['qtable']
    StateDict = data[-1]["statedict"]

    return qtable, StateDict

def main_loop(arglist):
    """The main loop for running experiments."""

    print("Initializing environment and agents.")

    '''
    
    Set the data_dir to be specific for each of our three levels, so we store it in the corresponding folder.
    E.g., misc/metrics/pickles/tomato_salad/
    '''
    if 'coffee' in arglist.level:
        level = arglist.level[:-7] if 'carpet' in arglist.level else arglist.level
    else:
        level = arglist.level[:-12] if 'placeholder' in arglist.level else arglist.level

    arglist.data_dir = arglist.data_dir  + level + '/'
    '''
    if we don't already have that specific experiment's folder than create it. 
    '''
    if not os.path.exists(arglist.data_dir):
        os.makedirs(arglist.data_dir)


    ''' 
    
    make and reset the env
    
    '''
    env = gym.envs.make("gym_cooking:overcookedEnv-v0", arglist=arglist)
    obs = env.reset()

    ''' 
    
    if we retrain (hence, we use a pretrained model to start from) then load the qtable / statedict 
    As we iteratively set the qtable, based on the states we visited (as we may add new states later when retraining)
    we keep track of the max id using our statedict (dictionary which maps a state to the id it got in our q-table)

    qtable[0] = values for the first state we visited
    qtable[1] = values for the second state we visited 
    etc ...
    
    This also lets us explore which (order) states were visited (in).
    '''


    decay_rate = 0.01
            # arglist.num_episodes = 500
            # arglist.max_num_timesteps = 500

    # Info bag for saving pkl files

    bag = Bag(arglist=arglist, filename=env.filename)
    # bag.set_recipe(recipe_subtasks=env.all_subtasks)
        
    '''
    Q TABLE / STATE ENCODING

    salad / cake scenario:
        qtable = np.zeros((num_orientations * nr_obj_locs**env.encoded_ingredients * env.encoded_ingredients**nr_of_obj_configs, len(NAV_ACTIONS)))

        We encode the agent's orientation. This depends on the task/level (see num_orientations above)
        We encode as well if an object is on the shelf / counter or at delivery (nr_obj_locs)
        We also encode for each obj in which state they are in (encoded_ingredients & nr_of_obj_configs)

    coffee scenario:
        qtable = np.zeros((num_locations**2, len(NAV_ACTIONS))) 

        we encode the agent's location and the coffee location (= env.world.width * env.world.height)

    '''

    if 'salad' in arglist.level:
        # ACTION_TO_NAME = {0: 'left', 1: 'right', 2: 'fetch', 3: 'chop', 4: 'deliver'} # (0, 0): 4}
        NAV_ACTIONS = [(-1, 0), (1, 0), "FETCH", "CHOP", "DELIVER"]#, (0, 0)]
        env.num_ingredients = 4  # 2 tomato 1 lettuce 1 plate
        env.encoded_ingredients = 3 # tomato and lettuce
        num_orientations = 7
        nr_obj_locs = 3 # the locs where the objects can be located ( e.g., shelf, counter, delivery spot)
        nr_of_obj_configs = 2
        if 'placeholder' not in arglist.level:
            max_idx = 0
            StateDict = {}
            qtable = np.zeros((num_orientations * nr_obj_locs**env.encoded_ingredients * env.encoded_ingredients**nr_of_obj_configs, len(NAV_ACTIONS)))

    elif 'flour' in arglist.level:
        # ACTION_TO_NAME = {0: 'left', 1: 'right', 2: 'fetch', 3: 'bake', 4: 'deliver'} # (0, 0): 4}
        NAV_ACTIONS = [(-1, 0), (1, 0), "FETCH", "BAKE", "DELIVER"]#, (0, 0)]
        env.num_ingredients = 8 # eggs, bread, flour, ham, bowl, almodnflour, tomato, cheese
        env.encoded_ingredients = 7 # all except bowl
        num_orientations = 10
        nr_obj_locs = 3 # the locs where the objects can be located ( e.g., shelf, counter, delivery spot)
        nr_of_obj_configs = 2
        if 'placeholder' not in arglist.level:
            max_idx = 0
            StateDict = {}
            qtable = np.zeros((num_orientations * nr_obj_locs**env.encoded_ingredients * env.encoded_ingredients**nr_of_obj_configs, len(NAV_ACTIONS)))

    elif 'coffee' in arglist.level:
        # ACTION_TO_NAME = {0: 'down', 1: 'up', 2: 'left', 3: 'right'} # (0, 0): 4}
        NAV_ACTIONS = [(-1, 0), (1, 0), (0, 1), (0, -1)]#, (0, 0)]
        num_locations = env.world.width * env.world.height # n x m grid
        ## agent can be in any of the cells, coffee too. So nxm**2 

        if 'placeholder' not in arglist.level:
            max_idx = 0
            StateDict = {}
            qtable = np.zeros((num_locations**2, len(NAV_ACTIONS)))    

    # print("qtable size: ", qtable.shape)
    # quit()


    for run in range(arglist.num_runs):
        epsilon = arglist.epsilon
        max_epsilon = arglist.epsilon
        min_epsilon = 0.01
        
        # early stopping
        thr = 0.00000001
        terminated = False
        if arglist.pretrained:
            print("Train starting with pretrained Q-table for run {} ".format(run))

            data, _ = load_data(arglist)
            qtable, StateDict = get_qtable(data)

            print("qtable: ", qtable)
            print("\n\n")
            max_idx = StateDict[list(StateDict.keys())[-1]]
            decay_rate = 0.05

        for episode in range(arglist.num_episodes):
            total_reward = 0

            print("-----------EPISODE %d-----------" % episode )
            print("===epsilon: %f ===" % epsilon)
            
            obs = env.reset()

            real_agents = initialize_agents(arglist=arglist)
            # Uncomment to print out the environment.
    #        env.display()
            delta = -np.inf

            while not env.done:

                if arglist.shield:
                    obs.start_shielding = True
                    obs.start_merging = True

                env.display()

                action_dict = {}
                state = obs.encode()

                # print("state: ", state)

                if state not in StateDict:
                    print("Adding state {}".format(state))
                    StateDict[state] = max_idx
                    max_idx += 1 

                for agent in real_agents:
                    agent.init_action(obs=obs)
                    action = agent.select_action(obs=copy.copy(obs), qtable=qtable, statedict=StateDict, epsilon=epsilon, episode=episode, use_shield=arglist.shield, shield_eps=arglist.num_episodes_shield)
                    if action is not None:
                        action_dict[agent.name] = action
                    else:
                        env.successful = False
                        env.termination_info = "terminated because of conflicting shields"
                        break
                
                old_q = qtable[StateDict[state], action]

                new_obs, reward, _, info = env.step(action_dict=action_dict, episode=episode)

                
                # update Q-values

                for agent in real_agents:
                    action = action_dict[agent.name]
                    new_state = new_obs.encode()
                    
                    if new_state not in StateDict:
                        StateDict[new_state] = max_idx
                        max_idx += 1
                    
                    #new_state = int(new_obs_encoded, 2)

                    qtable[StateDict[state], action] = qtable[StateDict[state], action] + arglist.lr * (reward + arglist.gamma * np.max(qtable[StateDict[new_state], :]) - qtable[StateDict[state], action])


                delta = max(delta, abs(old_q-qtable[StateDict[state], action]))

                obs = new_obs

                # print("JA: ", "(qtable[StateDict[new_state],:]: ", qtable[StateDict[new_state],:])
                # print("max id: ", max_idx)

                total_reward += reward
                # Saving info
                # we add the reward for each time step, the agent information, and episode
                bag.add_status(run="run_"+str(run), cur_time=info['t'], reward=reward, real_agents=real_agents, episode=episode)

            
            print("epsilon: ", epsilon)
            # upon termination we add if we were successful, the total reward of the episode

            if delta < thr and not terminated:    
                termination_info = episode
                terminated = True

            elif not terminated:
                termination_info = env.termination_info
            

            bag.set_termination(run="run_"+str(run), termination_info=termination_info,
                    successful=env.successful, total_r=total_reward, qtable=qtable, statedict=StateDict, episode=episode, t=env.t)

            
            print("===total reward of episode %d %f === " % (episode, total_reward))
            # if env.successful:
            #     quit()
            #print("QTABLE: \n")

            #print(qtable)
            epsilon = min_epsilon + (max_epsilon - min_epsilon)* np.exp(-decay_rate*episode)

            # if delta < thr:
            #     print("deltA: ", delta)
            #     print("thr: ", thr)
            #     print("stopping because no longer improving much")
            #     break

                #qdiff = old_diff - curr_diff


def read_recipe(arglist):
    with open('utils/levels/{}.txt'.format(arglist.level), 'r') as f:
        phase = 1
        recipes = []
        for line in f:
            line = line.strip('\n')
            if line == '':
                phase += 1

            # phase 2: read in recipe list
            elif phase == 2:
                recipes.append(globals()[line]())
    return recipes

if __name__ == '__main__':
    arglist = parse_arguments()
    assert 0.0 <= arglist.gamma <= 1.0, "should be between 0.0 and 1.0"
    assert 0.0 <= arglist.epsilon <= 1.0, "should be between 0.0 and 1.0"
    assert 0.0 <= arglist.lr <= 1.0, "should be between 0.0 and 1.0"
 
    if arglist.play:
        env = gym.envs.make("gym_cooking:overcookedEnv-v0", arglist=arglist)
        env.reset()
        recipe = read_recipe(arglist)
        game = GamePlay(env.filename, env.world, env.sim_agents, arglist.level, recipe)
        game.on_execute()
    else:
        # fix_seed(seed=arglist.seed)
        main_loop(arglist=arglist)
