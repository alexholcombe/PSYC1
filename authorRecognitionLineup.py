from __future__ import print_function
from psychopy import event, sound, logging
from psychopy import visual, event, sound, tools
import numpy as np
import string
from math import floor
from copy import deepcopy

def calcRespYandBoundingBox(possibleResps, i):
    spacingCtrToCtr = 2.0 / len(possibleResps)
    charHeight = spacingCtrToCtr
    startCoordinate = 1-charHeight/2 #top , to bottom
    increment = i*spacingCtrToCtr
    increment*=- 1 #go down from top
    coordinate = startCoordinate + increment
    boxWidth = spacingCtrToCtr #0.1
    boxHeight = spacingCtrToCtr
    return coordinate, boxWidth, boxHeight

def drawRespOption(myWin,bgColor,xStart,color,drawBoundingBox,relativeSize,possibleResps,i):
        #relativeSize multiplied by standard size to get desired size
        coord, w, h = calcRespYandBoundingBox( possibleResps, i )
        x = xStart
        y = coord
        if relativeSize != 1: #erase bounding box so erase old letter before drawing new differently-sized letter 
            print('drawing to erase')
            boundingBox = visual.Rect(myWin,width=w,height=h, pos=(x,y), fillColor=bgColor, lineColor=None, units='norm' ,autoLog=False) 
            boundingBox.draw()
        option = visual.TextStim(myWin,colorSpace='rgb',color=color,alignHoriz='center', alignVert='center',
                                                                    height=h*relativeSize,units='norm',autoLog=False)
        option.setText(possibleResps[i])
        option.pos = (x, y)
        option.draw()
        if drawBoundingBox:
            boundingBox = visual.Rect(myWin,width=w,height=h, pos=(x,y))
            boundingBox.draw()
        
def drawResponseArray(myWin,bgColor,xStart,possibleResps,selected,selectedColor):
    '''selected indicated whether each is selected or not
    possibleResps is array of all the authors to populate the screen with.
    '''
    #print("leftRight=",leftRight, "xOffset=",xOffset)
    numResps = len(possibleResps)
    dimRGB = -.3
    drawBoundingBox = False #to debug to visualise response regions, make True

    #Draw it vertically, from top to bottom
    for i in xrange(len(possibleResps)):
        if selected[i]:
            color = selectedColor
        else: 
            color = (1,1,1)
        drawRespOption(myWin,bgColor,xStart,color,drawBoundingBox,1,possibleResps,i)

def checkForOKclick(mousePos,respZone):
    OK = False
    if respZone.contains(mousePos):
            OK = True
    return OK

def convertXYtoNormUnits(XY,currUnits,win):
    if currUnits == 'norm':
        return XY
    else:
        widthPix = win.size[0]
        heightPix = win.size[1]
        if currUnits == 'pix':
            xNorm = XY[0]/ (widthPix/2)
            yNorm = XY[1]/ (heightPix/2)
        elif currUnits== 'deg':
            xPix = tools.monitorunittools.deg2pix(XY[0], win.monitor, correctFlat=False)
            yPix = tools.monitorunittools.deg2pix(XY[1], win.monitor, correctFlat=False)
            xNorm = xPix / (widthPix/2)
            yNorm = yPix / (heightPix/2)
            #print("Converted ",XY," from ",currUnits," units first to pixels: ",xPix,yPix," then to norm: ",xNorm,yNorm)
    return xNorm, yNorm

