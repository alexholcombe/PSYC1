from __future__ import print_function, division
from psychopy import event, sound, logging
from psychopy import visual, event, sound, tools, core
import numpy as np
import string
from math import floor, ceil
from copy import deepcopy

def calcXYstartWidthHeightSpacing(namesPerColumn, possibleResps):
    numColumns = ceil( len(possibleResps) / namesPerColumn )
    xStart = -.95
    screenHeight = 2.0 #because screen is 2.0 norm units high
    usableScreenHeight = screenHeight - .07 #Otherwise bottom author will be centered on bottom
    spacingCtrToCtrY = usableScreenHeight / namesPerColumn 
    spacingCtrToCtrX = (xStart*-1 - xStart) / numColumns
    charHeight = spacingCtrToCtrY/2
    yStart = 1-charHeight/2 #top , to bottom
    makeWayForInstructions = True
    if makeWayForInstructions:
        yStart -= .2
        
    return xStart, yStart, spacingCtrToCtrX, spacingCtrToCtrY

def calcWhichClicked(namesPerColumn,possibleResps,x,y):
    #Go through every box, check if coordinates inside it
    foundOne = False
    which = -999
    i  = 0
    while (not foundOne) and i < len(possibleResps):
        xCtr,yCtr,boxWidth,boxHeight = calcRespXYandBoundingBox(namesPerColumn,possibleResps, i)
        l = xCtr - boxWidth/2.
        r = xCtr + boxWidth/2.
        t = yCtr + boxHeight/2.
        b = yCtr - boxHeight/2.
        if x >= l and x <= r:
            if y >= b and y <= t:
                foundOne = True
                which = i
        i += 1
    return foundOne, which

alignTextOption = 'left'

def calcRespXYandBoundingBox(namesPerColumn,possibleResps, i):
    column = floor( i / namesPerColumn )
    row = i % namesPerColumn
    xStart, yStart, spacingCtrToCtrX, spacingCtrToCtrY = calcXYstartWidthHeightSpacing(namesPerColumn, possibleResps)
    incrementX = column * spacingCtrToCtrX
    x = xStart + incrementX
    incrementY = row*spacingCtrToCtrY
    incrementY*= -1 #go down from top
    y = yStart + incrementY
    boxWidth = .2 #0.1
    boxHeight = spacingCtrToCtrY
    if alignTextOption == 'left':
        x= x+boxWidth/2    
    return x,y, boxWidth, boxHeight

#In the first instance want to create all the textStims,
#later will just draw one 
def drawRespOption(myWin,bgColor,xStart,namesPerColumn,possibleResps,color,drawBoundingBox,relativeSize,authorStims,i):
        #relativeSize multiplied by standard size to get desired size
        x, y, w, h = calcRespXYandBoundingBox( namesPerColumn,possibleResps, i )
        if drawBoundingBox:
            boundingBox = visual.Rect(myWin,width=w,height=h, pos=(x,y), units='norm')
            boundingBox.draw() 
            
        option = authorStims[i]
        option.setText(possibleResps[i])
        option.setColor(color)
        option.pos = (x-w/2, y)
        option.draw()
            
def drawAllRespOptions(myWin,bgColor,xStart,namesPerColumn,possibleResps,color,drawBoundingBox,relativeSize):
    #relativeSize multiplied by standard size to get desired size
    authorStims = list()
    for i in range(len(possibleResps)):
        x, y, w, h = calcRespXYandBoundingBox( namesPerColumn,possibleResps, i )
        option = visual.TextStim(myWin,colorSpace='rgb',color=color,alignText=alignTextOption, anchorVert='center',
                                                                height=h*relativeSize,units='norm',autoLog=False)
        option.setText(possibleResps[i])
        option.pos = (x-w/2, y)
        option.draw()
        authorStims.append(option)
        if drawBoundingBox:
            boundingBox = visual.Rect(myWin,width=w,height=h, pos=(x,y), units='norm')
            boundingBox.draw()            
    return authorStims
     
def drawResponseArray(myWin,bgColor,xStart,namesPerColumn,possibleResps,selected,selectedColor,todraw,authorStims,firsttime):
    '''selected indicated whether each is selected or not
    possibleResps is array of all the authors to populate the screen with.
    '''
    numResps = len(possibleResps)
    dimRGB = -.3
    drawBoundingBox = False #to debug to visualise response regions, make True, but slows thigns down
    relativeHeight = .28
    if firsttime:
        authorStims = drawAllRespOptions(myWin,bgColor,xStart,namesPerColumn,possibleResps,(1,1,1),drawBoundingBox,relativeHeight)
    myWin.flip()
    #Draw it vertically, from top to bottom, and left to right
    for i in range(len(possibleResps)):
        if todraw[i]: #only draw those that need drawing, otherwise this code takes too long
            if selected[i]:
                color = selectedColor
            else: 
                color = (1,1,1)
            drawRespOption(myWin,bgColor,xStart,namesPerColumn,possibleResps,color,drawBoundingBox,relativeHeight,authorStims,i)
    return authorStims

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

