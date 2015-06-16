from Tkinter import *
from PIL import ImageTk, Image
from tkFont import Font
from TwitchBot import TwitchBot
import string,sys,time,socket,os,urllib2,threading


class Application(Frame):
    def saveState(self):
        with open("currentstate.txt","w") as f:
            f.write(str(self.totalButtons)+"\r\n")
            for i in range(0,8):
                f.write(self.badgeImages[i]+"\r\n")
            for i in range(0,6):
                f.write(self.pokeImages[i]+"\r\n")
    
    def loadState(self):
        with open("currentstate.txt","r") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            self.totalButtons = int(lines[0])
            for i in range(0,8):
                self.changeBadgeImage(i,lines[i+1],False)
            for i in range(0,6):
                self.changePokeImage(i,lines[i+9],False)

            self.totalButtonsLabel.config(text="{:,d}".format(self.totalButtons))
                
    def downloadImage(self, imageName):
        try:
            response = urllib2.urlopen('http://img.pokemondb.net/artwork/{}.jpg'.format(imageName))
            if response:
                t = response.read()
                with open(os.getcwd() + "\\images\\{}.jpg".format(imageName),"wb") as f:
                    f.write(t)
                self.convertJPGToPNG(imageName)
        except:
            pass

    def convertJPGToPNG(self, imageName):
        img = self.getImage(imageName, ext="jpg")
        if img:
            img.save(os.getcwd() + "\\images\\{}.png".format(imageName))
        
    def getImage(self, imageName, ext="png", shouldDL=True):
        path = os.getcwd() + "\\images\\{}.{}".format(imageName,ext)
        if os.path.isfile(path):
            return Image.open(path)
        else:
            if shouldDL:
                self.downloadImage(imageName)
                return self.getImage(imageName, shouldDL=False)
        return None
    
    def changeBadgeImage(self,slot, imageName, save):
        if slot >= 0 and slot <= 7:
            img = self.getImage(imageName)
            if img:
                img = img.resize((self.badgeSize,self.badgeSize),Image.ANTIALIAS)
                t = ImageTk.PhotoImage(img)
                self.badgeLabels[slot].configure(image = t)
                self.badgeLabels[slot].image = t
                self.badgeImages[slot] = imageName
                if save:
                    self.saveState()
            elif imageName != "none":
                self.changeBadgeImage(slot,"none",True)

    def changePokeImage(self, slot, imageName, save):   
        if slot >= 0 and slot <= 5:
            img = self.getImage(imageName)
            if img:
                img = img.resize((self.pokeSize,self.pokeSize),Image.ANTIALIAS)
                t = ImageTk.PhotoImage(img)
                self.pokeLabels[slot].configure(image = t)
                self.pokeLabels[slot].image = t
                self.pokeImages[slot] = imageName
                if save:
                    self.saveState()
            elif imageName != "none":
                self.changePokeImage(slot,"none",True)
                

    def updateTimer(self):
        self.timerLabel.config(text=time.strftime("%M:%S", time.gmtime()))
        self.after(250,self.updateTimer)

    def refresh(self):
        self.saveState()
        self.loadState()

    def onCommand(self, command):
        if command[0] == '!':
            if command.startswith("!pokemon"):
                strings = command.split(" ")
                try:
                    slot = int(strings[1])
                    self.changePokeImage(slot,strings[2],True)
                except:
                    pass
                    
            elif command.startswith("!badge"):
                strings = command.split(" ")
                try:
                    slot = int(strings[1])
                    self.changeBadgeImage(slot,strings[2],True)
                except:
                    pass

            elif command == "!refresh":
                self.refresh()
        else:
            self.textBox.insert(END,command+"\n")
            self.numCommands += 1
            self.totalButtons += 1
            self.totalButtonsLabel.config(text="{:,d}".format(self.totalButtons))
            while self.numCommands > self.numTextLines:
                self.textBox.delete(1.0,2.0)
                self.numCommands -= 1

            if self.totalButtons % 50 == 0:
                self.saveState()

    def createWidgets(self):
        textboxcolumns = 20

        font = Font(weight='bold',size=10)
        self.textBox = Text(self,width=60,height=self.numTextLines,font=font, foreground="#BBBBBB", bg="black", borderwidth=0,wrap=NONE)
        self.textBox.grid(column=0,row=0,columnspan=20,rowspan=4)
        x = textboxcolumns
        y = 0
        for i in range(0,8):
            self.badgeLabels[i] = Label(self, borderwidth=0, width=self.badgeSize,height=self.badgeSize, bg="Black")
            self.changeBadgeImage(i,"none",False)
            self.badgeLabels[i].grid(column=x,row=y)
            x += 1
            if x == textboxcolumns + 2:
                x = textboxcolumns
                y += 1
        for i in range(0,6):
            self.pokeLabels[i] = Label(self, borderwidth=0, width=self.pokeSize, height=self.pokeSize, bg="black")
            self.changePokeImage(i,"white",False)
            self.pokeLabels[i].grid(column=textboxcolumns+3+(i*4),row=0,columnspan=2,rowspan=2)

        font = Font(weight='bold',size=16)
        currentTime = time.strftime("%M:%S", time.gmtime())
        self.timerLabel = Label(self, borderwidth=0, font=font, text=currentTime, bg="black", fg="white")
        self.timerLabel.grid(column=textboxcolumns+23,row=3,rowspan=1)

        self.totalButtonsLabel = Label(self, borderwidth=0, text="0", bg="black", fg="white")
        self.totalButtonsLabel.grid(column=textboxcolumns+23,row=2,rowspan=2)

        self.loadState()

        self.updateTimer()

    def onClose(self,other=None):
        self.saveState()
        self.quit()

    def __init__(self, master=None):
        Frame.__init__(self, master=master, borderwidth=3, bg="#000000")
        self.master = master
        self.badgeSize = 40
        self.pokeSize = 80
        self.pokeLabels = [None]*6
        self.badgeLabels = [None]*8
        self.badgeImages = ["none"]*8
        self.pokeImages = ["none"]*8
        self.commands = [""] * 10
        self.numCommands = 0
        self.numTextLines = 11
        self.totalButtons = 0
        master.wm_title("Pokemon")
        master.protocol('WM_DELETE_WINDOW',self.onClose)

        master.geometry("+0+0")
        #master.bind("<Control-c>", self.onClose)
        self.pack()
        self.createWidgets()

root = Tk()
try:
    channel = "channelname"
    username = "username"
    password = "oauthkey"
    keyFile = "dskeys.txt"
    bannedWordFile = "bannedwords.txt"
    
    app = Application(master=root)
    
    twitchBot = TwitchBot(channel,username,password,keyFile,bannedWordFile)
    twitchBot.onCommandCallback = app.onCommand
    t = threading.Thread(target=twitchBot.run)
    t.daemon = True
    t.start()
    
    app.mainloop()
finally:
    root.destroy()
