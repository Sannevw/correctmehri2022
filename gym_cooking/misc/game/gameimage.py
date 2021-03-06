import pygame
import os
import numpy as np
from PIL import Image
from misc.game.game import Game
# from misc.game.utils import *
from datetime import datetime

class GameImage(Game):
    def __init__(self, filename, world, sim_agents, level, record=False, train=False, shield=False):
        Game.__init__(self, world, sim_agents, level)
        date = datetime.now().strftime("%Y_%m_%d")
        if train:
            self.game_record_dir = 'misc/game/record/trained_agent/{}/'.format(filename+'_'+date)
        else:
            self.game_record_dir = 'misc/game/record/{}/'.format(filename+'_'+date+'Shield_'+str(shield))
        self.record = record


    def on_init(self):
        super().on_init()

        if self.record:
            # Make game_record folder if doesn't already exist
            if not os.path.exists(self.game_record_dir):
                os.makedirs(self.game_record_dir)
        

            # Clear game_record folder
            # for f in os.listdir(self.game_record_dir):
            #     try:
            #         os.remove(os.path.join(self.game_record_dir, f))
            #     except:
            #         for sf in os.listdir(os.path.join(self.game_record_dir,f)):
            #             os.remove(os.path.join(self.game_record_dir, f, sf))

    def get_image_obs(self):
        self.on_render()
        img_int = pygame.PixelArray(self.screen)
        img_rgb = np.zeros([img_int.shape[1], img_int.shape[0], 3], dtype=np.uint8)
        for i in range(img_int.shape[0]):
            for j in range(img_int.shape[1]):
                color = pygame.Color(img_int[i][j])
                img_rgb[j, i, 0] = color.g
                img_rgb[j, i, 1] = color.b
                img_rgb[j, i, 2] = color.r
        return img_rgb

    def save_image_obs(self, t, episode):
        self.on_render()
        if episode % 1 == 0: # and episode > 199:
            os.makedirs(self.game_record_dir+'/'+str(episode)+'/', exist_ok=True)
            pygame.image.save(self.screen, '{}/t={:03d}.png'.format(os.path.join(self.game_record_dir, str(episode)), t))
        
