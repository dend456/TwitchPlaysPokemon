from IRCBot import IRCBot
from SendKeys import sendKeys
import time, re, win32api, win32con, win32gui, win32ui, ctypes

class TwitchBot(IRCBot):
    def __init__(self,channel,user,password,keyFile,bannedWordFile):
        IRCBot.__init__(self,"irc.twitch.tv",6667,channel,user,password)
        self.totalInput = 0
        self.lastSave = time.clock()
        self.paused = False
        self.positionPattern = re.compile(r'[0-9]{1,3},[0-9]{1,3}')
        self.basePos = (58,425)
        self.bannedWords = []
        self.bannedWordFile = bannedWordFile
        self.keyMap = dict()
        self.currentSaveSlot = 1
        self.allowTouching = False;
        self.allowDragging = False;
        self.inputDelay = 0.05
        self.onCommandCallback = None
        self.mods = []
        
        self.loadKeyMap(keyFile)
        t = self.keyMap.get("touching")
        if t == "true":
            self.allowTouching = True
        t = self.keyMap.get("dragging")
        if t == "true":
            self.allowDragging = True
        t = self.keyMap.get("inputDelay")
        if t:
            self.inputDelay = t
        
        if bannedWordFile:
            self.loadBannedWords(bannedWordFile)

    def _onMessage(self,name,message):
        currentTime = time.clock()
        if not self.paused and self.lastSave < currentTime - 120:
            self.lastSave = currentTime
            key = "F" + str(self.currentSaveSlot)
            self.sendKeyboardInput("+{"+key+"}")
            #print("\t\t\t\t\t\tsaved " + str(self.currentSaveSlot))
            title = "Saved slot - {} - {}".format(self.currentSaveSlot,time.strftime("%H:%M:%S"))
            ctypes.windll.kernel32.SetConsoleTitleA(title)
            self.currentSaveSlot += 1
            if self.currentSaveSlot == 10:
                self.currentSaveSlot = 1
        
        msg = message.lower()
        name = name.lower()
        
        button = ''

        if name == 'xXXXxxXxxXXXxX': #owner name
            if msg == '!pause':
                self.paused = True
            elif msg == '!unpause':
                self.paused = False
            elif msg == '!pong':
                print("\t\t\t\t\t\tping")
            elif msg == '!reload':
                self.allowTouching = False;
                self.allowDragging = False;
                
                self.loadKeyMap(self.bannedWordFile)
                t = self.keyMap.get("touching")
                if t == "true":
                    self.allowTouching = True
                t = self.keyMap.get("dragging")
                if t == "true":
                    self.allowDragging = True
                
                if self.bannedWordFile:
                    self.loadBannedWords(self.bannedWordFile)

        if name in self.mods:
            if msg[0] == '!':
                if msg.startswith("!"):
                    if self.onCommandCallback:
                        self.onCommandCallback(msg)

        button = self.keyMap.get(msg)
        
        #self.paused = True ######
        
        if not self.paused and button:
            self.totalInput += 1
            print(name + ": " + msg)
            self.sendKeyboardInput(button)
            if self.onCommandCallback:
                self.onCommandCallback(name + ": " + msg)
        elif not self.paused and self.allowTouching and msg.startswith("touch"):
            match = self.positionPattern.search(msg)
            if match:
                posStr = msg[match.start():match.end()]
                mid = posStr.index(",")
                x = int(posStr[0:mid])
                y = int(posStr[mid+1:])
                if x < 380 and y  < 280:
                    self.sendMouseClick(0,x,y)
                    command = "{}: touch {},{}".format(name,x,y)
                    print(command)
                    self.totalInput += 1
                    if self.onCommandCallback:
                        self.onCommandCallback(command)
        elif not self.paused and self.allowDragging and msg.startswith("drag"):
            match = self.positionPattern.search(msg)
            if match:
                posStr = msg[match.start():match.end()]
                mid = posStr.index(",")
                x1 = int(posStr[0:mid])
                y1 = int(posStr[mid+1:])

                stringEnd = msg[match.end()+1:]
                match = self.positionPattern.search(stringEnd)
                if match:
                    posStr = stringEnd[match.start():match.end()]
                    mid = posStr.index(",")
                    x2 = int(posStr[0:mid])
                    y2 = int(posStr[mid+1:])
                
                    if x1 < 380 and y1 < 280 and x2 < 380 and y2 < 280:
                        self.sendMouseDrag(0,x1,y1,x2,y2)
                        command = "{}: drag {},{} {},{}".format(name,x1,y1,x2,y2)
                        print(command)
                        self.totalInput += 1
                    if self.onCommandCallback:
                        self.onCommandCallback(command)
        else:
            for word in self.bannedWords:
                if word in msg:
                    #print("\t\t\t\t\t\tban {0}".format(name))
                    self.sendMessage("PRIVMSG {0} :.ban {1}\r\n".format(self.channel,name))

    def loadKeyMap(self,filename):
        try:
            self.keyMap = dict()
            with open(filename,"r") as f:
                for line in f:
                    line = line.strip()
                    strings = line.split(" ")
                    if strings[0] == "inputDelay":
                        strings[1] = float(strings[1])
                    self.keyMap[strings[0]] = strings[1]
        except:
            print("Error loading key map.")
            
    def loadBannedWords(self, filename):
        try:
            with open(filename,"r") as words:
                banned = words.readlines()
                banned = [word.strip("\r\n") for word in banned]
                self.bannedWords = banned
        except:
            print("Error loading banned words.")

    def sendKeyboardInput(self,keys):
        #sendKeys(keys,pause=self.inputDelay)
        pass
        
    def sendMouseClick(self, button, x, y):
        x += self.basePos[0]
        y += self.basePos[1]
        
        LEFT_DOWN = 0x2
        LEFT_UP = 0x4
        RIGHT_DOWN = 0x8
        RIGHT_UP = 0x10
        MIDDLE_DOWN = 0x20
        MIDDLE_UP = 0x40

        pos = win32gui.GetCursorPos()

        ctypes.windll.user32.SetCursorPos(x,y)

        time.sleep(.05)
        
        if button == 0:
            ctypes.windll.user32.mouse_event(LEFT_DOWN,0,0,0,0)
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(LEFT_UP,0,0,0,0)
        if button == 1:
            ctypes.windll.user32.mouse_event(RIGHT_DOWN,0,0,0,0)
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(RIGHT_UP,0,0,0,0)
        if button == 2:
            ctypes.windll.user32.mouse_event(MIDDLE_DOWN,0,0,0,0)
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(MIDDLE_UP,0,0,0,0)

        time.sleep(.05)

    def sendMouseDrag(self, button, x1, y1, x2, y2):
        x1 += self.basePos[0]
        y1 += self.basePos[1]
        x2 += self.basePos[0]
        y2 += self.basePos[1]
        
        LEFT_DOWN = 0x2
        LEFT_UP = 0x4
        RIGHT_DOWN = 0x8
        RIGHT_UP = 0x10
        MIDDLE_DOWN = 0x20
        MIDDLE_UP = 0x40

        pos = win32gui.GetCursorPos()

        ctypes.windll.user32.SetCursorPos(x1,y1)

        time.sleep(.05)
        
        if button == 0:
            ctypes.windll.user32.mouse_event(LEFT_DOWN,0,0,0,0)
        if button == 1:
            ctypes.windll.user32.mouse_event(RIGHT_DOWN,0,0,0,0)
        if button == 2:
            ctypes.windll.user32.mouse_event(MIDDLE_DOWN,0,0,0,0)

        time.sleep(0.05)
        ctypes.windll.user32.SetCursorPos(x2,y2)
        time.sleep(0.05)

        if button == 0:
            ctypes.windll.user32.mouse_event(LEFT_UP,0,0,0,0)
        if button == 1:
            ctypes.windll.user32.mouse_event(RIGHT_UP,0,0,0,0)
        if button == 2:
            ctypes.windll.user32.mouse_event(MIDDLE_UP,0,0,0,0)

        time.sleep(.05)

        
if __name__ == "__main__":
    channel = "xxxx"
    username = "xxxx"
    password = "xxxx"
    keyFile = "dskeys.txt"
    bannedWordFile = "bannedwords.txt"

    x = TwitchBot(channel,username,password,keyFile,bannedWordFile)
    x.run()
