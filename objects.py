import pygame
from pygame.math import Vector2
from setting import Setting
from util import *
from abstract_objects import Objects,Screen,Particle
import json
import numpy as np
import math

setting=Setting()
FRAME_SPEED=(1000//setting.FRAME)/(1000//120)
def set_speed(dt):
    global FRAME_SPEED
    FRAME_SPEED=dt/(1000//120)


class Hitbox(Objects):
    def __init__(self,pos=Vector2(0,0),image=pygame.Surface((20,20)),angle=0):
        super().__init__(pos,image,angle)
    
    def update(self,pos:Vector2):
        self.rect.center=pos

    def blit(self,background:pygame.Surface):
        background.blit(self.image,self.rect)

class Player(Objects):
    speed=2
    r=12
    distance=setting.CENTER[0]//5*2
    rewind_angle=0
    center=setting.PLAYER_CENTER["menu"]
    def __init__(self,color:tuple,center:tuple,direction:str):
        self.center=Vector2(center)
        self.angle=180 if direction=="left" else 0
        self.image=pygame.Surface((1,1),pygame.SRCALPHA)
        pygame.draw.rect(self.image,setting.WHITE,(0,0,*self.image.get_size()),1)
        pos=self.center+Vector2(self.distance,0).rotate(self.angle)
        super().__init__(pos,self.image,self.angle)
        
        self.alpha=180
        self.color=color
        self.particle_group=pygame.sprite.Group()
        self.rewind=[None,0]
        self.death_tick=0
        self.death_particle_group=pygame.sprite.Group()

    @classmethod
    def set_rewind_angle(cls,angle:int):
        cls.rewind_angle=angle

    def set_rewind_speed(self):
        self.rewind[1]=setting.FRAME*0.8
        self.rewind[0]=(540-Player.rewind_angle)/self.rewind[1]

    def change_center(self,screen:str):
        func=min if screen=="ingame" else max
        self.center[1]=func(setting.PLAYER_CENTER["ingame"][1]-setting.PLAYER_CENTER["menu"][1]/(setting.FRAME),setting.PLAYER_CENTER[screen][1])
        
    def reset_particle(self):
        self.particle_group=pygame.sprite.Group()

    def die(self):
        self.death_tick=84
        for _ in range(50): self.death_particle_group.add(DeathParticle(self.color,self.rect.center))

    def update(self,angle_plus:int):
        if not self.death_tick:
            if not self.rewind[1]:
                self.angle=(self.angle+angle_plus*self.speed*FRAME_SPEED)%360
            else:
                self.angle=(self.angle+self.rewind[0])%360
                self.rewind[1]-=1
                if not self.rewind[1]:
                    self.angle=round(self.angle)%360
                    # color=" red" if self.color==setting.RED else "blue"
                    # print(f"color: {color} angle: {self.angle}")
                    # # print(f"color: {" red" if self.color==setting.RED else "blue"} angle: {self.angle}")
        else:
            self.death_tick-=1
        self.rect.center=self.center+Vector2(self.distance,0).rotate(self.angle)
        if angle_plus:
            self.particle_group.add(PlayerParticle(self.color,self.rect.topleft,self.angle))
        else:
            self.particle_group.add(PlayerParticle(self.color,self.rect.topleft,0))
        self.particle_group.update()
        self.death_particle_group.update()
        for dp in self.death_particle_group:
            if not (dp.rect.x in range(setting.SIZE[0]+1) and dp.rect.y in range(setting.SIZE[1]+1)):
                self.death_particle_group.remove(dp)
        for p in self.particle_group:
            if (not p.image.get_alpha()) or (not p.size):
                self.particle_group.remove(p)


    def blit(self,background:pygame.Surface):
        player_surface=pygame.Surface(setting.SIZE,pygame.SRCALPHA)
        for p in self.particle_group: p.blit(player_surface)
        for dp in self.death_particle_group: dp.blit(player_surface)
        if not self.death_tick:
            pygame.draw.circle(player_surface,(*self.color,self.alpha),self.rect.topleft,self.r)

        if Objects.box:
            box=self.rect.copy()
            box.center=box.topleft
            player_surface.blit(self.image,box.topleft)
        background.blit(player_surface,(0,0))

class PlayerParticle(Particle):
    dy=0
    def __init__(self, color, pos=Vector2(0,0),angle=0):
        super().__init__(color,(17,10),pos,angle)
        self.image=pygame.transform.rotozoom(self.image,self.angle,1)
        self.blit_image=self.image.copy()
        self.alpha=128

    @classmethod
    def set_dy(cls,dy):
        cls.dy=dy

        
    def update(self):
        super().update()
        self.rect.y+=PlayerParticle.dy*FRAME_SPEED
        self.size=max(self.size-0.009*FRAME_SPEED,0)
        self.alpha=max(self.alpha-1.9*FRAME_SPEED,0)
        self.blit_image=pygame.transform.rotozoom(self.image,self.angle,self.size)
        self.blit_image.set_alpha(self.alpha)

    def blit(self,background:pygame.Surface):
        blit_pos=Vector2(*self.rect.topleft)-Vector2(*self.blit_image.get_size())//2
        background.blit(self.blit_image,blit_pos)


class DeathParticle(Particle):
    def __init__(self, color,pos=Vector2(0,0)):
        super().__init__(color,(3,3),pos)
        self.dx=(np.random.randint(0,2400)-1200)/1000
        self.dy=-np.random.randint(1500,5000)/1000
        self.pos=Vector2(self.rect.topleft)
        self.alpha=np.random.randint(128,255)
        """
            -500~500 / 1000 = -1.0~1.0 (좀더 많은 경우의 수)
            -50~50 / 100 = -1.5~5.0
        """

    def update(self):
        super().update()
        self.dy+=0.025
        self.alpha=max(self.alpha-0.1,0)
        self.image.set_alpha(self.alpha)
        self.pos+=Vector2(self.dx,self.dy)
        self.rect.topleft=self.pos

    def blit(self,background:pygame.Surface):
        background.blit(self.image,self.rect)


class Obstacle(Objects):
    def __init__(self,*args):
        shape,self.dx,self.dy,self.x,self.y,self.w,self.h,\
            self.angle,self.angle_plus,self.dx_plus,self.dy_plus=args
        image=pygame.Surface((self.w,self.h),pygame.SRCALPHA)
        image.fill(setting.WHITE)
        super().__init__(Vector2(self.x,self.y),image,self.angle)
        self.invincible=False
        self.pos=Vector2(self.rect.center)
        self.backup_image=self.image.copy()
        self.mask=pygame.mask.from_surface(self.image)
        self.extra_image_direction=0

    def reset(self):
        self.backup_image.fill(setting.WHITE)
    
    def pos_reset(self):
        self.rect.topleft=self.x,self.y
        self.rect.size=self.w,self.h
        self.pos=Vector2(self.rect.center)

    def update_invincible(self,flag=None):
        if flag==None:
            self.invincible=not self.invincible
        else:
            self.invincible=flag

    def is_finish(self):
        return self.rect.top>=setting.SIZE[1]

    def update(self,speed=1):
        if self.dx_plus: self.dx+=self.dx_plus*speed*FRAME_SPEED
        if self.dy_plus: self.dy+=self.dy_plus*speed*FRAME_SPEED
        self.pos[0]+=self.dx*speed*FRAME_SPEED
        self.pos[1]+=self.dy*speed*FRAME_SPEED
        self.rect.center=self.pos
        if not self.invincible: # 반대 벽에서 나오는거
            if self.dx>0 and self.rect.right>setting.SIZE[0]:
                self.extra_image_direction=1
                self.pos+=Vector2(-setting.SIZE[0],0)
                self.rect.move_ip(-setting.SIZE[0],0)
            elif self.dx<0 and self.rect.left<0:
                self.extra_image_direction=-1
                self.pos+=Vector2(setting.SIZE[0],0)
                self.rect.move_ip(setting.SIZE[0],0)
            
        if self.angle_plus:
            self.angle+=self.angle_plus*speed*FRAME_SPEED
            self.angle%=360
        if self.angle:
            self.image=pygame.transform.rotozoom(self.backup_image,-self.angle,1)
            self.rect=self.image.get_rect(center=self.pos)
            self.mask=pygame.mask.from_surface(self.image)
        else:
            self.image=self.backup_image

    def collide_check(self,players:list):
        if self.invincible or -400>Vector2(*self.rect.center).distance_to(setting.PLAYER_CENTER["ingame"]) and Vector2(*self.rect.center).distance_to(setting.PLAYER_CENTER["ingame"]) >600:
            re_value=[]
            return re_value
        else:
            re_value=[(pygame.sprite.collide_mask(self,players[i]),i) for i in range(2)]
        for row in re_value:
            if row[0]:
                color="red" if players[row[1]].color==setting.RED else "blue"
                paint=return_image("paint/"+color+"/"+str(np.random.randint(9))+".png")
                paint=pygame.transform.rotozoom(paint,np.random.randint(360),0.07)

                if self.angle%90:
                    if self.angle<0:
                        rotate_pos=(Vector2(row[0])-Vector2((0,self.w*math.sin(math.radians(abs(self.angle)))))).rotate(-self.angle)
                    elif self.angle>90:
                        rotate_pos=(Vector2(row[0])-Vector2(0,(self.h*math.sin(math.radians(self.angle%90))))).rotate(-self.angle%90)
                        self.angle-=180
                    else:
                        rotate_pos=(Vector2(row[0])-Vector2((self.h*math.sin(math.radians(self.angle))),0)).rotate(-self.angle)
                    self.backup_image.blit(paint,rotate_pos-Vector2(paint.get_size())//2)

                    
                    self.image=pygame.transform.rotozoom(self.backup_image,-self.angle,1)
                    
                
                else:
                    self.backup_image.blit(paint,Vector2(*row[0])-Vector2(paint.get_size())//2)
        return re_value
    
    def blit(self,background:pygame.Surface):
        background.blit(self.image,self.rect)
        if self.extra_image_direction: background.blit(self.image,Vector2(self.rect.topleft)+Vector2(self.extra_image_direction*setting.SIZE[0],0))
        if Objects.box:
            pygame.draw.rect(background,(255,0,0),self.rect,1)

class Button(Objects):
    def __init__(self,image=return_image(),pos=Vector2(0,0)):
        self.image=image.convert_alpha()
        self.mask=pygame.mask.from_surface(self.image)
        self.alpha=255
        super().__init__(pos,self.image)

    def mouse_check(self,mouse:Hitbox,click:bool):
        re_value=pygame.sprite.collide_mask(self,mouse),click if self.alpha in (255,170) else None,click
        self.alpha=170 if re_value[0] else 255
        return re_value
    
    def blit(self,background:pygame.Surface):
        self.image.set_alpha(self.alpha)
        background.blit(self.image,self.rect)
        if Objects.box:
            pygame.draw.rect(background,(255,0,0),self.rect,1)

class MenuButton(Button):
    def __init__(self,image:pygame.Surface,pos=Vector2(0,0)):
        super().__init__(image,pos)

    def plus_alpha(self,plus:int):
        self.alpha=max(min(self.alpha+plus,255),0)


class OnOffButton:
    def __init__(self,text="Test",flag=True,pos=Vector2(0,200)):
        self.image=pygame.Surface((setting.SIZE[0]//1.25,setting.SIZE[1]))
        self.image.fill(setting.WHITE)
        self.image.blit(return_text(return_font(),text),(0,0))
        self.buttons=[Button(return_text(return_font(),"켜기",color=setting.BLUE)),
                      Button(return_text(return_font(),"끄기",color=setting.RED))]
        self.pos=pos
        for b in self.buttons: b.rect.topright=(self.image.get_size()[0],self.pos[1])
        self.flag=flag
        self.image.fill(setting.WHITE,self.buttons[int(self.flag)].rect)
        self.buttons[int(self.flag)].blit(self.image)

    def mouse_check(self,mouse,click):
        if any([all(b.mouse_check(mouse,click)) for b in self.buttons]):
            self.flag=not self.flag
            self.image.fill(setting.WHITE,self.buttons[int(self.flag)].rect)
            self.buttons[int(self.flag)].blit(self.image)
    
    def blit(self,background:pygame.Surface):
        background.blit(self.image,self.pos)



class LevelText(Objects):
    def __init__(self,text):
        self.text=text
        self.alpha=255
        self.pos=Vector2(setting.CENTER)
        super().__init__(self.pos,return_text(return_font(),self.text))
        self.rect.center=self.pos

    def update(self):
        self.alpha=max(self.alpha-3,0)
        self.image.set_alpha(self.alpha)
        self.pos[1]=max(setting.CENTER[1]-60,self.pos[1]-0.6)
        self.rect.center=self.pos

    def is_alive(self): return bool(self.alpha)
        

class Intro(Screen):
    def __init__(self):
        super().__init__()
        self.is_screen=True
        self.alpha=30
        self.skip=False
        self.r=setting.SIZE[1]+200
        self.texts=[(return_text(return_font(30,self.kor_font),"제작",color=setting.BLACK),[setting.CENTER[0],setting.CENTER[1]-50]),
                    (return_text(return_font(30,self.eng_font,isfile=True),"Yoon Ho Yeop",color=setting.BLACK),list(setting.CENTER)),
                    (return_text(return_font(30,self.kor_font),"음악",color=setting.BLACK),[setting.CENTER[0],setting.CENTER[1]+50]),
                    (return_text(return_font(30,self.eng_font,isfile=True),"Tim Shiel",color=setting.BLACK),[setting.CENTER[0],setting.CENTER[1]+100])]
                
        for text in self.texts: text[1][0]-=text[0].get_size()[0]//2

    def is_intro_done(self):
        if self.is_screen and self.r==100:
            return True
        return False
    
    def update(self):
        if self.is_screen:
            self.r=max(self.r-3,100)
            if self.r>setting.SIZE[1]-100: self.alpha+=5
            else:
                self.alpha=max(self.alpha-4,0)
                for i in range(0,len(self.texts),2): self.texts[i][0].set_alpha(self.alpha)
            for i in range(0,len(self.texts),2): self.texts[i+1][0].set_alpha(self.alpha)
            if self.skip: self.r=100

    def blit(self,background:pygame.Surface):
        if self.is_screen:
            self.surface.fill(setting.BLACK)
            pygame.draw.circle(self.surface,setting.WHITE,setting.PLAYER_CENTER["menu"],self.r)
            for text in self.texts: self.surface.blit(*text)
            background.blit(self.surface,(0,0))
    

class Menu(Screen):
    def __init__(self, size=Vector2(*setting.SIZE)+Vector2(2*setting.SIZE[0]//1.25,0)):
        super().__init__(size)
        self.screens=[SettingMenu(),MainMenu(),PlayMenu()]
        self.pos=Vector2(-setting.SIZE[0]//1.25,0)
        self.now=setting.SCREEN.MAIN
        self.target=setting.SCREEN.MAIN
        self.direction=0
        
    def set_direction(self,direction:int):
        if self.screens[setting.SCREEN.MAIN].is_intro_finished():
            if -self.direction==direction:
                self.now-=self.direction
            if self.direction==direction:
                self.now=setting.SCREEN.MAIN
            self.direction=direction

    def button_check(self,mouse,click):
        re_value=[]
        if self.pos[0]==-setting.SIZE[0]//1.25:
            re_value.append(self.screens[setting.SCREEN.MAIN].button_check(mouse,click))
        else:
            re_value.append(None)

        if self.pos[0]==-setting.SIZE[0]//1.25*2:
            re_value.append(self.screens[setting.SCREEN.PLAY].button_check(mouse,click))
        else:
            re_value.append(None)

        if self.pos[0]==0:
            re_value.append(self.screens[setting.SCREEN.SETTING].button_check(mouse,click))
        else:
            re_value.append(None)
        return re_value


    def update(self):
        # print(f"self.target: {self.target}, self.now: {self.now}, self.direction: {self.direction}")
        self.pos[0]=min(max(self.pos[0]+13*self.direction,-setting.SIZE[0]//1.25*2),0)
        if self.pos[0]==0:
            self.now=setting.SCREEN.SETTING
            self.direction=0
        elif self.pos[0]==-setting.SIZE[0]//1.25*2:
            self.now=setting.SCREEN.PLAY
            self.direction=0
        if self.now!=setting.SCREEN.MAIN:
            if self.now==setting.SCREEN.PLAY:
                self.pos[0]=min(self.pos[0],-setting.SIZE[0]//1.25)
            if self.now==setting.SCREEN.SETTING:
                self.pos[0]=max(self.pos[0],-setting.SIZE[0]//1.25)

            if self.pos[0]==-setting.SIZE[0]//1.25:
                self.now=setting.SCREEN.MAIN
                self.direction=0

        if self.pos[0]!=-setting.SIZE[0]//1.25:
            for b in self.screens[setting.SCREEN.MAIN].buttons:
                b.plus_alpha(-6)
        else:
            for b in self.screens[setting.SCREEN.MAIN].buttons:
                b.plus_alpha(6)


        for s in self.screens:
            s.is_screen=self.is_screen
            s.update()

    def blit(self,background:pygame.Surface):
        if self.is_screen:
            self.surface.fill(setting.BLACK)
            for s in self.screens: s.blit(self.surface)
            background.blit(self.surface,self.pos)

class MainMenu(Screen):
    def __init__(self):
        super().__init__()
        self.start=False
        self.text=[return_text(return_font(120,self.eng_font,isfile=True),"DUET"),Vector2(setting.CENTER[0],0)]
        self.text[1]-=Vector2(*self.text[0].get_size())//2
        self.text[1][1]-=self.text[0].get_size()[1]//2
        self.button_size=60
        self.buttons=[MenuButton(return_image("setting.png",(self.button_size,self.button_size)),(20,setting.SIZE[1])),
                      MenuButton(return_image("play.png",(self.button_size,self.button_size)),(setting.SIZE[0]-20-self.button_size,setting.SIZE[1]))]
        
    def is_intro_finished(self):
        return all([button.rect.y==setting.SIZE[1]-self.button_size-20 for button in self.buttons])

    def update(self):
        if self.start and self.is_screen:
            if self.text[1][1]!=25: self.text[1][1]=min(self.text[1][1]+11*FRAME_SPEED,25)
            for button in self.buttons:
                if button.rect.y!=setting.SIZE[1]-self.button_size-20:
                    button.rect.y=max(button.rect.y-5,setting.SIZE[1]-self.button_size-20)
        elif self.start and not self.is_screen:
            for button in self.buttons: button.rect.y=setting.SIZE[1]
            self.start=False
        elif not self.start and self.is_screen:
            self.start=True


    def fill(self):
        self.surface.fill(setting.BLACK)

    def button_check(self,mouse,click):
        for button in self.buttons:
            if button==self.buttons[0] and all(button.mouse_check(mouse,click)): print("설정 메뉴(마우스)")
            elif button==self.buttons[1] and all(button.mouse_check(mouse,click)): print("플레이 메뉴(마우스)")
        return [button.mouse_check(mouse,click) for button in self.buttons]
        
    def blit(self,background:pygame.Surface):
        if self.is_screen:
            self.surface.blit(*self.text)
            for b in self.buttons: b.blit(self.surface)
            background.blit(self.surface,(setting.SIZE[0]//1.25,0))

class PlayMenu(Screen):
    def __init__(self):
        super().__init__((setting.SIZE[0]//1.25,setting.SIZE[1]))
        self.buttons=[Button(return_image("test_level.png",(60,60)),(Vector2(*self.surface.get_size())//2)-Vector2(60,0)),
                      Button(return_image(size=(60,60)),(Vector2(*self.surface.get_size())//2)+Vector2(30,0))
                      ]
        
        self.texts=[
            (return_text(return_font(25,self.kor_font),"플레이",color=setting.WHITE),Vector2(self.surface.get_size()[0]//2,10))
                    ]
        for text in self.texts: text[1][0]-=text[0].get_size()[0]//2

    def button_check(self,mouse,click):
        for b in self.buttons: b.rect.move_ip(setting.SIZE[0]-setting.SIZE[0]//1.25,0)
        re_value=[b.mouse_check(mouse,click) for b in self.buttons]
        for b in self.buttons: b.rect.move_ip(-(setting.SIZE[0]-setting.SIZE[0]//1.25),0)
        
        return re_value
    

    def blit(self,background:pygame.Surface):
        if self.is_screen:
            self.surface.fill(setting.BLACK)
            for i in range(45,90):
                blit_surface=pygame.Surface((1,setting.SIZE[1]),pygame.SRCALPHA)
                blit_surface.fill(setting.WHITE)
                blit_surface.set_alpha(int(255*(math.cos(math.radians(i)))))
                self.surface.blit(blit_surface,(i-45,0))
            for b in self.buttons: b.blit(self.surface)
            if Objects.box: pygame.draw.rect(self.surface,setting.RED,(0,0,*self.surface.get_size()),1)
            for text in self.texts: self.surface.blit(*text)
            background.blit(self.surface,(setting.SIZE[0]//1.25+setting.SIZE[0],0))

class SettingMenu(Screen):
    def __init__(self):
        super().__init__((setting.SIZE[0]//1.25,setting.SIZE[1]))
        self.texts=[
            (return_text(return_font(30,self.kor_font),"설정",color=setting.BLACK),Vector2(self.surface.get_size()[0]//2,10))
                    ]
        for text in self.texts: text[1][0]-=text[0].get_size()[0]//2
        self.buttons=[OnOffButton()]

    def button_check(self,mouse,click):
        for b in self.buttons: b.mouse_check(mouse,click)
    

    def blit(self,background:pygame.Surface):
        if self.is_screen:
            self.surface.fill(setting.WHITE)
            for text in self.texts: self.surface.blit(*text)
            for b in self.buttons: b.blit(self.surface)
            background.blit(self.surface,(0,0))

class InGame(Screen):
    def __init__(self):
        super().__init__()
        self.level=Level("tutorial")
        # self.level_texts=self.level.texts

    def set_level(self,name):
        self.level=Level(name)
        # self.level_texts=self.level.texts

    def update(self):
        if self.is_screen:
            self.level.update()

    
    def collide_check(self,players):
        return self.level.collide_check(players) if self.is_screen else False

    def fill(self):
        self.surface.fill(setting.BLACK)

    def blit(self,background:pygame.Surface):
        if self.is_screen:
            self.level.blit(self.surface)
            background.blit(self.surface,(0,0))

class PauseScreen(Screen):
    def __init__(self):
        super().__init__()
        self.button_size=60
        self.buttons=[Button(return_image("play.png",(self.button_size,self.button_size)),Vector2(20-100,setting.SIZE[1]-80)),
                      Button(return_image("exit.png",(self.button_size,self.button_size)),Vector2(setting.SIZE[0]-20-self.button_size-100,setting.SIZE[1]-80))]
        self.move=False
        self.is_screen=True

    def screen_onoff(self,flag=None):
        if flag==None:
            self.move=not self.move
        else:
            self.move=flag

    def button_check(self,mouse,click):
        return [button.mouse_check(mouse,click) for button in self.buttons]

    def update(self):
        if self.move:
            self.buttons[0].rect.x=max(Vector2(self.buttons[0].rect.x-5,setting.SIZE[0]-20-self.button_size))
            self.buttons[1].rect.x=min(Vector2(self.buttons[0].rect.x+5,20))
        else:
            self.buttons[0].rect.x=min(Vector2(self.buttons[0].rect.x+5,20-100))
            self.buttons[1].rect.x=max(Vector2(self.buttons[0].rect.x-5,setting.SIZE[0]-20-self.button_size-100))

    def blit(self,background:pygame.Surface):
        if self.is_screen:
            self.surface.fill((0,0,0,0))
            for b in self.buttons: self.surface.blit(b.image,b.rect)

            background.blit(self.surface,(0,0))

class Level:
    def __init__(self,name):
        self.name=name
        path="assets/level/"+name+".json"
        try:
            with open(path, encoding="utf-8") as json_file:data=json.load(json_file)
        except FileNotFoundError:
            try:
                with open("Duet/"+path,encoding="utf-8") as json_file:data=json.load(json_file)
            except FileNotFoundError:
                with open("./../Duet/"+path,encoding="utf-8") as json_file:data=json.load(json_file)
                 
        data_list=[[0 if v==None else v for v in obs.values()] for obs in data["obstacles"]]
        self.obs_group=pygame.sprite.Group(*[Obstacle(*i) for i in data_list])
        self.rewind=False
        self.progress=0
        self.pause_tick=0
        self.text=LevelText(data["description"])
        self.next_level=data["next"]
 
    def is_level_finished(self):
        return all([o.is_finish() for o in self.obs_group])

    def reset(self):
        for o in self.obs_group:
            o.pos_reset()
            o.reset()

    def update(self):
        if self.text.is_alive():
            if not self.pause_tick:
                if self.rewind:
                    for o in self.obs_group: o.update(-self.progress/(setting.FRAME*0.8))
                    if all(o.rect.y<=o.y for o in self.obs_group):
                        for o in self.obs_group:
                            o.pos_reset()
                            o.rect.topleft=o.x,o.y
                            o.rect.size=o.w,o.h
                        self.rewind_change(False)
                        self.progress=0
                else:
                    for o in self.obs_group: o.update()
                    self.progress+=1
                    if self.is_level_finished() and self.next_level: self.__init__(self.next_level)
            else:
                self.pause_tick-=1
        else:
            self.text.update()


    def rewind_change(self,flag=True):
        self.rewind=flag
        for o in self.obs_group: o.update_invincible(flag)
        if not flag:
            self.pause_tick=setting.FRAME*0.2
            PlayerParticle.set_dy(0.9)
        else:
            PlayerParticle.set_dy(-0.9*self.progress/(setting.FRAME*0.8))
            

    def collide_check(self,players=list):
        re_value=[]
        for o in self.obs_group:
            check=o.collide_check(players)
            for i in check:
                if i[0] and (re_value==[] or i[1]!=re_value[0][1]):
                    re_value.append(i)
        return re_value if len(re_value)!=1 else re_value[0]

    def blit(self,background:pygame.Surface):
        if self.text.is_alive():
            background.blit(self.text.image,self.text.rect)
        for obs in self.obs_group:
            obs.blit(background)


    def __str__(self):
        return self.name