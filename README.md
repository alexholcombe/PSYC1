TO-DO
* recover right correct
In particular oneTarget was NotScoredWhenRightOrUp position

* confirm stim position for methods section
* Write Draft methods 
* checkAlignment. That turns on fixation drawing. Rotated letters very close to being aligned but upper still slightly lower. Fortunately rotating 90 versus -90 can't result in different distances from fixation.

EXPERIMENT LIST 
0. 2 words, horizontally arrayed, 1/3 of trials single target
1. 2 words, vertically arrayed, 1/3 of trials single target
2. 2 letters, horizontally arrayed, 1/3 of trials single target
3. 2 letters, vertically arrayed, 1/3 of trials single target
4. 3 letters, horizontally arrayed (no single-target trials)
5. 2 letters, horizontally arrayed, flipped, 1/3 of trials single target
6. 2 letters, vertically arrayed, rotated 90 deg clockwise, 1/3 of trials single target
7. 2 letters, vertically arrayed, rotated -90 deg to face up, 1/3 of trials single target



-------------NOTES WHEN GETTING IT GOING FOR PSYC1----------
TIMING & DIFFICULTY LEVEL
* Make letters half brightness, and postmask dynamic and add premask
* With dynamic noise mask, 34 ms ISI is too easy and 17 might be too hard
* Make pixels in the noise bigger. Smithson


COMPUTER LAB
* Measure dimensions of the screens in all the rooms.
* Check vertical displacement of letters matches horizontal
* Try the html webform

The installed version is 1.84.2.  On GRasp is 1.90.2
Viewing distance is set to 57cm
python version 2.7.11
refresh rate 60 Hz

Resolution appears to be 1920 x 1080
screen is 57 cm wide. http://www.dell.com/ae/business/p/optiplex-24-7000-aio/pd


* Check path to Submissions 
* Add test for Submissions subdirectory and printing of present directory
* Does it have the accidental author double-click problem that my computer has when integrated? Might be something about the windows settings.
* Try from GRASP
* "research report experiment"
enter password: Loftus
* Check Humby data saved
* Make sure exits gracefully when run many but not all trials
* match Jen's font etc. Hers is upper case so there isn't much point.
* The password box is too small!
* Try all the paths in the right place


Check scaling of text

LONG-TERM
Execute batch file. Call ICT and get put through to ict-desktopmanagement
Get author/non-author score



OLD

* Turn off the sound with boolean flag.
It doesn't seem to like portaudio, has error closing it. But there is no sound anyway because by default the computers have no sound. And we probably don't have enough headphones, and then would have to unmute the sound. So add a sound flag and turn off sound. That might also fix the ungraceful quit.

* And somehow, double mouse-clicking was a problem for the second part. Second time I ran it, mouse-clicking slightly better. 

* Urgently check DLG window
