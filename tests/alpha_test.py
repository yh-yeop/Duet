import pygame
pygame.init()
background=pygame.display.set_mode((450,800))
size=(450,800)
center=(225,400)
s = pygame.Surface((150,30))
s.fill((255,255,255))
alpha=255
alpha_plus=-0.2
pygame.display.set_caption("Duet")
while True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            quit()

    alpha+=alpha_plus
    if alpha>255:
        alpha=255
        alpha_plus=-0.2
    if alpha<0:
        alpha=0
        alpha_plus=0.2
    s.set_alpha(alpha)

    background.fill((0,0,0))
    background.blit(s,(center[0]-s.get_size()[0]//2,size[1]//3))
    pygame.draw.circle(background,(200,200,200),(center[0],size[1]//4*3),center[0]//5*2,1)
    pygame.draw.circle(background,(255,0,0),(center[0]//5*3,size[1]//4*3),12)
    pygame.draw.circle(background,(0,0,255),(center[0]//5*7,size[1]//4*3),12)
    pygame.display.flip()