def collectLineupResponses(myWin,bgColor,myMouse,timeLimit,minMustClick,maxCanClick,instructionStim,OKtextStim,OKrespZone,continueTextStim,mustDeselectMsgStim,possibleResps,clickSound,badClickSound):
   minMustClick = round(minMustClick); 
   myMouse.clickReset()
   state = 'waitingForAnotherSelection' 
   #waitingForAnotherSelection means Finished is  not on the screen, so must click a lineup item
   expStop = False;
   earlyOut = False #so I don't have to click so many authors when trying out the real experiment
   successiveBadClicks = 0; successiveBadClicksLimit = 4
   firstTimeHitMax = True
   xStart = -.7
   timelimitClock = core.Clock(); timedout= False
   #Calculate how many names in a column
   namesPerColumn = 15
   numColumns = len(possibleResps) / namesPerColumn
   print('numColumns = ',numColumns)
   #Need to maintain a list of selected. Draw those in another color
   selected = [0] * len(possibleResps)
   selectedColor = (1,1,-.5)
   authorStims = list()
   #redraw indicates for each option whether it is time to redraw it. 
   todraw = [1] * len(possibleResps) #Set all to true initially so that initial draw is done
   authorStims = drawResponseArray(myWin,bgColor,xStart,namesPerColumn,possibleResps,selected,selectedColor,todraw,authorStims,firsttime=True)
   #todraw = [0] * len(possibleResps) #Set all to false
   while state != 'finished' and not expStop and not earlyOut and not successiveBadClicks == successiveBadClicksLimit and not timedout:
        #draw everything corresponding to this state
        #draw selecteds in selectedColor, remainder in white
        #print('state = ',state)
        authorStims = drawResponseArray(myWin,bgColor,xStart,namesPerColumn,possibleResps,selected,selectedColor,todraw,authorStims,firsttime=False)
        if (sum(selected) >= maxCanClick): #hit max allowed
                if firstTimeHitMax:
                    firstTimeHitMax = False
                else:
                    mustDeselectMsgStim.draw()
        instructionStim.draw()
        if any(selected) and sum(selected) < maxCanClick:
            continueTextStim.draw()
        #todraw =  [0] * len(possibleResps) #set all to false again
        if state == 'waitingForAnotherSelection':            
            #assume half are authors, therefore when have clicked half, have option to finish
            #print('Summing selected, ',selected, ' minMustClick=',minMustClick)
            if sum(selected) >= minMustClick:
                #print('drawing OKrespZone')
                OKrespZone.draw()
                OKtextStim.draw()
        myWin.flip()

        #Poll keyboard and mouse
        #Used to use pressed,times = myMouse.getPressed(getTime=True) because it's supposed to return all presses since last call to clickReset. But, doesn't seem to work. So, now loop
        #If getTime=True (False by default) then getPressed will return all buttons that have been pressed since the last call to mouse.clickReset as well as their time stamps:
        #pressed,times = myMouse.getPressed(getTime=True)
        #Avoid double-clicking problem by not counting as pressed if happened immediately after click events were cleared.
        pressed = [0,0,0]
        timeSinceLast = 0
        doubleClickingGuard = .05
        while not expStop and not earlyOut and not pressed[0] or timeSinceLast < doubleClickingGuard:  #0 is left (normal) click  #any(pressed): #wait until pressed
            pressed, times = myMouse.getPressed(getTime=True)
            timeSinceLast = times[0]
            key = event.getKeys(keyList=['z'], modifiers=True) #secret key is shift ctrl Z
            if key: #z must have been pressed
                modifiers = key[0][1]
                if modifiers['shift'] and modifiers['ctrl']: #secret key is shift-ctrl-Z
                    expStop = True
                if modifiers['shift'] and modifiers['capslock']: #secret continue key is shift caplocks z
                    #print('modifiers=',modifiers)
                    earlyOut = True
        mousePosRaw = myMouse.getPos()
        #print('timeSinceLast=',timeSinceLast)

        event.clearEvents(); myMouse.clickReset()  #Because sometimes I'd click and it both selected and deselected, as if clicked twice
        mousePos = convertXYtoNormUnits(mousePosRaw,myWin.units,myWin)
        #print('myWin.units=',myWin.units,'mousePosRaw=',mousePosRaw,'mousePos=',mousePos)
        #Check what was clicked, if anything
        OK = False
        if not expStop and not earlyOut and any(pressed):
            #print('pressed=',pressed)
            if state == 'waitingForAnotherSelection':
                OK = False
                #print('selected=',selected)
                if sum(selected) >= minMustClick:
                    OK = checkForOKclick(mousePos,OKrespZone)
                if OK:
                    state = 'finished'
            if not OK: #didn't click OK. Check whether clicked near a response array item
                #First calculate the entire array of response regions and see if falls within that
                clickedAnOption, which = calcWhichClicked(namesPerColumn,possibleResps,mousePos[0],mousePos[1])
                #print("clickedAnOption=",clickedAnOption," which=",which)
                if not clickedAnOption:
                        if badClickSound is not None:
                            badClickSound.play()
                        successiveBadClicks += 1
                else: #clickedAnOption == TRUE
                    successiveBadClicks = 0
                    if (sum(selected) >= maxCanClick)   &   (selected[which]==0): #Clicked on one that is already selected but already hit max allowed
                        if firstTimeHitMax:
                            pass
                        else:
                            if badClickSound is not None:
                                badClickSound.play()
                            mustDeselectMsgStim.draw()
                    else:
                        if clickSound is not None:
                            clickSound.play()
                        selected[which] = -1 * selected[which] + 1 #change 0 to 1 and 1 to 0.   Can't use not because can't sum true/false
                        todraw[which] = 1
                        #print('Changed selected #',which,', selected=',selected)
                        #print("which clicked = ",which, " About to redraw")
                        lastValidClickButtons = deepcopy(pressed) #record which buttons pressed. Have to make copy, otherwise will change when pressd changes later
        if timelimitClock.getTime() > timeLimit:
            timedout = True
   #print('Returning with selected=',selected,' expStop=',expStop)
   return selected, expStop, timedout
        

