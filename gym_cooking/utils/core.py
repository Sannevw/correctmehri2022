# recipe planning
import recipe_planner.utils as recipe

# helpers
import numpy as np
import copy
import random
from termcolor import colored as color
from itertools import combinations
from collections import namedtuple
import hashlib 

# -----------------------------------------------------------
# GRIDSQUARES
# -----------------------------------------------------------
GridSquareRepr = namedtuple("GridSquareRepr", "name location holding")

#ADD_INGREDIENT

class Rep:
    FLOOR = ' '
    COUNTER = '-'
    CARPET = '('
    SHELF = '+'
    WALL = '='
    CUTBOARD = '/'
    DELIVERY = '*'
    TOMATO = 't'
    LETTUCE = 'l'
    ONION = 'o'
    PLATE = 'p'
    CHEESE = 'c'
    BREAD = 'b'
    SINK = 'S'
    HAM = 'h'
    EGGS = 'e'
    OVEN = 'O'
    FLOUR = 'f'
    ALMONDFLOUR = 'a'
    PAN = '&'
    BOWL = 's'
    PLACEHOLDER = '$'
    COFFEE = 'C'

class GridSquare:
    def __init__(self, name, location):
        self.name = name
        self.location = location   # (x, y) tuple
        self.holding = None
        self.color = 'white'
        self.collidable = True     # cannot go through
        self.dynamic = False       # cannot move around

    def __str__(self):
        return color(self.rep, self.color)

    def __eq__(self, o):
        return isinstance(o, GridSquare) and self.name == o.name

    def __copy__(self):
        gs = type(self)(self.location)
        gs.__dict__ = self.__dict__.copy()
        if self.holding is not None:
            gs.holding = copy.copy(self.holding)
        return gs

    def acquire(self, obj):
        obj.location = self.location
        self.holding = obj

    def release(self):
        temp = self.holding
        self.holding = None
        return temp

    def is_chopped(self):
        return False

class Floor(GridSquare):
    def __init__(self, location):
        GridSquare.__init__(self,"Floor", location)
        self.color = None
        self.rep = Rep.FLOOR
        self.collidable = False
    def __eq__(self, other):
        return GridSquare.__eq__(self, other)
    def __hash__(self):
        return GridSquare.__hash__(self)

class Carpet(GridSquare):
    def __init__(self, location):
        GridSquare.__init__(self,"Carpet", location)
        self.color = None
        self.rep = Rep.CARPET
        self.collidable = False
    def __eq__(self, other):
        return GridSquare.__eq__(self, other)
    def __hash__(self):
        return GridSquare.__hash__(self)

class Counter(GridSquare):
    def __init__(self, location):
        GridSquare.__init__(self,"Counter", location)
        self.rep = Rep.COUNTER
    def __eq__(self, other):
        return GridSquare.__eq__(self, other)
    def __hash__(self):
        return GridSquare.__hash__(self)
    def is_chopped(self):
        return True

class Shelf(GridSquare):
    def __init__(self, location):
        GridSquare.__init__(self,"Shelf", location)
        self.rep = Rep.SHELF
    def __eq__(self, other):
        return GridSquare.__eq__(self, other)
    def __hash__(self):
        return GridSquare.__hash__(self)

class Wall(GridSquare):
    def __init__(self, location):
        GridSquare.__init__(self,"Wall", location)
        self.rep = Rep.WALL
    def __eq__(self, other):
        return GridSquare.__eq__(self, other)
    def __hash__(self):
        return GridSquare.__hash__(self)

class AgentCounter(Counter):
    def __init__(self, location):
        GridSquare.__init__(self,"Agent-Counter", location)
        self.rep = Rep.COUNTER
        self.collidable = True
    def __eq__(self, other):
        return Counter.__eq__(self, other)
    def __hash__(self):
        return Counter.__hash__(self)
    def get_repr(self):
        return GridSquareRepr(name=self.name, location=self.location, holding= None)

class Cutboard(GridSquare):
    def __init__(self, location):
        GridSquare.__init__(self, "Cutboard", location)
        self.rep = Rep.CUTBOARD
        self.collidable = True
    def __eq__(self, other):
        return GridSquare.__eq__(self, other)
    def __hash__(self):
        return GridSquare.__hash__(self)

class Pan(GridSquare):
    def __init__(self, location):
        GridSquare.__init__(self, "Pan", location)
        self.rep = Rep.PAN
        self.collidable = True
    def __eq__(self, other):
        return GridSquare.__eq__(self, other)
    def __hash__(self):
        return GridSquare.__hash__(self)

