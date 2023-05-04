#Alex Holcombe alex.holcombe@sydney.edu.au
#See the github repository for more information: https://github.com/alexholcombe/PSYC1002
from __future__ import print_function, division
from psychopy import monitors, visual, event, data, logging, core, gui
import psychopy.info
useSound = False
if useSound:
    from psychopy import sound
import random, scipy
import numpy as np
from math import atan, log, ceil
import copy, time, datetime, sys, os, string, shutil
#try:
#    from noiseStaircaseHelpers import printStaircase, toStaircase, outOfStaircase, createNoise, plotDataAndPsychometricCurve
#except ImportError:
#    print('Could not import from noiseStaircaseHelpers.py (you need that file to be in the same directory)')
try:
    import stringResponse
except ImportError:
    print('Could not import stringResponse.py (you need that file to be in the same directory)')
#try:
#    import letterLineupResponse
#except ImportError:
#    print('Could not import letterLineupResponse.py (you need that file to be in the same directory)')
try:
    from authorRecognitionLineup import doAuthorLineup
except ImportError:
    print('Could not import authorRecognitionLineup.py (you need that file to be in the same directory)')
print('platform=')
print(sys.platform)

if sys.platform == "win32":  #this means running in PSYC computer labs
    topDir = 'abgdj'
else:
    topDir = '.'
sys.path.append( os.path.join(topDir,'PISandConsentForm') )   #because current working directory ends up being the PSYC1002 grasp folder, NOT the folder with PSYC1002.py in it
try:
    from PISandConsentForm import doParticipantInformationStatement, doConsentForm
except ImportError:
    print('Could not import PISandConsentForm.py (you need that file to be in the same directory)')
try:
    from getpass import getuser
    from socket import gethostname
except ImportError:
    print('ERROR Could not import getpass')

wordEccentricity=  0.9 
tasks=['T1']; task = tasks[0]
#same screen or external screen? Set scrn=0 if one screen. scrn=1 means display stimulus on second screen.
#widthPix, heightPix
quitFinder = False 
autopilot=False
demo=False #False
exportImages= False #quits after one trial
subject=getuser()  #https://stackoverflow.com/a/842096/302378
networkMachineName = gethostname()
#subject = 'abajjjjd8333763' #debug
if autopilot: subject='auto'
cwd = os.getcwd()
print('current working directory =',cwd)
if sys.platform == "win32":  #this means running in PSYC computer labs
    pathToData = 'Submissions'  # os.path.join('..',"Submissions")
else:
    pathToData = 'Submissions'
#if os.path.isdir('.'+os.sep+'Submissions'):
if os.path.isdir(pathToData):
    dataDir='Submissions'
else:
    print('"Submissions" directory does not exist, so saving data in abgdj directory')
    dataDir='abgdj'
    if not os.path.isdir(dataDir):
        print("Error, can't even find the ",dataDir," directory")
        core.quit()
timeDateStart = time.strftime("%d%b%Y_%H-%M-%S", time.localtime()) #used for filename
now = datetime.datetime.now() #used for JSON

showRefreshMisses=True #flicker fixation at refresh rate, to visualize if frames missed
feedback=True 
autoLogging=False
refreshRate = 60
if demo:
   refreshRate = 60.;  #100

numWordsInStream = 1
myFont =  'Arial' # 'Sloan' # 

#Set up the list of experiments, then allocate one to the subject
experimentTypesStim = ['word','letter']  #'digit']
experimentTypesSpatial = ['horiz','vert']
#experimentTypesNumletters
#create dictionary of all combinations
experimentsList = []
#Creating the list of experiments
#Implement the fully factorial part of the design by creating every combination of the following conditions
oneTargetConditions = [False,False,True] #1/3 of trials single-target
for stim in experimentTypesStim:
    if stim == 'word':
        ISIms = 34
    else:
        ISIms = 34
    for spatial in experimentTypesSpatial:
        experimentsList.append( {'numSimultaneousStim': 2, 'stimType':stim, 'flipped':False, 'spatial':spatial, 'ori':0, 'ISIms':ISIms, 'oneTargetConditions':oneTargetConditions} )
#add Tess' experiment to list, making it number 4
experimentsList.append( {'numSimultaneousStim': 2, 'stimType':'word', 'flipped':False, 'spatial':'vert', 'ori':0, 'ISIms':34, 'oneTargetConditions':[False,False,False] } )

seed = int( np.floor( time.time() ) )
random.seed(seed); np.random.seed(seed) #https://stackoverflow.com/a/48056075/302378
import json
otherData= {} #stuff to record in authors data file
otherData.update( {'networkMachineName': networkMachineName} )
#print('otherData=',otherData)
otherData.update( {'datetime':now.isoformat()} )
otherData.update( {'seed':seed} )

experimentNum = 4 #abs(  hash(subject)   ) % len(experimentsList)   #https://stackoverflow.com/a/16008760/302378
knownMachinesForPilot = ['W5FB2LG2','W5FFZKG2','W5FGZKG2','W5FFXKG2','W5FF2LG2','W5FD1LG2','W5FDYKG2','W5B5LG2' ]
if now.day==31 or now.day < 4:  #week 1, before 4 August, piloting
    if networkMachineName in knownMachinesForPilot:
        experimentNum = knownMachinesForPilot.index(networkMachineName)
        experimentNum = experimentNum % len(experimentsList)
        otherData.update({'knownMachinesForPilot.index(networkMachineName)':knownMachinesForPilot.index(networkMachineName)})
#experimentNum = 0
experiment = experimentsList[ experimentNum ]
#print('experiment=',experiment)
otherData.update(experiment)

#Determine stimuli for this participant
if experiment['stimType'] == 'letter':
    stimList =  list(string.ascii_lowercase)
    toRemove = ['d','b','l','i','o','q','p','v','w','x'] #because symmetrical, see rotatedLettersAndSymbols.jpg 
    for ltr in toRemove:
        stimList.remove(ltr)
elif experiment['stimType'] == 'digit':
    stimList = ['0','1','2','3','4','5','6','7','8','9']
elif experiment['stimType'] == 'word':
    stimList = list()
    numStimsWanted = 266
    #read word list
    stimDir = 'inputFiles'
    stimFilename = os.path.join(topDir, stimDir,"BrysbaertNew2009_3ltrWords_don_others_functions_deleted_from_first_266.txt")
    f = open(stimFilename)
    eachLine = f.readlines()
    if len(eachLine) < numStimsWanted:
        print("ERROR file doesn't have as many lines as expected, wanted more words.")
    for l in range(1,numStimsWanted):#skip first, header line, therefore start with line 1
        line = eachLine[l]
        values = line.split() #splits on tabs or whitespaces and trims leading,following including newlines
        word = values[0]
        stimList.append( word )
        print(word,'\t')
#print('stimlist=',stimList)
bgColor = [-.7,-.7,-.7] # [-1,-1,-1]
cueColor = [-.7,-.7,-.7] #originally [1.,1.,1.]
ltrColor = .9 #[.9,.9,.9]# [-.3,-.3,-.3]
cueRadius = 7 #6 deg in Goodbourn & Holcombe
#1920 x 1080 for psyc lab OTC machines
widthPix= 1920 #monitor width in pixels of Agosta  [1280]
heightPix= 1080 #800 #monitor height in pixels [800]
monitorwidth = 57 #38.7 #monitor width in cm [was 38.7]
scrn=0 #0 to use main screen, 1 to use external screen connected to computer
fullscr=True #True to use fullscreen, False to not. Timing probably won't be quite right if fullscreen = False
allowGUI = False
if demo: monitorwidth = 23#18.0
if exportImages:
    widthPix = 600; heightPix = 600
    monitorwidth = 13.0
    fullscr=False; scrn=1
    framesSaved=0
if demo:    
    scrn=1; fullscr=False
    widthPix = 800; heightPix = 600
    monitorname='testMonitor'
    allowGUI = True
