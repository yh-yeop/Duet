import pygame
from setting import *
from objects import *
from util import *

class Duet(Setting):
    def __init__(self):
        super().__init__()
        self.background=pygame.display.set_mode(self.size)
        self.icon=return_image("icon.jpg")
        pygame.display.set_icon(self.icon)
        self.player=pygame.sprite.Group(Player(self.red,self.player_center["menu"],"left"),
                                        Player(self.blue,self.player_center["menu"],"right"))
        self.init_pygame()
        self.clock=pygame.time.Clock()
        self.direction=1
        self.now=pygame.time.get_ticks()
        self.time_count={"menu_after_intro":0}
        
        self.intro=Intro()
        self.menu=Menu()
        self.in_game=InGame()
        # self.in_game.level=Level("test_level_2")
        self.screens=[self.intro,self.menu,self.in_game]

        self.mouse_hitbox=Objects(pygame.mouse.get_pos(),pygame.Surface((1,1)))

        # self.menu.log_print=True
        self.check={"menu":None}
        

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Duet")

    def mainloop(self):
        while True:
            self.inputs()
            self.move()
            self.draw()
    
    def inputs(self):        
        self.now=pygame.time.get_ticks()
        if self.time_count["menu_after_intro"]:
            if self.now-self.time_count["menu_after_intro"]>=1500:
                self.menu.start=True
            elif self.now-self.time_count["menu_after_intro"]>=1000:
                for p in self.player: p.speed=1.7

        if not self.intro.is_screen:
            m_pos=pygame.mouse.get_pos()
            self.mouse_hitbox.rect.center=m_pos

        keys=pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type==pygame.QUIT or \
            (not self.in_game.is_screen and event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                pygame.quit()
                quit()
            if self.in_game.is_screen or True:
                if event.type==pygame.KEYDOWN:
                    if any(map(lambda s: s.is_screen,self.screens)):
                        if event.key==pygame.K_LEFT:
                            self.direction=-1
                        if event.key==pygame.K_RIGHT:
                            self.direction=1
                        if self.in_game.is_screen and event.key==pygame.K_ESCAPE:
                            screen_change(self.screens,self.menu)

                        if event.key==pygame.K_0:
                            self.player.sprites()[0].angle=180
                            self.player.sprites()[1].angle=0
                        if event.key==pygame.K_1:
                            Objects.box=not Objects.box
                    if event.key==pygame.K_3:
                        self.direction=0
                        self.in_game.is_screen=not self.in_game.is_screen
                        Player.pause=not Player.pause


                if event.type==pygame.KEYUP:
                    if event.key==pygame.K_LEFT and self.direction==-1:
                        self.direction=int(keys[pygame.K_RIGHT])
                    if event.key==pygame.K_RIGHT and self.direction==1:
                        self.direction=-int(keys[pygame.K_LEFT])


            if not self.intro.is_screen:
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if self.menu.is_screen:
                        self.check["menu"]=self.menu.button_check(self.mouse_hitbox,True)



    def move(self):
        self.intro.update(self.now)
        for screen in self.screens[1:]: screen.update()
        if self.in_game.is_screen:
            print(self.in_game.collide_check(self.player.sprites()))


        if not self.check["menu"]: self.check["menu"]=self.menu.button_check(self.mouse_hitbox,False)

        if all(self.check["menu"][1]):
            self.check["menu"]=False
            self.direction=0
            self.player.sprites()[0].angle=180
            self.player.sprites()[1].angle=0
            for p in self.player: p.speed=2.4 # 2.4
            Particle.speed=0.7
            screen_change(self.screens,self.in_game)

        if self.intro.is_intro_done():
            for p in self.player:
                p.r=100
                p.distance=0
            self.time_count["menu_after_intro"]=self.now
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

        self.player.update(self.direction)
        
                    

    def draw(self):
        if any(map(lambda s: s.is_screen,self.screens)):
            self.background.fill(self.black)

        if self.in_game.is_screen:
            draw_player(self.player,self.in_game.surface,"ingame")

        else:
            draw_player(self.player,self.menu.surface,"menu")


        for screen in self.screens:
            screen.blit(self.background)
        
        pygame.display.flip()   
        self.clock.tick(self.frame)

if __name__=="__main__":
    duet=Duet()
    duet.mainloop()