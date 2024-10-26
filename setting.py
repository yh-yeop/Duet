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
        self.ENG_FONT="Montserrat/static/Montserrat-Thin.ttf"
        self.KOR_FONT="Noto_Sans_KR/static/NotoSansKR-Regular.ttf"
        self.MAINMENU_BUTTON={"SETTING":0,
                              "PLAY":1}
        
        self.SETTINGMENU_BUTTON={"BGM":0}

        self.MENU_SCREEN={"SETTING":0,
                          "MAIN":1,
                          "PLAY":2}