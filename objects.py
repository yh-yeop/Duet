import pygame
from setting import Setting
from pygame.math import Vector2
from util import *
import pandas as pd
import numpy as np
import math
setting=Setting()
FRAME_SPEED=(1000//setting.FRAME)/(1000//120)
def set_speed(dt):
    global FRAME_SPEED
    FRAME_SPEED=dt/(1000//120)

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
    distance=setting.CENTER[0]//5*2
    def __init__(self,color,center,direction):
        self.center=Vector2(center)
        self.angle=180 if direction=="left" else 0
        pos=self.center+Vector2(self.distance,0).rotate(self.angle)
        self.image=pygame.Surface((5,5),pygame.SRCALPHA)
        pygame.draw.rect(self.image,setting.WHITE,(0,0,*self.image.get_size()),1)
        super().__init__(pos,self.image,self.angle)
        
        self.alpha=180
        self.color=color
        self.particle_group=pygame.sprite.Group()
        self.rewind=[None,0]

    def set_rewind_speed(self,angle):
        self.rewind[1]=setting.FRAME*0.8
        self.rewind[0]=(540-angle)/self.rewind[1]

    
    def update(self,angle_plus):
        if not self.rewind[1]:
            self.angle=(self.angle+angle_plus*self.speed*FRAME_SPEED)%360
        else:
            self.angle=(self.angle+self.rewind[0])%360
            self.rewind[1]-=1
            if not self.rewind[1]:
                self.angle=round(self.angle)%360
                print(f"color: {" red" if self.color==setting.RED else "blue"} angle: {self.angle}")
        self.rect.center=self.center+Vector2(self.distance,0).rotate(self.angle)
        self.particle_group.add(PlayerParticle(self.color,self.rect.topleft,self.angle))
        self.particle_group.update()
        for p in self.particle_group:
            if (not p.image.get_alpha()) or (not p.size):
                self.particle_group.remove(p)



    def blit(self,background):
        player_surface=pygame.Surface(setting.SIZE,pygame.SRCALPHA)
        for p in self.particle_group: p.blit(player_surface)
        pygame.draw.circle(player_surface,(*self.color,self.alpha),self.rect.topleft,self.r)
        if self.box:
            a=self.rect.copy()
            a.center=a.topleft
            player_surface.blit(self.image,a.topleft)
        background.blit(player_surface,(0,0))

class Particle(Objects):
    def __init__(self,color,size,pos=Vector2(0,0),angle=0):
        self.image=pygame.Surface(size,pygame.SRCALPHA)
        self.color=color
        self.image.fill(self.color)
        self.alpha=128
        self.size=1
        super().__init__(pos,self.image,angle)
        self.blit_image=self.image.copy()

    def update(self):
        self.size=max(self.size-0.01*FRAME_SPEED,0)
        self.alpha=max(self.alpha-2.5*FRAME_SPEED,0)
        self.blit_image=pygame.transform.rotozoom(self.image,self.angle,self.size)

    def blit(self,background):
        blit_pos=Vector2(*self.rect.topleft)-Vector2(*self.blit_image.get_size())//2
        background.blit(self.blit_image,blit_pos)

class PlayerParticle(Particle):
    dy=0
    def __init__(self, color, pos=Vector2(0,0),angle=0):
        super().__init__(color,(17,10),pos,angle)
        self.image=pygame.transform.rotozoom(self.image,self.angle,1)

    @classmethod
    def set_dy(cls,dy):
        cls.dy=dy

        
    def update(self):
        super().update()
        self.blit_image.set_alpha(self.alpha)
        self.rect.y+=PlayerParticle.dy*FRAME_SPEED


class DeathParticle(Particle):
    def __init__(self, color,pos=Vector2(0, 0)):
        super().__init__(color,(10,10),pos)
        self.dx=(np.random.randint(0,1000)-500)/1000
        """
            -500~500 / 1000 = -0.5~0.5 (좀더 많은 갯수)
            -50~50 / 100 = -0.5~0.5
        """

    def update(self):
        super().update()


class Obstacle(Objects):
    def __init__(self,*args):
        """shape: [rect,special]
            special: [1,2]"""
            # args[i]=string_to_int(args[i])
        self.shape,self.dx,self.dy,self.x,self.y,self.w,self.h,\
            self.angle,self.angle_plus,self.dx_plus,self.dy_plus=args
        if self.shape=="rect": image=pygame.Surface((self.w,self.h),pygame.SRCALPHA)
        else: raise SyntaxError
        image.fill(setting.WHITE)
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
        if self.rect.y>=setting.CENTER[1]:
            if self.dx_plus: self.dx+=self.dx_plus*speed*FRAME_SPEED
            if self.dy_plus: self.dy+=self.dy_plus*speed*FRAME_SPEED

    def collide_check(self,players):
        re_value=[(pygame.sprite.collide_mask(self,players[i]),i) for i in range(2)]
        if self.invincible:
            re_value=[]
            return re_value
        for row in re_value:
            if row[0]:
                print("충돌함")
                if self.angle:
                    pygame.draw.rect(self.image,players[row[1]].color,(*row[0],5,5))

                    angle_rad=math.radians(self.angle)
                    original_x = row[0][0]*math.cos(-angle_rad) - row[0][1]*math.sin(-angle_rad)
                    original_y = row[0][0]*math.sin(-angle_rad) + row[0][1]*math.cos(-angle_rad)
                    blit_pos=Vector2(original_x,original_y)-Vector2(2.5,2.5)
                    pygame.draw.rect(self.backup_image,players[row[1]].color,(*blit_pos,5,5))
                else:
                    pygame.draw.rect(self.backup_image,players[row[1]].color,(*(Vector2(row[0])-Vector2(2.5,2.5)),5,5))
        return re_value
    
    def blit(self,background):
        background.blit(self.image,self.rect)
        if self.box:
            pygame.draw.rect(background,(255,0,0),self.rect,1)

class Button(Objects):
    def __init__(self,image,pos=Vector2(0,0)):
        self.image=image.convert_alpha()
        self.alpha=255
        super().__init__(pos,self.image)

    def mouse_check(self,mouse,click):
        return pygame.sprite.collide_mask(mouse,self),click if self.alpha==255 else None,click
    
    def blit(self,background):
        background.blit(self.image,self.rect.topleft)
        if self.box:
            pygame.draw.rect(background,(255,0,0),self.rect,1)



class Screen:
    def __init__(self,size=setting.SIZE):
        self.surface=pygame.Surface(size,pygame.SRCALPHA)
        self.eng_font="Montserrat/static/Montserrat-Thin.ttf"
        self.kor_font="malgungothic"
        self.pos=(0,0)
        self.is_screen=False

    def update(self,*args):
        pass

    def blit(self,background):
        background.blit(self.surface,self.pos)


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

    def blit(self,background):
        if self.is_screen:
            self.surface.fill(setting.BLACK)
            pygame.draw.circle(self.surface,setting.WHITE,setting.PLAYER_CENTER["menu"],self.r)
            for text in self.texts: self.surface.blit(*text)
            background.blit(self.surface,(0,0))
    

class Menu(Screen):
    def __init__(self, size=Vector2(*setting.SIZE)+Vector2(2*setting.SIZE[0]//1.25,0)):
        super().__init__(size)
        self.screens=[SettingMenu(),MainMenu(),PlayMenu()]
        for s in self.screens: s.is_screen=True
        self.pos=[-setting.SIZE[0]//1.25,0]
        self.now=setting.SCREEN.MAIN
        self.target=setting.SCREEN.MAIN
        self.direction=0
        
    def set_direction(self,direction):
        if -self.direction==direction:
            self.now-=self.direction
        if self.direction==direction:
            self.now=setting.SCREEN.MAIN
        self.direction=direction


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
        for s in self.screens: s.update()

    def blit(self,background):
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
        self.buttons=[Button(return_image("setting.png",(self.button_size,self.button_size)),[20,setting.SIZE[1]]),
                      Button(return_image("play.png",(self.button_size,self.button_size)),[setting.SIZE[0]-20-self.button_size,setting.SIZE[1]])]
        
    
    def update(self):
        if self.start and self.is_screen:
            if self.text[1][1]!=25: self.text[1][1]=min(self.text[1][1]+11*FRAME_SPEED,25)
            for button in self.buttons:
                if button.rect.y!=setting.SIZE[1]-self.button_size-20:
                    button.rect.y=max(button.rect.y-5,setting.SIZE[1]-self.button_size-20)

    def fill(self):
        self.surface.fill(setting.BLACK)

    def button_check(self,mouse,click):
        for button in self.buttons:
            if button==self.buttons[0] and all(button.mouse_check(mouse,click)): print("설정 메뉴(마우스)")
            elif button==self.buttons[1] and all(button.mouse_check(mouse,click)): print("플레이 메뉴(마우스)")
        return [button.mouse_check(mouse,click) for button in self.buttons]
        
    def blit(self,background):
        if self.is_screen:
            self.surface.blit(*self.text)
            for b in self.buttons: b.blit(self.surface)
            background.blit(self.surface,(setting.SIZE[0]//1.25,0))

class PlayMenu(Screen):
    def __init__(self):
        super().__init__((setting.SIZE[0]//1.25,setting.SIZE[1]))
        self.buttons=[Button(return_image("test_level.png",(60,60)),(Vector2(*self.surface.get_size())//2)-Vector2(30,0)),
                      Button(return_image("lv.png",(60,60)),(Vector2(*self.surface.get_size())//2)+Vector2(-30,80)),
                      Button(return_text(return_font(50,self.eng_font,isfile=True),"IV"),(Vector2(*self.surface.get_size())//2)+Vector2(-17,80))
                      ]

    def button_check(self,mouse,click):
        for button in self.buttons:
            button.rect.move_ip(setting.SIZE[0]-setting.SIZE[0]//1.25,0)
            if button==self.buttons[0] and all(button.mouse_check(mouse,click)): print("테스트 레벨 누름")
        
        re_value=[button.mouse_check(mouse,click) for button in self.buttons]
        
        for button in self.buttons: button.rect.move_ip(-(setting.SIZE[0]-setting.SIZE[0]//1.25),0)
        
        return re_value
    

    def blit(self,background):
        if self.is_screen:
            self.surface.fill(setting.BLACK)
            for i in range(45,90):
                blit_surface=pygame.Surface((1,setting.SIZE[1]),pygame.SRCALPHA)
                blit_surface.fill(setting.WHITE)
                blit_surface.set_alpha(int(255*(math.cos(math.radians(i)))))
                self.surface.blit(blit_surface,(i-45,0))
            for b in self.buttons: b.blit(self.surface)
            if Objects.box: pygame.draw.rect(self.surface,setting.RED,(0,0,*self.surface.get_size()),1)
            background.blit(self.surface,(setting.SIZE[0]//1.25+setting.SIZE[0],0))

class SettingMenu(Screen):
    def __init__(self):
        super().__init__((setting.SIZE[0]//1.25,setting.SIZE[1]))
        self.texts=[(return_text(return_font(50,self.eng_font,isfile=True),"ABCDEFGHI",color=setting.BLACK),(20,0)),
                    (return_text(return_font(50,self.eng_font,isfile=True),"JKLMNOPQR",color=setting.BLACK),(20,50)),
                    (return_text(return_font(50,self.eng_font,isfile=True),"STUVWXYZ",color=setting.BLACK),(20,100))
                    ]
    def blit(self,background):
        if self.is_screen:
            self.surface.fill(setting.WHITE)
            for text in self.texts: self.surface.blit(*text)
            background.blit(self.surface,(0,0))

class InGame(Screen):
    def __init__(self):
        super().__init__()
        self.level=Level("test_level")

    def update(self):
        if self.is_screen:
            self.level.update()

    
    def collide_check(self,players):
        return self.level.collide_check(players) if self.is_screen else False

    def fill(self):
            self.surface.fill(setting.BLACK)

    def blit(self,background):
        if self.is_screen:
            self.level.blit(self.surface)
            background.blit(self.surface,(0,0))

class PauseScreen(Screen):
    def __init__(self):
        super().__init__()

class Level:
    def __init__(self,name):
        path="assets/level/"+name+".csv"
        try:
            self.df=pd.read_csv(path,encoding="cp949")
        except FileNotFoundError:
            try: self.df=pd.read_csv("Duet/"+path,encoding="cp949")
            except FileNotFoundError: self.df=pd.read_csv("Duet-main/"+path,encoding="cp949")
        self.max_obs=len(self.df)
        df_list=[list(self.df.loc[i].to_dict().values()) for i in range(self.max_obs)]
        for i in range(len(df_list)):
            for j in range(len(df_list[i])):
                if str(df_list[i][j])=="nan":
                    df_list[i][j]=0
        # self.obs_group=pygame.sprite.Group(*[Obstacle(*self.df.loc[i].to_dict().values()) for i in range(self.max_obs)])
        self.obs_group=pygame.sprite.Group(*[Obstacle(*i) for i in df_list])
        self.rewind=False
        self.progress=0
        self.player_angle=0
        self.rewind_speed=5

    def update(self):
        if self.rewind:
            for o in self.obs_group: o.update(-self.rewind_speed)
            if self.obs_group.sprites()[0].rect.y<=self.df.loc[0].to_dict()["y"]:
                for o in self.obs_group:
                    o.rect.topleft=o.x,o.y
                    o.rect.size=o.w,o.h
                self.rewind_change(False)
                self.progress=0
        else:
            for o in self.obs_group: o.update()
            self.progress+=1

        if self.obs_group.sprites()[-1].rect.top>setting.SIZE[1]:
            self.rewind_change()


    def rewind_change(self,flag=True):
        self.rewind=flag
        for o in self.obs_group: o.invincible=flag
            

    def collide_check(self,players):
        re_value=[]
        for o in self.obs_group:
            check=o.collide_check(players)
            for i in check:
                if i[0] and (re_value==[] or i[1]!=re_value[0][1]):
                    re_value.append(i)
        return re_value if len(re_value)!=1 else re_value[0]

    def blit(self,background):
        for obs in self.obs_group:
            obs.blit(background)



if __name__=="__main__":
    lv=Level("test_level")
    for obs in lv.obs_group:
        print(obs.rect.y)