class Delivery(GridSquare):
    def __init__(self, location):
        GridSquare.__init__(self, "Delivery", location)
        self.rep = Rep.DELIVERY
        self.holding = []
    def acquire(self, obj):
        obj.location = self.location
        self.holding.append(obj)
    def release(self):
        if self.holding:
            return self.holding.pop()
        else: return None
    def __eq__(self, other):
        return GridSquare.__eq__(self, other)
    def __hash__(self):
        return GridSquare.__hash__(self)

class Sink(GridSquare):
    def __init__(self, location):
        GridSquare.__init__(self, "Sink", location)
        self.rep = Rep.SINK
        self.collidable = True
    def __eq__(self, other):
        return GridSquare.__eq__(self, other)
    def __hash__(self):
        return GridSquare.__hash__(self)

class Oven(GridSquare):
    def __init__(self, location):
        GridSquare.__init__(self, "Oven", location)
        self.rep = Rep.OVEN
        self.collidable = True
    def __eq__(self, other):
        return GridSquare.__eq__(self, other)
    def __hash__(self):
        return GridSquare.__hash__(self)
# -----------------------------------------------------------
# OBJECTS
# -----------------------------------------------------------
# Objects are wrappers around foods items, plates, and any combination of them

ObjectRepr = namedtuple("ObjectRepr", "name location number is_held")

