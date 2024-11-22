import pygame
from setting import Setting
from objects import Objects,Hitbox,Player,PlayerParticle,Intro,Menu,InGame,set_speed,PauseScreen,ClearScreen,Vector2
from util import return_image,screen_change,draw_player,return_sound

class Duet(Setting):
    def __init__(self):
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
        self.clear_screen=ClearScreen()
        self.screens=[self.intro,self.menu,self.in_game]

        self.mouse_hitbox=Hitbox(pygame.mouse.get_pos(),pygame.Surface((1,1)))
        
        self.check={"menu":{"main":None,
                            "play":None,
                            "setting":None,
                            "main_screen":None},
                    "pause":None
                            }
        


        self.play=True
        self.clear=False
        self.sounds={"death":return_sound("death.mp3"),
                     "rewind":return_sound("rewind.mp3")}

        self.player_area=False
        self.area_surface=pygame.Surface(self.SIZE,pygame.SRCALPHA)
        for angle in range(360):
            pygame.draw.circle(self.area_surface,(*self.WHITE,30),Vector2(self.PLAYER_CENTER["ingame"])+Vector2(Player.distance,0).rotate(angle),Player.r)

    def init_pygame(self):
        pygame.init()
        self.background=pygame.display.set_mode(self.SIZE)
        pygame.display.set_caption("Duet")
        icon=return_image("icon.jpg")
        pygame.display.set_icon(icon)
        self.set_bgm("Theme_from_Duet")

    def set_bgm(self,name):
        path="assets/sound/bgm/"
        try: pygame.mixer.music.load(path+name+".mp3")
        except pygame.error:
            try: pygame.mixer.music.load("Duet/"+path+name+".mp3")
            except pygame.error: pygame.mixer.music.load("./../Duet/"+path+name+".mp3")
        pygame.mixer.music.play(-1)

    def mainloop(self):
        while True:
            self.setting() # 변수 초기화
            self.inputs() # 입력 이벤트 처리
            if not self.play: # 종료 이벤트 발생 시 반복 종료
                return
            self.update() # 이동 관리
            self.collide_check() # 충돌 관리
            self.draw() # 그리기
    
    def setting(self):
        if not self.pause:
            if self.time_count["menu_after_intro"]:
                self.time_count["menu_after_intro"]-=1
                if self.time_count["menu_after_intro"]<=0:
                    self.menu.screens[1].start=True
                elif self.time_count["menu_after_intro"]<=60:
                    for p in self.player: p.speed=1.7
            if self.rewind_pause and self.time_count["rewind"]:
                self.time_count["rewind"]-=1
                if self.time_count["rewind"]<=0:
                    self.rewind_pause=False
                    for p in self.player: p.set_rewind_speed()
                    self.sounds["rewind"].play()
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
            self.check["menu"]["main_screen"]=None
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
                        if not self.pause:
                            self.direction=0
                            self.pause=True
                            self.pause_screen.screen_onoff(True)

                    
                
                if self.menu.is_screen:
                    if event.key==pygame.K_LEFT:
                        self.menu.set_direction(1)
                    if event.key==pygame.K_RIGHT:
                        self.menu.set_direction(-1)


                if True: # 테스트용 기능
                    if event.key==pygame.K_F1:
                        print("\nF1: 도움말\nF2: 박스 활성화/비활성화\nF6: 무적 활성화/비활성화\nF4: 장애물 페인트 초기화\nF5: 플레이어 위치 초기화\nF7: 플레이어 사망\nesc: 인트로 스킵\nS: 레벨 스킵\nF8: 플레이어 이동반경 활성화/비활성화")
                    
                    if event.key==pygame.K_F2:
                        Objects.onoff_box()
                        print(f"박스: {Objects.box}")
                    
                    if event.key==pygame.K_F6:
                        for o in self.in_game.level.obs_group:
                            o.update_invincible()
                        print(f"무적: {self.in_game.level.obs_group.sprites()[0].invincible}")

                    if event.key==pygame.K_F4:
                        print("장애물 페인트 초기화")
                        for o in self.in_game.level.obs_group:
                            o.reset()
                    
                    if event.key==pygame.K_F5:
                        print("플레이어 위치 초기화")
                        self.player.sprites()[0].angle=180
                        self.player.sprites()[1].angle=0

                    if event.key==pygame.K_F7:
                        print("플레이어 사망")
                        for p in self.player:
                            p.die()

                    if event.key==pygame.K_F8:
                        self.player_area=not self.player_area
                        print(f"플레이어 이동반경 표시: {self.player_area}")

                    if event.key==pygame.K_ESCAPE:
                        if self.intro.is_screen:
                            print("인트로 스킵")
                            self.intro.skip=True

                    if event.key==pygame.K_s:
                        if self.in_game.is_screen and self.in_game.level.next_level:
                            print("레벨 스킵")
                            self.in_game.set_next_level()
                


            if event.type==pygame.KEYUP:
                if event.key==pygame.K_LEFT and self.direction==-1:
                    self.direction=int(keys[pygame.K_RIGHT])
                if event.key==pygame.K_RIGHT and self.direction==1:
                    self.direction=-int(keys[pygame.K_LEFT])


            if not self.intro.is_screen:
                if self.menu.is_screen:
                    self.check["menu"]["main"],self.check["menu"]["play"],self.check["menu"]["setting"]=self.menu.button_check(self.mouse_hitbox,event.type==pygame.MOUSEBUTTONDOWN)
                    if self.menu.now!=self.MENU_SCREEN["MAIN"]:
                        collide_pos=pygame.sprite.collide_mask(Hitbox(Vector2(self.SIZE[0]//1.25,0)+self.menu.pos,self.menu.screens[self.MENU_SCREEN["MAIN"]].surface),self.mouse_hitbox)
                        self.check["menu"]["main_screen"]=collide_pos,event.type==pygame.MOUSEBUTTONDOWN
                if self.in_game.is_screen:
                    self.check["pause"]=self.pause_screen.button_check(self.mouse_hitbox,event.type==pygame.MOUSEBUTTONDOWN)

    def set_level(self,lv):
        self.check["menu"]["play"]=False
        self.direction=0
        self.player.sprites()[0].angle=180
        self.player.sprites()[1].angle=0
        Player.set_rewind_angle(180)
        Player.set_player_center(1)
        for p in self.player:
            p.speed=2.4
            p.reset_particle()
            p.set_rewind_speed()
        PlayerParticle.set_dy(0.9)
        self.in_game.set_level(lv)
        screen_change(self.screens,self.in_game)
        self.menu.direction=0
        self.menu.now=self.MENU_SCREEN["MAIN"]
        self.menu.pos=[-self.SIZE[0]//1.25,0]
        self.sounds["rewind"].play()

    def update(self):
        self.pause_screen.update()
        self.clear_screen.update()
        if self.clear and self.clear_screen.is_circle_getting_smaller():
            screen_change(self.screens,self.menu)
            for p in self.player:
                p.distance=Player.distance
                p.speed=2
            if self.clear_screen.w==450:
                self.clear=False
                self.clear_screen.__init__()
        elif self.clear_screen.is_screen:
            self.menu.screens[self.MENU_SCREEN["MAIN"]].reset()

        if not self.pause:
            if not self.rewind_pause:
                for screen in self.screens: screen.update()
                if self.check["menu"]["main"]:
                    if all(self.check["menu"]["main"][self.MAINMENU_BUTTON["PLAY"]]):
                        self.menu.set_direction(-1)
                    elif all(self.check["menu"]["main"][self.MAINMENU_BUTTON["SETTING"]]):
                        self.menu.set_direction(1)

                if self.check["menu"]["main_screen"] and all(self.check["menu"]["main_screen"]):
                    if self.check["menu"]["main_screen"][0][0]<self.menu.screens[self.MENU_SCREEN["MAIN"]].surface.get_size()[0]//2: self.menu.set_direction(-1)
                    else: self.menu.set_direction(1)
                

                if self.check["menu"]["play"]:
                    if all(self.check["menu"]["play"][0]):
                        self.set_level("tutorial")
                    elif all(self.check["menu"]["play"][1]):
                        self.set_level("level2")

                bgm=self.menu.screens[self.MENU_SCREEN["SETTING"]].get_onoff()[self.SETTINGMENU_BUTTON["BGM"]]
                sfx=self.menu.screens[self.MENU_SCREEN["SETTING"]].get_onoff()[self.SETTINGMENU_BUTTON["SFX"]]
                if pygame.mixer.music.get_volume()!=int(bgm):
                    pygame.mixer.music.set_volume(int(bgm))
                if self.sounds["death"].get_volume()!=int(sfx):
                    for k in self.sounds:
                        self.sounds[k].set_volume(int(sfx))


                if self.intro.is_intro_done():
                    for p in self.player:
                        p.r=100
                        p.distance=0
                        p.reset_particle()
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

                finished=self.in_game.is_level_finished()
                reset_angle=self.player.sprites()[0].angle if min(tuple(map(lambda p: p.rect.x,self.player.sprites())))==self.player.sprites()[0].rect.x else self.player.sprites()[1].angle
                
                if self.menu.is_screen:
                    self.direction=1
                elif self.in_game.level.rewind:
                    self.direction=0
                elif all(finished):
                    self.in_game.set_next_level()
                    Player.set_reset_angle(-1 if 270>reset_angle>90 else 1)
                if Player.reset_direction:
                    for p in self.player:
                        if p.angle in (0,180):
                            Player.set_reset_angle(0)
                            break
                    
                Player.player_center_update()
                self.player.update(self.direction)

                rewind_angle=self.player.sprites()[0].angle if min(tuple(map(lambda p: p.rect.x,self.player.sprites())))==self.player.sprites()[0].rect.x else self.player.sprites()[1].angle
                Player.set_rewind_angle(rewind_angle)
                
                if finished[0] and not finished[1]:
                    self.in_game.level.reset()
                    screen_change(self.screens,self.menu)
                    Player.set_player_center(-0.5)
                    for p in self.player:
                        p.reset_particle()
                        p.speed=1.5
                    PlayerParticle.set_dy(0)
                    self.pause=False
                    self.clear=True
                if self.clear: # 클리어 연출
                    self.menu.screens[self.MENU_SCREEN["MAIN"]].reset()
                    for p in self.player:
                        p.speed=min(p.speed+0.01,3.5)
                        if p.speed>=2.5: p.distance=max(p.distance-Player.distance/500,0)
                    if not self.player.sprites()[0].distance:
                        self.clear_screen.is_screen=True
                    self.player.update(0.5)

            else: # rewind_pause일 시
                self.player.update(0)


        else:
            if PauseScreen.level_name!=self.in_game.level.name:
                PauseScreen.set_level_name(self.in_game.level.name)
            if self.check["pause"]:
                if all(self.check["pause"][0]):
                    self.direction=0
                    self.pause=False
                    self.pause_screen.screen_onoff(False)

                if all(self.check["pause"][1]):
                    screen_change(self.screens,self.menu)
                    Player.set_player_center(-1)
                    PlayerParticle.set_dy(0)
                    for p in self.player:
                        p.reset_death()
                        p.speed=2
                        p.reset_particle()
                        p.set_rewind_speed()
                    self.pause=False
                    self.pause_screen.screen_onoff(False)
                    self.rewind_pause=False
                    self.sounds["rewind"].play()

    def collide_check(self):
        if (not self.pause and not self.rewind_pause) and self.in_game.is_screen:
            check=self.in_game.collide_check(self.player.sprites())
            if check:
                self.sounds["death"].play()
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
            draw_player(self.player,self.in_game.surface,Player.get_center())
            self.in_game.blit(self.background)

        else:
            self.menu.screens[self.MENU_SCREEN["MAIN"]].fill()
            draw_player(self.player,self.menu.screens[1].surface,Player.get_center())
            self.menu.blit(self.background)

        self.intro.blit(self.background)
        
        self.clear_screen.blit(self.background)
        self.pause_screen.blit(self.background)

        if self.player_area:
                self.background.blit(self.area_surface,(0,0))
        
        pygame.display.flip()