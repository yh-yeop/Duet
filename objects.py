import pygame
from setting import *
from pygame.math import Vector2
from util import *
import pandas as pd
import numpy as np
setting=Setting()
FRAME_SPEED=setting.SPEED_CONSTANT

class Objects(pygame.sprite.Sprite):
    box=False
    def __init__(self,pos=Vector2(0,0),image=pygame.Surface((20,20)),angle=0):
        pygame.sprite.Sprite.__init__(self)
        self.image=image
        self.rect=self.image.get_rect()
        self.rect.topleft=pos
        self.angle=angle


class Player(Objects):
    speed=2
    r=12
    distance=setting.center[0]//5*2
    def __init__(self,color,center,direction):
        self.center=Vector2(center)
        self.angle=180 if direction=="left" else 0
        pos=self.center+Vector2(self.distance,0).rotate(self.angle)
        self.color=color
        self.alpha=220
        self.image=pygame.Surface((5,5),pygame.SRCALPHA)
        pygame.draw.rect(self.image,setting.white,(0,0,*self.image.get_size()),1)
        self.particle_group=pygame.sprite.Group()
        super().__init__(pos,self.image,self.angle)

    
    def update(self,angle_plus):
        self.angle+=angle_plus*self.speed*FRAME_SPEED
        self.rect.center=self.center+Vector2(self.distance,0).rotate(self.angle)
        self.particle_group.add(Particle(self.color,self.rect.topleft,self.angle))
        self.particle_group.update()
        for p in self.particle_group:
            if (not p.image.get_alpha()) or (not p.size):
                self.particle_group.remove(p)



    def blit(self,background):
        player_surface=pygame.Surface(setting.size,pygame.SRCALPHA)
        for p in self.particle_group: p.blit(player_surface)
        pygame.draw.circle(player_surface,(*self.color,self.alpha),self.rect.topleft,self.r)
        if self.box:
            a=self.rect.copy()
            a.center=a.topleft
            player_surface.blit(self.image,a.topleft)
        background.blit(player_surface,(0,0))

class Particle(Objects):
    speed=0
    def __init__(self,color,pos=Vector2(0,0),angle=0):
        self.image=pygame.Surface((17,10),pygame.SRCALPHA)
        self.color=color
        self.image.fill(self.color)
        self.alpha=128
        # self.image.set_alpha(self.alpha)
        super().__init__(pos,self.image,angle)
        self.image=pygame.transform.rotozoom(self.image,self.angle,1)
        self.blit_image=self.image.copy()
        self.size=1

    def update(self):
        self.size=max(self.size-0.01*FRAME_SPEED,0)
        self.alpha=max(self.alpha-2.5*FRAME_SPEED,0)
        self.rect.y+=self.speed*FRAME_SPEED
        self.blit_image=pygame.transform.rotozoom(self.image,self.angle,self.size)
        self.blit_image.set_alpha(self.alpha)

    def blit(self,background):
        blit_pos=Vector2(*self.rect.topleft)-Vector2(*self.blit_image.get_size())//2
        background.blit(self.blit_image,blit_pos)

