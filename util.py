import pygame
from setting import Setting
setting=Setting()

def draw_player_circle(background,r=setting.CENTER[0]//5*2,alpha=128,center=setting.PLAYER_CENTER["menu"]):
    circle_surface=pygame.Surface(setting.SIZE,pygame.SRCALPHA)
    pygame.draw.circle(circle_surface,(200,200,200,alpha),center,r,1)
    background.blit(circle_surface,(0,0))

def return_font(size,name="malgungothic",bold=False,italic=False,isfile=False):
    if isfile:
        name="assets/font/"+name
        try:
            return pygame.font.Font(name,size)
        except FileNotFoundError:
            try: return pygame.font.Font("Duet/"+name,size)
            except FileNotFoundError: return pygame.font.Font("./../Duet/"+name,size)
    return pygame.font.SysFont(name,size,bold,italic)

def return_text(font,text="test",antialias=True,color=setting.WHITE):
    return font.render(text,antialias,color)

def return_image(path,size=False):
    path="assets/image/"+path
    try:
        image=pygame.image.load(path)
    except FileNotFoundError:
        try: image=pygame.image.load("Duet/"+path)
        except FileNotFoundError: image=pygame.image.load("./../Duet/"+path)
    if size: return pygame.transform.scale(image,size)
    else: return image

def draw_player(player,background,screen):
    pos=setting.PLAYER_CENTER[screen]
    draw_player_circle(background,center=pos)
    for p in player:
        p.center=pos
        p.blit(background)


def screen_change(screens,screen):
    for s in screens: s.is_screen=False
    screens[screens.index(screen)].is_screen=True
    return screens