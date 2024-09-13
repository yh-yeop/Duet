import pygame
from setting import Setting
from objects import *
from util import *


class Duet(Setting):
    def __init__(self):
        super().__init__()
        self.background=pygame.display.set_mode(self.size)
        self.icon=return_image("icon.jpg")
        pygame.display.set_icon(self.icon)
        self.init_pygame()
        self.player=pygame.sprite.Group(Player(self.red,self.player_center["menu"],"left"),
                                        Player(self.blue,self.player_center["menu"],"right"))
        self.clock=pygame.time.Clock()
        self.direction=1
        self.now=pygame.time.get_ticks()
        self.time_count={"menu_after_intro":0,
                         "rewind":0}
        self.pause=False
        self.rewind_pause=False
        
        self.intro=Intro()
        self.menu=Menu()
        self.in_game=InGame()
        self.screens=[self.intro,self.menu,self.in_game]

        self.mouse_hitbox=Objects(pygame.mouse.get_pos(),pygame.Surface((1,1)))

        self.check={"main_menu":None,
                    "play_menu":None}
        
        self.play=True

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Duet")

    def mainloop(self):
        while True:
            self.setting()
            self.inputs()
            if not self.play:
                return
            self.move()
            self.collide_check()
            self.draw()
    
    def setting(self):
        if not self.pause:
            if self.time_count["menu_after_intro"]:
                self.time_count["menu_after_intro"]-=1
                if self.time_count["menu_after_intro"]<=0:
                    self.menu.screens[1].start=True
                elif self.time_count["menu_after_intro"]<=60:
                    for p in self.player: p.speed=1.7
            if self.time_count["rewind"]:
                self.time_count["rewind"]-=1
                if self.time_count["rewind"]<=0:
                    self.rewind_pause=False
                    self.in_game.level.rewind_change()
        else:
            print("일시정지")
        if not self.intro.is_screen:
            self.mouse_hitbox.rect.center=pygame.mouse.get_pos()
        dt=self.clock.tick(self.frame)
        set_speed(dt)
        # fps=1000/dt
        # print(f"FPS: 정상({fps:.2f})" if fps>90 else f"FPS: 비정상({fps:.2f})")
        

    def inputs(self):
        keys=pygame.key.get_pressed()
        events=pygame.event.get()
        if not events:
            self.check["main_menu"]=self.menu.screens[self.SCREEN.MAIN].button_check(self.mouse_hitbox,False)
            self.check["play_menu"]=self.menu.screens[self.SCREEN.PLAY].button_check(self.mouse_hitbox,False)
        for event in events:
            if event.type==pygame.QUIT or \
            (not self.in_game.is_screen and not self.intro.is_screen and event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                self.play=False
                return
            if event.type==pygame.KEYDOWN:
                if self.in_game.is_screen and (not self.pause and not self.rewind_pause):
                    if event.key==pygame.K_LEFT:
                        self.direction=-1
                    if event.key==pygame.K_RIGHT:
                        self.direction=1
                    if event.key==pygame.K_ESCAPE:
                        screen_change(self.screens,self.menu)
                if self.intro.is_screen:
                    if event.key==pygame.K_ESCAPE:
                        self.intro.skip=True
                
                if self.menu.is_screen:
                    if event.key==pygame.K_LEFT:
                        self.menu.set_direction(1)
                    if event.key==pygame.K_RIGHT:
                        self.menu.set_direction(-1)

                if event.key==pygame.K_0:
                    self.player.sprites()[0].angle=180
                    self.player.sprites()[1].angle=0
                if event.key==pygame.K_1:
                    Objects.box=not Objects.box
                if event.key==pygame.K_2:
                    for o in self.in_game.level.obs_group:
                        o.invincible=not o.invincible
                if event.key==pygame.K_3:
                    self.direction=0
                    self.pause=not self.pause


            if event.type==pygame.KEYUP:
                if event.key==pygame.K_LEFT and self.direction==-1:
                    self.direction=int(keys[pygame.K_RIGHT])
                if event.key==pygame.K_RIGHT and self.direction==1:
                    self.direction=-int(keys[pygame.K_LEFT])


            if not self.intro.is_screen:
                if self.menu.is_screen:
                    self.check["main_menu"]=self.menu.screens[self.SCREEN.MAIN].button_check(self.mouse_hitbox,event.type==pygame.MOUSEBUTTONDOWN)
                    self.check["play_menu"]=self.menu.screens[self.SCREEN.PLAY].button_check(self.mouse_hitbox,event.type==pygame.MOUSEBUTTONDOWN)

    def move(self):
        if (not self.pause and not self.rewind_pause):
            for screen in self.screens: screen.update()

            if self.check["main_menu"]:
                if all(self.check["main_menu"][self.BUTTON.PLAY]):
                    self.menu.set_direction(-1)
                elif all(self.check["main_menu"][self.BUTTON.SETTING]):
                    self.menu.set_direction(1)

            if self.check["play_menu"]:
                if all(self.check["play_menu"][0]):
                    self.check["play_menu"]=False
                    self.direction=0
                    self.player.sprites()[0].angle=180
                    self.player.sprites()[1].angle=0
                    for p in self.player: p.speed=2.4 # 2.4
                    Particle.speed=0.7
                    self.in_game.level=Level("test_level")
                    screen_change(self.screens,self.in_game)
                    self.menu.direction=0
                    self.menu.pos=[-setting.size[0]//1.25,0]

            if self.intro.is_intro_done():
                for p in self.player:
                    p.r=100
                    p.distance=0
                self.time_count["menu_after_intro"]=180 if not self.intro.skip else 1
                self.screens=screen_change(self.screens,self.menu)

            if self.player.sprites()[0].r!=Player.r:
                for p in self.player:
                    p.r-=(100-Player.r)/50
                    p.distance+=Player.distance/50
                    p.speed+=(2-1.5)/25
                    if p.r<=Player.r:
                        p.r=Player.r
                        p.distance=Player.distance
                        p.speed=2
            if self.in_game.level.rewind:
                self.direction=0
            elif self.menu.is_screen:
                self.direction=1
            self.player.update(self.direction)
        else:
            pass


    def collide_check(self):
        if (not self.pause and not self.rewind_pause) and self.in_game.is_screen:
            check=self.in_game.collide_check(self.player.sprites())
            if check:
                self.time_count["rewind"]=84
                self.rewind_pause=True


        

    def draw(self):
        self.background.fill(self.black)

        if self.in_game.is_screen:
            self.in_game.fill()
            draw_player(self.player,self.in_game.surface,"ingame")

        else:
            self.menu.screens[self.SCREEN.MAIN].fill()
            draw_player(self.player,self.menu.screens[1].surface,"menu")


        for screen in self.screens:
            screen.blit(self.background)
        
        pygame.display.flip()   

if __name__=="__main__":
    duet=Duet()
    duet.mainloop()
    pygame.quit()