viewdist = 57 #50. #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
    
doStaircase = True
checkRefreshEtc = True 
if quitFinder and sys.platform != "win32":  #Don't know how to quitfinder on windows
    import os
    applescript="\'tell application \"Finder\" to quit\'"
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)
    
#set location of stimuli
#letter size 2.5 deg
letterDurMs = 34
ISIms =  experiment['ISIms']
letterDurFrames = int( np.floor(letterDurMs / (1000./refreshRate)) )
cueDurFrames = letterDurFrames
ISIframes = int( np.floor(ISIms / (1000./refreshRate)) )
#have set ISIframes and letterDurFrames to integer that corresponds as close as possible to originally intended ms
rateInfo = 'base total SOA=' + str(round(  (ISIframes + letterDurFrames)*1000./refreshRate, 2)) + ' or ' + str(ISIframes + letterDurFrames) + ' frames, comprising\n'
rateInfo+=  'base ISIframes ='+str(ISIframes)+' or '+str(ISIframes*(1000./refreshRate))+' ms and letterDurFrames ='+str(letterDurFrames)+' or '+str(round( letterDurFrames*(1000./refreshRate), 2))+'ms'
logging.info(rateInfo); #print(rateInfo)
logging.info('current working directory is ' + cwd)

monitorname = 'testmonitor'
waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPix,heightPix) )
units='deg' #'cm'

trialsPerCondition = 30
defaultNoiseLevel = 0
if not demo:
    allowGUI = False

#set up output data file, log file,  copy of program code, and logging
infix = ''
fileName = os.path.join(dataDir, subject + '_' + infix+ timeDateStart)
if not demo and not exportImages:
    dataFile = open(fileName+'.txt', 'w')
    #save copy of this script so no mistaking the version of the code run by this subject
    #saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileName + '.py'    #only works on OSX
    #os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run   #only works on OSX
    thisScriptName = sys.argv[0]
    scriptDestination = os.path.join(fileName + '.py')
    #print('thisScriptName=', thisScriptName, 'scriptDestination=',scriptDestination)
    shutil.copyfile(thisScriptName, scriptDestination)
    logFname = fileName+'.log'
    ppLogF = logging.LogFile(logFname, 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#errors, data and warnings will be sent to this logfile
if demo or exportImages: 
  dataFile = sys.stdout; logF = sys.stdout
  logging.console.setLevel(logging.ERROR)  #only show this level  messages and higher
logging.console.setLevel(logging.ERROR) #DEBUG means set  console to receive nearly all messges, INFO next level, EXP, DATA, WARNING and ERROR 

includeConsentDemographicsAuthor = False #AHdebug True
if includeConsentDemographicsAuthor:
        # require password
        succeeded = False
        attempts = 0
        while attempts < 3 and not succeeded:
                info = {'\n\n\n\nPassword\n\n\n':'', '':''}
                infoDlg = gui.DlgFromDict(dictionary=info, title='Research Report Experiment',
                    tip={'\n\n\n\n\nPassword\n\n\n': 'Famous psychologist'}, 
                    fixed=['']
                )
                word = ''
                if infoDlg.OK:  # this will be True (user hit OK) or False (cancelled)
                    word = info['\n\n\n\nPassword\n\n\n']
                    word = word.upper()
                    if word == 'LOFTUS':
                        succeeded = True
                    else:
                        print('Password incorrect.')
                else:
                    print('User cancelled')
                    core.quit()
                attempts += 1
        if not succeeded:
            core.quit()
    
def openMyStimWindow(): #make it a function because if do it multiple times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    return myWin
myWin = openMyStimWindow()

if includeConsentDemographicsAuthor:
    myMouse = event.Mouse(visible=True) #the mouse absolutely needs to be reset, it seems, otherwise maybe it returns coordinates in wrong units or with wrong scaling?
    dir = os.path.join(topDir,'PISandConsentForm')
    page1 = os.path.join(dir,'PIS2underlined.png') #"PISandConsentForm/PIS2underlined.png" 
    page2 = os.path.join(dir,'PIS2underlined_p2.png')  #  PISandConsentForm/PIS2underlined_p2.png   
    clickedContinue = doParticipantInformationStatement(page1,page2, myWin, myMouse, exportImages)
    #myMouse = event.Mouse(visible=True) #the mouse absolutely needs to be reset, it seems, otherwise maybe it returns coordinates in wrong units or with wrong scaling?
    page = os.path.join(dir,'consentForm.png') #"PISandConsentForm/'consentForm.png'
    secretKeyPressed, choiceDicts = doConsentForm(page, subject, myWin, myMouse, exportImages)
    for c in choiceDicts:
        print(c['name']," ['checked']=",c['checked'])
        otherData.update(  {   (c['name'],  c['checked'])    } )#add to json data file
    myWin.close() #have to close window to show pop-up to display dlg
    if secretKeyPressed:
        core.quit()
        
    # Collect demographic variables
    # Use a gui.Dlg and so you can avoid labeling the cancel button , but can't avoid showing it
    # This approach gives more control, eg, text color.
    questions = ['What is the first language you learned to read?','What is your age?','Which is your dominant hand for common tasks,\nlike writing, throwing, and brushing your teeth?\n\n',
                         'What is your biological sex?']
    dlg = gui.Dlg(title="PSYC1002", labelButtonOK=u'         OK         ', labelButtonCancel=u'', pos=(200, 400)) # Cancel (decline to answer all)
    dlg.addField(questions[0], choices=[ 'English','Arabic','Pali','Hebrew','Farsi','Chinese','Korean','Japanese','Other','Decline to answer'])
    dlg.addField(questions[1], choices = ['15 or under','16 or 17', '18 or 19', '20 or 21', '22, 23, or 24', '24 to 30', '30 to 50', 'over 50','Decline to answer'])
    dlg.addField(questions[2], choices=['Decline to answer','Left','Right','Neither (able to use both hands equally well)'])
    dlg.addField(questions[3], choices=['Decline to answer','Male','Female','Other'])
    #dlg.addFixedField(label='', initial='', color='', choices=None, tip='') #Just to create some space
    #dlg.addField('Your gender (as listed on birth certificate):', choices=["male", "female"])
    thisInfo = dlg.show()  # you have to call show() for a Dlg (automatic with a DlgFromDict)
    
    demographics = {q: 'Decline to answer (pressed unlabeled cancel button)' for q in questions}  #Assume pressed cancel unless get values
    if dlg.OK:
        print(thisInfo)
        demographics = dict([        (questions[0], thisInfo[0]),   (questions[1], thisInfo[1]),   (questions[2], thisInfo[2]),   (questions[3], thisInfo[3])                ])
    otherData.update(demographics)
    print('otherData=',otherData)
    #end demographics collection

myWin = openMyStimWindow()

if fullscr and not demo and not exportImages:
    runInfo = psychopy.info.RunTimeInfo(
        win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=True, ## True means report on everything 
        userProcsDetailed=True,  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        )
    #print('runInfo='); print(runInfo)
    logging.info(runInfo)
    print('Finished runInfo- which assesses the refresh and processes of this computer') 

if checkRefreshEtc and (not demo) and (myWin.size != [widthPix,heightPix]).any():
    msgWrongResolution = 'Screen apparently NOT the desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels!!'
    logging.error(msgWrongResolution)
    print(msgWrongResolution)

if checkRefreshEtc and (not demo):
    #check screen refresh is what assuming it is ##############################################
    Hzs=list()
    myWin.flip(); myWin.flip();myWin.flip()
    myWin.setRecordFrameIntervals(True) #otherwise myWin.fps won't work
    print('About to measure frame flips') 
    for i in range(50):
        myWin.flip()
        Hzs.append( myWin.fps() )  #varies wildly on successive runs!
    myWin.setRecordFrameIntervals(False)
    # end testing of screen refresh########################################################
    Hzs = np.array( Hzs );     Hz= np.median(Hzs)
    msPerFrame= 1000./Hz
    refreshMsg1= 'Frames per second ~='+ str( np.round(Hz,1) )
    refreshMsg2 = ''
    refreshRateTolerancePct = 3
    pctOff = abs( (np.median(Hzs)-refreshRate) / refreshRate)
    refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
    if refreshRateWrong:
        refreshMsg1 += ' BUT'
        refreshMsg1 += ' program assumes ' + str(refreshRate)
        refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
    else:
        refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
    if refreshRateWrong:
        logging.error(refreshMsg1+refreshMsg2)
    else: logging.info(refreshMsg1+refreshMsg2)
logging.flush()

def calcStimPos(trial,i):
    #i is position index, either 0, 1, or 2.  Just 0 or 1 unless Humby experimnet with 3 positions
    global experiment
    amountNeedToCompensateForRotation = 0.08 #when text rotated by 90 deg, not centered at x-coord any more
    if trial['horizVert']:            # bottom,           top
        if experiment['ori'] == 90:
            x = amountNeedToCompensateForRotation
        elif experiment['ori'] == -90:
            x = -amountNeedToCompensateForRotation
        elif experiment['ori'] == 0:
            x = 0
        positions = [ [x,-wordEccentricity], [x,wordEccentricity] ]
    else:                                   #left      ,        right 
        positions = [ [-wordEccentricity,0], [wordEccentricity,0] ]
    #insert 3rd position of 3 stimuli
    if experiment['numSimultaneousStim'] == 3:
        positions.insert( 1, [0,0] )  #put 0,0 into middle (index 1) of list, so will present a letter at fovea
    else:
        positions.append( [0,0] ) #For two-stimuli experiments, will draw third noise in middle
    return positions[i]

stimuliStream1 = list()
stimuliStream2 = list() #used for second, simultaneous RSVP stream
stimuliStream3 = list()
checkAlignment = False
if checkAlignment:
    alignmentCheck = visual.Line(myWin, start=(-1, 0), end=(1, 0), fillColor = (0,1,0)) 

def calcAndPredrawStimuli(stimList,i,j,k):
   global stimuliStream1, stimuliStream2, stimuliStream3
   del stimuliStream1[:]
   del stimuliStream2[:]
   del stimuliStream3[:] #only used for Humby's experiment
   #draw the stimuli that will be used on this trial, the first numWordsInStream of the shuffled list
   indices = [i,j,k]
   textStimuli = list()
   for i in range(3):
        #
        stim = visual.TextStim(myWin, text = stimList[indices[i]],
                                           height=ltrHeight,font=myFont,colorSpace='rgb',color=ltrColor, 
                                           ori=experiment['ori'],alignHoriz='center',alignVert='center',units='deg',autoLog=autoLogging)
        textStimuli.append( stim )
        
   stimuliStream1.append( textStimuli[0] )
   stimuliStream2.append( textStimuli[1] )
   stimuliStream3.append( textStimuli[2] )
#end calcAndPredrawStimuli
   
#create click sound for keyboard
clickSound = None
if useSound:
    try:
        clickSound=sound.Sound('406__tictacshutup__click-1-d.wav')
    except: #in case file missing, create inferiro click manually
        logging.warn('Could not load the desired click sound file, instead using manually created inferior click')
        clickSound=sound.Sound('D',octave=4, sampleRate=22050, secs=0.015, bits=8)
badSound = None
if useSound:
    try:
        badSound = sound.Sound('A',octave=5, sampleRate=22050, secs=0.08, bits=8)
    except:
        badSound = None
        print('Could not create an invalid key sound for typing feedback')

if showRefreshMisses:
    fixSizePix = 36 #2.6  #make fixation bigger so flicker more conspicuous
else: fixSizePix = 36
fixColor = (1,-.5,-.5)
if exportImages: fixColor= [0,0,0]
fixationPoint= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=fixColor,size=4,units='pix',autoLog=autoLogging)
taskInstructionString1 = 'Which side you are asked to report varies.\n Be sure to report the side asked for.'
taskInstructionString2 = 'Sometimes you may not be able to see any ' + experiment['stimType'] + 's.\nIn those cases, guess.\n\nPlease do your best!'
taskInstructionPos = (0,0)
taskInstructionStim1 = visual.TextStim(myWin,pos=taskInstructionPos,colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.5,units='deg',autoLog=autoLogging)
taskInstructionStim2 = visual.TextStim(myWin,pos=taskInstructionPos,colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.5,units='deg',autoLog=autoLogging)
taskInstructionStim1.setText(taskInstructionString1,log=False)
taskInstructionStim2.setText(taskInstructionString2,log=False)
trialInstructionString = 'Keep your eyes on the red dot'
trialInstructionPos = (0,1)
trialInstructionStim = visual.TextStim(myWin,pos=trialInstructionPos,colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.5,units='deg',autoLog=autoLogging)
trialInstructionStim.setText(trialInstructionString,log=False)
respPromptStim1 = visual.TextStim(myWin,pos=(0, -.9),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.5,units='deg',autoLog=autoLogging)
respPromptStim2 = visual.TextStim(myWin,colorSpace='rgb',color=(.8,.8,0),wrapWidth=999,alignHoriz='center', alignVert='center',height=.09,units='norm',autoLog=autoLogging)
respPromptStim3 = visual.TextStim(myWin,colorSpace='rgb',color=(.8,.8,0),wrapWidth=999,alignHoriz='center', alignVert='center',height=.09,units='norm',autoLog=autoLogging)

