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

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

if __name__ == '__main__':

    path = './pickles/salad/'

    print('Loading data from path: {}'.format(path))

    # load data for each variation
    p_init = pickle.load(open(path+'init_agent.pkl','rb'))
    p_shield = pickle.load(open(path+'withshield.pkl','rb'))
    p_without = pickle.load(open(path+'withoutshield.pkl','rb'))


    # extract rewards
    r_init = np.array([np.sum(list(s['rewards'].values())) for s in list(p_init['run_0'].values()) if s['rewards']])
    r_shield = [np.array([np.sum(list(s['rewards'].values())) for s in list(p_shield['run_'+str(i)].values())]) for i in range(10)]
    r_shield_av = np.average(r_shield,axis=0)
    r_without = [np.array([np.sum(list(s['rewards'].values())) for s in list(p_without['run_'+str(i)].values())]) for i in range(10)]
    r_without_av = np.average(r_without,axis=0)

    print('Data is for experiment: {}'.format(p_init['level']))

    print('Creating figures:')

    # set matplotlib things
    matplotlib.rcParams['svg.fonttype'] = 'none'
    matplotlib.rcParams['font.sans-serif'] = 'Latin Modern Math'
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['font.size'] = 10

    av_filter = 5

    plt.figure(figsize=(3.5,2))
    #plt.plot(r_init,'-k')
    #plt.plot(moving_average(r_shield[0],av_filter),'-b')
    plt.plot(moving_average(r_shield_av,av_filter),'-b')
    plt.plot(moving_average(r_without[0],av_filter),'-r')
    #plt.plot(r_without_av,'-r')
    plt.plot(moving_average(r_init,av_filter),'-k')
    plt.plot([0,250],[0.6,0.6],'--k')
    plt.autoscale()
    plt.xlabel('episodes')
    plt.ylabel('reward')
    plt.show()