def collectLineupResponses(myWin,bgColor,myMouse,minMustClick,maxCanClick,OKtextStim,OKrespZone,mustDeselectMsgStim,possibleResps,clickSound,badClickSound):
   
   myMouse.clickReset()
   whichResp = -1
   state = 'waitingForAnotherSelection' 
   #waitingForAnotherSelection means OK is  not on the screen, so must click a lineup item
   #'finished' exit this lineup, choice has been made
   expStop = False
   xStart = -.9
   #Need to maintain a list of selected. Draw those in another color
   selected = [0] * len(possibleResps)
   selectedColor = (1,1,-1)

   while state != 'finished' and not expStop:
        #draw everything corresponding to this state
        #draw selecteds in selectedColor, remainder in white
        print('state = ',state)
        drawResponseArray(myWin,bgColor,xStart,possibleResps,selected,selectedColor)
        if state == 'waitingForAnotherSelection':
            #buttonThis = np.where(pressed)[0] #assume only one button can be recorded as pressed
            #drawRespOption(myWin,bgColor,constCoord,selectedColor,False,1.5,possibleResps,whichResp)
            
            #assume half are authors, therefore when have clicked half, have option to finish
            print('Summing selected, ',selected, ' minMustClick=',minMustClick)
            if sum(selected) >= minMustClick:
                print('drawing OKrespZone')
                OKrespZone.draw()
                OKtextStim.draw()
        myWin.flip()

        #Poll keyboard and mouse
        #Used to use pressed,times = myMouse.getPressed(getTime=True) because it's supposed to return all presses since last call to clickReset. But, doesn't seem to work. So, now loop
        #If getTime=True (False by default) then getPressed will return all buttons that have been pressed since the last call to mouse.clickReset as well as their time stamps:
        pressed,times = myMouse.getPressed(getTime=True)
        while not any(pressed): #wait until pressed
            pressed = myMouse.getPressed() 
        mousePos = myMouse.getPos()
        mousePos = convertXYtoNormUnits(mousePos,myWin.units,myWin)
        #Check what was clicked, if anything
        OK = False
        if any(pressed):
            if state == 'waitingForAnotherSelection':
                OK = False
                print('selected=',selected)
                if sum(selected) >= minMustClick:
                    OK = checkForOKclick(mousePos,OKrespZone)
                if OK:
                    state = 'finished'
            if not OK: #didn't click OK. Check whether clicked near a response array item
                topmostCoord, topmostW, topmostH =  calcRespYandBoundingBox( possibleResps, 0) #determine bounds of adjacent option
                topmostX = xStart
                topmostY = topmostCoord
                btmmostCoord, btmmostW, btmmostH =  calcRespYandBoundingBox(possibleResps, len(possibleResps)-1)
                btmmostX = xStart
                btmmostY = btmmostCoord
                w = topmostW
                h = topmostH
                horizBounds = [ xStart-w/2, xStart+w/2 ]
                vertBounds = [btmmostY - h/2, topmostY + h/2]
                #print("horizBounds=",horizBounds," vertBounds=",vertBounds)
                xValid = horizBounds[0] <= mousePos[0] <= horizBounds[1]  #clicked in a valid x-position
                yValid = vertBounds[0] <= mousePos[1] <= vertBounds[1]  #clicked in a valid y-position
                if xValid and yValid: #clicked near a response array item
                    relToBtm = mousePos[1] - vertBounds[0] #mouse coordinates go up from -1 to +1
                    relToLeft = mousePos[0] - horizBounds[0]
                    whichResp = int (relToBtm / h)
                    #change from relToBtm to relative to top
                    whichResp = len(possibleResps) - 1- whichResp
                    if (sum(selected) >= maxCanClick)   &   (selected[whichResp]==0): #Clicked on one that is already selected but already hit max allowed
                        badClickSound.play()
                        mustDeselectMsgStim.draw()
                    else:
                        clickSound.play()
                        selected[whichResp] = -1 * selected[whichResp] + 1 #change 0 to 1 and 1 to 0.   Can't use not because can't sum true/false
                        print('Changed selected #',whichResp,', selected=',selected)
                        print("whichResp from top = ",whichResp, " About to redraw")
                        lastValidClickButtons = deepcopy(pressed) #record which buttons pressed. Have to make copy, otherwise will change when pressd changes later
                        print('lastValidClickButtons=',lastValidClickButtons)
                    #state = 'waitingForAnotherSelection' 
                else: 
                    badClickSound.play()
            for key in event.getKeys(): #only checking keyboard if mouse was clicked, hoping to improve performance
                key = key.upper()
                if key in ['ESCAPE']:
                    expStop = True
                    #noResponseYet = False
   
   print('Returning with selected=',selected,' expStop=',expStop)
   return selected, expStop
        