class Obstacle(Objects):
    def __init__(self,*args):
        """shape: [rect,special]
            special: [1,2]"""
            # args[i]=string_to_int(args[i])
        self.shape,self.dx,self.dy,self.x,self.y,self.w,self.h,\
            self.angle,self.angle_plus,self.dx_plus,self.dy_plus=args
        if self.shape=="rect": image=pygame.Surface((self.w,self.h),pygame.SRCALPHA)
        else: raise SyntaxError
        image.fill(setting.white)
        super().__init__(Vector2(self.x,self.y),image,self.angle)
        self.invincible=False
        self.pos=list(self.rect.center)
        self.backup_image=self.image.copy()


    def update(self,speed=1):
        self.pos[0]+=self.dx*speed*FRAME_SPEED
        self.pos[1]+=self.dy*speed*FRAME_SPEED
        self.rect.center=self.pos
        if self.angle_plus:
            self.angle+=self.angle_plus*speed*FRAME_SPEED
        if self.angle:
            self.image=pygame.transform.rotozoom(self.backup_image,-self.angle,1)
            self.rect=self.image.get_rect(center=self.pos)
        else:
            self.image=self.backup_image
        if self.rect.y>=setting.center[1]:
            if self.dx_plus: self.dx+=self.dx_plus*speed*FRAME_SPEED
            if self.dy_plus: self.dy+=self.dy_plus*speed*FRAME_SPEED

    def collide_check(self,players):
        re_value=[(pygame.sprite.collide_mask(self,players[i]),i) for i in range(2)]
        if self.invincible:
            re_value=[]
            return re_value
        for row in re_value:
            if row[0]:
                if self.angle:
                    self.backup_image=pygame.transform.rotozoom(self.backup_image,-self.angle,1)
                    pygame.draw.rect(self.backup_image,players[row[1]].color,(*(Vector2(row[0])-Vector2(2.5,2.5)),5,5))
                    self.backup_image=pygame.transform.rotozoom(self.backup_image,self.angle,1)

                else:
                    pygame.draw.rect(self.backup_image,players[row[1]].color,(*(Vector2(row[0])-Vector2(2.5,2.5)),5,5))
        return re_value

class Button(Objects):
    def __init__(self,image,pos=Vector2(0,0)):
        self.image=image
        super().__init__(pos,self.image)

    def mouse_check(self,mouse,click):
        return pygame.sprite.collide_mask(mouse,self),click
    
    def blit(self,background):
        background.blit(self.image,self.rect.topleft)
        if self.box:
            pygame.draw.rect(background,setting.white,self.rect,1)



class Screen:
    name="Screen"
    def __init__(self,size=setting.size):
        self.surface=pygame.Surface(size,pygame.SRCALPHA)
        self.is_screen=True
        self.eng_font="Montserrat/static/Montserrat-Thin.ttf"
        self.kor_font="malgungothic"
        self.pos=(0,0)

    def update(self,*args):
        pass

    def blit(self,background):
        background.blit(self.surface,self.pos)


class Intro(Screen):
    name="Intro"
    def __init__(self):
        super().__init__()
        self.alpha=30
        self.r=setting.size[1]+200
        self.texts=[(return_text(return_font(30,self.kor_font),"제작",color=setting.black),[setting.center[0],setting.center[1]-50]),
                    (return_text(return_font(30,self.eng_font,isfile=True),"Yoon Ho Yeop",color=setting.black),list(setting.center)),
                    (return_text(return_font(30,self.kor_font),"음악",color=setting.black),[setting.center[0],setting.center[1]+50]),
                    (return_text(return_font(30,self.eng_font,isfile=True),"Tim Shiel",color=setting.black),[setting.center[0],setting.center[1]+100])]
                
        for text in self.texts: text[1][0]-=text[0].get_size()[0]//2

    def is_intro_done(self):
        if self.is_screen and self.r==100:
            self.is_screen=False
            return True
        return False
    
    def update(self):
        if self.is_screen:
            self.r=max(self.r-3,100)
            if self.r>setting.size[1]-100: self.alpha+=5

            else:
                self.alpha=max(self.alpha-4,0)
                for i in np.arange(0,len(self.texts),2): self.texts[i][0].set_alpha(self.alpha)

            for i in np.arange(0,len(self.texts),2): self.texts[i+1][0].set_alpha(self.alpha)

    def blit(self,background):
        if self.is_screen:
            self.surface.fill(setting.black)
            pygame.draw.circle(self.surface,setting.white,setting.player_center["menu"],self.r)
            for text in self.texts:
                self.surface.blit(*text)
            background.blit(self.surface,(0,0))
    
