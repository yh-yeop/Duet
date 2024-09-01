import pygame
import pygame.gfxdraw

bg=pygame.display.set_mode((640,480))
pygame.init()
play=True
aa=False
color=(255,0,0)
while play:
    for event in pygame.event.get():
        if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
            play=False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_1:
                aa=not aa
            if event.key==pygame.K_2:
                if color==(255,0,0):
                    color=(100,100,100)
                else:
                    color=(255,0,0)
    bg.fill((0,0,0,0))
    pygame.draw.circle(bg,(100,100,100),(320,240),200)
    if aa: pygame.gfxdraw.aacircle(bg,320,240,200,color)
    else: pygame.draw.circle(bg,color,(320,240),200,1)
    pygame.display.flip()
pygame.quit()
quit()