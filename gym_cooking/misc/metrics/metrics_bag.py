from os import stat
import pickle as pickle
import copy
from datetime import datetime

class Bag:
    def __init__(self, arglist, filename):
        self.data = {}
        self.arglist = arglist
        self.directory = arglist.data_dir
        self.filename = filename
        self.set_general()
        self.shield = arglist.shield

    def set_general(self):
        self.data["level"] = self.arglist.level

        ''' add a run because we do 10 runs with different random choice'''

        for run_ in range(self.arglist.num_runs):
            run = "run_"+str(run_)
            self.data.setdefault(run, {})
            # print("self data: ", self.data)
            # Prepare for agent information
            for episode in range(self.arglist.num_episodes):
                self.data[run][episode] = {}
                for info in ["states","actions"]: #,"holding"]:
                    self.data[run][episode][info] = {"agent-{}".format(1): []}
                self.data[run][episode]["rewards"] = {}

    def add_status(self, run, cur_time, reward, real_agents, episode):
        for a in real_agents:
            self.data[run][episode]["states"][a.name].append(copy.copy(a.location))
            # self.data[run][episode]["holding"][a.name].append(a.get_holding())
            self.data[run][episode]["actions"][a.name].append(a.action)
            self.data[run][episode]["rewards"].setdefault(cur_time, [])
            self.data[run][episode]["rewards"][cur_time] = reward

    def set_termination(self, run, termination_info, successful, total_r, qtable, statedict, episode, t):
        self.data[run][episode]["termination"] = termination_info
        self.data[run][episode]["was_successful"] = successful
        self.data[run][episode]["total_rewards"] = total_r
        self.data[run][episode]["qtable"] = qtable
        self.data[run][episode]["statedict"] = statedict
        self.data[run][episode]["timesteps"] = t
        # self.data[run][episode].setdefault("terminated_at_timstep", [])
        # self.data[run]["terminated_at_episode"] = terminated
            # self.data[run][episode]["terminated_at_timestep"] = terminated

# /        print("self data: ", self.data)
        pickle.dump(self.data, open(self.directory+self.filename+'Shielded_'+str(self.shield)+'.pkl', "wb"))
        print("Saved to {}".format(self.directory+self.filename+'Shielded_'+str(self.shield)+'.pkl'))

