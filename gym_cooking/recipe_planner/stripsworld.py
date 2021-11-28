import recipe_planner.utils as recipe

# core modules
from utils.core import Object

# helpers
import networkx as nx
import copy


class STRIPSWorld:
    def __init__(self, world, recipes):
        self.initial = recipe.STRIPSState()
        self.recipes = recipes

        # set initial state
        self.initial.add_predicate(recipe.NoPredicate())
        for obj in world.get_object_list():
            if isinstance(obj, Object):
                for obj_name in ['Plate', 'Tomato', 'Lettuce', 'Onion', 'Bread', 'Cheese']:
                    if obj.contains(obj_name):
                        self.initial.add_predicate(recipe.Fresh(obj_name))


    def get_subtasks(self, max_path_length=10, draw_graph=False):
        action_paths = []

        for recipe in self.recipes:
            graph, goal_state = self.generate_graph(recipe, max_path_length)

            if draw_graph:   # not recommended for path length > 4
                nx.draw(graph, with_labels=True)
                plt.show()
            
            all_state_paths = nx.all_shortest_paths(graph, self.initial, goal_state)
            union_action_path = set()
            for state_path in all_state_paths:
                action_path = [graph[state_path[i]][state_path[i+1]]['obj'] for i in range(len(state_path)-1)]
                union_action_path = union_action_path | set(action_path)
            # print('all tasks for recipe {}: {}\n'.format(recipe, ', '.join([str(a) for a in union_action_path])))
            action_paths.append(union_action_path)

        return action_paths
        

    def check_goal(self, recipe, state):
        # check if this state satisfies completion of this recipe
        return state.contains(recipe.goal)




