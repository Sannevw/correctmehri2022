from recipe_planner.recipe import *
from utils.world import World
from utils.agent import RealAgent, SimAgent, COLORS
from utils.core import *
from misc.game.gameplay import GamePlay

import numpy as np
import random
import argparse
from collections import namedtuple
import sys
import os
import pickle
import collections
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageFont, ImageDraw 

import gym

def parse_arguments():
    parser = argparse.ArgumentParser("Overcooked argument parser")
    parser.add_argument("--fname", type=str, default="tomato_salad_placeholder_seed1_date2021_08_16-16:15Shielded_False.pkl", required=False)
    parser.add_argument("--fname_no", type=str, default="", required=False)
    
    parser.add_argument("--data_dir", type=str, default="misc/metrics/pickles/", required=False)
    parser.add_argument("--train", action="store_true", default=True, help="Save observation at each time step as an image in misc/game/record")
    
    parser.add_argument("--level", type=str, required=True)
    parser.add_argument("--max-num-timesteps", type=int, default=100, help="Max number of timesteps to run")
    parser.add_argument("--seed", type=int, default=1, help="Fix pseudorandom seed")
    parser.add_argument("--with-image-obs", action="store_true", default=False, help="Return observations as images (instead of objects)")
    parser.add_argument("--num_episodes", type=int, default=100, help="Max number of episodes")
    parser.add_argument("--shield", action="store_true", default=False, help="Whether or not to use a shield")
    parser.add_argument("--num_episodes_shield", type=int, default=1, help="number of episodes after which to shield")
    parser.add_argument("--reward_shaping", action="store_true", default=False, help="Whether or not to use reward shaping")
    

 # Q-learning parameters
    parser.add_argument("--lr", type=float, default=0.3, help="learning rate")
    parser.add_argument("--gamma", type=float, default=0.75, help="gamma")
    parser.add_argument("--epsilon", type=float, default=1.0, help="epsilon")


    # Visualizations
    parser.add_argument("--play", action="store_true", default=False, help="Play interactive game with keys")
    parser.add_argument("--record", action="store_true", default=False, help="Save observation at each time step as an image in misc/game/record")

    return parser.parse_args()

def load_data(arglist):
    data_dir = arglist.data_dir
    fname, fname_no = arglist.fname, arglist.fname_no
    data_no_final = None

    if os.path.exists(os.path.join(data_dir, fname)):
        try:
            print("Successfully loaded: {}".format(fname))
            data = pickle.load(open(os.path.join(data_dir, fname), "rb"))
        except:
            print("trouble loading: {}".format(fname))
            exit()

    data_final = []

    successes = []

    print(data.keys())
    for k, item in data.items():
        if k == 'level':
            continue
        
        for k_ in item.keys():

            print("termin: ", item[k_]["termination"])
            
            if 'qtable' in item[k_].keys():
                data_final.append(item[k_])
                successes.append(item[k_]["was_successful"])

    print("---Was successful in {} of {} episodes, {} percent of the time----".format(sum(successes),len(successes),(sum(successes)/len(successes))))

    if arglist.fname_no != "":
        if os.path.exists(os.path.join(data_dir, fname_no)):
            try:
                print("Successfully loaded: {}".format(fname_no))
                data_ = pickle.load(open(os.path.join(data_dir, fname_no), "rb"))
            except:
                print("trouble loading: {}".format(fname_no))
                exit()

        data_no_final = []
        successes_ = []
        for item in data_.items():
            if item[0] == 'level':
                continue
            if 'qtable' in item[1].keys():
                data_no_final.append(item)
                successes_.append(item[1]["was_successful"])
        print("---Was successful in {} of {} episodes, {} percent of the time----".format(sum(successes_),len(successes_),(sum(successes_)/len(successes_))))




    return data_final, data_no_final

def get_qtable(data):
    qtable = data[-1]['qtable']
    StateDict = data[-1]["statedict"]

    return qtable, StateDict
    


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
                            shieldName, shieldObject = item.split('-')
                            shieldNames[i] = (shieldName, shieldObject)
                        except:
                            shieldNames[i] = (item)
                    

            elif phase == 4:
                real_agent = RealAgent(
                        arglist=arglist,
                        name='agent-'+str(len(real_agents)+1),
                        id_color=COLORS[len(real_agents)],
                        recipes=recipes,
                        shield_names=shieldNames)
                real_agents.append(real_agent)
    return real_agents