class Object:
    def __init__(self, location, contents, number=None):
        self.location = location
        self.contents = contents if isinstance(contents, list) else [contents]
        self.is_held = False
        self.update_names()
        self.collidable = False
        self.dynamic = False
        self.number = number
        self.unique_name = hashlib.md5(str(contents).encode("utf-8")+str(location).encode("utf-8")).hexdigest()


    def __str__(self):
        res = "-".join(list(map(lambda x : str(x), sorted(self.contents, key=lambda i: i.name))))
        return res

    def __eq__(self, other):
        # check that content is the same and in the same state(s)
        return isinstance(other, Object) and \
                self.name == other.name and \
                len(self.contents) == len(other.contents) and \
                self.full_name == other.full_name
                # all([i == j for i, j in zip(sorted(self.contents, key=lambda x: x.name),
                #                             sorted(other.contents, key=lambda x: x.name))])

    def __copy__(self):
        new = Object(self.location, self.contents[0])
        new.__dict__ = self.__dict__.copy()
        new.contents = [copy.copy(c) for c in self.contents]
        return new

    def get_number(self):
        numbers = []
        for c in self.contents:
            numbers.append(c.number)
        return numbers

    def get_individual_repr(self):
        return ObjectRepr(name=self.unique_name, location=self.location, is_held=self.is_held)

    def get_repr(self):
        return ObjectRepr(name=self.full_name, location=self.location, number=self.number, is_held=self.is_held)

    def update_names(self):
        # concatenate names of alphabetically sorted items, e.g.
        sorted_contents = sorted(self.contents, key=lambda c: c.name)
        if len(sorted_contents) > 1:
            self.name = "-".join([c.name for c in sorted_contents if c.name != "Plate" and c.name != "Bowl"])
            self.full_name = "-".join([c.full_name for c in sorted_contents if c.full_name != 'Plate' and c.full_name != "Bowl"])
            if "Plate" in [c.name for c in sorted_contents]:
                self.name = "Plate-"+self.name
                self.full_name = "Plate-"+self.full_name
            if "Bowl" in [c.name for c in sorted_contents]:
                self.name = "Bowl-"+self.name
                self.full_name = "Bowl-"+self.full_name
        else:
            self.name = "-".join([c.name for c in sorted_contents])
            self.full_name = "-".join([c.full_name for c in sorted_contents])
            
            # print("SELF FULL NAME: ", self.full_name)
        

    def contains(self, c_name):
        return c_name in list(map(lambda c : c.name, self.contents))

    def needs_chopped(self):
        if len(self.contents) > 1: return False
        return self.contents[0].needs_chopped()

    def is_chopped(self):
        for c in self.contents:
            if isinstance(c, Plate) or isinstance(c, Bowl) or 'Chopped' not in c.get_state(): #!= 'Chopped':
                return False
        return True

    # def needs_mixed(self):
    #     if len(self.contents) > 1: return False
    #     return self.contents[0].needs_mixed()

    # def is_mixed(self):
    #     for c in self.contents:
    #         if isinstance(c, Plate) or 'Mixed' not in c.get_state(): #!= 'Chopped':
    #             return False
    #     return True

    def needs_baked(self):
        contents = self.contents.copy()
        baked = []
        try:
            contents.remove(Bowl())
            for c in contents:
                if not isinstance(c, Plate) or not isinstance(c, Bowl): #!= 'Chopped':
                    baked.append("Baked" not in c.full_name) #c.state_seq[(c.state_index+1)%len(c.state_seq)] == FoodState.BAKED
            if all(baked):
                return True
        except:
            return False 

    def is_baked(self):
        for c in self.contents:
            if isinstance(c, Plate) or isinstance(c, Bowl) or 'Baked' not in c.get_state(): #!= 'Chopped':
                return False
        return True

    # def needs_washed(self):
    #     if len(self.contents) > 1: return False
    #     return self.contents[0].needs_washed()

    # def is_washed(self):
    #     for c in self.contents:
    #         if isinstance(c, Plate) or c.get_state() != 'ChoppedWashed':
    #             return False
    #     return True


    def chop(self):
        if not self.is_chopped():
            assert len(self.contents) == 1
            assert self.needs_chopped()
            self.contents[0].update_state()
            assert not (self.needs_chopped())
            self.update_names()
            return 1

    def bake(self):
        contents = self.contents.copy()
        try:
            contents.remove(Bowl())
        except:
            pass
        finally:
            if not self.is_baked():
                # print("SELF: " , contents)
                #assert len(self.contents) == 1
                for c in contents:
                    print("C:", c)
                    assert c.needs_baked()
                    
                    c.update_state()
                    # print("c.get: ", c.get_state())
                    assert not (self.needs_baked())
                    #c.update_names()
                    # print("cname: ", c.full_name)
                self.update_names()
                return 1

    def wash(self):
        assert len(self.contents) == 1
        assert self.needs_washed()
        self.contents[0].update_state()
        assert not (self.needs_washed())
        self.update_names()
        return 1

    def mix(self):
        if not self.is_mixed():
            assert len(self.contents) == 1
            assert self.needs_mixed()
            self.contents[0].update_state()
            assert not (self.needs_mixed())
            self.update_names()
            return 1


    def merge(self, obj):
        if isinstance(obj, Object):
            # move obj's contents into this instance
            for i in obj.contents: self.contents.append(i)     
        elif not (isinstance(obj, Food) or isinstance(obj, Plate) or isinstance(obj, Bowl)):
            raise ValueError("Incorrect merge object: {}".format(obj))
        else:
            self.contents.append(obj)
        # print("self: ", self)
        # print("obj: ", obj)
        if not isinstance(obj, Plate): self.number = self.number * obj.number
        self.update_names()
        

    def unmerge(self, full_name):
        # remove by full_name, assumming all unique contents
        # print("self.contents: ", self.contents)
        # print([x.full_name for x in self.contents]) 
        matching = list(filter(lambda c: c.full_name == full_name, self.contents))
        # print("matching: ", matching)
        # print("matching[0] 1: ", matching[0])
        self.contents.remove(matching[0])
        # print("self.contents AFTER: ", self.contents)
        self.update_names()
        return matching[0]

    def is_merged(self):
        return len(self.contents) > 1

    def is_deliverable(self):
        # must be merged, and all contents must be Plates or Foods in done state
        # we serve every dish on a plate
        if "Plate" in [x.name for x in self.contents] or 'Bowl' in [x.name for x in self.contents] or 'Coffee' in [x.name for x in self.contents]:
            for c in self.contents: 
                if not (isinstance(c, Bowl) or (isinstance(c,Plate)) or (isinstance(c, Food))): # and not c.done()):
                    return False
            return True #self.is_merged()
        else:
            # no plate, no delivery
            print("no bowl/plate")
            return False

    def is_plated(self):
        for c in self.contents:
            if isinstance(c, Plate):
                return True
        return False

    def is_plated(self):
        for c in self.contents:
            if isinstance(c, Plate):
                return True
        return False


def mergeable(obj1, obj2,level=None):
    # query whether two objects are mergeable
    contents = obj1.contents + obj2.contents
    # check that there is at most one plate
    try:
        contents.remove(Plate())
    except:
        pass  # do nothing, 1 plate is ok
    finally:
        try:
            contents.remove(Plate())
        except:
            try:
                contents.remove(Bowl())
            except:
                for c in contents:   # everything else must be in last state
                    if not c.done(level):
                        print("c: ", c.full_name)
                        print("c.done: ", c.done(level))
                        return False # changed to have anything be plated, was False
                    # elif 'FriedEggs' in shield_obj:
                        # if not c.done():
                            # return False
                    #else:
                    
        else:
            return False  # more than 1 plate
    return True


# -----------------------------------------------------------