def doAuthorLineup(myWin,bgColor,myMouse,clickSound,badClickSound,possibleResps,autopilot):
    expStop = False
    minMustClick = 10# len(possibleResps) / 2 -1
    maxCanClick = len(possibleResps) / 2 +1
    print('minMustClick=',minMustClick, 'maxCanClick=',maxCanClick)
    selectedAutopilot = [0]*len(possibleResps);  selectedAutopilot[0]=1
    if autopilot: #I haven't bothered to make autopilot display the response screen
        selected = [0]*len(possibleResps) #won't be used anyway but have to give it a value
    else:
        OKrespZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=256, color=[1,1,1], units='norm', size=[2, .2], sf=[0, 0], pos=(0,.88), name='OKrespZone')
        OKtextStim = visual.TextStim(myWin,pos=(0, .88),colorSpace='rgb',color=(.5,-1,-1),alignText='center', anchorVert='center',height=.10,units='norm',autoLog=False)
        OKtextStim.setText('Click here if finished')
        continueTextStim = visual.TextStim(myWin,pos=(-.85, .88),colorSpace='rgb',color=(1,1,1),alignText='center', anchorVert='center',height=.06,units='norm',autoLog=False)
        continueTextStim.setText('Click another!')
        instructionStim = visual.TextStim(myWin,pos=(-.95, .95),colorSpace='rgb',color=(1,1,1),alignText='left', anchorVert='center',
                                        height=.06,wrapWidth=3,font='Times',units='norm',autoLog=False)
        instructionStim.setText('Click on the names that are published authors. When not sure, guess.')
        instructionStim.draw()
        myMouse.setPos([-10,-10]) #setPos([-.5,-.5]) #Seems to have no effect. 
        mustDeselectMsgStim = visual.TextStim(myWin,pos=(0, .5),colorSpace='rgb',color=(1,-.9,-.9),alignText='center', anchorVert='center',height=.13,units='norm',autoLog=False)
        mustDeselectMsgStim.setText('You\'ve already selected half. If you wish to select another, you must unselect an author (by clicking on it) first.')
        timeLimit = 200 #sec
        selected, expStop, timedout = \
                collectLineupResponses(myWin,bgColor,myMouse,timeLimit,minMustClick,maxCanClick,instructionStim,
                                                        OKtextStim,OKrespZone,continueTextStim,mustDeselectMsgStim,possibleResps,clickSound,badClickSound)
    return expStop,timedout,selected,selectedAutopilot

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
    bgColor = [-1,-1,-1] 
    myWin = visual.Window(fullscr=True,monitor=mon,colorSpace='rgb',color=bgColor,units=windowUnits)
    #myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor

    logging.console.setLevel(logging.WARNING)
    autopilot = False
    useSound = False
    clickSound = None; badClickSound = None
    if useSound:
        clickSound, badClickSound = setupSoundsForResponse()
    alphabet = list(string.ascii_uppercase)
    possibleResps = alphabet
    
    sixteen = [ 'V.C. Andrews','Lauren Adamson', 'Eric Amsel', 'Carter Anvari', 'Isaac Asimov', 'Margaret Atwood','Russell Banks', 'David Baldacci', 'Carol Berg', 'Pierre Berton', 'Maeve Binchy', 'Judy Blume', 'Dan Brown','Agatha Christie', 'Robertson Davies','Charles Dickens' ]
    #possibleResps.remove('C'); possibleResps.remove('V') #per Goodbourn & Holcombe, including backwards-ltrs experiments
    oneThirtyEight =['Agatha Christie', 'Aimee Dorr', 'Alex Lumsden', 'Alice Munro', 'Alvin Toffler', 'Amy Tan', 'Andrew Greeley', 'Anne Rice', 'Arthur C. Clarke', 'Barbara Cartland', 'Brian Bigelow', 'C.S. Lewis', 'Caleb Lim', 'Carl Corter', 'Carla Grinton', 'Carol Berg', 'Carol Shields', 'Carter Anvari', 'Charles Condie', 'Christopher Barr', 'Christopher Moore', 'Dale Blyth', 'Dan Brown', 'Daniel Quinn', 'Danielle Steel', 'David Baldacci', 'David Perry', 'David Singer', 'Dean Koontz', 'Denise Daniels', 'Devon Chang', 'Diana Gabaldon', 'Diane Cuneo', 'Edward Cornell', 'Elizabeth George', 'Elliot Blass', 'Eric Amsel', 'Erica Jong', 'Frances Fincham', 'Frank Gresham', 'Frank Herbert', 'Frank Kiel', 'Frank Manis', 'Gary Beauchamp', 'George R.R. Martin', 'Geraldine Dawson', 'Harrison Boldt', 'Hilda Borko', 'Hugh Lytton', 'Isaac Asimov', 'Jackie Collins', 'James Clavell', 'James Michener', 'James Morgan', 'Janet Evanovich', 'Janice Taught', 'Jean M. Auel', 'Jeffery Eugenides', 'Jennifer Butterworth', 'Jennifer Marshal', 'John Condry', 'John Grisham', 'John Jakes', 'Judith Krantz', 'Judy Blume', 'Julia Connerty', 'K. Warner Schaie', 'Kate Grenville', 'Kate Pullinger', 'Katherine Carpenter', 'Kirby Kavanagh', 'Lauren Benjamin', 'Laurie King', 'Lena Johns', 'Lilly Jack', "Louis L'Amour", 'Lynn Liben', 'M. Scott Peck', 'Maeve Binchy', 'Margaret Atwood', 'Margaret Laurence', 'Margarita Azmitia', 'Mark Elder', 'Mark Strauss', 'Martin Ford', 'Michael Moore', 'Mimi Hall', 'Miriam Sexton', 'Miriam Toews', 'Mordecai Richler', 'Morton Mendelson', 'Naomi Choy', 'Naomi Klein', 'Noam Chomsky', 'Oscar Barbary', 'Patricia Cornwell', 'Peter Carey', 'Peter Rigg', 'Pierre Berton', 'Pricilla Levy', 'Reed Larson', 'Reuben Baron', 'Richard Passman', 'Robert Emery', 'Robert Fulghum', 'Robert Inness', 'Robert J. Sawyer', 'Robert Jordan', 'Robert Ludlum', 'Robert Siegler', 'Robertson Davies', 'Rohinton Mistry', 'Russell Banks', 'Ryan Gilbertson', 'Ryan Morris', 'S.E. Hinton', 'Samuel Paige', 'Scott Paris', 'Sheryl Green', 'Sidney Sheldon', 'Sophia Martin', 'Sophie Kinsella', 'Stephen Coonts', 'Stephen J. Gould', 'Stephen King', 'Stirling King', 'Sue Grafton', 'Susan Kormer', 'Suzanne Clarkson', 'Thomas Bever', 'Timothy Findley', 'Tom Clancy', 'Tracy Tomes', 'Ursula LeGuin', 'V.C. Andrews', 'W. Patrick Dickson', 'Wayne Johnston', 'Wayson Choy']
    oneThirtyFive = oneThirtyEight[0:-3]
    possibleResps = oneThirtyFive #oneThirtyEight #sixteen
    print('num authors = ',len(possibleResps))
    print('oneThirtyFive=',oneThirtyFive)
    myWin.flip()
    myMouse = event.Mouse(win=myWin)
    
    expStop,timedout,selected,selectedAutopilot = \
                doAuthorLineup(myWin, bgColor,myMouse, clickSound, badClickSound, possibleResps, autopilot)

    print('Names of selected=',end='')
    for i in range(len(selected)):
        if selected[i]:
            print(possibleResps[i],end=',')
    print('')
    print('expStop=',expStop,' timedout=', timedout) #'' selectedAutopilot =', selectedAutopilot)
    print('Finished') 
