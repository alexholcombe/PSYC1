from __future__ import division
from psychopy import visual, event
import numpy as np

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
#mousePos = convertXYtoNormUnits(mousePosRaw,myWin.units,myWin)


def doParticipantInformationStatement(img1filename, img2filename, myWin, myMouse, exportImages):
    
    #In theory can override the window units for each thing drawn, but it seems like this could cause the mouse to have different units
    originalUnits =  myWin.units
    myWin.setUnits('norm')
    #if myWin.units != "norm":
    #    print('Error! doParticipantInformationStatement expects window units to be "norm"')
    #Display multiple pages side by side
    PISp1 = visual.ImageStim(myWin, image=img1filename, pos=(-.5,0), units='norm')
    PISp2 = visual.ImageStim(myWin, image=img2filename, pos=(.5,0), units='norm')
    #From the aspect ratio of the images, I should be able to scale their size into norm units that will fit.
    PISp1.size=(1,2)
    PISp2.size=(1,2)

    #Create OK clicking area and message
    OKpos = (-.2,-.92)
    OKrespZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=256, color=[1,.5,.5], units='norm', size=[2.3, .2], sf=[0, 0], pos=OKpos, name='OKrespZone')
    OKtextStim = visual.TextStim(myWin,pos=OKpos,colorSpace='rgb',color=(.5,-1,-1),alignText='center', anchorVert='center',height=.07,units='norm',autoLog=False)
    OKtextStim.setText('Please read and then CLICK HERE to continue')

    myMouse.setPos( (-.5, -.8) ) #Bizarrely, while the documentatoin it says 0,0 is the center and units are the same as the window, I've found that 0,0 is the top right and negative means down and left
    firstTime = True
    clickedContinue = False
    secretKeyPressed = False
    while not secretKeyPressed and not clickedContinue:
        key = event.getKeys(keyList=['z'], modifiers=True) #secret key is shift ctrl Z
        if key: #z must have been pressed
            modifiers = key[0][1]
            if modifiers['shift'] and modifiers['ctrl']: #secret key is shift-ctrl-Z
                secretKeyPressed = True
        #if key[0][0] == 'z' and key[0][1]['shift'] and key[0][1]['ctrl']:
        PISp1.draw()
        PISp2.draw()
        OKrespZone.draw()
        OKtextStim.draw()
        mousePos = myMouse.getPos()
        #event.clearEvents(); myMouse.clickReset()  #Because sometimes I'd click once on my laptop and it both selected and deselected, as if clicked twice
        #print('myWin.units=',myWin.units,'mousePosRaw=',mousePosRaw,'mousePos=',mousePos)
        pressed, times = myMouse.getPressed(getTime=True)
        if pressed[0] and OKrespZone.contains(mousePos):
            clickedContinue = True
            if firstTime and exportImages and clickedContinue:
                myWin.getMovieFrame() #I cant explain why another getMovieFrame, and core.wait is needed
                myWin.saveMovieFrames('PIS.png') #mov not currently supported 
                firstTime = False
        myWin.flip()
    myWin.setUnits(originalUnits)
    return clickedContinue
#######################################################################################################################