def run_agent(data=None):
    print("===Initializing environment and agent.===")
    qtable, StateDict = get_qtable(data)


    env = gym.envs.make("gym_cooking:overcookedEnv-v0", arglist=arglist)
    obs = env.reset()
    max_steps = 25

    if 'tomato_salad' in arglist.level:
        env.num_ingredients = 4  # 2 tomato 1 lettuce 1 plate
        env.encoded_ingredients = 3 # tomato and lettuce

    elif 'flour' in arglist.level:
        env.num_ingredients = 8
        env.encoded_ingredients = 7
    
    elif 'coffee' in arglist.level: 
        env.num_ingredients = 1
        env.encoded_ingredients = 0
        
        
    infos = []
    for episode in range(1):
        obs = env.reset()
        total_reward = 0

        real_agents = initialize_agents(arglist=arglist)
        # color robot

        step_ = 0
        print("===Episode: %d ===" % episode)
        
        while not env.done and step_ < max_steps:
            env.display()

            state = obs.encode()

            action_dict = {}
            print("state:" , state)
            # quit()

            for agent in real_agents:
                if state not in StateDict:
                    print("add state")
                    value = StateDict[next(reversed(StateDict))]
                    StateDict[state] = value+1
                print("(qtable[StateDict[state],:]: ", qtable[StateDict[state],:])
                action = np.argmax(qtable[StateDict[state],:])

                action_dict[agent.name] = action

            new_obs, reward, _, info = env.step(action_dict=action_dict, episode=episode)

            infos.append(info)

            #agent.refresh_subtasks(world=env.world)
            obs = new_obs

            step_ +=1
            total_reward += reward

        if env.done:
            print("===total reward of episode %d %f === " % (episode, total_reward))

            break
    if arglist.record:  
        game_record_dir = env.game_record_dir
        print("GAME RECORD DIR: ", game_record_dir)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 28, encoding="unic")


        for i, file in enumerate(os.listdir(game_record_dir+"/0")):
            try: 
                print("FILE: ", file)
                my_image = Image.open(game_record_dir+"/0/"+file)

                text = "Next Action: \n" + infos[i]["action"] + "\n Step: " + str(i)
                print("TEXT: ", text)
                image_editable = ImageDraw.Draw(my_image)
                image_editable.text((15,15), text, (237, 230, 211), font=title_font)
                my_image.save(game_record_dir+"/0/"+file)
            except:
                pass


def getAvgReward(item=None):
    timesteps = list(item.keys())[-1]
    return sum(list(item.values())) / timesteps, timesteps

def plot_reward(x=None, y=None, y_=None, title='Training progress', fname='', xlabel='episodes', ylabel='total rewards'):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.plot(x, y_)

    ax.set(xlabel=xlabel, ylabel=ylabel,
        title='Training progress')
    ax.grid()

    fig.savefig("misc/metrics/graphs_rewards/{}_rewards.png".format(fname))

def plot_timesteps(x=None, y=None, y_=None, ylabel=''):
    fig, ax = plt.subplots()

    print("y: ", y)
    print("Y_: ", y_)
        
    ax.plot(x, y, label="with reward shaping")
    ax.plot(x, y_, label="without reward shaping")

    ax.set(xlabel='', ylabel=ylabel, title='Time to complete task')

    ax.grid()
    plt.legend()
    plt.show()


    #fig.savefig("misc/metrics/graphs_rewards/{}_rewards.png".format(fname))

if __name__ == '__main__':
    arglist = parse_arguments()

    print("=== RUN TRAINED AGENT AND CREATE VISUALIZATION ===")
    if 'coffee' in arglist.level:
        level = arglist.level[:-7] if 'carpet' in arglist.level else arglist.level
    else:
        level = arglist.level[:-12] if 'placeholder' in arglist.level else arglist.level
        
    arglist.data_dir = arglist.data_dir  + level + '/'

    if not os.path.exists(arglist.data_dir):
        os.makedirs(arglist.data_dir)
    data, data_no = load_data(arglist)
    run_agent(data)
    







    
