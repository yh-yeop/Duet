class Setting:
    def __init__(self):
        self.size=(450,800)
        self.center=tuple([size//2 for size in self.size])
        self.black=(0,0,0)
        self.white=(255,255,255)
        self.red=(255,100,100)
        self.blue=(100,100,255)
        self.frame=120
        self.player_center={"ingame":(self.center[0],self.size[1]//3*2),
                            "menu":self.center}
        self.SPEED_CONSTANT=1/(1000//120)*(1000//self.frame)