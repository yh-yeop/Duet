import pygame
from pygame.math import Vector2
from setting import Setting


setting=Setting()

class Objects(pygame.sprite.Sprite):
    box=False
    def __init__(self,pos=Vector2(0,0),image=pygame.Surface((20,20)),angle=0):
        pygame.sprite.Sprite.__init__(self)
        self.image=image
        self.rect=self.image.get_rect()
        self.rect.topleft=pos
        self.angle=angle
        self.mask=pygame.mask.from_surface(self.image)

    @classmethod
    def onoff_box(cls,flag=None):
        if flag==None:
            cls.box=not cls.box
        else:
            cls.box=flag

    def update(self):
        pass
    
    def blit(self):
        pass


class Screen:
    def __init__(self,size=setting.SIZE):
        self.surface=pygame.Surface(size,pygame.SRCALPHA)
        self.pos=(0,0)
        self.is_screen=False

    def update(self):
        pass

    def blit(self,*args):
        pass



class Particle(Objects):
    def __init__(self,color,size,pos=Vector2(0,0),angle=0):
        self.image=pygame.Surface(size,pygame.SRCALPHA)
        self.color=color
        self.image.fill(self.color)
        self.alpha=255
        self.size=1
        super().__init__(pos,self.image,angle)

    def update(self):
        pass

    def blit(self):
        pass