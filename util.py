import pygame
from setting import Setting
setting=Setting()


def return_sound(name):
    name="assets/sound/"+name
    try:
        return pygame.mixer.Sound(name)
    except FileNotFoundError:
        try: return pygame.mixer.Sound("Duet/"+name)
        except FileNotFoundError: return pygame.mixer.Sound("./../Duet/"+name)

def return_image(name="lv.png",size=None):
    name="assets/image/"+name
    try:
        image=pygame.image.load(name)
    except FileNotFoundError:
        try: image=pygame.image.load("Duet/"+name)
        except FileNotFoundError: image=pygame.image.load("./../Duet/"+name)
    if size: return pygame.transform.scale(image,size)
    else: return image
        
def return_font(size=30,name="malgungothic",bold=False,italic=False,isfile=False):
    if isfile:
        name="assets/font/"+name
        try:
            return pygame.font.Font(name,size)
        except FileNotFoundError:
            try: return pygame.font.Font("Duet/"+name,size)
            except FileNotFoundError: return pygame.font.Font("./../Duet/"+name,size)
    return pygame.font.SysFont(name,size,bold,italic)

def return_text(font:pygame.font.Font,text="test",antialias=True,color=setting.WHITE):
    return font.render(text,antialias,color)




def draw_player_circle(background:pygame.Surface,r=setting.CENTER[0]//5*2,alpha=128,center=setting.PLAYER_CENTER["menu"]):
    circle_surface=pygame.Surface(setting.SIZE,pygame.SRCALPHA)
    pygame.draw.circle(circle_surface,(200,200,200,alpha),center,r,1)
    background.blit(circle_surface,(0,0))

def draw_player(player,background,screen):
    pos=setting.PLAYER_CENTER[screen]
    draw_player_circle(background,center=pos)
    for p in player:
        # p.change_center(screen)
        p.center=pos
        p.blit(background)



def screen_change(screens,screen):
    for s in screens: s.is_screen=False
    screens[screens.index(screen)].is_screen=True