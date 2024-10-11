import pygame
from setting import Setting
from objects import Objects,Hitbox,Player,PlayerParticle,Intro,Menu,InGame,set_speed,PauseScreen
from util import *


class Duet(Setting):
    def __init__(self):
        print("1: 박스 활성화/비활성화\n2: 무적 활성화/비활성화\n3: 일시정지 활성화/비활성화\n4: 장애물 페인트 초기화\nesc: 인트로 스킵, 일시정지\nm: 음소거 활성화/비활성화")
        super().__init__()
        self.init_pygame()
        self.player=pygame.sprite.Group(Player(self.RED,self.PLAYER_CENTER["menu"],"left"),
                                        Player(self.BLUE,self.PLAYER_CENTER["menu"],"right"))
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
        self.pause_screen=PauseScreen()
        self.screens=[self.intro,self.menu,self.in_game]

        self.mouse_hitbox=Hitbox(pygame.mouse.get_pos(),pygame.Surface((1,1)))

        self.check={"menu":{"main":None,
                            "play":None,
                            "setting":None},
                    "pause":None
                            }
        
        self.play=True

        self.gameover=False


    def init_pygame(self):
        pygame.init()
        self.background=pygame.display.set_mode(self.SIZE)
        pygame.display.set_caption("Duet")
        icon=return_image("icon.jpg")
        pygame.display.set_icon(icon)
        try: pygame.mixer.music.load("assets/sound/Theme_from_Duet.mp3")
        except pygame.error:
            try: pygame.mixer.music.load("Duet/assets/sound/Theme_from_Duet.mp3")
            except pygame.error: pygame.mixer.music.load("./../Duet/assets/sound/Theme_from_Duet.mp3")
        pygame.mixer.music.play(-1)
        

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
                    for p in self.player: p.set_rewind_speed(self.in_game.level.player_angle)
                    self.in_game.level.rewind_change()
        if not self.intro.is_screen:
            self.mouse_hitbox.update(pygame.mouse.get_pos())
        dt=self.clock.tick(self.FRAME)
        set_speed(dt)
        

    def inputs(self):
        keys=pygame.key.get_pressed()
        events=pygame.event.get()
        if not events:
            self.check["menu"]["main"],self.check["menu"]["play"],self.check["menu"]["setting"]=self.menu.button_check(self.mouse_hitbox,False)
            self.check["pause"]=self.pause_screen.button_check(self.mouse_hitbox,False)

        for event in events:
            if event.type==pygame.QUIT:
                pygame.mixer.music.set_volume(0)
                self.play=False
                return
            
            if event.type==pygame.KEYDOWN:
                if self.in_game.is_screen:
                    if not (self.pause or self.rewind_pause):
                        if event.key==pygame.K_LEFT:
                            self.direction=-1
                        if event.key==pygame.K_RIGHT:
                            self.direction=1

                if event.key==pygame.K_ESCAPE:
                    if self.intro.is_screen:
                        print("인트로 스킵")
                        self.intro.skip=True
                    elif self.in_game.is_screen:
                        self.direction=0
                        self.pause=True
                        self.pause_screen.screen_onoff(True)
                        print(f"일시정지: {self.pause}")
                
                if self.menu.is_screen:
                    if event.key==pygame.K_LEFT:
                        self.menu.set_direction(1)
                        print("설정 메뉴(키보드)")
                    if event.key==pygame.K_RIGHT:
                        self.menu.set_direction(-1)
                        print("플레이 메뉴(키보드)")

                if event.key==pygame.K_0:
                    print("플레이어 위치 초기화")
                    self.player.sprites()[0].angle=180
                    self.player.sprites()[1].angle=0

                if event.key==pygame.K_1:
                    Objects.onoff_box()
                    print(f"박스: {Objects.box}")

                if event.key==pygame.K_2:
                    for o in self.in_game.level.obs_group:
                        o.update_invincible()
                    print(f"무적: {self.in_game.level.obs_group.sprites()[0].invincible}")


                if event.key==pygame.K_4:
                    print("장애물 페인트 초기화")
                    for o in self.in_game.level.obs_group:
                        o.reset()

                if event.key==pygame.K_5:
                    print("테스트 페인트 초기화")
                    for o in self.in_game.level.obs_group:
                        o.reset2()

                if event.key==pygame.K_m:
                    print("음소거: ",end="")
                    if pygame.mixer.music.get_volume():
                        print("ON")
                        pygame.mixer.music.set_volume(0)
                    else:
                        print("OFF")
                        pygame.mixer.music.set_volume(1)


            if event.type==pygame.KEYUP:
                if event.key==pygame.K_LEFT and self.direction==-1:
                    self.direction=int(keys[pygame.K_RIGHT])
                if event.key==pygame.K_RIGHT and self.direction==1:
                    self.direction=-int(keys[pygame.K_LEFT])


            if not self.intro.is_screen:
                if self.menu.is_screen:
                    self.check["menu"]["main"],self.check["menu"]["play"],self.check["menu"]["setting"]=self.menu.button_check(self.mouse_hitbox,event.type==pygame.MOUSEBUTTONDOWN)
                if self.in_game.is_screen:
                    self.check["pause"]=self.pause_screen.button_check(self.mouse_hitbox,event.type==pygame.MOUSEBUTTONDOWN)


    def set_level(self,lv):
        self.check["menu"]["play"]=False
        self.direction=0
        self.player.sprites()[0].angle=180
        self.player.sprites()[1].angle=0
        for p in self.player: p.speed=2.4
        PlayerParticle.set_dy(0.9)
        self.in_game.set_level(lv)
        screen_change(self.screens,self.in_game)
        self.menu.direction=0
        self.menu.now=self.SCREEN.MAIN
        self.menu.pos=[-setting.SIZE[0]//1.25,0]

    def move(self):
        if not self.pause:
            if not self.rewind_pause:
                for screen in self.screens: screen.update()
                if self.check["menu"]["main"]:
                    if all(self.check["menu"]["main"][self.BUTTON.PLAY]):
                        self.menu.set_direction(-1)
                    elif all(self.check["menu"]["main"][self.BUTTON.SETTING]):
                        self.menu.set_direction(1)

                if self.check["menu"]["play"]:
                    if all(self.check["menu"]["play"][0]):
                        self.set_level("tutorial")
                        print("Tutorial")
                    elif all(self.check["menu"]["play"][1]):
                        print("test_lv")
                        self.set_level("test_level")


                if self.intro.is_intro_done():
                    for p in self.player:
                        p.r=100
                        p.distance=0
                    self.time_count["menu_after_intro"]=180 if not self.intro.skip else 1
                    screen_change(self.screens,self.menu)

                if self.player.sprites()[0].r!=Player.r:
                    for p in self.player:
                        p.r-=(100-Player.r)/50
                        p.distance+=Player.distance/50
                        p.speed+=(2-1.5)/25
                        if p.r<=Player.r:
                            p.r=Player.r
                            p.distance=Player.distance
                            p.speed=2

                if self.menu.is_screen:
                    self.direction=1
                elif self.in_game.level.rewind:
                    self.direction=0

                self.player.update(self.direction)

                self.in_game.level.player_angle=self.player.sprites()[0].angle \
                    if min(tuple(map(lambda p: p.rect.x,self.player.sprites())))==self.player.sprites()[0].rect.x \
                    else self.player.sprites()[1].angle
                
                if self.in_game.level.is_level_finished():
                    self.in_game.level.reset()
                    screen_change(self.screens,self.menu)
                    for p in self.player:
                        p.speed=2
                    for p in self.player: p.set_rewind_speed(self.in_game.level.player_angle)
                    PlayerParticle.set_dy(0)
                    self.pause=False
                    print(f"메뉴로 돌아옴(레벨 끝남)")

            else:
                self.player.update(0)
        else:
            self.pause_screen.update()
            if self.check["pause"]:
                if all(self.check["pause"][0]):
                    self.direction=0
                    self.pause=False
                    self.pause_screen.screen_onoff(False)
                    print(f"일시정지: {self.pause}")

                if all(self.check["pause"][1]):
                    screen_change(self.screens,self.menu)
                    for p in self.player:
                        p.speed=2
                    for p in self.player: p.set_rewind_speed(self.in_game.level.player_angle)
                    PlayerParticle.set_dy(0)
                    self.pause=False
                    print(f"메뉴로 돌아옴\n일시정지: {self.pause}")


    def collide_check(self):
        if (not self.pause and not self.rewind_pause) and self.in_game.is_screen:
            check=self.in_game.collide_check(self.player.sprites())
            if check:
                if isinstance(check,list):
                    for row in check:
                        self.player.sprites()[row[1]].die()
                else:
                    self.player.sprites()[check[1]].die()
                self.time_count["rewind"]=84
                self.rewind_pause=True
                PlayerParticle.set_dy(0)


        

    def draw(self):
        self.background.fill(self.BLACK)



        if self.in_game.is_screen:
            self.in_game.fill()
            draw_player(self.player,self.in_game.surface,"ingame")
            self.in_game.blit(self.background)

        else:
            self.menu.screens[self.SCREEN.MAIN].fill()
            draw_player(self.player,self.menu.screens[1].surface,"menu")
            self.menu.blit(self.background)

        self.intro.blit(self.background)

        if self.pause:
            self.pause_screen.blit(self.background)


        # for o in self.in_game.level.obs_group:
        #     if o.collide_pos!=[]:
        #         paint=pygame.Surface((20,20),pygame.SRCALPHA)
        #         paint.fill((66,255,37,50))
        #         for angle,pos in o.collide_pos:
        #             self.background.blit(paint,pos)
        
        pygame.display.flip()   

if __name__=="__main__":
    duet=Duet()
    duet.mainloop()
    pygame.quit()