class FoodState:
    FRESH = globals()['recipe'].__dict__['Fresh']
    CHOPPED = globals()['recipe'].__dict__['Chopped']
    BAKED = globals()['recipe'].__dict__['Baked']
    MIXED = globals()['recipe'].__dict__['Mixed']
    CHOPPED_WASHED = globals()['recipe'].__dict__['ChoppedWashed']


class FoodSequence:
    FRESH = [FoodState.FRESH]
    FRESH_BAKED = [FoodState.FRESH, FoodState.BAKED] 
    FRESH_CHOPPED = [FoodState.FRESH, FoodState.CHOPPED]
    FRESH_CHOPPED_BAKED = [FoodState.FRESH, FoodState.CHOPPED, FoodState.BAKED]
    CHOPPED_WASHED = [FoodState.CHOPPED, FoodState.CHOPPED_WASHED]
    FRESH_MIXED = [FoodState.FRESH, FoodState.MIXED]

class Food:
    def __init__(self):
        self.state = self.state_seq[self.state_index]
        self.movable = False
        self.color = self._set_color()
        self.update_names()

    def __str__(self):
        return color(self.rep, self.color)

    # def __hash__(self):
    #     return hash((self.state, self.name))

    def __eq__(self, other):
        return isinstance(other, Food) and self.get_state() == other.get_state()

    def __len__(self):
        return 1   # one food unit

    def set_state(self, state):
        assert state in self.state_seq, "Desired state {} does not exist for the food with sequence {}".format(state, self.state_seq)
        self.state_index = self.state_seq.index(state)
        self.state = state
        self.update_names()

    def get_state(self):
        return self.state.__name__

    def update_names(self):
        self.full_name = '{}{}'.format(self.get_state(), self.name)

    def needs_chopped(self):
        try:
            return self.state_seq[(self.state_index+1)%len(self.state_seq)] == FoodState.CHOPPED
        except:
            return False

    def needs_baked(self):
        try:
            return self.state_seq[(self.state_index+1)%len(self.state_seq)] == FoodState.BAKED
        except:
            return False


    def needs_mixed(self):
        try:
            return self.state_seq[(self.state_index+1)%len(self.state_seq)] == FoodState.MIXED
        except:
            return False

    def done(self,level=None):
        if 'salad' in level:
            return (self.state_index % len(self.state_seq)) == len(self.state_seq) - 2
        else:
            return (self.state_index % len(self.state_seq)) == len(self.state_seq) - 1

    def update_state(self):
        self.state_index += 1

        assert 0 <= self.state_index and self.state_index < len(self.state_seq), "State index is out of bounds for its state sequence"
        self.state = self.state_seq[self.state_index]
        self.update_names()

    def _set_color(self):
        pass

class Tomato(Food):
    def __init__(self, state_index = 1):
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH_CHOPPED_BAKED
        self.rep = 't'
        self.name = 'Tomato'

        Food.__init__(self)
    def __hash__(self):
        return Food.__hash__(self)
    def __eq__(self, other):
        return Food.__eq__(self, other)
    def __str__(self):
        return Food.__str__(self)

class Coffee(Food):
    def __init__(self, state_index = 0):
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH
        self.rep = 'C'
        self.name = 'Coffee'

        Food.__init__(self)
    def __hash__(self):
        return Food.__hash__(self)
    def __eq__(self, other):
        return Food.__eq__(self, other)
    def __str__(self):
        return Food.__str__(self)
        
class Lettuce(Food):
    def __init__(self, state_index = 1):
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH_CHOPPED_BAKED
        self.rep = 'l'
        self.name = 'Lettuce'
        Food.__init__(self)
    def __eq__(self, other):
        return Food.__eq__(self, other)
    def __hash__(self):
        return Food.__hash__(self)

class Onion(Food):
    def __init__(self, state_index = 0):
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH_CHOPPED
        self.rep = 'o'
        self.name = 'Onion'
        Food.__init__(self)
    def __eq__(self, other):
        return Food.__eq__(self, other)
    def __hash__(self):
        return Food.__hash__(self)

class Bread(Food):
    def __init__(self, state_index=1):
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH_CHOPPED_BAKED
        self.rep = 'b'
        self.name = 'Bread'
        Food.__init__(self)
    def __hash__(self):
        return Food.__hash__(self)
    def __eq__(self, other):
        return Food.__eq__(self, other)
    def __str__(self):
        return Food.__str__(self)

class Cheese(Food):
    def __init__(self, state_index = 1):
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH_CHOPPED_BAKED
        self.rep = 'c'
        self.name = 'Cheese'

        Food.__init__(self)
    def __hash__(self):
        return Food.__hash__(self)
    def __eq__(self, other):
        return Food.__eq__(self, other)
    def __str__(self):
        return Food.__str__(self)

