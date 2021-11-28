import os
import pygame
import numpy as np
from utils.core import *
from misc.game.utils import *

graphics_dir = 'misc/game/graphics'
_image_library = {}

SHELF_LOCATION = (2, 1)
DROP_LOCATION = (1, 2)

def get_image(path):
    global _image_library
    image = _image_library.get(path)
    if image == None:
        canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
        print("path: ", canonicalized_path)
        try:
            image = pygame.image.load(canonicalized_path)
        except:
            image = pygame.image.load("misc/game/graphics/ChoppedHam.png")
        _image_library[path] = image
    return image


class Game:
    def __init__(self, world, sim_agents, level=None, play=False):
        self._running = True
        self.world = world
        self.sim_agents = sim_agents
        self.current_agent = self.sim_agents[0]
        self.play = play
        self.level = level
        
        # Visual parameters
        if 'coffee' in self.level:
            self.scale = 200
            self.agent_scale = 160
            self.agent_tile_size = (self.agent_scale, self.agent_scale)
        else:
            self.scale = 300   # num pixels per tile
            self.tile_size = (self.scale, self.scale)
            self.agent_tile_size = self.tile_size
        self.shelf_scale = 200
        
        
        self.width = self.scale * self.world.width
        self.height = self.scale * self.world.height
        self.tile_size = (self.scale, self.scale)
        self.holding_scale = 0.5
        self.container_scale = 0.7
        self.shelf_tile_size = (self.shelf_scale, self.shelf_scale)
        self.holding_size = tuple((self.holding_scale * np.asarray(self.tile_size)).astype(int))
        self.container_size = tuple((self.container_scale * np.asarray(self.tile_size)).astype(int))
        self.holding_container_size = tuple((self.container_scale * np.asarray(self.holding_size)).astype(int))


    def on_init(self):
        pygame.init()
        if self.play:
            self.screen = pygame.display.set_mode((self.width, self.height))
        else:
            # Create a hidden surface
            self.screen = pygame.Surface((self.width, self.height))
        self._running = True


    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False


    def on_render(self):
        self.screen.fill(Color.FLOOR)
        objs = []

        # Draw gridsquares
        for o_list in self.world.objects.values():
            for o in o_list:
                if isinstance(o, GridSquare):
                    self.draw_gridsquare(o)
                elif o.is_held == False:
                    objs.append(o)
        
        # Draw objects not held by agents       
        for o in objs:
            self.draw_object(o)

        # Draw agents and their holdings
        for agent in self.sim_agents:
            self.draw_agent(agent)

        if self.play:
            pygame.display.flip()
            pygame.display.update()


    def draw_gridsquare(self, gs):
        sl = self.scaled_location(gs.location)
        fill = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
        fill_s = pygame.Rect(sl[0], -sl[1], self.scale, self.scale*10)

        if isinstance(gs, Wall):
            pygame.draw.rect(self.screen, Color.WALL, fill)
            pygame.draw.rect(self.screen, Color.WALL_BORDER, fill, 1)            
        elif isinstance(gs, Counter):
            pygame.draw.rect(self.screen, Color.COUNTER, fill)
            pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
        elif isinstance(gs, Shelf):
            pygame.draw.rect(self.screen, Color.SHELF, fill_s)
            pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill_s, 1)

        elif isinstance(gs, Carpet):
            pygame.draw.rect(self.screen, Color.CARPET, fill)
            pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
            self.draw('carpet', self.tile_size, sl)
        elif isinstance(gs, Delivery):
            pygame.draw.rect(self.screen, Color.DELIVERY, fill)
            self.draw('delivery', self.tile_size, sl)

        elif isinstance(gs, Cutboard):
            pygame.draw.rect(self.screen, Color.COUNTER, fill)
            pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
            self.draw('cutboard', self.tile_size, sl)


        elif isinstance(gs, Oven):
            pygame.draw.rect(self.screen, Color.COUNTER, fill)
            pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
            self.draw('Oven', self.tile_size, sl)

        elif isinstance(gs, Sink):
            pygame.draw.rect(self.screen, Color.COUNTER, fill)
            pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
            self.draw('sink', self.tile_size, sl)

        elif isinstance(gs, Bowl):
            pygame.draw.rect(self.screen, Color.COUNTER, fill)
            pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
            self.draw('bowl', self.tile_size, sl)

        elif isinstance(gs, Pan):
            pygame.draw.rect(self.screen, Color.COUNTER, fill)
            pygame.draw.rect(self.screen, Color.COUNTER_BORDER, fill, 1)
            self.draw('pan', self.tile_size, sl)
        return


    def rot_center(self, image, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def draw(self, path, size, location, orientation=None):
        if path != "":
            if path == 'Bowl-BakedEggs-BakedFlour' or path == 'Bowl-BakedAlmondFlour-BakedEggs':
                path = 'Bowl-BakedSuccess'
            elif 'Baked' in path:
                path = 'Bowl-BakedFail'
            elif 'Bowl-' in path:
                path = 'Bowl-Content'
                
            image_path = '{}/{}.png'.format(graphics_dir, path)
            oldimage = get_image(image_path)

            if orientation is not None:
                if orientation == 0:
                    angle = -180
                elif orientation == 1:
                    angle = -90
                elif orientation == 2:
                    angle = -10
                elif orientation == 3:
                    angle = 20
                if "salad" in self.level:
                    if orientation == 4: # or orientation==5:
                        angle = 60
                    elif orientation == 5: #6 or orientation==7:
                        angle = 80
                    elif orientation == 6:
                        angle = 100
                    elif orientation == 7:
                        angle = 120
                elif "flour" in self.level:
                    if orientation == 2:
                        angle = 0
                    if orientation == 3 or orientation==4:
                        angle = 60
                    elif orientation == 5 or orientation==6:
                        angle = 80
                    elif orientation == 7 or orientation ==8:
                        angle = 100
                    elif orientation == 9 or orientation==10:
                        angle = 120
                
                image = pygame.transform.scale(get_image(image_path), size)
                image = self.rot_center(oldimage, angle) #pygame.transform.rotate(pygame.transform.scale(get_image(image_path), size), angle)
            else:
                image = pygame.transform.scale(get_image(image_path), size)
            self.screen.blit(image, location)



    ## DEPRECATED as I'm now collecting the full run of steps
    ## and then add text later on in trained_agent.py
    ## because while we run the agent, we don't know the "next action" yet.
    ## can't display the next action in text at this point.
    ## if you want to display something about the CURRENT timestep, you can use this func.
    def message_display(self, text,t):
        font = pygame.font.Font('freesansbold.ttf', 32)
        # create a text surface object,
        # on which text is drawn on it.
        green = (0, 255, 0)
        blue = (0, 0, 128)
        text_ = font.render(text+" Step: "+str(t), True, green, blue)
        textRect = text_.get_rect()
        textRect.center = (900 // 2, 100 // 2)
        self.screen.blit(text_, textRect)


    
    def draw_agent(self, agent):
        self.draw('agent-{}'.format(agent.color),
            self.agent_tile_size, self.scaled_location(agent.location,True), agent.orientation)
        self.draw_agent_object(agent.holding)

    def draw_agent_object(self, obj):
        # Holding shows up in bottom right corner.
        if obj is None: return
        # print("[c for c in conetns: ", [c for c in obj.contents])
        if any([isinstance(c, Plate) for c in obj.contents]): 
            self.draw('Plate', self.holding_size, self.holding_location(obj.location))
            if len(obj.contents) > 1:
                plate = obj.unmerge('Plate')
                self.draw(obj.full_name, self.holding_container_size, self.holding_container_location(obj.location))
                obj.merge(plate)
        else:
            if not obj.full_name == '':
                #obj.full_name = "empty"
                self.draw(obj.full_name, self.holding_size, self.holding_location(obj.location))

    def draw_object(self, obj):
        ## objects should not be shifted unless specified (shift means visually drawn somewhere else on the canvas)
        shift = None


        if obj.location == SHELF_LOCATION and "salad" in self.level:
            ## this just places the objects visually on the shelf, not on top of each other.
            if 'ChoppedTomato' in obj.full_name or 'Placeholder' in obj.name:
                shift = (30, 350)
            elif 'FreshTomato' in obj.full_name:
                shift = (30, -300)
            elif 'Lettuce' in obj.full_name:
                shift = (30, 100)
            elif 'Plate' in obj.full_name:
                shift = (30, -100)
        elif obj.location == SHELF_LOCATION and "flour" in self.level:
            ## this just places the objects visually on the shelf, not on top of each other.
            if 'ChoppedTomato' in obj.full_name:
                shift = (0, -280)
            elif 'FreshAlmondFlour' == obj.full_name:
                shift = (130, -100)
            elif 'FreshTomato' in obj.full_name:
                shift = (0, -280)
            elif 'Cheese' in obj.full_name:
                shift = (130, -280)
            elif 'Lettuce' in obj.full_name:
                shift = (0, 100)
            elif  'FreshFlour' == obj.full_name:
                shift = (0, 100)
            elif 'Plate' in obj.full_name or 'Bowl' in obj.full_name:
                shift = (0, -100)
            elif  'Eggs' in obj.full_name:
                shift = (0, 350)
            elif 'Bread' in obj.full_name:
                shift = (130, 350)
            elif 'Ham' in obj.full_name:
                shift = (130, 100)
        elif obj.location == DROP_LOCATION and "salad" in self.level:
            if 'Chopped' in obj.full_name:
                shift = (100, 0)
            else:
                shift = (-100, 0) 
        elif obj.location == DROP_LOCATION and "flour" in self.level:
            if 'Baked' in obj.full_name or 'Chopped' in obj.full_name:
                shift = (100, 0)
            else:
                shift = (-100, 0) 
            ################################################################################## 


        if obj is None: return
        if any([isinstance(c, Plate) for c in obj.contents]): 
            # we alter the loc/size of the plate when its on the shelf, purely for visualization.
            if obj.location == SHELF_LOCATION:
                self.draw(obj.full_name, self.shelf_tile_size, self.shelf_location(obj.location, shift))
            else:
                self.draw('Plate', self.tile_size, self.scaled_location(obj.location))
            if len(obj.contents) > 1:
                plate = obj.unmerge('Plate')
                self.draw(obj.full_name, self.container_size, self.container_location(obj.location))
                obj.merge(plate)
        elif obj.location == SHELF_LOCATION:
            self.draw(obj.full_name, self.shelf_tile_size, self.shelf_location(obj.location, shift))
        elif obj.location == DROP_LOCATION:
            self.draw(obj.full_name, self.tile_size, self.shelf_location(obj.location, shift))
        else:
            self.draw(obj.full_name, self.tile_size, self.scaled_location(obj.location))
        



    def scaled_location(self, loc, agent=False):
        if agent:
            return tuple(self.scale * np.asarray(loc))
        """Return top-left corner of scaled location given coordinates loc, e.g. (3, 4)"""
        return tuple(self.scale * np.asarray(loc))

    def holding_location(self, loc):
        """Return top-left corner of location where agent holding will be drawn (bottom right corner) given coordinates loc, e.g. (3, 4)"""
        scaled_loc = self.scaled_location(loc)
        return tuple((np.asarray(scaled_loc) + self.scale*(1-self.holding_scale)).astype(int))

    def container_location(self, loc):
        """Return top-left corner of location where contained (i.e. plated) object will be drawn, given coordinates loc, e.g. (3, 4)"""
        scaled_loc = self.scaled_location(loc)
        return tuple((np.asarray(scaled_loc) + self.scale*(1-self.container_scale)/2).astype(int))

    def holding_container_location(self, loc):
        """Return top-left corner of location where contained, held object will be drawn given coordinates loc, e.g. (3, 4)"""
        scaled_loc = self.scaled_location(loc)
        factor = (1-self.holding_scale) + (1-self.container_scale)/2*self.holding_scale
        return tuple((np.asarray(scaled_loc) + self.scale*factor).astype(int))

    def shelf_location(self, loc, shift=None):
        """Return shelf location given coordinates loc, e.g. (3, 4)"""
        scaled_loc = self.scaled_location(loc) 
        if shift is not None:
            scaled_loc = tuple(shift + np.asarray(scaled_loc))
        return tuple((np.asarray(scaled_loc)))

    def drop_location(self, loc, shift):
        """Return drop location given coordinates loc, e.g. (3, 4)"""
        scaled_loc = self.scaled_location(loc)
        return tuple((np.asarray(scaled_loc) + self.scale*(1-self.holding_scale)).astype(int))


    def on_cleanup(self):
        # pygame.display.quit()
        pygame.quit()