class Menu(Screen):
    name="Menu"
    def __init__(self):
        super().__init__()
        self.is_screen=False
        self.start=False
        self.text=[return_text(return_font(120,self.eng_font,isfile=True),"DUET"),Vector2(setting.center[0],0)]
        self.text[1]-=Vector2(*self.text[0].get_size())//2
        self.text[1][1]-=self.text[0].get_size()[1]//2
        self.button_size=60
        self.buttons=[Button(return_image("setting.png",(self.button_size,self.button_size)),[20,setting.size[1]]),
                      Button(return_image("play.png",(self.button_size,self.button_size)),[setting.size[0]-20-self.button_size,setting.size[1]])]
        self.pos=[0,0]
        self.log_print=False
        self.playmenu=PlayMenu()
        self.settingmenu=SettingMenu()
    
    def update(self):
        self.surface.fill(setting.black)
        if self.start and self.is_screen:
            if self.text[1][1]!=25:
                self.text[1][1]=min(self.text[1][1]+11*FRAME_SPEED,25)
            for button in self.buttons:
                if button.rect.y!=setting.size[1]-self.button_size-20:
                    button.rect.y=max(button.rect.y-5,setting.size[1]-self.button_size-20)

    def button_check(self,mouse,click):
        for button in self.buttons:
            if button==self.buttons[0] and all(button.mouse_check(mouse,click)):
                print("설정 누름")
            elif button==self.buttons[1] and all(button.mouse_check(mouse,click)):
                print("플레이 누름")
        return [button.mouse_check(mouse,click) for button in self.buttons]
        
    def blit(self,background):
        if self.is_screen:
            self.surface.blit(*self.text)
            for b in self.buttons: b.blit(self.surface)
            background.blit(self.surface,self.pos)

class PlayMenu(Screen):
    def __init__(self):
        super().__init__((setting.size[0]//1.3,setting.size[1]))
        self.pos=[setting.size[0],0]
        self.is_screen=False

class SettingMenu(Screen):
    def __init__(self):
        super().__init__((setting.size[0]//1.3,setting.size[1]))
        self.pos=[-self.surface.get_size()[0],0]
        self.is_screen=False

class InGame(Screen):
    name="InGame"
    def __init__(self):
        super().__init__()
        self.is_screen=False
        self.level=Level("test_level")

    def update(self):
        if self.is_screen:
            self.surface.fill(setting.black)
            self.level.update()

    
    def collide_check(self,players):
        return self.level.collide_check(players) if self.is_screen else False

    def blit(self,background):
        if self.is_screen:
            self.level.blit(self.surface)
            background.blit(self.surface,(0,0))

class PauseScreen(Screen):
    def __init__(self):
        super().__init__()

class Level:
    def __init__(self,name):
        path="assets/level/"+name
        try:
            self.df=pd.read_csv(path,encoding="cp949")
        except FileNotFoundError:
            self.df=pd.read_csv("Duet/"+path+".csv",encoding="cp949")
        self.max_obs=len(self.df)
        self.obs_group=pygame.sprite.Group(*[Obstacle(*self.df.loc[i].to_dict().values()) for i in range(self.max_obs)])
        self.rewind=False

    def update(self):
        if self.rewind:
            for o in self.obs_group: o.update(-20)
            if self.obs_group.sprites()[0].rect.y<=self.df.loc[0].to_dict()["y"]:
                for o in self.obs_group:
                    o.rect.topleft=o.x,o.y
                    o.rect.size=o.w,o.h
                self.rewind=False
                for o in self.obs_group: o.invincible=False
        else:
            for o in self.obs_group: o.update()

        if self.obs_group.sprites()[-1].rect.top>setting.size[1]:
            self.rewind=True
            for o in self.obs_group: o.invincible=True
            

    def collide_check(self,players):
        re_value=[]
        for o in self.obs_group:
            check=o.collide_check(players)
            for i in check:
                if i[0] and (re_value==[] or i[1]!=re_value[0][1]):
                    re_value.append(i)
        # if re_value:
        #     self.rewind=True
        #     for o in self.obs_group: o.invincible=True
        return re_value if len(re_value)!=1 else re_value[0]

    def blit(self,background):
        for obs in self.obs_group:
            background.blit(obs.image,obs.rect)
            if obs.box:
                pygame.draw.rect(background,setting.white,obs.rect,1)



if __name__=="__main__":
    lv=Level("test_level")
    for obs in lv.obs_group:
        print(obs.rect.y)