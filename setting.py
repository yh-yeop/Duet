class Setting:
    def __init__(self):
        self.SIZE=(450,800)
        self.CENTER=tuple([size//2 for size in self.SIZE])
        self.BLACK=(0,0,0)
        self.WHITE=(255,255,255)
        self.RED=(255,100,100)
        self.BLUE=(100,100,255)
        self.FRAME=120
        self.PLAYER_CENTER={"ingame":(self.CENTER[0],self.SIZE[1]//8*7),
                            "menu":self.CENTER}
        self.BUTTON=ButtonConstant()
        self.SCREEN=ScreenConstant()
        

class ButtonConstant:
    def __init__(self):
        self.SETTING=0
        self.PLAY=1

class ScreenConstant:
    def __init__(self):
        self.SETTING=0
        self.MAIN=1
        self.PLAY=2