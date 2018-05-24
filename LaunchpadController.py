from launchpad import LaunchpadMk2
from Config import Config
import json
import os
import pyaudio
import time
import random
import numpy



class Database:
    def __init__(self, name):
        self.name = name + '.json'
        if self.name in os.listdir('.'):
            print('Found existing DB')
        else:
            print('Creating new DB')
            with open(self.name, 'w') as jFile:
                json.dump({}, jFile)

    def writePattern(self, pName, pData):
        currentData = self.getAllData()
        cont = 'y'
        if pName in currentData:
            cont = raw_input('This pattern exists. Overwrite?: ').lower()
        if 'y' in cont:
            currentData[pName] = pData
            with open(self.name, 'w') as jFile:
                json.dump(currentData, jFile)
        return

    def readPattern(self, pName):
        with open(self.name, 'r') as jFile:
            return json.load(jFile)[pName]

    def getAllPatterns(self):
        with open(self.name, 'r') as jFile:
            return [pName for pName in json.load(jFile)]

    def getAllData(self):
        with open(self.name, 'r') as jFile:
            return json.load(jFile)



class LaunchpadController:

    def __init__(self):
        self.lp = LaunchpadMk2()
        self.lp.Open()
        self.lp.Reset()
        self.state = [0 for x in range(64)]
        self.db = Database('patterns')
        self.config = Config()

    def doNothing(self, button):
        return

    def ledAllOn(self, r, g, b):
        for x in range(8):
            for y in range(8):
                self.lp.LedCtrlXY(x, y+1, r, g, b)
        self.state = [1 for x in range(64)]

    def ledAllOff(self):
        self.lp.reset()
        self.state = [0 for x in range(64)]

    def getButton(self):
        output = {}
        state = self.lp.ButtonStateXY()
        control = self.getControlButton(state)
        fluid = self.getFluidButton(state)
        if not state:
            return {}
        if control != []:
            return {'c':control}
        if fluid != []:
            return {'f':fluid}
        if state[2] == 127:
            return {'b': [state[0], state[1] - 1]}
        return {}

    def getControlButton(self, state):
        if not state:
            return []
        if state[2] == 127 and state[1] == 0:
            return state[0]
        return []

    def getFluidButton(self, state):
        if not state:
            return []
        if state[2] == 127 and state[0] == 8:
            return state[1] - 1
        return []

    def convertToXY(self, ind):


    def convertToInd(self, x, y):
        index = x
        for i in range(y):
            index += 8
        return index

    def updateStateXY(self, x, y, s):
        index = self.convertToInd(x, y)
        self.state[index] = s

    def updateStateInd(self, index, s):
        self.state[index] = s

    def ledOn(self, x, y, r, g, b):
        self.lp.LedCtrlXY(x, y + 1, r, g, b)
        self.updateStateXY(x, y, 1)

    def ledOff(self, x, y):
        self.lp.LedCtrlXY(x, y + 1, 0, 0, 0)
        self.updateStateXY(x, y, 0)

    def getState(self, x, y):
        index = x
        for i in range(y):
            index += 8
        return self.state[index]

    def rainbow(self, speed=0.1, brightness=63):
        r = brightness
        g = 0
        b = 0
        while True:
            for i in range(brightness):
                r -= 1
                b += 1
                launchpad.ledAllOn(r, g, b)
                time.sleep(speed)
            for i in range(brightness):
                b -= 1
                g += 1
                launchpad.ledAllOn(r, g, b)
                time.sleep(speed)
            for i in range(brightness):
                g -= 1
                r += 1
                launchpad.ledAllOn(r, g, b)
                time.sleep(speed)

    def savePattern(self):
        pName = raw_input('Enter a name for this pattern: ').lower()
        self.db.writePattern(pName, self.state)

    def record(self, button):
        if not button:
            return
        if 'b' in button:
            normal = button['b']
            x = normal[0]
            y = normal[1]
            if self.getState(x, y) == 1:
                self.ledOff(x, y)
                return
            if self.getState(x, y) == 0:
                self.ledOn(x, y, 63, 63, 63)
                return
        if 'f' in button:
            fluid = button['f']
            if fluid in self.config.fluids[self.currentMode]:
                todo = eval(self.config.fluids[self.currentMode][fluid])
                todo()

    def recall(self):
        pName = raw_input('Pattern name to recall: ').lower()
        pData = self.db.readPattern()







###   MAIN   ###


    def main(self):
        currentControl = self.doNothing
        self.currentMode = -1

        while True:

            button = self.getButton()

            if 'c' in button:
                control = button['c']
                if control in self.config.controls:
                    print('Setting control to mode ' + str(control))
                    self.currentMode = control
                    currentControl = eval(self.config.controls[control])

            if button:
                print(button)

            currentControl(button)
            time.sleep(0.1)


lp = LaunchpadController()
lp.main()
