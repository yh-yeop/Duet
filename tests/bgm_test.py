import pygame
pygame.init()
background=pygame.display.set_mode((450,800))
size=(450,800)
center=(225,400)
pygame.display.set_caption("Duet")
pygame.mixer.music.load("./Duet/assets/sound/bgm/Theme_from_Duet.mp3")
pygame.mixer.music.play(-1)
while True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            quit()

  

    background.fill((0,0,0))
    pygame.display.flip()