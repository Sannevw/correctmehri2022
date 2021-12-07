#from gym_cooking.utils.interact import 
import numpy as np
from collections import defaultdict, OrderedDict
from itertools import product, combinations

from numpy.core.fromnumeric import _all_dispatcher
# import networkx as nx
import copy
import matplotlib.pyplot as plt
from functools import lru_cache

import recipe_planner.utils as recipe
from utils.core import Object, GridSquare


class World:
    """World class that hold all of the non-agent objects in the environment."""

    static_names = ["Wall","Counter","Shelf","Carpet","Floor","Supply","Delivery","Sink","Cutboard","Pan","Bowl","Oven"]
    
    #FETCH_LOCATION = (2, 1)

    def __init__(self, arglist):
        self.rep = [] # [row0, row1, ..., rown]
        self.arglist = arglist
        self.objects = defaultdict(lambda : [])
        if "salad" in arglist.level:
            self.ACTION_TO_NAME = {(-1, 0): 0, (1, 0): 1, "FETCH": 2, "CHOP": 3, "DELIVER": 4} # (0, 0): 4}
        elif 'flour' in arglist.level:
            self.ACTION_TO_NAME = {(-1, 0): 0, (1, 0): 1, "FETCH": 2, "BAKE": 3, "DELIVER": 4} # (0, 0): 4}
        elif 'coffee' in arglist.level:
            self.ACTION_TO_NAME = {(0, 1): 0, (0, -1): 1, (-1, 0): 2, (1, 0): 3}
        
    def get_repr(self):
        return self.get_dynamic_objects()

    def merge_start(self):
        self.merge_starting = True

    def __str__(self):
        _display = list(map(lambda x: ''.join(map(lambda y: y + ' ', x)), self.rep))
        return '\n'.join(_display)

    def __copy__(self):
        new = World(self.arglist)
        new.__dict__ = self.__dict__.copy()
        new.objects = copy.deepcopy(self.objects)
        #new.reachability_graph = self.reachability_graph
        #new.distances = self.distances
        return new

    def get_action_name(self, val):
        for key, value in self.ACTION_TO_NAME.items():
            if val == key:
                return value
        return "key doesn't exist"

    def update_display(self):
        # Reset the current display (self.rep).
        self.rep = [[' ' for i in range(self.width)] for j in range(self.height)]
        objs = []
        for o in self.objects.values():
            objs += o
        for obj in objs:
            self.add_object(obj, obj.location)
        for obj in self.objects["Tomato"]:
            self.add_object(obj, obj.location)
        return self.rep

    def print_objects(self):
        for k, v in self.objects.items():
            print(k, list(map(lambda o: o.location, v)))

    def make_loc_to_gridsquare(self):
        """Creates a mapping between object location and object."""
        self.loc_to_gridsquare = {}
        for obj in self.get_object_list():
            if isinstance(obj, GridSquare):
                self.loc_to_gridsquare[obj.location] = obj


    def is_occupied(self, location):
        o = list(filter(lambda obj: obj.location == location and
         isinstance(obj, Object) and not(obj.is_held), self.get_object_list()))
        if o:
            return True
        return False

    def clear_object(self, position):
        """Clears object @ position in self.rep and replaces it with an empty space"""
        x, y = position
        self.rep[y][x] = ' '

    def clear_all(self):
        self.rep = []

    def add_object(self, object_, position):
        x, y = position
        self.rep[y][x] = str(object_)

    def insert(self, obj):
        self.objects.setdefault(obj.name, []).append(obj)

    def remove(self, obj):
        num_objs = len(self.objects[obj.name])
        index = None

        for i in range(num_objs):
            print(self.objects[obj.name][i].full_name)
            if self.objects[obj.name][i].location == obj.location and self.objects[obj.name][i].full_name == obj.full_name:
                index = i
        assert index is not None, "Could not find {} at {}!".format(obj.full_name, obj.location)
        
        self.objects[obj.name].pop(index)

        assert len(self.objects[obj.full_name]) < num_objs, "Nothing from {} was removed from world.objects".format(obj.name)

    def get_object_list(self):
        all_obs = []
        for o in self.objects.values():
            all_obs += o
        return all_obs

    def get_dynamic_objects(self):
        """Get objects that can be moved."""
        objs = list()

        for key in sorted(self.objects.keys()):
            if key not in World.static_names:
                # obj_ = list(map(lambda o: o.get_individual_repr(), self.objects[key]))
                obj_ = list(map(lambda o: o.get_repr(), self.objects[key]))
                if obj_:
                    if len(obj_) > 1:
                        for i in range(len(obj_)):
                            objs.append((obj_[i],))
                    else:
                        objs.append(tuple(obj_))

        # Must return a tuple because this is going to get hashed.
        return tuple(objs)

    def get_collidable_objects(self):
        return list(filter(lambda o : o.collidable, self.get_object_list()))

    def get_collidable_object_locations(self):
        return list(map(lambda o: o.location, self.get_collidable_objects()))

    def get_dynamic_object_locations(self):
        return list(map(lambda o: o.location, self.get_dynamic_objects()))

    def is_collidable(self, location):
        return location in list(map(lambda o: o.location, list(filter(lambda o: o.collidable, self.get_object_list()))))

    def get_object_locs(self, obj, is_held):
        if obj.name not in self.objects.keys():
            return []

        if isinstance(obj, Object):
            return list(
                    map(lambda o: o.location, list(filter(lambda o: obj == o and
                    o.is_held == is_held, self.objects[obj.name]))))
        else:
            return list(map(lambda o: o.location, list(filter(lambda o: obj == o,
                self.objects[obj.name]))))

    def get_all_object_locs(self, obj):
        return list(set(self.get_object_locs(obj=obj, is_held=True) + self.get_object_locs(obj=obj, is_held=False)))

    def get_object_at(self, location, desired_obj, find_held_objects):
        # Map obj => location => filter by location => return that object.
        all_objs = self.get_object_list()

        if desired_obj is None:
            objs = list(filter(
                lambda obj: obj.location == location and isinstance(obj, Object) and obj.is_held is find_held_objects,
                all_objs))
            
            if len(objs) > 1:
                objs = [x for x in objs if 'Chopped' in x.full_name or 'Plate' in x.full_name]

        else:
            if type(desired_obj) is str:
                objs = list(filter(lambda obj: obj.name == desired_obj and obj.location == location and
                isinstance(obj, Object) or desired_obj == 'AlmondFlour' and desired_obj in obj.name,     all_objs)) 
                # print("objs after FRESHH: ", [x.full_name for x in objs])        
            else:
                objs = list(filter(lambda obj: obj.name == desired_obj.name and obj.location == location and
                    isinstance(obj, Object) and obj.is_held is find_held_objects,
                    all_objs))

        # print("objs: ", [x.name for x in objs])

        assert len(objs) == 1, "looking for {}, found {} at {}".format(desired_obj, ','.join(o.get_name() for o in objs), location)

        return objs[0]

    def get_all_object_at(self, location):
        return list(filter(lambda obj: obj.location == location and isinstance(obj, Object), self.get_object_list()))


    def get_gridsquare_at(self, location):
        gss = list(filter(lambda o: o.location == location and\
            isinstance(o, GridSquare), self.get_object_list()))

        assert len(gss) == 1, "{} gridsquares at {}: {}".format(len(gss), location, gss)
        return gss[0]

    def inbounds(self, location):
        """Correct locaiton to be in bounds of world object."""
        x, y = location
        return min(max(x, 0), self.width-1), min(max(y, 0), self.height-1)