class Eggs(Food):
    def __init__(self, state_index = 0):
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH_BAKED
        self.rep = 'e'
        self.name = 'Eggs'

        Food.__init__(self)
    def __hash__(self):
        return Food.__hash__(self)
    def __eq__(self, other):
        return Food.__eq__(self, other)
    def __str__(self):
        return Food.__str__(self)

class Flour(Food):
    def __init__(self, state_index = 0):
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH_BAKED
        self.rep = 'f'
        self.name = 'Flour'

        Food.__init__(self)
    def __hash__(self):
        return Food.__hash__(self)
    def __eq__(self, other):
        return Food.__eq__(self, other)
    def __str__(self):
        return Food.__str__(self)

class AlmondFlour(Food):
    def __init__(self, state_index = 0):
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH_BAKED
        self.rep = 'a'
        self.name = 'AlmondFlour'

        Food.__init__(self)
    def __hash__(self):
        return Food.__hash__(self)
    def __eq__(self, other):
        return Food.__eq__(self, other)
    def __str__(self):
        return Food.__str__(self)


class Ham(Food):
    def __init__(self, state_index = 1):
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH_CHOPPED_BAKED
        self.rep = 'h'
        self.name = 'Ham'

        Food.__init__(self)
    def __hash__(self):
        return Food.__hash__(self)
    def __eq__(self, other):
        return Food.__eq__(self, other)
    def __str__(self):
        return Food.__str__(self)

class Placeholder:
    def __init__(self, state_index = 1):
        self.rep = Rep.PLACEHOLDER
        self.state_index = state_index   # index in food's state sequence
        self.state_seq = FoodSequence.FRESH_CHOPPED
        self.name = 'Placeholder'
        self.full_name = ""
        self.color = 'white'

    def __hash__(self):
        return hash((self.name))
    def __str__(self):
        return color(self.rep, self.color)
    def __eq__(self, other):
        return isinstance(other, Plate)
    def __copy__(self):
        return Placeholder()


        
# -----------------------------------------------------------

class Plate:
    def __init__(self):
        self.rep = Rep.PLATE
        self.name = 'Plate'
        self.full_name = 'Plate'
        self.color = 'white'
    def __hash__(self):
        return hash((self.name))
    def __str__(self):
        return color(self.rep, self.color)
    def __eq__(self, other):
        return isinstance(other, Plate)
    def __copy__(self):
        return Plate()
    def needs_chopped(self):
        return False
    def needs_washed(self):
        return False
    def needs_mixed(self):
        return False
    def done(self):
        return False

class Bowl:
    def __init__(self, state_index = 0):
        self.rep = Rep.BOWL
        self.name = 'Bowl'
        self.full_name = 'Bowl'
        self.color = 'white'
    def __hash__(self):
        return hash((self.name))
    def __str__(self):
        return color(self.rep, self.color)
    def __eq__(self, other):
        return isinstance(other, Bowl)
    def __copy__(self):
        return Bowl()
    def needs_chopped(self):
        return False
    def needs_washed(self):
        return False
    def needs_baked(self):
        return True
    def needs_mixed(self):
        return False
    def done(self,level=None):
        return False


# -----------------------------------------------------------
# PARSING
# -----------------------------------------------------------
RepToClass = {
    Rep.FLOOR: globals()['Floor'],
    Rep.COUNTER: globals()['Counter'],
    Rep.CARPET: globals()['Carpet'],
    Rep.SHELF: globals()['Shelf'],
    Rep.WALL: globals()['Wall'],
    Rep.CUTBOARD: globals()['Cutboard'],
    Rep.DELIVERY: globals()['Delivery'],
    Rep.TOMATO: globals()['Tomato'],
    Rep.LETTUCE: globals()['Lettuce'],
    Rep.ONION: globals()['Onion'],
    Rep.PLATE: globals()['Plate'],
    Rep.BREAD: globals()['Bread'],
    Rep.CHEESE: globals()['Cheese'],
    Rep.EGGS: globals()['Eggs'],
    Rep.HAM: globals()['Ham'],
    Rep.FLOUR: globals()['Flour'],
    Rep.ALMONDFLOUR: globals()['AlmondFlour'],
    Rep.SINK: globals()['Sink'],
    Rep.PAN: globals()['Pan'],
    Rep.BOWL: globals()['Bowl'],
    Rep.OVEN: globals()['Oven'],
    Rep.PLACEHOLDER: globals()['Placeholder'],
    Rep.COFFEE: globals()['Coffee'],
}