def doConsentForm(imgFilename, subjectName, myWin, myMouse, exportImages):
    #do Consent form
    #In theory can override the window units for each thing drawn, but it seems like this could cause the mouse to have different units
    originalUnits =  myWin.units
    myWin.setUnits('norm')
    OKpos = (-.2,-.92)
    OKrespZone = visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=256, color=[1,.5,.5], units='norm', size=[2.3, .2], sf=[0, 0], pos=OKpos, name='OKrespZone')
    OKtextStim = visual.TextStim(myWin,pos=OKpos,colorSpace='rgb',color=(.5,-1,-1),alignText='center', anchorVert='center',height=.07,units='norm',autoLog=False)
    OKtextStim.setText('CLICK HERE to continue')
    
    consentImage = visual.ImageStim(myWin, image=imgFilename, pos=(0,0), units='norm')
    consentImage.size=(1.1,2)
    subjectPos = (-.45,.37)
    subjectTextStim = visual.TextStim(myWin,pos=subjectPos,colorSpace='rgb',color=(-1,-1,-1),alignText='center', anchorVert='center',height=.04,units='norm',autoLog=False,
                                                            text=subjectName)
    
    choiceTextColor = (-1,-1,-1)
    choiceTextSz = .05
    checkmarkText = u"\u2713" #checkmark
    
    #For each box, need: pos, textStimY, respZoneY, checkmark status, checkmarkStim. List of dictionaries a good way to do this.
    #First make list of properties for each one
    names=list(['Yconsent','Nconsent','YshareData','NshareData'])
    posList = list(); textList = list(); checkedList = list(); excludedPartner = list()
    hOffset = np.array([.3,0]) 
    posList.append( np.array( [-.2,-.42] )  ) #Y1
    textList.append( "YES" )
    excludedPartner.append( len(excludedPartner) +1 ) #which button, if clicked, means this one has to not be clicked?
    posList.append( posList[0] + hOffset ) #N1
    textList.append( "NO" )
    excludedPartner.append( len(excludedPartner) -1 )
    vOffset =  np.array([0,-.3]) #lower down
    posList.append( posList[0] + vOffset ) #Y2
    textList.append( "YES" )
    excludedPartner.append( len(excludedPartner) +1 )
    posList.append( posList[ len(posList)-1 ] + hOffset )  #N2
    textList.append( "NO" )
    excludedPartner.append( len(excludedPartner) -1 )
    
    #set up list of dictionaries. Each dictionary contains all the characteristics and stimuli associated with  the button
    choiceDicts= list(  )
    for i in range(len(posList)):
        this = {}
        this['textStim'] = \
            visual.TextStim(myWin,pos=posList[i],colorSpace='rgb',color=choiceTextColor,alignText='center', anchorVert='center',height=choiceTextSz,units='norm',text=textList[i],autoLog=False)
        this['respZone'] = \
            visual.GratingStim(myWin, tex="sin", mask="gauss", texRes=256, color=[1,.5,.5], units='norm', size=[.3, .2], sf=[0, 0], pos=posList[i])
        this['checked'] = False
        this['checkmarkStim'] = \
            visual.TextStim(myWin,pos=posList[i]+np.array([.06,0]),colorSpace='rgb',color=choiceTextColor,alignText='right', anchorVert='center',height=choiceTextSz*2,units='norm',
                                    text=checkmarkText,autoLog=False)
        this['name'] = names[i]
        choiceDicts.append(this)
        
    doubleClickingGuard = .05
    secretKeyPressed = False
    clickedOK = False
    firstTime = True
    timeSinceLast = 0
    while not secretKeyPressed and not clickedOK:
        keyAndModifiers = event.getKeys(keyList=['z'], modifiers=True) #secret key is shift-ctrl-Z
        if keyAndModifiers: #z was pressed
            modifiers = keyAndModifiers[0][1]
            if modifiers['shift'] and modifiers['ctrl']: #secret key is shift-ctrl-Z
                secretKeyPressed = True
        consentImage.draw()
        subjectTextStim.draw()
        
        for d in choiceDicts:
            d['respZone'].draw()
            d['textStim'].draw()
            if d['checked']:
                d['checkmarkStim'].draw()
     
        pressed, times = myMouse.getPressed(getTime=True)
        if pressed[0]:
            timeSinceLast = times[0]
            #print('presssed and timeSinceLast=',timeSinceLast)
            event.clearEvents(); myMouse.clickReset()  #Because sometimes I'd click and it both selected and deselected, as if clicked twice
        if timeSinceLast < doubleClickingGuard: #apparently trapped a double-click, or bug masquerading as it, so don't count as pressed
            pressed = [0,0,0]
        mousePos = myMouse.getPos()
        if pressed[0]:
            for idx, d in enumerate(choiceDicts):
                if d['respZone'].contains(mousePos):
                    d['checked'] = not d['checked']
                    if choiceDicts[ excludedPartner[idx] ]['checked']: #check whether excluded partner is true, if so must turn it off
                        choiceDicts[ excludedPartner[idx] ]['checked'] = False
        
        howManyAnswered = 0
        for d in choiceDicts:
            howManyAnswered += d['checked']
    
        if howManyAnswered >1:
            OKtextStim.draw()
            if pressed[0]:
                if OKrespZone.contains(mousePos):
                    clickedOK = True
        myWin.flip()
        if firstTime and exportImages and clickedOK:
             myWin.getMovieFrame() #I cant explain why another getMovieFrame, and core.wait is needed
             myWin.saveMovieFrames('consent.png') #mov not currently supported 
    myWin.setUnits(originalUnits)
    return secretKeyPressed, choiceDicts

if __name__=='__main__':  #Running this file directly, must want to test functions in this file
    #do Participant Information Statement
    # Create a window to draw in
    #psych labs screen is 1920 x 1080, but my program sets it to 1920 x 1080
    subjectName = 'aholcombe'
    exportImages = True
    fullscr=True 
    myWin = visual.Window((1920, 1080), allowGUI=False, winType='pyglet',
                monitor='testMonitor', fullscr=fullscr, units ='norm', screen=0)
    myMouse = event.Mouse(win=myWin, visible=True) #, newPos=(-.5,-.5))
    clickedContinue = doParticipantInformationStatement("PIS2underlined.png", "PIS2underlined_p2.png", myWin, myMouse, exportImages)
    print('clickedContinue=',clickedContinue)
    
    #do consent form
    filename = 'consentForm.png'
    secretKeyPressed, choiceDicts = doConsentForm(filename, subjectName, myWin, myMouse, exportImages)
    for c in choiceDicts:
        print(c['name']," ['checked']=",c['checked'])