def doLineup(myWin,bgColor,myMouse,clickSound,badClickSound,possibleResps,bothSides,leftRightCentral,autopilot):
    expStop = False
    passThisTrial = False
    minMustClick = 2   #len(possibleResps)[2]
    maxCanClick = 9
    selectedAutopilot = [0]*len(responses)
    if not autopilot: #I haven't bothered to make autopilot display the response screen
        OKrespZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=64, units='norm', size=[.5, .5], sf=[0, 0], name='OKrespZone')
        OKtextStim = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color=(-1,-1,-1),alignHoriz='center', alignVert='center',height=.13,units='norm',autoLog=False)
        OKtextStim.setText('OK')
        mustDeselectMsgStim = visual.TextStim(myWin,pos=(0, .5),colorSpace='rgb',color=(-1,-1,-1),alignHoriz='center', alignVert='center',height=.13,units='norm',autoLog=False)
        mustDeselectMsgStim.setText('You\'ve already selected the maximum. You must deselect an author in order to select another.')
        selected, expStop = \
                collectLineupResponses(myWin,bgColor,myMouse,minMustClick,maxCanClick,OKtextStim,OKrespZone,mustDeselectMsgStim,possibleResps,clickSound,badClickSound)

    return expStop,passThisTrial,selected,selectedAutopilot

def setupSoundsForResponse():
    fileName = '406__tictacshutup__click-1-d.wav'
    try:
        clickSound=sound.Sound(fileName)
    except:
        print('Could not load the desired click sound file, instead using manually created inferior click')
        try:
            clickSound=sound.Sound('D',octave=3, sampleRate=22050, secs=0.015, bits=8)
        except:
            clickSound = None
            print('Could not create a click sound for typing feedback')
    try:
        badKeySound = sound.Sound('A',octave=5, sampleRate=22050, secs=0.08, bits=8)
    except:
        badKeySound = None
        print('Could not create an invalid key sound for typing feedback')
        
    return clickSound, badKeySound

if __name__=='__main__':  #Running this file directly, must want to test functions in this file
    from psychopy import monitors
    monitorname = 'testmonitor'
    mon = monitors.Monitor(monitorname,width=40.5, distance=57)
    windowUnits = 'deg' #purely to make sure lineup array still works when windowUnits are something different from norm units
    bgColor = [-.7,-.7,-.7] 
    myWin = visual.Window(monitor=mon,colorSpace='rgb',color=bgColor,units=windowUnits)
    #myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor

    logging.console.setLevel(logging.WARNING)
    autopilot = False
    clickSound, badClickSound = setupSoundsForResponse()
    alphabet = list(string.ascii_uppercase)
    possibleResps = alphabet
    #possibleResps.remove('C'); possibleResps.remove('V') #per Goodbourn & Holcombe, including backwards-ltrs experiments
    myWin.flip()
    passThisTrial = False
    myMouse = event.Mouse()

    #Do vertical lineups
    responseDebug=False; responses = list(); responsesAutopilot = list();
    expStop = False
    
    bothSides = True
    leftRightFirst = False
    expStop,passThisTrial,selected,selectedAutopilot = \
                doLineup(myWin, bgColor,myMouse, clickSound, badClickSound, possibleResps, bothSides, leftRightFirst, autopilot)

    print('expStop=',expStop,' passThisTrial=',passThisTrial,' selected=',selected, ' selectedAutopilot =', selectedAutopilot)
    
    print('Finished') 