#promptLtrsStimuli = list()
#for s in stimList:
#    respPromptStim2 = visual.TextStim(myWin,colorSpace='rgb',color=(.8,.8,0),wrapWidth=999,alignHoriz='center', alignVert='center',height=1.2,units='deg',autoLog=autoLogging)
    
promptText =''  #Show entire array of possible responses to subject, unless words
for s in stimList:
    promptText += s + '   '
respPromptStim2.setText(promptText); respPromptStim3.setText(promptText)
if experiment['stimType']=='word' or experiment['numSimultaneousStim']==3:
    respPromptStim2.setText(''); respPromptStim3.setText(''); 
respPromptStim2.ori = experiment['ori']; respPromptStim3.ori = experiment['ori']
if experiment['flipped']:
    respPromptStim2.flipHoriz = True; respPromptStim3.flipHoriz = True
print('promptText=',promptText)

acceptTextStim = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.05,units='norm',autoLog=autoLogging)
acceptTextStim.setText('Hit ENTER to accept. Backspace to edit')
respStim = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=(.8,.8,0),alignHoriz='center', alignVert='center',height=1,units='deg',
                                            ori =  experiment['ori'] , autoLog=autoLogging)
#clickSound, badSound = stringResponse.setupSoundsForResponse()
requireAcceptance = False
nextText = visual.TextStim(myWin,pos=(0, .1),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(0,.2),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
screenshot= False; screenshotDone = False
conditionsList = []
if experiment['spatial'] == 'vert':
    horizVert = True
else: horizVert = False
#SETTING THE CONDITIONS
#Implement the fully factorial part of the design by creating every combination of the following conditions
for rightResponseFirst in [False,True]:
  for trialInstructionPos in [(0,-1), (0,1)]: #half of trials instruction to fixate above fixation, half of trials below
    for oneTarget in experiment['oneTargetConditions']:
        conditionsList.append( {'rightResponseFirst':rightResponseFirst, 'leftStreamFlip':experiment['flipped'], 'trialInstructionPos':trialInstructionPos,
                                               'oneTarget':oneTarget, 'horizVert':horizVert, 'rightStreamFlip':experiment['flipped'], 'probe':'both', 'ISIframes':ISIframes} )

trials = data.TrialHandler(conditionsList,trialsPerCondition) #method of constant stimuli

def numberToLetter(number): #0 = A, 25 = Z
    #if it's not really a letter, return @
    if number < 0 or number > 25:
        return ('@')
    else: #it's probably a letter
        try:
            return chr( ord('A')+number )
        except:
            return('@')

def letterToNumber(letter): #A = 0, Z = 25
    #if it's not really a letter, return -999
    #HOW CAN I GENERICALLY TEST FOR LENGTH. EVEN IN CASE OF A NUMBER THAT' SNOT PART OF AN ARRAY?
    try:
        #if len(letter) > 1:
        #    return (-999)
        if letter < 'A' or letter > 'Z':
            return (-999)
        else: #it's a letter
            return ord(letter)-ord('A')
    except:
        return (-999)

def stimToIdx(stim,stimList):
    #if it's not in the list of stimuli, return -999
    try:
        #http://stackoverflow.com/questions/7102050/how-can-i-get-a-python-generator-to-return-none-rather-than-stopiteration
        firstMatchIdx = next((i for i, val in enumerate(stimList) if val.upper()==stim), None) #return i (index) unless no matches, in which case return None
        #print('Looked for ',word,' in ',stimList,'\nfirstMatchIdx =',firstMatchIdx)
        return firstMatchIdx
    except:
        print('Unexpected error in stimToIdx with stim=',stim)
        return (None)
        
maxNumRespsWanted = 3

#print header for data file
print('experimentPhase\ttrialnum\tsubject\ttask\toneTarget\t',file=dataFile,end='')
print('noisePercent\tISIframes\tltrColorThis\tleftStreamFlip\trightStreamFlip\trightResponseFirst\tprobe\ttrialInstructionPos\t',end='',file=dataFile)
    
for i in range( experiment['numSimultaneousStim'] ): #range(maxNumRespsWanted):
   dataFile.write('responseOrder'+str(i)+'\t')
   dataFile.write('answer'+str(i)+'\t')
   dataFile.write('response'+str(i)+'\t')
   dataFile.write('correct'+str(i)+'\t')
#   dataFile.write('responsePosRelative'+str(i)+'\t')
print('timingBlips',file=dataFile)
#end of header

def oneFrameOfStim( n,cue,seq1,seq2,seq3,cueDurFrames,letterDurFrames,thisTrial,textStimuliStream1,textStimuliStream2,textStimuliStream3,
                                       ltrColorThis,noise,proportnNoise,allFieldCoords,numNoiseDots): 
#defining a function to draw each frame of stim.
#seq1 is an array of indices corresponding to the appropriate pre-drawn stimulus, contained in textStimuli
  
  SOAframes = letterDurFrames+thisTrial['ISIframes']
  cueFrames = 0 
  stimN = int( np.floor(n/SOAframes) )
  frameOfThisLetter = n % SOAframes #every SOAframes, new letter
  timeToShowStim = frameOfThisLetter < letterDurFrames #if true, it's not time for the blank ISI.  it's still time to draw the letter
  #print 'n=',n,' SOAframes=',SOAframes, ' letterDurFrames=', letterDurFrames, ' (n % SOAframes) =', (n % SOAframes)  #DEBUGOFF
  if seq1 is not None:
    thisStimIdx = seq1[stimN] #which letter, from A to Z (1 to 26), should be shown?
  if seq2 is not None:
    thisStim2Idx = seq2[stimN]
  if seq3 is not None:
    thisStim3idx = seq3[stimN]
  #so that any timing problems occur just as often for every frame, always draw the letter and the cue, but simply draw it in the bgColor when it's not meant to be on
  cue.setLineColor( bgColor )
  if type(cueFrames) not in [tuple,list,np.ndarray]: #scalar. But need collection to do loop based on it
    cueFrames = list([cueFrames])
  for cueFrame in cueFrames: #check whether it's time for any cue
      if n>=cueFrame and n<cueFrame+cueDurFrames:
         cue.setLineColor( cueColor )
  if checkAlignment:
      alignmentCheck.setPos( calcStimPos(thisTrial,0) ); alignmentCheck.draw()
      alignmentCheck.setPos( calcStimPos(thisTrial,1) ); alignmentCheck.draw()
  if timeToShowStim: #time to show critical stimulus
        #print('thisStimIdx=',thisStimIdx, ' seq1 = ', seq1, ' stimN=',stimN)
        if seq1 is not None:
            stimuliStream1[thisStimIdx].setPos( calcStimPos(thisTrial,0) )
            stimuliStream1[thisStimIdx].setColor( ltrColorThis )
        if seq2 is not None:
            stimuliStream2[thisStim2Idx].setColor( ltrColorThis )
            stimuliStream2[thisStim2Idx].setPos( calcStimPos(thisTrial,1) )
        if seq3 is not None:
            stimuliStream3[thisStim2Idx].setColor( ltrColorThis )
            stimuliStream3[thisStim2Idx].setPos( calcStimPos(thisTrial,2) )
  else:
    if seq1 is not None:
        stimuliStream1[thisStimIdx].setColor( bgColor )
    if seq2 is not None:
        stimuliStream2[thisStim2Idx].setColor( bgColor )
    if seq3 is not None:
        stimuliStream3[thisStim2Idx].setColor( bgColor )
  if seq1 is not None:
      stimuliStream1[thisStimIdx].flipHoriz = thisTrial['leftStreamFlip']
      stimuliStream1[thisStimIdx].draw()
  if seq2 is not None:
      stimuliStream2[thisStim2Idx].flipHoriz = thisTrial['rightStreamFlip']
      stimuliStream2[thisStim2Idx].draw()
  if seq3 is not None:
    stimuliStream3[thisStim2Idx].draw()
  cue.draw()
  refreshNoise = False #Not recommended because takes longer than a frame, even to shuffle apparently. Or may be setXYs step
  if proportnNoise>0 and refreshNoise: 
    if frameOfThisLetter ==0: 
        np.random.shuffle(allFieldCoords) 
        dotCoords = allFieldCoords[0:numNoiseDots]
        noise.setXYs(dotCoords)
  if proportnNoise>0:
    noise.draw()
  return True
# #######End of function definition that displays the stimuli!!!! #####################################
#############################################################################################################################
  thisProbe = thisTrial['probe']
  #if thisProbe=='both':
  #  numRespsWanted = 1
  #else: numRespsWanted = 0
  
cue = visual.Circle(myWin, 
     radius=cueRadius,#Martini used circles with diameter of 12 deg
     lineColorSpace = 'rgb',
     lineColor=bgColor,
     lineWidth=4.0, #in pixels. Was thinner (2 pixels) in letter AB experiments
     units = 'deg',
     fillColorSpace = 'rgb',
     fillColor=None, #beware, with convex shapes fill colors don't work
     pos= [0,0], #the anchor (rotation and vertices are position with respect to this)
     interpolate=True,
     autoLog=False)#this stim changes too much for autologging to be useful
     
ltrHeight =  0.7 #Martini letters were 2.5deg high
#All noise dot coordinates ultimately in pixels, so can specify each dot is one pixel 
noiseFieldWidthDeg=ltrHeight *1.0
noiseFieldWidthPix = int( round( noiseFieldWidthDeg*pixelperdegree ) )

def timingCheckAndLog(ts,trialN):
    #check for timing problems and log them
    #ts is a list of the times of the clock after each frame
    interframeIntervs = np.diff(ts)*1000
    #print '   interframe intervs were ',around(interframeIntervs,1) #DEBUGOFF
    frameTimeTolerance=.3 #proportion longer than refreshRate that will not count as a miss
    longFrameLimit = np.round(1000/refreshRate*(1.0+frameTimeTolerance),2)
    idxsInterframeLong = np.where( interframeIntervs > longFrameLimit ) [0] #frames that exceeded 150% of expected duration
    numCasesInterframeLong = len( idxsInterframeLong )
    if numCasesInterframeLong >0 and (not demo):
       longFramesStr =  'ERROR,'+str(numCasesInterframeLong)+' frames were longer than '+str(longFrameLimit)+' ms'
       if demo: 
         longFramesStr += 'not printing them all because in demo mode'
       else:
           longFramesStr += ' apparently screen refreshes skipped, interframe durs were:'+\
                    str( np.around(  interframeIntervs[idxsInterframeLong] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeLong)
       if longFramesStr != None:
                logging.error( 'trialnum='+str(trialN)+' '+longFramesStr )
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                        if idx-1>=0:
                            flankingAlso.append(idx-1)
                        else: flankingAlso.append(np.NaN)
                        flankingAlso.append(idx)
                        if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                        else: flankingAlso.append(np.NaN)
                    flankingAlso = np.array(flankingAlso)
                    flankingAlso = flankingAlso[~(np.isnan(flankingAlso))]  #remove nan values
                    flankingAlso = flankingAlso.astype(np.integer) #cast as integers, so can use as subscripts
                    logging.info( 'flankers also='+str( np.around( interframeIntervs[flankingAlso], 1) )  ) #because this is not an essential error message, as previous one already indicates error
                      #As INFO, at least it won't fill up the console when console set to WARNING or higher
    return numCasesInterframeLong
    #end timing check
    
trialClock = core.Clock()
numTrialsCorrect = 0; 
numTrialsApproxCorrect = 0;
numTrialsEachCorrect= np.zeros( experiment['numSimultaneousStim'] )
numTrialsEachApproxCorrect= np.zeros( experiment['numSimultaneousStim'] )

def do_RSVP_stim(thisTrial, seq1, seq2, seq3, ltrColorThis, proportnNoise,trialN,thisProbe):
    #relies on global variables:
    #   textStimuli, logging, bgColor, trialInstructionStim
    global framesSaved #because change this variable. Can only change a global variable if you declare it
    cuesPos = [] #will contain the positions in the stream of all the cues (targets)
    cuesPos.append(0)
    cuesPos = np.array(cuesPos)
    noise = None; allFieldCoords=None; numNoiseDots=0
    if proportnNoise > 0: #generating noise is time-consuming, so only do it once per trial. Then shuffle noise coordinates for each letter
        (noise,allFieldCoords,numNoiseDots) = createNoise(proportnNoise,myWin,noiseFieldWidthPix, bgColor)
    preDrawStimToGreasePipeline = list() #I don't know why this works, but without drawing it I previously have had consistent timing blip first time that draw 
    cue.setLineColor(bgColor)
    preDrawStimToGreasePipeline.extend([cue])
    for stim in preDrawStimToGreasePipeline:
        stim.draw()
    trialInstructionStim.draw(); myWin.flip(); trialInstructionStim.draw(); myWin.flip()
    trialDurFrames = int( numWordsInStream*(thisTrial['ISIframes']+letterDurFrames) ) #trial duration in frames
    logging.info( 'numtrials=' + str(trials.nTotal) + ' and this trialDurFrames='+str(trialDurFrames)+' or '+str(trialDurFrames*(1000./refreshRate))+ \
               ' ms' + '  task=' + task)
               
    noiseTexture = scipy.random.rand(8,8)*2.0-1
    myNoise1 = visual.GratingStim(myWin, tex=noiseTexture, size=(1.5,1), units='deg', interpolate=False,
             pos = calcStimPos(thisTrial,0), autoLog=False)#this stim changes too much for autologging to be useful
    myNoise2 = visual.GratingStim(myWin, tex=noiseTexture, size=(1.5,1), units='deg', interpolate=False,
             pos = calcStimPos(thisTrial,1), autoLog=False)
    #if experiment['numSimultaneousStim'] == 3:
    myNoise3 = visual.GratingStim(myWin, tex=noiseTexture, size=(1.5,1), units='deg', interpolate=False,
                                                          pos = calcStimPos(thisTrial,2), autoLog=False)
    #end preparation of stimuli
    
    core.wait(.1)
    trialClock.reset()
    fixatnPeriodMin = 0.
    fixatnPeriodFrames = int(   (np.random.rand(1)/4.+fixatnPeriodMin)   *refreshRate)  #random interval between 0 and 1/4 seconds
    ts = list(); #to store time of each drawing, to check whether skipped frames
    instructionFrames = 50
    if trialN > 2: 
        instructionFrames = 20
    for i in range(instructionFrames):
        trialInstructionStim.draw()
        if i%4 > 1: fixationPoint.draw()
        myWin.flip()
    for i in range(fixatnPeriodFrames):  #prestim fixation interval
        #if i%4>=2 or demo or exportImages: #flicker fixation on and off at framerate to see when skip frame
        #      fixation.draw()
        #else: fixationBlank.draw()
        if i%4 > 1: fixationPoint.draw()
        myWin.flip()  #end fixation interval
    #myWin.setRecordFrameIntervals(True);  #can't get it to stop detecting superlong frames
    t0 = trialClock.getTime()

    midDelay = 0.4 #0.5
    midDelayFrames = int(midDelay *refreshRate)
    #insert a pause to allow the window and python all to finish initialising (avoid initial frame drops)
    for i in range(midDelayFrames):
        if i%4 > 1: fixationPoint.draw()
        myWin.flip()

    for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
            worked = oneFrameOfStim( n,cue,seq1,seq2,seq3,cueDurFrames,letterDurFrames,thisTrial,stimuliStream1,stimuliStream2,stimuliStream3,
                                                         ltrColorThis, noise,proportnNoise,allFieldCoords,numNoiseDots ) #draw letter and possibly cue and noise on top
            #fixationPoint.draw()
            if exportImages:
                myWin.getMovieFrame(buffer='back') #for later saving
                framesSaved +=1
            myWin.flip()
            t=trialClock.getTime()-t0;  ts.append(t);

    #draw the noise mask
    thisProbe = thisTrial['probe']
    if thisProbe == 'long':
        noiseMaskMin = 0.1 #.2
    else: noiseMaskMin = 0.1 # .2
        
    noiseMaskFrames = int(noiseMaskMin *refreshRate)
    for i in range(noiseMaskFrames):
        myNoise1.phase = scipy.random.rand(1); myNoise2.phase = scipy.random.rand(1); myNoise3.phase = scipy.random.rand(1)
        if seq1:
            myNoise1.draw(); 
        if seq2:
            myNoise2.draw()
        if seq1 and seq2: #if left or right (two stimuli presented), also draw middle noise (only don't draw it if only one stim presented)
            myNoise3.draw()
        #fixationPoint.draw()
        if exportImages:
            myWin.getMovieFrame(buffer='back') #for later saving
            framesSaved +=1
        myWin.flip()
    #myWin.flip() #Need this
    if thisProbe == 'long':
        probeDelay = 1.5
    else: probeDelay = 0.0
    
    probeDelayFrames = int(probeDelay *refreshRate)
    #insert a pause to allow the window and python all to finish initialising (avoid initial frame drops)
    for i in range(probeDelayFrames):
         myWin.flip()
           
    #end of big stimulus loop
    myWin.setRecordFrameIntervals(False);
    
    if task=='T1':
        respPromptStim1.setText('What was the underlined word?',log=False)   
    else: respPromptStim1.setText('Error: unexpected task',log=False)
    
    return ts

pctCompletedBreak = -99 #no break

def handleAndScoreResponse(passThisTrial,response,responseAutopilot,task,correctAnswer):
    #Handle response, calculate whether correct, ########################################
    #responses are actual characters
    #correctAnswer is index into stimSequence
    #autopilot is global variable
    #print('response=',response)
    if autopilot or passThisTrial:
        response = responseAutopilot
    correct = 0
    #approxCorrect = 0

    correctAnswer = correctAnswer.upper()
    responseString= ''.join(['%s' % char for char in response])
    responseString= responseString.upper()
    #print('correctAnswer=',correctAnswer ,' responseString=',responseString)
    if correctAnswer == responseString:
        correct = 1
    #print('correct=',correct)
    
    print(correctAnswer, '\t', end='', file=dataFile) #answerN
    print(responseString, '\t', end='', file=dataFile) #responseN
    print(correct, '\t', end='',file=dataFile)  #correctN
    return correct
    #end handleAndScoreResponses
def play_high_tone_correct_low_incorrect(correct, passThisTrial=False):
    highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.3, bits=8)
    low = sound.Sound('F',octave=3, sampleRate=6000, secs=.3, bits=8)
    highA.setVolume(0.9)
    low.setVolume(1.0)
    if correct:
        highA.play()
    elif passThisTrial:
        high= sound.Sound('G',octave=4, sampleRate=2000, secs=.08, bits=8)
        for i in range(2): 
            high.play();  low.play(); 
    else: #incorrect
        low.play()

def doAuthorRecognitionTest(autopilot):
    oneThirtyEight =['Agatha Christie', 'Aimee Dorr', 'Alex Lumsden', 'Alice Munro', 'Alvin Toffler', 'Amy Tan', 'Andrew Greeley', 'Anne Rice', 'Arthur C. Clarke', 'Barbara Cartland', 'Brian Bigelow', 'C.S. Lewis', 'Caleb Lim', 'Carl Corter', 'Carla Grinton', 'Carol Berg', 'Carol Shields', 'Carter Anvari', 'Charles Condie', 'Christopher Barr', 'Christopher Moore', 'Dale Blyth', 'Dan Brown', 'Daniel Quinn', 'Danielle Steel', 'David Baldacci', 'David Perry', 'David Singer', 'Dean Koontz', 'Denise Daniels', 'Devon Chang', 'Diana Gabaldon', 'Diane Cuneo', 'Edward Cornell', 'Elizabeth George', 'Elliot Blass', 'Eric Amsel', 'Erica Jong', 'Frances Fincham', 'Frank Gresham', 'Frank Herbert', 'Frank Kiel', 'Frank Manis', 'Gary Beauchamp', 'George R.R. Martin', 'Geraldine Dawson', 'Harrison Boldt', 'Hilda Borko', 'Hugh Lytton', 'Isaac Asimov', 'Jackie Collins', 'James Clavell', 'James Michener', 'James Morgan', 'Janet Evanovich', 'Janice Taught', 'Jean M. Auel', 'Jeffery Eugenides', 'Jennifer Butterworth', 'Jennifer Marshal', 'John Condry', 'John Grisham', 'John Jakes', 'Judith Krantz', 'Judy Blume', 'Julia Connerty', 'K. Warner Schaie', 'Kate Grenville', 'Kate Pullinger', 'Katherine Carpenter', 'Kirby Kavanagh', 'Lauren Benjamin', 'Laurie King', 'Lena Johns', 'Lilly Jack', "Louis L'Amour", 'Lynn Liben', 'M. Scott Peck', 'Maeve Binchy', 'Margaret Atwood', 'Margaret Laurence', 'Margarita Azmitia', 'Mark Elder', 'Mark Strauss', 'Martin Ford', 'Michael Moore', 'Mimi Hall', 'Miriam Sexton', 'Miriam Toews', 'Mordecai Richler', 'Morton Mendelson', 'Naomi Choy', 'Naomi Klein', 'Noam Chomsky', 'Oscar Barbary', 'Patricia Cornwell', 'Peter Carey', 'Peter Rigg', 'Pierre Berton', 'Pricilla Levy', 'Reed Larson', 'Reuben Baron', 'Richard Passman', 'Robert Emery', 'Robert Fulghum', 'Robert Inness', 'Robert J. Sawyer', 'Robert Jordan', 'Robert Ludlum', 'Robert Siegler', 'Robertson Davies', 'Rohinton Mistry', 'Russell Banks', 'Ryan Gilbertson', 'Ryan Morris', 'S.E. Hinton', 'Samuel Paige', 'Scott Paris', 'Sheryl Green', 'Sidney Sheldon', 'Sophia Martin', 'Sophie Kinsella', 'Stephen Coonts', 'Stephen J. Gould', 'Stephen King', 'Stirling King', 'Sue Grafton', 'Susan Kormer', 'Suzanne Clarkson', 'Thomas Bever', 'Timothy Findley', 'Tom Clancy', 'Tracy Tomes', 'Ursula LeGuin', 'V.C. Andrews', 'W. Patrick Dickson', 'Wayne Johnston', 'Wayson Choy']
    oneThirtyFive = oneThirtyEight[0:-3]
    possibleResps = oneThirtyFive #oneThirtyEight #sixteen
    #print('num authors = ',len(possibleResps))
    myWin.flip()
    expStop = False
    myMouse = event.Mouse(visible=True) #the mouse absolutely needs to be reset, it seems, otherwise maybe it returns coordinates in wrong units or with wrong scaling?
    expStop,timedout,selected,selectedAutopilot = \
                doAuthorLineup(myWin, bgColor,myMouse, clickSound, badSound, possibleResps, autopilot)
    if autopilot:
        selected = selectedAutopilot
    return expStop,timedout,selected

expStop=False
#Do authors task
myWin.allowGUI =True
#myWin.close() #Seems to work better if close and open new window (even though units the same), both in terms of dimensions (even though same here!) and double-clicking
#take a couple extra seconds to close and reopen window unfortunately
#myWin = visual.Window(fullscr=True,monitor=mon,colorSpace='rgb',color=bgColor,units='deg')
if includeConsentDemographicsAuthor:
    expStop,timedout,selected = doAuthorRecognitionTest(autopilot)
    #save authors file, in json format
    infix = 'authors'
    authorsFileName = os.path.join(dataDir, subject + '_' + timeDateStart + infix + '.json')
    otherData['selected'] = selected
    otherData['authors_expStop'] = expStop
    otherData['authors_timedout'] = timedout
    with open(authorsFileName, 'w') as outfile:  
        json.dump(otherData, outfile)
    #End doing authors task

experimentClock = core.Clock()
expTimeLimit = 60*17
expTimedOut = False
nDoneMain = -1 #change to zero once start main part of experiment
if doStaircase:
        #create the staircase handler
        stepSizesLinear = [.6,.6,.5,.5,.4,.3,.3,.1,.1,.1,.1,.05]
        minVal = bgColor[0]+.15
        maxMoreFramesAllowed = 6
        #lumRange = 1 - minVal
        staircase = data.StairHandler(
            startVal=ltrColor,
            stepType='lin',
            stepSizes=stepSizesLinear,  # reduce step size every two reversals
            minVal=minVal, 
            maxVal=maxMoreFramesAllowed + .99, 
            nUp=1, nDown=2,  # 1-up 3-down homes in on the 80% threshold. Gravitates toward a value that has an equal probability of getting easier and getting harder.
            #See Wetherill & Levitt 1965, 1 up 2 down goes for 71% correct. And if 2 letters are independent, each correct = sqrt(.71) = 84% correct.
            nTrials=500)
        print('created conventional staircase')
        
    #phasesMsg = ('Doing '+str(prefaceStaircaseTrialsN)+'trials with noisePercent= '+str(prefaceStaircaseNoise)+' then doing a max '+str(staircaseTrials)+'-trial staircase')
    #print(phasesMsg); logging.info(phasesMsg)

    #printStaircase(staircase, descendingPsycho, briefTrialUpdate=True, printInternalVal=True, alsoLog=False)
    #print('staircase.quantile=',round(staircase.quantile(),2),' sd=',round(staircase.sd(),2))

noisePercent = defaultNoiseLevel
phasesMsg = 'Experiment will have '+str(trials.nTotal)+' trials. Letters will be drawn with superposed noise of ' + "{:.2%}".format(defaultNoiseLevel)
print(phasesMsg); logging.info(phasesMsg)
nDoneMain =0
while nDoneMain < trials.nTotal and expStop!=True: #MAIN EXPERIMENT LOOP
    #print('nDoneMain=',nDoneMain)
    whichStim0 = np.random.randint(0, len(stimList) )
    whichStim1 = np.random.randint(0, len(stimList) ) 
    #check that whichStim0 and whichStim1 don't have letters in common. If they do generate a new pair
    whichStim2 = np.random.randint(0, len(stimList) ) #only used in Humby experiment
    calcAndPredrawStimuli(stimList,whichStim0,whichStim1,whichStim2)
    trial = trials.next()
    thisTrial = copy.deepcopy(trial) #so that can change its values, otherwise messing with it screws up the trialhandler
    ltrColorThis = ltrColor
    if nDoneMain==0: #First trial
        msg='Starting main part of experiment'
        howManyMoreFrames =0
        logging.info(msg)
        thisTrial['ISIframes'] *= 13 #ease the participants into it
    elif nDoneMain == 1:  #Show instructions
        thisTrial['ISIframes'] *= 10
        event.clearEvents(); keyPressed = False; f =0
        while f < 500 and not keyPressed:
            taskInstructionStim1.draw()
            myWin.flip(); f += 1
            keyPressed = event.getKeys() #keyList=list(string.ascii_lowercase))
    elif nDoneMain ==2:
        thisTrial['ISIframes'] *= 8
    elif nDoneMain ==3:
        thisTrial['ISIframes'] *= 8
    elif nDoneMain ==4:
        thisTrial['ISIframes'] *= 6
        event.clearEvents(); keyPressed = False; f =0
        while f < 500 and not keyPressed:
            taskInstructionStim2.draw()
            myWin.flip(); f += 1
            keyPressed = event.getKeys() #keyList=list(string.ascii_lowercase))        
    else:
        if doStaircase:
            print('staircase.stepSizeCurrent = ',staircase.stepSizeCurrent, 'staircase._nextIntensity=',staircase._nextIntensity, 'howManyMoreFrames=',howManyMoreFrames)
            ltrColorThis = staircase.next()
            #if ltrColorThis <= 1:
            #    howManyMoreFrames = 0
            #elif ltrColorThis > howManyMoreFrames + 1: #can't have lum greater than 1, so instead increase duration
                #print('thisTrial[ISIframes]=', thisTrial['ISIframes'])
            howManyMoreFrames = scipy.floor(ltrColorThis)
            #    print('changed howManyMoreFrames to ', howManyMoreFrames)
            thisTrial['ISIframes'] += howManyMoreFrames #increase duration by however much it is greater than 1
            if howManyMoreFrames>0:
                #need the base brightness when longer frames to be pretty high, otherwise they might never get back to lower number of frames
                ltrColorThis = min(1,   0 + (ltrColorThis - howManyMoreFrames)   ) #For each bit greater 1, increase luminance
                print('thisTrial[ISIframes]=', thisTrial['ISIframes'], ' and now ltrColorThis =',ltrColorThis)
            ltrColorThis = round(ltrColorThis,2)
            #print('staircase.stepSizeCurrent = ',staircase.stepSizeCurrent, 'staircase._nextIntensity=',staircase._nextIntensity)
            #print('ltrColorThis=',ltrColorThis)
            #trialInstructionStim.setText('lum=' + str(ltrColorThis)+ ' f='+ str(howManyMoreFrames), log=False) #debug
    trialInstructionStim.setPos( thisTrial['trialInstructionPos'] )
    if nDoneMain <= 1: #extra long instruction
        for i in range(70):
            trialInstructionStim.draw()
            if i > 30:
                fixationPoint.draw()
            myWin.flip()
    thisProbe = thisTrial['probe']
    if thisProbe=='both':
      numRespsWanted = experiment['numSimultaneousStim']
    else: numRespsWanted = 1
    
    #Determine which words will be drawn
    idxsStream1 = [0]; idxsStream2 = [0]
    if thisTrial['oneTarget']:
        idxsStream3 = None #no middle target (3-letter condition)
        if thisTrial['rightResponseFirst']: #in oneTarget condition, rightResponseFirst controls which is shown
            idxsStream1 = None 
        else:
            idxsStream2 = None
    idxsStream3 = None
    if experiment['numSimultaneousStim'] == 3:
       idxsStream3 = [0]
    ts  =  do_RSVP_stim(thisTrial, idxsStream1, idxsStream2, idxsStream3, ltrColorThis, noisePercent/100.,nDoneMain,thisProbe)
    numCasesInterframeLong = timingCheckAndLog(ts,nDoneMain)
    #call for each response
    myMouse = event.Mouse(visible=False)
    possibleResps = stimList
    showBothSides = True
    sideFirstLeftRightCentral = 0
    #possibleResps.remove('C'); possibleResps.remove('V
    
    expStop = list(); passThisTrial = list(); responses=list(); responsesAutopilot=list()
    numCharsInResponse = len(stimList[0])
    dL = [None]*numRespsWanted #dummy list for null values
    expStop = copy.deepcopy(dL); responses = copy.deepcopy(dL); responsesAutopilot = copy.deepcopy(dL); passThisTrial=copy.deepcopy(dL)
    if thisProbe == 'both': #Either have word on both sides or letter on both sides
        if thisTrial['oneTarget']:
            numToReport = 1
        else:
            numToReport =  experiment['numSimultaneousStim']
        responseOrder = list( range(numToReport) )
        if (numToReport == 3): #not counterbalanced, so just shuffle
            random.shuffle(responseOrder)
        elif thisTrial['rightResponseFirst']: #change order of indices depending on rightResponseFirst. response0, answer0 etc refer to which one had to be reported first
            responseOrder.reverse()
        #print('responseOrder=',responseOrder)
        respI = 0
        while respI < numToReport and not np.array(expStop).any():
            if numToReport ==1:
                side = thisTrial['rightResponseFirst'] * 2 - 1
            elif numToReport == 2:
                side = responseOrder[respI] * 2 -1  #-1 for left/top, 1 for right/bottom
            elif numToReport == 3:
                side = (responseOrder[respI] - 1)  #-1 for left/top, 0 for middle, 1 for right/bottom
                
            dev = 2*wordEccentricity * side #put response prompt farther out than stimulus, so participant is sure which is left and which right
            
            if numToReport == 1 or numToReport == 2:
                locationNames= [ 'the left', 'the right',  'the bottom','top' ]
                numLocations = 2
            elif numToReport == 3:
                locationNames = [ 'the left', 'at centre', 'the right',  'the bottom', 'at centre', 'top' ]
                numLocations = 3
            respPromptString = 'Type the ' + experiment['stimType']
            if numToReport == 1:
                respPromptString += ' that was presented'
                #locationName = locationNames[   thisTrial['horizVert'] * numLocations + int((side+1)/2)   ]
            else:
                locationName  = locationNames[      thisTrial['horizVert'] * numLocations  +   responseOrder[respI]      ]
                respPromptString += ' that was on ' +  locationName
            respPromptStim1.setText(respPromptString,log=False)
            if thisTrial['horizVert']:
                x=0; y=dev
                if numToReport == 3: #need an orthogonal offset, so doesn't overlap when at fixation
                    x = -wordEccenticity
            else:
                x=dev; y=0
                if numToReport == 3: #need an orthogonal offset, so doesn't overlap when at fixation
                    y = -wordEccentricity
            if thisTrial['horizVert']: #x coordinate have to compensate if rotated, use calcStimPos to check
                 pos  = calcStimPos(thisTrial,0)
                 x = pos[0]
            respStim.setPos([x,y])

            respStim.flipHoriz = experiment['flipped']
            #Set position of respPromptStim
            xPrompt =  x*2 if thisTrial['horizVert'] else x*4  #needs to be further out if horizontal to fit the text
            respPromptStim1.setPos([xPrompt, y*2])
            #respPromptStim2, 3 will be at left and right, vertically arrayed if vertical stimuli arrangement,
            #  at top and bottom, horizontally arrayed if horizontal stimuli arrangement
            edge = .7
            if thisTrial['horizVert'] and experiment['ori'] != 0: # rotated, draw text left and right
                    respPromptStim2.setPos( [-edge,0] ) #left
                    respPromptStim3.setPos( [edge, 0] ) #right
            else:
                respPromptStim2.setPos( [0,-edge] ) #bottom
                respPromptStim3.setPos( [0, edge] ) #top
                
            #expStop,passThisTrial,responses,buttons,responsesAutopilot = \
            #        letterLineupResponse.doLineup(myWin,bgColor,myMouse,clickSound,badSound,possibleResps,showBothSides,sideFirstLeftRightCentral,autopilot) #CAN'T YET HANDLE MORE THAN 2 LINEUPS
            changeToUpper = False
            fixationPoint.setColor([.7,.7,.7]) #white not red so person doesnt' feel they have to look at it
            expStop[respI],passThisTrial[respI],responses[respI],responsesAutopilot[respI] = stringResponse.collectStringResponse(
                                    numCharsInResponse,x,y,respPromptStim1,respPromptStim2,respPromptStim3,respStim,acceptTextStim,fixationPoint, (1 if experiment['stimType']=='digit' else 0), myWin,
                                    clickSound,badSound, requireAcceptance,autopilot,changeToUpper,responseDebug=True )
            fixationPoint.setColor(fixColor)
            respI += 1
        expStop = np.array(expStop).any(); passThisTrial = np.array(passThisTrial).any()
    
    if not expStop:
            print('main\t', end='', file=dataFile) #first thing printed on each line of dataFile to indicate main part of experiment, not staircase
            print(nDoneMain,'\t', end='', file=dataFile)
            print(subject,'\t',task,'\t', thisTrial['oneTarget'], '\t', round(noisePercent,3),'\t', end='', file=dataFile)
            print(thisTrial['ISIframes'],'\t', end='', file=dataFile)
            print(ltrColorThis,'\t', end='', file=dataFile)
            print(thisTrial['leftStreamFlip'],'\t', end='', file=dataFile)
            print(thisTrial['rightStreamFlip'],'\t', end='', file=dataFile)
            print(thisTrial['rightResponseFirst'],'\t', end='', file=dataFile)
            print(thisTrial['probe'],'\t', end='', file=dataFile)
            print(thisTrial['trialInstructionPos'],'\t', end='', file=dataFile)
                
            eachCorrect = np.ones(numRespsWanted)*-999

            #print("numRespsWanted = ",numRespsWanted, 'getting ready to score response')
            numToPrint = numRespsWanted
            if thisTrial['oneTarget']:
                numToPrint = 1 #kludge, see line 993
            for streami in range(numToPrint): #scored and printed to dataFile in left first, right second order even if collected in different order
                print(responseOrder[streami],'\t', end='', file=dataFile)
                if streami==0:
                    sequenceStream = idxsStream1; correctAnswerIdx = whichStim0
                elif streami==1: 
                    sequenceStream = idxsStream2; correctAnswerIdx = whichStim1
                elif streami==2:
                    sequenceStream = idxsStream2; correctAnswerIdx = whichStim2
                #print ("stimList = ", stimList, " correctAnswer = stimList[correctAnswerIdx] = ",stimList[correctAnswerIdx])
                if thisTrial['oneTarget'] and streami==1: #only streami==0 is used
                    correct = -99
                else:
                    respThisStreamI = responseOrder.index(streami)
                    respThisStream = responses[respThisStreamI]
                #print ("responses = ", responses, 'respThisStream = ', respThisStream)   #responseOrder
                    correct = ( handleAndScoreResponse(passThisTrial,respThisStream,responsesAutopilot,task,stimList[correctAnswerIdx]) )
                eachCorrect[streami] = correct
            
            #kludge to pad with null datafile spaces when only one target presented
            if thisTrial['oneTarget']:
                for i in range(experiment['numSimultaneousStim']-1):
                    print(-99, '\t', end='', file=dataFile) #responseOrderN
                    print(-99, '\t', end='', file=dataFile) #answerN
                    print(-99, '\t', end='', file=dataFile) #responseN
                    print(-99, '\t', end='',file=dataFile)  #correctN
            
            print(numCasesInterframeLong, file=dataFile) #timingBlips, last thing recorded on each line of dataFile
            #Don't want to feed allCorrect into staircase because then for e.g. a staircase targeting 70% correct, they will get 84% correct on each if two letters but even higher if 3 letters
            #Instead, average and round. This means that if get 1 out of 2 correct, counts as correct. If get 2 out of 3 correct, counts as correct but one is not enough.
            correctForStaircase = round( scipy.mean(eachCorrect) )
            if thisTrial['oneTarget']:
                not99idx = np.where(eachCorrect != -99)[0][0]
                #not99idx = not eachCorrect.index(-99)
                correctForStaircase = eachCorrect[not99idx]
            print('eachCorrect=',eachCorrect, 'correctForStaircase=',correctForStaircase)
            if doStaircase and nDoneMain>4:
                staircase.addResponse( correctForStaircase )
            numTrialsCorrect += eachCorrect.all() #so count -1 as 0
            numTrialsEachCorrect += eachCorrect #list numRespsWanted long
                
            if exportImages:  #catches one frame of response
                 myWin.getMovieFrame() #I cant explain why another getMovieFrame, and core.wait is needed
                 framesSaved +=1; core.wait(.1)
                 myWin.saveMovieFrames('images_sounds_movies/frames.png') #mov not currently supported 
                 expStop=True
            #core.wait(.1)
            if feedback and useSound: 
                play_high_tone_correct_low_incorrect(correctForStaircase, passThisTrial=False)
            nDoneMain+=1
            dataFile.flush(); logging.flush()
            print('nDoneMain=', nDoneMain,' trials.nTotal=',trials.nTotal, 'expStop=',expStop) #' trials.thisN=',trials.thisN
            #check whether time for break
            if (trials.nTotal > 6 and nDoneMain > 2 and nDoneMain %
                 ( trials.nTotal*pctCompletedBreak/100. ) ==1 ):  #dont modulus 0 because then will do it for last trial
                    nextText.setText('Press "SPACE" to continue!')
                    nextText.draw()
                    progressMsg = 'Completed ' + str(nDoneMain) + ' of ' + str(trials.nTotal) + ' trials'
                    NextRemindCountText.setText(progressMsg)
                    NextRemindCountText.draw()
                    myWin.flip() # myWin.flip(clearBuffer=True) 
                    waiting=True
                    while waiting:
                       if autopilot: break
                       elif expStop == True:break
                       for key in event.getKeys():      #check if pressed abort-type key
                             if key in ['space','ESCAPE']: 
                                waiting=False
                             if key in ['ESCAPE']:
                                expStop = True
                    myWin.clearBuffer()
            #end break
            core.wait(.05);  time.sleep(.05)
            if experimentClock.getTime() > expTimeLimit:
                expTimedOut = True
            print('got to end of loop')
        #end main trials loop
timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
msg = 'Stopping at '+timeAndDateStr
print(msg); logging.info(msg)
if expStop:
    msg = 'user aborted experiment on keypress with trials done=' + str(nDoneMain) + ' of ' + str(trials.nTotal+1)
    print(msg); logging.error(msg)
if expTimedOut:
    msg = 'Experiment timed out with trials done=' + str(nDoneMain) + ' of ' + str(trials.nTotal+1)
    print(msg); logging.info(msg)
if nDoneMain >0:
    print('Of ',nDoneMain,' trials, on ',numTrialsCorrect*1.0/nDoneMain*100., '% of all trials all targets reported exactly correct',sep='')
    for i in range(numRespsWanted):
        print('stream',i,': ',round(numTrialsEachCorrect[i]*1.0/nDoneMain*100.,2), '% correct',sep='')
dataFile.flush(); logging.flush(); dataFile.close()

logging.info("Program terminating normally."); print("Terminated normally.")
core.quit()
