'''
Program designed to (currently) take a Pulse test and/or IV test in a 64 x 64
array of RRAM devices/cells and, using the expected serial PCB board inputs/outputs
generated in the GUI based on user input voltages, receive the outputted
current/resistance to determine how responsive the program is to determining
"brightness"

Definitions:
RRAM = resistive random-access memory
PCB = printed circuit board
GUI = graphical user interface
MSB = most significant byte
LSB = least significant byte

Updated version by Nicholas Van Nostrand, last update: 6/23/25
'''

#imports (FOLLOW INSTALLATION INSTRUCTIONS PROVIDED IF NECESSARY)
import promptlib #installed promptlib (pip install promptlib (https://pypi.org/project/promptlib/))

'''
pySerial module "encapsulates the access for the serial
port." (https://pyserial.readthedocs.io/en/latest/index.html)
'''
import serial #installed pySerial library (python -m pip install pyserial (https://pyserial.readthedocs.io/en/latest/pyserial.html#installation))
import serial.tools.list_ports #module to get list of ports (https://pyserial.readthedocs.io/en/latest/tools.html)

'''
"tkinter" package "is the standard Python interface to
the Tcl/Tk GUI toolkit" (https://docs.python.org/3/library/tkinter.html)
'''
from tkinter import _setit
from tkinter import *
import tkinter as tk
from tkinter import ttk #ttk = themed Tkinter for "improved aesthetics and additional widgets"
import tkinter.font

import matplotlib.pyplot as plt #installed matplotlib (python -m pip install -U matplotlib (https://matplotlib.org/stable/install/index.html))
import numpy as np

#miscellaneous imports
import math
import os
import csv
import time
from datetime import datetime

#-------------------------------------------------------------------------

#interactive grid (tkinter widget) class that can vary in
#row/column dimension sizes (BUT IN THIS CODE'S CASE, THE DIMENSIONS ARE FIXED)
class interactiveGrid:

    def __init__ (self, master): #set input requirements
    
        #NOTE: "master" input is a "tkinter.Tk()" class object/main window

        #set class variables based on inputs
        self.master = master
        self.rows = 64 #FIXED TO MEET THE 64x64 REQUIREMENT
        self.columns = 64 #FIXED TO MEET THE 64x64 REQUIREMENT
        self.grid = [] #grid to be made as a 2D list of buttons
        
        #2D list to store all boolean logic associated with the
        #grid buttons, all set to "False" by default
        #meant to be the same dimensions as self.grid
        self.gridBooleans = [[False for GridY in \
                              range(self.columns)] for GridX in range(self.rows)]

        #call built-in "createAndMaintainGrid" function below as part of the
        #initialization process
        self.createAndMaintainGrid()

    # - - - - - - - - -

    #allow for class ojbect to be iterable when necessary
    def __iter__(self):
        return iter(self.grid)

    # - - - - - - - - -

    #creates the grid using the provided row/column dimensions and
    #will update each grid cell (represented as a button) when clicked
    #also initializes "gridBooleans" to all be "False" from the start
    def createAndMaintainGrid(self):
        
        #create grid of buttons that will call built-in function
        #clickedButton" to change the "gridBoolean" logic AND button
        #color when clicked
        #NOTE: Default Button Color = False, Black Button = True
        for gridRow in range(self.rows):
            
            row_widgets = [] #create list for row buttons/widgets
            
            for gridColumn in range(self.columns):

                #create grid cell button and have it call "clickedButton"
                #when pressed
                #NOTE: "lambda" function is used to pass arguments to a
                #button's command
                gridCellButton = tk.Button(self.master, width = 4, \
                                           height = 2, command = lambda \
                                           gr = gridRow, gc = gridColumn: \
                                           self.clickedButton(gr, gc), \
                                           bg = 'white', \
                                           text = ''.join([str(gridRow + 1), '/', str(gridColumn + 1)]))

                #"sticky = 'nsew'" sets button to stall to all four sides of its cell (i.e.
                #fill entire cell, regardless of initial or current size)
                #set up grid to make sure these buttons are all shown
                #NOTE: The +1 to the rows and columns are meant to accomodate for the inclusion
                #of the "select all row/column" buttons to the top/right of the grid
                gridCellButton.grid(row = gridRow + 1, column = gridColumn + 1, sticky = 'nsew')
                
                #append button to list for future appending to self.grid
                row_widgets.append(gridCellButton)

            #after getting each row, append to self.grid to create a 2D list of buttons
            self.grid.append(row_widgets)

        '''
        at Jeelka's request, adding row and column buttons that,
        when pressed, will set the selected button's row or column
        to True

        Addressed by logic below
        '''
        
        #create full row selection buttons
        for rowIndex in range(self.rows):

            #create the button with the associated design and command logic
            rowButtonAtIndex = tk.Button(self.master, text = '>', bg = 'light green', height = 2)
            rowButtonAtIndex.grid(row = rowIndex + 1, column = 0) #to the right of the 2D grid
            rowButtonAtIndex.config(command = lambda rowVal = rowIndex: self.selectAllRowCol(rowVal, 'row'))

        #create full column selection buttons
        for colIndex in range(self.columns):

            #create the button with the associated design and command logic
            colButtonAtIndex = tk.Button(self.master, text = '\\/', bg = 'light green', width = 4)
            colButtonAtIndex.grid(row = 0, column = colIndex + 1) #to the top of the 2D grid
            colButtonAtIndex.config(command = lambda colVal = colIndex: self.selectAllRowCol(colVal, 'column'))

    # - - - - - - - - -

    #function to address changes in button/boolean state for a cell at any
    #set row/column combination when the self.grid button for this cell is clicked
    def clickedButton(self, row, column):

        #get single button at inputted row/column combination
        singleCellButton = self.grid[row][column]
        singleCellBoolean = self.gridBooleans[row][column] #boolean equivalent of the same cell/button

        #for the sake of visual clarity when a button has been pressed,
        #the color of the button will be changed when clicked
        #determine current color and change
        currentButtonColor = singleCellButton.cget('bg') #bg = background (i.e. get background color)

        #since calling this function means the button was pressed, change
        #the color and Boolean information of the cell at the inputted row/column position

        if(currentButtonColor == 'white'): #if currently white ("default" color for this program)
            #to still see the text of the buttons, change the colors from black to red
            #while setting the background to black
            singleCellButton.config(bg = 'black', fg = 'red')
            
        else: #otherwise (i.e. if black, reset to default text and background colors)
            singleCellButton.config(bg = 'white', fg = 'black')

        #change Boolean logic at the determined row/column cell position
        self.gridBooleans[row][column] = not singleCellBoolean

    # - - - - - - - - -

    #function to return "gridBooleans" list when called
    def returnBooleans(self):
        return self.gridBooleans

    # - - - - - - - - -

    #function to return number of rows when called
    def returnRowNum(self):
        return self.rows

    # - - - - - - - - -

    #function to return number of columns when called
    def returnColumnNum(self):
        return self.columns

    # - - - - - - - - -

    #function that will set all cells/devices to FALSE when prompted
    def allFalse(self):

        #set boolean logic to all FALSE in self.gridBooleans
        self.gridBooleans = [[False for GridY in \
                              range(self.columns)] for GridX in range(self.rows)]

        #set the color for all buttons to their "FALSE" defaults
        #of a WHITE background with BLACK text
        for gridRow in range(self.rows):            
            for gridColumn in range(self.columns):
                singleCellButton = self.grid[gridRow][gridColumn]
                singleCellButton.config(bg = 'white', fg = 'black')                

    # - - - - - - - - -

    #function that will set all cells/devices to TRUE when prompted
    def allTrue(self):

        #set boolean logic to all TRUE in self.gridBooleans
        self.gridBooleans = [[True for GridY in \
                              range(self.columns)] for GridX in range(self.rows)]

        #set the color for all buttons to their "TRUE" defaults
        #of a BLACK background with RED text
        for gridRow in range(self.rows):            
            for gridColumn in range(self.columns):
                singleCellButton = self.grid[gridRow][gridColumn]
                singleCellButton.config(bg = 'black', fg = 'red')

    # - - - - - - - - -

    #function that will be called if any of the buttons around the grid
    #that represent all of one row or column is selected and will set all
    #of the grid buttons within that said row/column to True when pressed
    def selectAllRowCol(self, selectedRowColIndex, directionString):
        
        if(directionString == 'row'): #if an all row button is pressed

            #loop through all columns and set the 2D grid buttons to True at the
            #shared row
            for gridColumn in range(self.columns):

                self.gridBooleans[selectedRowColIndex][gridColumn] = True
                self.grid[selectedRowColIndex][gridColumn].config(bg = 'black', fg = 'red')

        else: #if an all column button is pressed

            #loop through all rows and set the 2D grid buttons to True at the
            #shared column
            for gridRow in range(self.rows):

                self.gridBooleans[gridRow][selectedRowColIndex] = True
                self.grid[gridRow][selectedRowColIndex].config(bg = 'black', fg = 'red')

    # - - - - - - - - -

    #function that will disable/return the buttons' states to normal in regards
    #to user interactivity
    #this is done to prevent users from changing buttons at unwanted times
    def changeGridButtonStates(self, chosenStateCommand):

        #go through the entire list (grid) of buttons and set them
        #all to the chosenStateCommand state
        for gridRow in range(self.rows):            
            for gridColumn in range(self.columns):
                singleCellButton = self.grid[gridRow][gridColumn]
                singleCellButton['state'] = chosenStateCommand

#-------------------------------------------------------------------------

#at Jeelka's request, have both frames for both modes be within the same
#window
#in order to achieve this, the following class is designed to represent
#each of the window's frames for each mode
class masterWindowClass: #overarching Tkinter window class to hold both frames

    def __init__(self, masterWindow, startRun): #create initializing functionality
        self.master = masterWindow
        self.startRun = startRun

        masterWindow.title("Packaged RRAM Testing GUI")

        #prevent changing the size of the GUI as well as closing protocols
        masterWindow.resizable(False, False)
    
        masterWindow.protocol("WM_DELETE_WINDOW", \
                          lambda: closeMaster(masterWindow)) #calls built-in "closeMaster" function

        # - - - - - - - - - - -

        #set directory related widgets for drop down menu logic,
        #CHANGE IF NECESSARY
        self.saveFileNameString = StringVar()
        self.saveFileNameString.set('')

        #CURRENT folder (where code is) is the default directory for all CSV related functions
        self.csvDirectoryString = StringVar()
        self.csvDirectoryString.set(os.getcwd())

        # - - - - - - - - - - -

        #declare all input byte variables (in HEXIDECIMAL) to be sent to the board as
        #string variables to be shared between widgets and functions
        #see "GUI requirements doc" document for input ranges and expected values per byte
        #NOTE: Since this is for one UI, the byte title information will be strictly in relation to the
        #UI's expected Hexidemical values, hence why the bytes are given more descriptive names
        #NOTE: "StringVar()" is a Tkinter built-in programming type with getter/setter methods to
        #access and change values (https://www.askpython.com/python-modules/tkinter/stringvar-with-examples)
        #NOTE: The first and last two bytes to be inputted into the board (hence why they are skipped
        #based on variable name) are hard coded elsewhere and are not based on user input
        #NOTE: Most board inputs will be based on two bytes sequences per GUI variable (31 bytes total)
        #NOTE: MSB: "most significant byte", LSB: "least significant byte"
        self.byte3_GateVoltageMSB = StringVar()
        self.byte4_GateVoltageLSB = StringVar()
        self.byte5_FORMSETVoltageMSB = StringVar()
        self.byte6_FORMSETVoltageLSB = StringVar()
        self.byte7_FORMSETTimeMSB = StringVar()
        self.byte8_FORMSETTimeLSB = StringVar()
        self.byte9_delayPeriodTimeMSB = StringVar() #delay period for ALL pulses EQUALLY
        self.byte10_delayPeriodTimeLSB = StringVar()
        self.byte11_FORMSETREADVoltageMSB = StringVar()
        self.byte12_FORMSETREADVoltageLSB = StringVar()
        self.byte13_FORMSETREADTimeMSB = StringVar()
        self.byte14_FORMSETREADTimeLSB = StringVar()
        self.byte15_RESETVoltageMSB = StringVar()
        self.byte16_RESETVoltageLSB = StringVar()
        self.byte17_RESETTimeMSB = StringVar()
        self.byte18_RESETTimeLSB = StringVar()
        self.byte19_RESETREADVoltageMSB = StringVar()
        self.byte20_RESETREADVoltageLSB = StringVar()
        self.byte21_RESETREADTimeMSB = StringVar()
        self.byte22_RESETREADTimeLSB = StringVar()
        self.byte25_CyclesNumberMSB = StringVar()
        self.byte26_CyclesNumberLSB = StringVar()
        self.byte27_StepNumberMSB = StringVar() #step input specific to the IV test, NOT the pulse test
        self.byte28_StepNumberLSB = StringVar()
        self.byte29_modeState = StringVar()

        # - - - - - - - - - - -

        #set default values for each byte

        #first, create IntVars and DoubleVars that can be changed will update their
        #associated byte information in real time upon IntVar changes
        self.gateVoltage = DoubleVar()
        self.FORMSETVoltage = DoubleVar()
        self.FORMSETTime = IntVar()
        self.delayPeriodTime = IntVar()
        self.FORMSETREADVoltage = DoubleVar()
        self.FORMSETREADTime = IntVar()
        self.RESETVoltage = DoubleVar()
        self.RESETTime = IntVar()
        self.RESETREADVoltage = DoubleVar()
        self.RESETREADTime = IntVar()
        self.cycleNumber = IntVar()
        self.stepNumber = IntVar()

        self.FORMSETStateString = StringVar()

        self.IVTestState = StringVar() #still expected in submit button function call

        #UNIQUE TO STEP PULSE TEST
        self.maxStepVoltage = DoubleVar()
        self.chosenStepVoltage = StringVar()
        self.stepVoltageDirection = StringVar()

        #UNIQUE TO IV TEST AND PULSE TEST SET/RESET SWITCH MODES
        self.SETGateVoltage = DoubleVar()
        self.RESETGateVoltage = DoubleVar()

        # - - - - - - - -

        self.gateVoltage.set(1.5) #volts, CHANGE IF NECESSARY

        #NOTE: All voltage values to be inputted to the PCB are in
        #MILLIVOLTS, so perform the conversion during the byte
        #splitting process (1000 millivolts = 1 volt)
        #NOTE: For the sake of all byte information being in "Int" format,
        #convert the floats to integers post multiplication
        self.MSBGateVoltHexInt, self.LSBGateVoltHexInt = \
                           twoByteComboSplit(int(self.gateVoltage.get() * 1000))
        self.byte3_GateVoltageMSB.set(str(self.MSBGateVoltHexInt))
        self.byte4_GateVoltageLSB.set(str(self.LSBGateVoltHexInt))

        # - - - - - - - -

        self.delayPeriodTime.set(500) #microseconds, CHANGE IF NECESSARY
        self.MSBDelayPeriodTimeHexInt, self.LSBDelayPeriodTimeHexInt = \
                              twoByteComboSplit(self.delayPeriodTime.get())
        self.byte9_delayPeriodTimeMSB.set(str(self.MSBDelayPeriodTimeHexInt))
        self.byte10_delayPeriodTimeLSB.set(str(self.LSBDelayPeriodTimeHexInt))

        # - - - - - - - -

        self.FORMSETREADVoltage.set(0.2) #volts, CHANGE IF NECESSARY

        #NOTE: All voltage values to be inputted to the PCB are in
        #MILLIVOLTS, so perform the conversion during the byte
        #splitting process (1000 millivolts = 1 volt)
        #NOTE: For the sake of all byte information being in "Int" format,
        #convert the floats to integers post multiplication
        self.MSBFORMSETVoltHexInt, self.LSBFORMSETVoltHexInt = \
                           twoByteComboSplit(int(self.FORMSETREADVoltage.get() * 1000))
        self.byte11_FORMSETREADVoltageMSB.set(str(self.MSBFORMSETVoltHexInt))
        self.byte12_FORMSETREADVoltageLSB.set(str(self.LSBFORMSETVoltHexInt))

        # - - - - - - - -

        self.FORMSETREADTime.set(500) #microseconds, CHANGE IF NECESSARY
        self.MSBFORMSETREADTimeHexInt, self.LSBFORMSETREADTimeHexInt = \
                              twoByteComboSplit(self.FORMSETREADTime.get())
        self.byte13_FORMSETREADTimeMSB.set(str(self.MSBFORMSETREADTimeHexInt))
        self.byte14_FORMSETREADTimeLSB.set(str(self.LSBFORMSETREADTimeHexInt))

        # - - - - - - - -

        self.RESETVoltage.set(1) #volts, CHANGE IF NECESSARY

        #NOTE: All voltage values to be inputted to the PCB are in
        #MILLIVOLTS, so perform the conversion during the byte
        #splitting process (1000 millivolts = 1 volt)
        #NOTE: For the sake of all byte information being in "Int" format,
        #convert the floats to integers post multiplication
        self.MSBGateVoltHexInt, self.LSBGateVoltHexInt = \
                           twoByteComboSplit(int(self.RESETVoltage.get() * 1000))
        self.byte15_RESETVoltageMSB.set(str(self.MSBGateVoltHexInt))
        self.byte16_RESETVoltageLSB.set(str(self.LSBGateVoltHexInt))

        # - - - - - -

        self.RESETTime.set(100) #microseconds, CHANGE IF NECESSARY
        self.MSBRESETTimeHexInt, self.LSBRESETTimeHexInt = \
                          twoByteComboSplit(self.RESETTime.get())
        self.byte17_RESETTimeMSB.set(str(self.MSBRESETTimeHexInt))
        self.byte18_RESETTimeLSB.set(str(self.LSBRESETTimeHexInt))

        # - - - - - - - -

        self.RESETREADVoltage.set(0.2) #volts, CHANGE IF NECESSARY

        #NOTE: All voltage values to be inputted to the PCB are in
        #MILLIVOLTS, so perform the conversion during the byte
        #splitting process (1000 millivolts = 1 volt)
        #NOTE: For the sake of all byte information being in "Int" format,
        #convert the floats to integers post multiplication
        self.MSBRESETVoltHexInt, self.LSBRESETVoltHexInt = \
                           twoByteComboSplit(int(self.RESETREADVoltage.get() * 1000))
        self.byte19_RESETREADVoltageMSB.set(str(self.MSBRESETVoltHexInt))
        self.byte20_RESETREADVoltageLSB.set(str(self.LSBRESETVoltHexInt))

        # - - - - - - - -

        self.RESETREADTime.set(500) #microseconds, CHANGE IF NECESSARY
        self.MSBRESETREADTimeHexInt, self.LSBRESETREADTimeHexInt = \
                              twoByteComboSplit(self.RESETREADTime.get())
        self.byte21_RESETREADTimeMSB.set(str(self.MSBRESETREADTimeHexInt))
        self.byte22_RESETREADTimeLSB.set(str(self.LSBRESETREADTimeHexInt))

        # - - - - - - - -

        self.cycleNumber.set(1)
        self.MSBCycleNumberHexInt, self.LSBCycleNumberHexInt = \
                            twoByteComboSplit(self.cycleNumber.get())
        self.byte25_CyclesNumberMSB.set(str(self.MSBCycleNumberHexInt))
        self.byte26_CyclesNumberLSB.set(str(self.LSBCycleNumberHexInt))

        # - - - - - - - -

        self.stepNumber.set(0) #set to 0 for PULSE TESTING default
        self.MSBStepNumberHexInt, self.LSBStepNumberHexInt = \
                            twoByteComboSplit(self.stepNumber.get())
        self.byte27_StepNumberMSB.set(str(self.MSBStepNumberHexInt))
        self.byte28_StepNumberLSB.set(str(self.LSBStepNumberHexInt))

        # - - - - - - - -

        #PULSE TESTING defaults, seeing that the code opens with
        #the Pulse Test window
        self.byte29_modeState.set('Pulse Test')

        self.IVTestState.set('None')

        self.maxStepVoltage.set(2) #volts, CHANGE IF NECESSARY, PULSE STEP TEST ONLY

        self.chosenStepVoltage.set('None')
        self.stepVoltageDirection.set('None')

        # - - - - - - - -

        #PULSE TEST SET/RESET SWITCH AND IV TESTING DEFAULTS

        self.SETGateVoltage.set(self.gateVoltage.get())
        self.RESETGateVoltage.set(3.3)

        # - - - - - - - -

        #Other variables to utilize as Tkinter widget variables to
        #be changed/shared between programs
        
        self.toggledOhmsLawUnit = StringVar()
        self.toggledOhmsLawUnit.set('uA') #start as "current" (microAmps)

        #.csv interaction variable to be altered in toggle CheckButton widget
        self.csvControlVariable = BooleanVar()

        #interaction variable for changing the IV state test from the default
        #SET->RESET order to the inverse (RESET->SET)
        self.invertIVStates = BooleanVar()
        self.invertIVStates.set('False')

        #string of driver to search for expected board port
        #NOTE: String input is to be dependent on the installed driver,
        #with the one below being obtained from the following website:
        #https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
        #CHANGE IF NECESSARY
        self.expectedPortDriverSearch = StringVar()
        self.expectedPortDriverSearch.set('Silicon Labs CP210x')

        #runtime Boolean toggle to print run time if set
        self.showRunTime = BooleanVar()

        #toggle for choosing to generate and save plots
        self.createSavePlots = BooleanVar()

        #toggle for PULSE TEST to decide if a current/resistance range for
        #a selectable number of cycles should be implemented
        self.utilizeCurResRange = BooleanVar()

        #toggle for PULSE TEST to decide if a heatmap is created
        self.createHeatMap = BooleanVar()

        #corresponding PULSE TEST range entry variables
        self.pulseTestRangeMin = DoubleVar()
        self.pulseTestRangeMax = DoubleVar()
        self.pulseTestRangeCycleCount = IntVar()

        #toggle for PULSE TEST to HARD CODE (...) selected devices/cells with specific
        #RESET values and non-selected devices/cells with specific SET values
        #NOTE: this is at Jeelka's and Dr. Cady's request, alongside the specific
        #hard coded values, hard coding is otherwise not encouraged by this programmer
        self.hardCodeDevices = BooleanVar()

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #to match Jeelka's formatting request, create two frames, one for the
        #buttons and the other for the Canvas with all of the buttons

        #button frame (to the left of the master window)
        #NOTE: bg = background (color), bd = border width, relief = controls appearance of border
        self.ModeButtonFrame = Frame(masterWindow, bg = 'lightblue')
        self.ModeButtonFrame.grid(row = 0, column = 0, sticky = 'nsew') #left most column of the two

        # - - - - - - - - - - - - - - - - - - -

        #add the buttons to the button frame, as these will not change
        #all call their respective class functions for deconstructing and reconstructing the canvas upon
        #button presses
        #Pulse Test (NOT step voltage pulse test)
        self.pulseButton = Button(self.ModeButtonFrame, text = 'Pulse Testing', \
                                     command = self.createPulseCanvas, padx = 5, \
                                     pady = 20, bg = 'light gray')
        self.pulseButton.grid(row = 0, column = 0, sticky = 'nsew', \
                              padx = 10, pady = 10) #top button to match Jeelka's format request

        # - - - - - - - -

        #Pulse Test - Step Voltage
        self.pulseStepButton = Button(self.ModeButtonFrame, text = 'Pulse Testing - Step Voltage', \
                                     command = self.createPulseStepCanvas, padx = 5, \
                                     pady = 20, bg = 'light gray')
        self.pulseStepButton.grid(row = 1, column = 0, sticky = 'nsew', \
                              padx = 10, pady = 10) #second from top button to match Jeelka's format request

        # - - - - - - - -

        #Pulse Test (NOT step voltage pulse test) - SET/RESET Alternating per cycle
        self.pulseSETRESETSwitchButton = Button(self.ModeButtonFrame, text = 'Pulse Testing - SET/RESET Switch per Cycle', \
                                     command = self.createPulseSETRESETSwitchCanvas, padx = 5, \
                                     pady = 20, bg = 'light gray')
        self.pulseSETRESETSwitchButton.grid(row = 2, column = 0, sticky = 'nsew', \
                              padx = 10, pady = 10) #third from top button to match Jeelka's format request

        # - - - - - - - -

        #IV Test
        self.IVTestButton = Button(self.ModeButtonFrame, text = 'IV Testing', \
                                     command = self.createIVCanvas, padx = 5, \
                                     pady = 20, bg = 'light gray')
        self.IVTestButton.grid(row = 3, column = 0, sticky = 'nsew', \
                              padx = 10, pady = 10) #bottom button to match Jeelka's format request

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #create overarching Canvas frame (to the right of the master window)
        #NOTE: bg = background (color), bd = border width, relief = controls appearance of border
        self.ModeCanvasFrame = Frame(masterWindow, bd = 2, relief = 'solid')
        self.ModeCanvasFrame.grid(row = 0, column = 1, sticky = 'nsew') #right most column of the two

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #create all canvases WITH THEIR INFORMATION PROVIDED BELOW

        '''
        pulse testing canvas (NOT step voltage)
        '''
        self.pulseCanvas = Canvas(self.ModeCanvasFrame, width = 625, height = 500)

        #separates canvases into N number of equally spaced columns/rows
        self.pulseCanvas.grid(rowspan = 20, columnspan = 4)

        masterWindow.update() #update masterWindow to save Canvas dimensions

        # - - - - - - - - - - - - -

        #create and place title label
        self.titlePulseLabel = Label(self.pulseCanvas, text = 'Pulse Test Mode', font = \
                       ('calibre', 20, 'bold'))
        self.titlePulseLabel.place(x = 45, y = 25)

        # - - - - - - - - - - - - -

        #at Jeelka's request, she wants all Entry boxes to have the same
        #X position in their respective column, so the following variable
        #will be used to store the maximum X position of each of the
        #Entry boxes in this column before setting them all to this value
        self.maxEntryXPosFirstColumn = 0
        self.maxEntryXPosSecondColumn = 0
        self.foundFirstColumnEntryPos = False
        self.foundSecondColumnEntryPos = False

        #setup canvas for all adjustable byte values

        #gate voltage
        #variable label
        self.gateVoltageLabel = Label(self.pulseCanvas, text = 'Gate Voltage:', font = \
                       ('calibre', 10, 'normal'))
        self.gateVoltageLabel.place(x = 5, y = 70)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.gateVoltageLabel.update()

        #entry widget to input data
        self.gateVoltageEntry = Entry(self.pulseCanvas, width = 6, textvariable = self.gateVoltage, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.gateVoltageEntry.place(x = int(self.gateVoltageLabel.place_info()['x']) + \
                                    int(self.gateVoltageLabel.winfo_width()), y = \
                                    self.gateVoltageLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.gateVoltageEntry.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumn
        if(self.maxEntryXPosFirstColumn < \
           int(self.gateVoltageEntry.place_info()['x'])):
            self.maxEntryXPosFirstColumn = \
                int(self.gateVoltageEntry.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #delay time period
        #variable label
        #NOTE: new "column", hence the hard coded X value this time to shift to the right
        #NOTE: MOVED UP HERE TO BE PREPARED BEFORE CALLING "changeFORMSETState" FUNCTION TO
        #ADDRESS THE VARIABLES OF THIS COMBO
        self.secondColumnXPos = 200
        self.delayPeriodLabel = Label(self.pulseCanvas, text = 'Delay Period:', font = \
                       ('calibre', 10, 'normal'))
        self.delayPeriodLabel.place(x = self.secondColumnXPos, y = int(self.gateVoltageLabel.place_info()['y']))

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.delayPeriodLabel.update()

        #entry widget to input data
        self.delayPeriodEntry = Entry(self.pulseCanvas, width = 6, textvariable = self.delayPeriodTime, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.delayPeriodEntry.place(x = int(self.delayPeriodLabel.place_info()['x']) + \
                                    int(self.delayPeriodLabel.winfo_width()), y = \
                                    self.delayPeriodLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.delayPeriodEntry.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumn
        if(self.maxEntryXPosSecondColumn < \
           int(self.delayPeriodEntry.place_info()['x'])):
            self.maxEntryXPosSecondColumn = \
                int(self.delayPeriodEntry.place_info()['x'])

        # - - - - - - - - - - - - -

        #toggle to decide between FORM state or SET state for inputted data (can ONLY BE ONE
        #OF THESE STATES AT A TIME for pulse test)

        #prompt label
        #NOTE: X and Y dimension positions based on existing widget dimensions
        #within the canvas above to avoid requiring hard coded values for each set of widgets
        self.FORMOrSETLabel = Label(self.pulseCanvas, text = 'Select FORM/SET state:', font = \
                       ('calibre', 10, 'normal'))
        self.FORMOrSETLabel.place(x = int(self.gateVoltageLabel.place_info()['x']), y = \
                                  int(self.gateVoltageLabel.place_info()['y']) + \
                                  int(self.gateVoltageLabel.winfo_height() + 5))

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.FORMOrSETLabel.update()

        #create the two buttons associated with the two states of interest and have them
        #call the same function to change the state information accordingly
        self.FORMSelectButton = Button(self.pulseCanvas, text = 'FORM')
        self.SETSelectButton = Button(self.pulseCanvas, text = 'SET')

        self.FORMSelectButton.config(command = lambda: self.changeFORMSETState('FORM', \
                                    self.FORMSelectButton, self.SETSelectButton, \
                                    self.startRun, self.maxEntryXPosFirstColumn, \
                                    self.foundFirstColumnEntryPos, self.maxEntryXPosSecondColumn, \
                                    self.foundSecondColumnEntryPos, self.FORMSETStateString), \
                                    padx = 1, pady = 2, bg = 'light gray')
        self.FORMSelectButton.place(x = int(self.FORMOrSETLabel.place_info()['x']) + 15, y = \
                                  int(self.FORMOrSETLabel.place_info()['y']) + \
                                  int(self.FORMOrSETLabel.winfo_height()))

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.FORMSelectButton.update()
        
        self.SETSelectButton.config(command = lambda: self.changeFORMSETState('SET', \
                                    self.FORMSelectButton, self.SETSelectButton, \
                                    self.startRun, self.maxEntryXPosFirstColumn, \
                                    self.foundFirstColumnEntryPos, self.maxEntryXPosSecondColumn, \
                                    self.foundSecondColumnEntryPos, self.FORMSETStateString), \
                                    padx = 1, pady = 2, bg = 'light gray')
        self.SETSelectButton.place(x = int(self.FORMSelectButton.place_info()['x']) + \
                                   int(self.FORMSelectButton.winfo_width()) + 15, y = \
                                  int(self.FORMSelectButton.place_info()['y']))
        
        #for initial run, start with FORM state by calling changeFORMSETState function
        if(self.startRun):
            self.changeFORMSETState('FORM', self.FORMSelectButton, \
                                    self.SETSelectButton, self.startRun, \
                                    self.maxEntryXPosFirstColumn, self.foundFirstColumnEntryPos, \
                                    self.maxEntryXPosSecondColumn, self.foundSecondColumnEntryPos, \
                                    self.FORMSETStateString)

        # - - - - - - - - - - - - -

        #RESET voltage
        #variable label
        #NOTE: Y axis value hard coded this time to avoid having to work with buttons getting
        #height outputs from the changeFORMSETState function
        self.RESETVoltageLabel = Label(self.pulseCanvas, text = 'RESET Voltage:', font = \
                       ('calibre', 10, 'normal'))
        self.RESETVoltageLabel.place(x = int(self.gateVoltageLabel.place_info()['x']),\
                                     y = 205)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETVoltageLabel.update()

        #entry widget to input data
        self.RESETVoltageEntry = Entry(self.pulseCanvas, width = 6, textvariable = self.RESETVoltage, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.RESETVoltageEntry.place(x = int(self.RESETVoltageLabel.place_info()['x']) + \
                                    int(self.RESETVoltageLabel.winfo_width()), y = \
                                    self.RESETVoltageLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETVoltageEntry.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumn
        if(self.maxEntryXPosFirstColumn < \
           int(self.RESETVoltageEntry.place_info()['x'])):
            self.maxEntryXPosFirstColumn = \
                int(self.RESETVoltageEntry.place_info()['x'])

        # - - - - - - - - - - - - -

        #RESET time
        #variable label
        self.RESETTimeLabel = Label(self.pulseCanvas, text = 'RESET Time:', font = \
                       ('calibre', 10, 'normal'))
        self.RESETTimeLabel.place(x = int(self.gateVoltageLabel.place_info()['x']), y = \
                                  int(self.RESETVoltageLabel.place_info()['y']) + \
                                  int(self.RESETVoltageLabel.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETTimeLabel.update()

        #entry widget to input data
        self.RESETTimeEntry = Entry(self.pulseCanvas, width = 6, textvariable = self.RESETTime, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.RESETTimeEntry.place(x = int(self.RESETTimeLabel.place_info()['x']) + \
                                    int(self.RESETTimeLabel.winfo_width()), y = \
                                    self.RESETTimeLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETTimeEntry.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumn
        if(self.maxEntryXPosFirstColumn < \
           int(self.RESETTimeEntry.place_info()['x'])):
            self.maxEntryXPosFirstColumn = \
                int(self.RESETTimeEntry.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #with the found maxEntryXPosFirstColumn (ignored row and column
        #Entries above since they clearly aren't the longest), adjust
        #all entry and unit label positions for this row
        #NOTE: all unit label positions set HERE now

        #count the number of entries here to avoid having to worry
        #about repeating these through the same logic again
        entryCounter = 0

        for widgetItem in self.pulseCanvas.winfo_children():
            if(isinstance(widgetItem, tk.Entry)): #if an Entry, prepare to move position

                #IGNORE ANY SECOND COLUMN WIDGETS WITHIN THIS LOOP (specifically
                #the delay period widget, but keep this ambiguous for better coding
                #practices)
                if(int(widgetItem.place_info()['x']) >= self.secondColumnXPos):
                    entryCounter += 1
                    continue
                widgetItem.place(x = self.maxEntryXPosFirstColumn, \
                                y = widgetItem.place_info()['y'])
                widgetItem.update()
                entryCounter += 1

        self.foundFirstColumnEntryPos = True

        #gate voltage unit label
        self.gateVoltageUnitLabel = Label(self.pulseCanvas, text = 'V', font = \
                       self.gateVoltageLabel['font'])
        self.gateVoltageUnitLabel.place(x = int(self.gateVoltageEntry.place_info()['x']) + \
                                    int(self.gateVoltageEntry.winfo_width()), y = \
                                    self.gateVoltageLabel.place_info()['y'])

        #reset voltage unit label
        self.RESETVoltageUnitLabel = Label(self.pulseCanvas, text = 'V', font = \
                       self.gateVoltageLabel['font'])
        self.RESETVoltageUnitLabel.place(x = int(self.RESETVoltageEntry.place_info()['x']) + \
                                    int(self.RESETVoltageEntry.winfo_width()), y = \
                                    self.RESETVoltageEntry.place_info()['y'])

        #reset time unit label
        self.RESETTimeUnitLabel = Label(self.pulseCanvas, text = 'us', font = \
                       self.gateVoltageLabel['font'])
        self.RESETTimeUnitLabel.place(x = int(self.RESETTimeEntry.place_info()['x']) + \
                                    int(self.RESETTimeEntry.winfo_width()), y = \
                                    self.RESETTimeEntry.place_info()['y'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #RESET READ Voltage
        #variable label
        #NOTE: Y axis value hard coded this time to avoid having to work with buttons getting
        #height outputs from the changeFORMSETState function
        self.RESETREADVoltageLabel = Label(self.pulseCanvas, text = 'RESET READ Voltage:', font = \
                       ('calibre', 10, 'normal'))
        self.RESETREADVoltageLabel.place(x = int(self.delayPeriodLabel.place_info()['x']), y = 150)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETREADVoltageLabel.update()

        #entry widget to input data
        self.RESETREADVoltageEntry = Entry(self.pulseCanvas, width = 6, textvariable = self.RESETREADVoltage, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.RESETREADVoltageEntry.place(x = int(self.RESETREADVoltageLabel.place_info()['x']) + \
                                    int(self.RESETREADVoltageLabel.winfo_width()), y = \
                                    self.RESETREADVoltageLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETREADVoltageEntry.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumn
        if(self.maxEntryXPosSecondColumn < \
           int(self.RESETREADVoltageEntry.place_info()['x'])):
            self.maxEntryXPosSecondColumn = \
                int(self.RESETREADVoltageEntry.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #RESET READ Time
        #variable label
        self.RESETREADTimeLabel = Label(self.pulseCanvas, text = 'RESET READ Time:', font = \
                       ('calibre', 10, 'normal'))
        self.RESETREADTimeLabel.place(x = int(self.delayPeriodLabel.place_info()['x']), y = \
                                  int(self.RESETREADVoltageLabel.place_info()['y']) + \
                                  int(self.RESETREADVoltageLabel.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETREADTimeLabel.update()

        #entry widget to input data
        self.RESETREADTimeEntry = Entry(self.pulseCanvas, width = 6, textvariable = self.RESETREADTime, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.RESETREADTimeEntry.place(x = int(self.RESETREADTimeLabel.place_info()['x']) + \
                                    int(self.RESETREADTimeLabel.winfo_width()), y = \
                                    self.RESETREADTimeLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETREADTimeEntry.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumn
        if(self.maxEntryXPosSecondColumn < \
           int(self.RESETREADTimeEntry.place_info()['x'])):
            self.maxEntryXPosSecondColumn = \
                int(self.RESETREADTimeEntry.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #Cycle Number
        #variable label
        self.cycleNumberLabel = Label(self.pulseCanvas, text = 'Cycle Number:', font = \
                       ('calibre', 10, 'normal'))
        self.cycleNumberLabel.place(x = int(self.delayPeriodLabel.place_info()['x']), y = \
                                  int(self.RESETREADTimeLabel.place_info()['y']) + \
                                  int(self.RESETREADTimeLabel.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.cycleNumberLabel.update()

        #entry widget to input data
        self.cycleNumberEntry = Entry(self.pulseCanvas, width = 6, textvariable = self.cycleNumber, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.cycleNumberEntry.place(x = int(self.cycleNumberLabel.place_info()['x']) + \
                                    int(self.cycleNumberLabel.winfo_width()), y = \
                                    self.cycleNumberLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.cycleNumberLabel.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumn
        if(self.maxEntryXPosSecondColumn < \
           int(self.cycleNumberEntry.place_info()['x'])):
            self.maxEntryXPosSecondColumn = \
                int(self.cycleNumberEntry.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #with the found maxEntryXPosSecondColumn (ignored row and column
        #Entries above since they clearly aren't the longest), adjust
        #all entry and unit label positions for this row
        #NOTE: all unit label positions set HERE now

        for widgetItem in self.pulseCanvas.winfo_children():
            if(isinstance(widgetItem, tk.Entry)): #if an Entry, prepare to move position

                #shift ONLY THE ENTRIES IN THE SECOND COLUMN BASED ON ASSIGNED
                #secondColumnXPos POSITION
                if(int(widgetItem.place_info()['x']) >= self.secondColumnXPos):

                    widgetItem.place(x = self.maxEntryXPosSecondColumn, \
                                y = widgetItem.place_info()['y'])
                    widgetItem.update()

        self.foundSecondColumnEntryPos = True

        #delay period unit label
        self.delayPeriodUnitLabel = Label(self.pulseCanvas, text = 'us', font = \
                       self.gateVoltageLabel['font'])
        self.delayPeriodUnitLabel.place(x = int(self.delayPeriodEntry.place_info()['x']) + \
                                    int(self.delayPeriodEntry.winfo_width()), y = \
                                    self.delayPeriodEntry.place_info()['y'])

        #RESET READ Voltage unit label
        self.RESETREADVoltageUnitLabel = Label(self.pulseCanvas, text = 'V', font = \
                       self.gateVoltageLabel['font'])
        self.RESETREADVoltageUnitLabel.place(x = int(self.RESETREADVoltageEntry.place_info()['x']) + \
                                    int(self.RESETREADVoltageEntry.winfo_width()), y = \
                                    self.RESETREADVoltageEntry.place_info()['y'])


        #RESET READ Time unit label
        self.RESETREADTimeUnitLabel = Label(self.pulseCanvas, text = 'us', font = \
                       self.gateVoltageLabel['font'])
        self.RESETREADTimeUnitLabel.place(x = int(self.RESETREADTimeEntry.place_info()['x']) + \
                                    int(self.RESETREADTimeEntry.winfo_width()), y = \
                                    self.RESETREADTimeEntry.place_info()['y'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #PULSE TEST current/resistance range checkbox
        self.utilizeCurResRangeCheckBoxButton = Checkbutton(self.pulseCanvas, text = \
                                'Select Ranges\nfor Read-Write\nVerification', variable = self.utilizeCurResRange)
        self.utilizeCurResRangeCheckBoxButton.place(x = 350, y = 265)

        #create corresponding range text and Entries
        self.rangeVerificationTitleLabel = Label(self.pulseCanvas, text = \
                                ''.join(['Read-Write Range (', self.toggledOhmsLawUnit.get(), ')']))
        self.rangeVerificationTitleLabel.place(x = 120, y = 262)

        #minimum range label and entry box
        self.rangeMinLabel = Label(self.pulseCanvas, text = 'Min: ')
        self.rangeMinLabel.place(x = 90, y = 282)
        self.rangeMinLabel.update() #update to get rangeMinLabel position for Entry positioning below
        self.rangeMinEntry = Entry(self.pulseCanvas, width = 6, textvariable = self.pulseTestRangeMin, \
                                   font = self.gateVoltageLabel['font'], bg = 'white')
        self.rangeMinEntry.place(x = int(self.rangeMinLabel.place_info()['x']) + \
                                    int(self.rangeMinLabel.winfo_width()), y = \
                                    self.rangeMinLabel.place_info()['y'])
        self.rangeMinEntry.update() #update to get rangeMinEntry position for label positioning below

        #text label for range dash character (aesthetic only)
        self.rangeDashCharLabel = Label(self.pulseCanvas, text = ' - ')
        self.rangeDashCharLabel.place(x = int(self.rangeMinEntry.place_info()['x']) + \
                                    int(self.rangeMinEntry.winfo_width()), y = \
                                    self.rangeMinEntry.place_info()['y'])
        self.rangeDashCharLabel.update() #update to get rangeDashCharLabel position for label positioning below

        #maximum range label and entry box
        self.rangeMaxLabel = Label(self.pulseCanvas, text = 'Max: ')
        self.rangeMaxLabel.place(x = int(self.rangeDashCharLabel.place_info()['x']) + \
                                    int(self.rangeDashCharLabel.winfo_width()), y = \
                                    self.rangeDashCharLabel.place_info()['y'])
        self.rangeMaxLabel.update() #update to get rangeMaxLabel position for Entry positioning below
        self.rangeMaxEntry = Entry(self.pulseCanvas, width = 7, textvariable = self.pulseTestRangeMax, \
                                   font = self.gateVoltageLabel['font'], bg = 'white')
        self.rangeMaxEntry.place(x = int(self.rangeMaxLabel.place_info()['x']) + \
                                    int(self.rangeMaxLabel.winfo_width()), y = \
                                    self.rangeMaxLabel.place_info()['y'])
        self.rangeMaxEntry.update() #update to get rangeMaxEntry position for label positioning below

        #text label for comma separating the range from the range cycle (aeshetic only)
        self.rangeCommaCharLabel = Label(self.pulseCanvas, text = ', ')
        self.rangeCommaCharLabel.place(x = int(self.rangeMaxEntry.place_info()['x']) + \
                                    int(self.rangeMaxEntry.winfo_width()), y = \
                                    self.rangeMaxEntry.place_info()['y'])
        self.rangeCommaCharLabel.update() #update to get rangeCommaCharLabel position for label positioning below

        #maximum number of cycles to check the established range label and entry box
        self.rangeMaxCycleLabel = Label(self.pulseCanvas, text = 'Max Cycle Limit: ')
        self.rangeMaxCycleLabel.place(x = int(self.rangeMinLabel.place_info()['x']) + 20, y = \
                                    int(self.rangeMinLabel.place_info()['y']) + 25)
        self.rangeMaxCycleLabel.update() #update to get rangeMaxCycleLabel position for Entry positioning below
        self.rangeMaxCycleEntry = Entry(self.pulseCanvas, width = 6, textvariable = self.pulseTestRangeCycleCount, \
                                   font = self.gateVoltageLabel['font'], bg = 'white')
        self.rangeMaxCycleEntry.place(x = int(self.rangeMaxCycleLabel.place_info()['x']) + \
                                    int(self.rangeMaxCycleLabel.winfo_width()), y = \
                                    self.rangeMaxCycleLabel.place_info()['y'])
        
        # - - - - - - - - - - - - - - - - - - - - - - - -

        #"Unit" Button FOR PULSE TEST and Label to toggle between Current (uA)
        #and Resistance (KOhm) in an Ohm's Law relationship (V = IR) for output
        #display of non-Voltage units
        self.toggleOhmsLawUnitLabel = Label(self.pulseCanvas, text = 'Unit:')
        self.toggleOhmsLawUnitLabel.place(x = 350, y = 400)

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.toggleOhmsLawUnitLabel.update()

        #calls built-in "toggleOhmsLawUnit" function when pressed AND displays
        #the current/changed unit on the button
        self.toggleOhmsLawUnitButton = Button(self.pulseCanvas, text = \
                                    self.toggledOhmsLawUnit.get(), command = lambda: \
                                    toggleOhmsLawUnit(self.toggledOhmsLawUnit, \
                                    self.toggleOhmsLawUnitButton, self.rangeVerificationTitleLabel), \
                                    width = 5, padx = 2, pady = 1, \
                                    bg = 'light gray')
        
        self.toggleOhmsLawUnitButton.place(x = int(self.toggleOhmsLawUnitLabel.place_info()['x']) + \
                                    int(self.toggleOhmsLawUnitLabel.winfo_width()), y = \
                                    int(self.toggleOhmsLawUnitLabel.place_info()['y']))

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #export to .csv file checkbox FOR PULSE TEST
        self.exportCheckBoxButton = Checkbutton(self.pulseCanvas, text = \
                                'Export to CSV', variable = self.csvControlVariable)
        self.exportCheckBoxButton.place(x = 350, y = 365)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        
        #checkbox FOR PULSE TEST to choose to print out the runtime of the
        #"pressedSubmitData" function
        self.runtimeCheckBoxButton = Checkbutton(self.pulseCanvas, text = \
                                'Print RunTime', variable = self.showRunTime)
        self.runtimeCheckBoxButton.place(x = 350, y = 340)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #PULSE TEST generate/save plots checkbox
        self.createSavePlotsCheckBoxButton = Checkbutton(self.pulseCanvas, text = \
                                'Create Plots', variable = self.createSavePlots)
        self.createSavePlotsCheckBoxButton.place(x = 350, y = 315)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #PULSE TEST heat map selection checkbox for creating a heatmap plot
        #(ONLY WHEN PLOTTING)
        self.heatMapCheckBoxButton = Checkbutton(self.pulseCanvas, text = \
                                'Make Heatmap', variable = self.createHeatMap)
        self.heatMapCheckBoxButton.place(x = 350, y = 245)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #PULSE TEST checkbox to hard code devices to specific SET or RESET values
        #based on whether or not a device is selected (i.e. the unselected devices
        #are NOT ignored but instead of specific values)
        self.hardCodeDevicesCheckBoxButton = Checkbutton(self.pulseCanvas, text = \
                                'Hard Code SET/RESET\n for all devices', variable = self.hardCodeDevices)
        self.hardCodeDevicesCheckBoxButton.place(x = 470, y = 240)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #message text box FOR PULSE TEST (as a ListBox to have scrolling
        #functionality for this version)
        self.messageListBox = Listbox(self.pulseCanvas, bd = 1, relief = SUNKEN, height = 4, \
                                 width = 44, bg = 'light gray', justify = CENTER)
        self.messageListBox.place(x = 50, y = 420)

        self.messageListScrollLabel = Label(self.pulseCanvas, text = \
                                       'Output Display Window')
        self.messageListScrollLabel.place(x = 120, y = 400)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #clear button FOR PULSE TEST

        #calls built-in "pressedClearOutput" function when button is pressed
        self.clearButton = Button(self.pulseCanvas, text = 'Clear', command = lambda: \
                             pressedClearOutput(self.messageListBox), padx = 8, \
                             pady = 15, bg = 'white')
        self.clearButton.place(x = 330, y = 435)

        #------------------------------------------------------

        '''
        pulse STEP VOLTAGE testing canvas
        '''
        self.pulseStepCanvas = Canvas(self.ModeCanvasFrame, width = 450, height = 600)

        #separates canvases into N number of equally spaced columns/rows
        self.pulseStepCanvas.grid(rowspan = 20, columnspan = 4)

        masterWindow.update() #update masterWindow to save Canvas dimensions

        # - - - - - - - - - - - - -

        #create and place title label
        self.titlePulseStepLabel = Label(self.pulseStepCanvas, text = 'Pulse Test Mode - Step Voltage', font = \
                       ('calibre', 20, 'bold'))
        self.titlePulseStepLabel.place(x = 20, y = 25)

        # - - - - - - - - - - - - -

        #at Jeelka's request, she wants all Entry boxes to have the same
        #X position in their respective column, so the following variable
        #will be used to store the maximum X position of each of the
        #Entry boxes in this column before setting them all to this value
        self.maxEntryXPosFirstColumnStep = 0
        self.maxEntryXPosSecondColumnStep = 0
        self.foundFirstColumnEntryPosStep = False
        self.foundSecondColumnEntryPosStep = False

        #setup canvas for all adjustable byte values

        #gate voltage
        #variable label
        self.gateVoltageLabelStep = Label(self.pulseStepCanvas, text = 'Gate Voltage:', font = \
                       ('calibre', 10, 'normal'))
        self.gateVoltageLabelStep.place(x = 5, y = 70)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.gateVoltageLabelStep.update()

        #entry widget to input data
        self.gateVoltageEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = self.gateVoltage, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.gateVoltageEntryStep.place(x = int(self.gateVoltageLabelStep.place_info()['x']) + \
                                    int(self.gateVoltageLabelStep.winfo_width()), y = \
                                    self.gateVoltageLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.gateVoltageEntryStep.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnStep
        if(self.maxEntryXPosFirstColumnStep < \
           int(self.gateVoltageEntryStep.place_info()['x'])):
            self.maxEntryXPosFirstColumnStep = \
                int(self.gateVoltageEntryStep.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #delay time period
        #variable label
        #NOTE: new "column", hence the hard coded X value this time to shift to the right
        #NOTE: MOVED UP HERE TO BE PREPARED BEFORE CALLING "changeFORMSETState" FUNCTION TO
        #ADDRESS THE VARIABLES OF THIS COMBO
        self.secondColumnXPosStep = 210
        self.delayPeriodLabelStep = Label(self.pulseStepCanvas, text = 'Delay Period:', font = \
                       ('calibre', 10, 'normal'))
        self.delayPeriodLabelStep.place(x = self.secondColumnXPosStep, y = \
                        int(self.gateVoltageLabelStep.place_info()['y']))

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.delayPeriodLabelStep.update()

        #entry widget to input data
        self.delayPeriodEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = self.delayPeriodTime, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.delayPeriodEntryStep.place(x = int(self.delayPeriodLabelStep.place_info()['x']) + \
                                    int(self.delayPeriodLabelStep.winfo_width()), y = \
                                    self.delayPeriodLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.delayPeriodEntryStep.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumnStep
        if(self.maxEntryXPosSecondColumnStep < \
           int(self.delayPeriodEntryStep.place_info()['x'])):
            self.maxEntryXPosSecondColumnStep = \
                int(self.delayPeriodEntryStep.place_info()['x'])

        # - - - - - - - - - - - - -

        #toggle to decide between FORM state or SET state for inputted data (can ONLY BE ONE
        #OF THESE STATES AT A TIME for pulse test)

        #prompt label
        #NOTE: X and Y dimension positions based on existing widget dimensions
        #within the canvas above to avoid requiring hard coded values for each set of widgets
        self.FORMOrSETLabelStep = Label(self.pulseStepCanvas, text = 'Select FORM/SET state:', font = \
                       ('calibre', 10, 'normal'))
        self.FORMOrSETLabelStep.place(x = int(self.gateVoltageLabelStep.place_info()['x']), y = \
                                  int(self.gateVoltageLabelStep.place_info()['y']) + \
                                  int(self.gateVoltageLabelStep.winfo_height() + 5))

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.FORMOrSETLabelStep.update()

        #create the two buttons associated with the two states of interest and have them
        #call the same function to change the state information accordingly
        self.FORMSelectButtonStep = Button(self.pulseStepCanvas, text = 'FORM')
        self.SETSelectButtonStep = Button(self.pulseStepCanvas, text = 'SET')

        self.FORMSelectButtonStep.config(command = lambda: self.changeFORMSETStateStep('FORM', \
                                    self.FORMSelectButtonStep, self.SETSelectButtonStep, \
                                    self.startRun, self.maxEntryXPosFirstColumnStep, \
                                    self.foundFirstColumnEntryPosStep, self.maxEntryXPosSecondColumnStep, \
                                    self.foundSecondColumnEntryPosStep, self.FORMSETStateString), \
                                    padx = 1, pady = 2, bg = 'light gray')
        self.FORMSelectButtonStep.place(x = int(self.FORMOrSETLabelStep.place_info()['x']) + 15, y = \
                                  int(self.FORMOrSETLabelStep.place_info()['y']) + \
                                  int(self.FORMOrSETLabelStep.winfo_height()))

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.FORMSelectButtonStep.update()
        
        self.SETSelectButtonStep.config(command = lambda: self.changeFORMSETStateStep('SET', \
                                    self.FORMSelectButtonStep, self.SETSelectButtonStep, \
                                    self.startRun, self.maxEntryXPosFirstColumnStep, \
                                    self.foundFirstColumnEntryPosStep, self.maxEntryXPosSecondColumnStep, \
                                    self.foundSecondColumnEntryPosStep, self.FORMSETStateString), \
                                    padx = 1, pady = 2, bg = 'light gray')
        self.SETSelectButtonStep.place(x = int(self.FORMSelectButtonStep.place_info()['x']) + \
                                   int(self.FORMSelectButtonStep.winfo_width()) + 15, y = \
                                  int(self.FORMSelectButtonStep.place_info()['y']))

        #start with FORM state by calling changeFORMSETStateStep function
        if(self.startRun):
            self.changeFORMSETStateStep('FORM', self.FORMSelectButtonStep, \
                                    self.SETSelectButtonStep, self.startRun, \
                                    self.maxEntryXPosFirstColumnStep, self.foundFirstColumnEntryPosStep, \
                                    self.maxEntryXPosSecondColumnStep, self.foundSecondColumnEntryPosStep, \
                                    self.FORMSETStateString)

        # - - - - - - - - - - - - -

        #RESET voltage
        #variable label
        #NOTE: Y axis value hard coded this time to avoid having to work with buttons getting
        #height outputs from the changeFORMSETStateStep function
        self.RESETVoltageLabelStep = Label(self.pulseStepCanvas, text = 'Min RESET Voltage:', font = \
                       ('calibre', 10, 'normal'))
        self.RESETVoltageLabelStep.place(x = int(self.gateVoltageLabelStep.place_info()['x']),\
                                     y = 205)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETVoltageLabelStep.update()

        #entry widget to input data
        self.RESETVoltageEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = self.RESETVoltage, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.RESETVoltageEntryStep.place(x = int(self.RESETVoltageLabelStep.place_info()['x']) + \
                                    int(self.RESETVoltageLabelStep.winfo_width()), y = \
                                    self.RESETVoltageLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETVoltageEntryStep.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnStep
        if(self.maxEntryXPosFirstColumnStep < \
           int(self.RESETVoltageEntryStep.place_info()['x'])):
            self.maxEntryXPosFirstColumnStep = \
                int(self.RESETVoltageEntryStep.place_info()['x'])

        # - - - - - - - - - - - - -

        #RESET time
        #variable label
        self.RESETTimeLabelStep = Label(self.pulseStepCanvas, text = 'RESET Time:', font = \
                       ('calibre', 10, 'normal'))
        self.RESETTimeLabelStep.place(x = int(self.gateVoltageLabelStep.place_info()['x']), y = \
                                  int(self.RESETVoltageLabelStep.place_info()['y']) + \
                                  int(self.RESETVoltageLabelStep.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETTimeLabelStep.update()

        #entry widget to input data
        self.RESETTimeEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = self.RESETTime, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.RESETTimeEntryStep.place(x = int(self.RESETTimeLabelStep.place_info()['x']) + \
                                    int(self.RESETTimeLabelStep.winfo_width()), y = \
                                    self.RESETTimeLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETTimeEntryStep.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnStep
        if(self.maxEntryXPosFirstColumnStep < \
           int(self.RESETTimeEntryStep.place_info()['x'])):
            self.maxEntryXPosFirstColumnStep = \
                int(self.RESETTimeEntryStep.place_info()['x'])

        # - - - - - - - - - - - - -

        #MAXIMUM VOLTAGE WIDGET FOR PULSE STEP TEST
        #variable label
        self.maxVoltageLabel = Label(self.pulseStepCanvas, text = 'Max Step Voltage:', font = \
                       ('calibre', 10, 'normal'))
        self.maxVoltageLabel.place(x = int(self.gateVoltageLabelStep.place_info()['x']), y = \
                                  int(self.RESETTimeLabelStep.place_info()['y']) + \
                                  int(self.RESETTimeLabelStep.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.maxVoltageLabel.update()

        #entry widget to input data
        self.maxVoltageEntry = Entry(self.pulseStepCanvas, width = 6, textvariable = self.maxStepVoltage, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.maxVoltageEntry.place(x = int(self.maxVoltageLabel.place_info()['x']) + \
                                    int(self.maxVoltageLabel.winfo_width()), y = \
                                    self.maxVoltageLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.maxVoltageEntry.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnStep
        if(self.maxEntryXPosFirstColumnStep < \
           int(self.maxVoltageEntry.place_info()['x'])):
            self.maxEntryXPosFirstColumnStep = \
                int(self.maxVoltageEntry.place_info()['x'])

        # - - - - - - - - - - - - -

        #STEP VOLTAGE WIDGET FOR PULSE STEP TEST
        #variable label
        self.stepVoltageLabel = Label(self.pulseStepCanvas, text = 'Step #:', font = \
                       ('calibre', 10, 'normal'))
        self.stepVoltageLabel.place(x = int(self.gateVoltageLabelStep.place_info()['x']), y = \
                                  int(self.maxVoltageLabel.place_info()['y']) + \
                                  int(self.maxVoltageLabel.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.stepVoltageLabel.update()

        #entry widget to input data
        self.stepVoltageEntry = Entry(self.pulseStepCanvas, width = 6, textvariable = self.stepNumber, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.stepVoltageEntry.place(x = int(self.stepVoltageLabel.place_info()['x']) + \
                                    int(self.stepVoltageLabel.winfo_width()), y = \
                                    self.stepVoltageLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.stepVoltageEntry.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnStep
        if(self.maxEntryXPosFirstColumnStep < \
           int(self.stepVoltageEntry.place_info()['x'])):
            self.maxEntryXPosFirstColumnStep = \
                int(self.stepVoltageEntry.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #with the found maxEntryXPosFirstColumnStep (ignored row and column
        #Entries above since they clearly aren't the longest), adjust
        #all entry and unit label positions for this row
        #NOTE: all unit label positions set HERE now

        #count the number of entries here to avoid having to worry
        #about repeating these through the same logic again
        entryCounterStep = 0

        for widgetItem in self.pulseStepCanvas.winfo_children():
            if(isinstance(widgetItem, tk.Entry)): #if an Entry, prepare to move position

                #IGNORE ANY SECOND COLUMN WIDGETS WITHIN THIS LOOP (specifically
                #the delay period widget, but keep this ambiguous for better coding
                #practices)
                if(int(widgetItem.place_info()['x']) >= self.secondColumnXPosStep):
                    entryCounterStep += 1
                    continue
                widgetItem.place(x = self.maxEntryXPosFirstColumnStep, \
                                y = widgetItem.place_info()['y'])
                widgetItem.update()
                entryCounterStep += 1

        self.foundFirstColumnEntryPosStep = True

        #gate voltage unit label
        self.gateVoltageUnitLabelStep = Label(self.pulseStepCanvas, text = 'V', font = \
                       self.gateVoltageLabelStep['font'])
        self.gateVoltageUnitLabelStep.place(x = int(self.gateVoltageEntryStep.place_info()['x']) + \
                                    int(self.gateVoltageEntryStep.winfo_width()), y = \
                                    self.gateVoltageLabelStep.place_info()['y'])

        #reset voltage unit label
        self.RESETVoltageUnitLabelStep = Label(self.pulseStepCanvas, text = 'V', font = \
                       self.gateVoltageLabelStep['font'])
        self.RESETVoltageUnitLabelStep.place(x = int(self.RESETVoltageEntryStep.place_info()['x']) + \
                                    int(self.RESETVoltageEntryStep.winfo_width()), y = \
                                    self.RESETVoltageEntryStep.place_info()['y'])

        #reset time unit label
        self.RESETTimeUnitLabelStep = Label(self.pulseStepCanvas, text = 'us', font = \
                       self.gateVoltageLabelStep['font'])
        self.RESETTimeUnitLabelStep.place(x = int(self.RESETTimeEntryStep.place_info()['x']) + \
                                    int(self.RESETTimeEntryStep.winfo_width()), y = \
                                    self.RESETTimeEntryStep.place_info()['y'])

        #maximum voltage unit label
        self.maxVoltageUnitLabel = Label(self.pulseStepCanvas, text = 'V', font = \
                       self.gateVoltageLabelStep['font'])
        self.maxVoltageUnitLabel.place(x = int(self.maxVoltageEntry.place_info()['x']) + \
                                    int(self.maxVoltageEntry.winfo_width()), y = \
                                    self.maxVoltageEntry.place_info()['y'])

        #step voltage unit label
        self.stepVoltageUnitLabel = Label(self.pulseStepCanvas, text = 'V', font = \
                       self.gateVoltageLabelStep['font'])
        self.stepVoltageUnitLabel.place(x = int(self.stepVoltageEntry.place_info()['x']) + \
                                    int(self.stepVoltageEntry.winfo_width()), y = \
                                    self.stepVoltageEntry.place_info()['y'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #RESET READ Voltage
        #variable label
        #NOTE: Y axis value hard coded this time to avoid having to work with buttons getting
        #height outputs from the changeFORMSETStateStep function
        self.RESETREADVoltageLabelStep = Label(self.pulseStepCanvas, text = 'RESET READ Voltage:', font = \
                       ('calibre', 10, 'normal'))
        self.RESETREADVoltageLabelStep.place(x = int(self.delayPeriodLabelStep.place_info()['x']), y = 150)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETREADVoltageLabelStep.update()

        #entry widget to input data
        self.RESETREADVoltageEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = self.RESETREADVoltage, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.RESETREADVoltageEntryStep.place(x = int(self.RESETREADVoltageLabelStep.place_info()['x']) + \
                                    int(self.RESETREADVoltageLabelStep.winfo_width()), y = \
                                    self.RESETREADVoltageLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETREADVoltageEntryStep.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumnStep
        if(self.maxEntryXPosSecondColumnStep < \
           int(self.RESETREADVoltageEntryStep.place_info()['x'])):
            self.maxEntryXPosSecondColumnStep = \
                int(self.RESETREADVoltageEntryStep.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #RESET READ Time
        #variable label
        self.RESETREADTimeLabelStep = Label(self.pulseStepCanvas, text = 'RESET READ Time:', font = \
                       ('calibre', 10, 'normal'))
        self.RESETREADTimeLabelStep.place(x = int(self.delayPeriodLabelStep.place_info()['x']), y = \
                                  int(self.RESETREADVoltageLabelStep.place_info()['y']) + \
                                  int(self.RESETREADVoltageLabelStep.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETREADTimeLabelStep.update()

        #entry widget to input data
        self.RESETREADTimeEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = self.RESETREADTime, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.RESETREADTimeEntryStep.place(x = int(self.RESETREADTimeLabelStep.place_info()['x']) + \
                                    int(self.RESETREADTimeLabelStep.winfo_width()), y = \
                                    self.RESETREADTimeLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETREADTimeEntryStep.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumnStep
        if(self.maxEntryXPosSecondColumnStep < \
           int(self.RESETREADTimeEntryStep.place_info()['x'])):
            self.maxEntryXPosSecondColumnStep = \
                int(self.RESETREADTimeEntryStep.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #Cycle Number
        #variable label
        self.cycleNumberLabelStep = Label(self.pulseStepCanvas, text = 'Cycle Number:', font = \
                       ('calibre', 10, 'normal'))
        self.cycleNumberLabelStep.place(x = int(self.delayPeriodLabelStep.place_info()['x']), y = \
                                  int(self.RESETREADTimeLabelStep.place_info()['y']) + \
                                  int(self.RESETREADTimeLabelStep.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.cycleNumberLabelStep.update()

        #entry widget to input data
        self.cycleNumberEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = self.cycleNumber, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.cycleNumberEntryStep.place(x = int(self.cycleNumberLabelStep.place_info()['x']) + \
                                    int(self.cycleNumberLabelStep.winfo_width()), y = \
                                    self.cycleNumberLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.cycleNumberEntryStep.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumn
        if(self.maxEntryXPosSecondColumnStep < \
           int(self.cycleNumberEntryStep.place_info()['x'])):
            self.maxEntryXPosSecondColumnStep = \
                int(self.cycleNumberEntryStep.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #with the found maxEntryXPosSecondColumnStep (ignored row and column
        #Entries above since they clearly aren't the longest), adjust
        #all entry and unit label positions for this row
        #NOTE: all unit label positions set HERE now

        for widgetItem in self.pulseStepCanvas.winfo_children():
            if(isinstance(widgetItem, tk.Entry)): #if an Entry, prepare to move position

                #shift ONLY THE ENTRIES IN THE SECOND COLUMN BASED ON ASSIGNED
                #secondColumnXPos POSITION
                if(int(widgetItem.place_info()['x']) >= self.secondColumnXPosStep):

                    widgetItem.place(x = self.maxEntryXPosSecondColumnStep, \
                                y = widgetItem.place_info()['y'])
                    widgetItem.update()

        self.foundSecondColumnEntryPosStep = True

        #delay period unit label
        self.delayPeriodUnitLabelStep = Label(self.pulseStepCanvas, text = 'us', font = \
                       self.gateVoltageLabelStep['font'])
        self.delayPeriodUnitLabelStep.place(x = int(self.delayPeriodEntryStep.place_info()['x']) + \
                                    int(self.delayPeriodEntryStep.winfo_width()), y = \
                                    self.delayPeriodEntryStep.place_info()['y'])

        #RESET READ Voltage unit label
        self.RESETREADVoltageUnitLabelStep = Label(self.pulseStepCanvas, text = 'V', font = \
                       self.gateVoltageLabelStep['font'])
        self.RESETREADVoltageUnitLabelStep.place(x = int(self.RESETREADVoltageEntryStep.place_info()['x']) + \
                                    int(self.RESETREADVoltageEntryStep.winfo_width()), y = \
                                    self.RESETREADVoltageEntryStep.place_info()['y'])


        #RESET READ Time unit label
        self.RESETREADTimeUnitLabelStep = Label(self.pulseStepCanvas, text = 'us', font = \
                       self.gateVoltageLabelStep['font'])
        self.RESETREADTimeUnitLabelStep.place(x = int(self.RESETREADTimeEntryStep.place_info()['x']) + \
                                    int(self.RESETREADTimeEntryStep.winfo_width()), y = \
                                    self.RESETREADTimeEntryStep.place_info()['y'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #create buttons to let the user toggle between whether the SET or RESET voltage incorporates
        #the step voltage logic

        #prompt label
        self.FORMOrSETVoltageLabelStep = Label(self.pulseStepCanvas, text = 'Select Voltage to use step logic:', font = \
                       ('calibre', 10, 'normal'))
        self.FORMOrSETVoltageLabelStep.place(x = self.delayPeriodLabelStep.place_info()['x'], \
                                             y = 255)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.FORMOrSETVoltageLabelStep.update()

        #create the two buttons to toggle between the selected state being chosen for
        #using the step logic
        self.FORMSETVoltageStepChosenButton = Button(self.pulseStepCanvas, text = 'SET')
        self.RESETVoltageStepChosenButton = Button(self.pulseStepCanvas, text = 'RESET')

        #default will have FORM/SET chosen first in earlier initialized/set variables, so have the FORM/SET button
        #have the green "selected" visual color
        self.FORMSETVoltageStepChosenButton.config(bg = 'lightgreen')

        #place the buttons
        self.FORMSETVoltageStepChosenButton.place(x = 230, \
                                                  y = int(self.FORMOrSETVoltageLabelStep.place_info()['y']) + \
                                                  int(self.FORMOrSETVoltageLabelStep.winfo_height()) + 5)
        self.FORMSETVoltageStepChosenButton.update() #to get position info
        self.RESETVoltageStepChosenButton.place(x = int(self.FORMSETVoltageStepChosenButton.place_info()['x']) + \
                                                int(self.FORMSETVoltageStepChosenButton.winfo_width()) + 15, \
                                                  y = self.FORMSETVoltageStepChosenButton.place_info()['y'])
        self.RESETVoltageStepChosenButton.update()

        #create the button command logic that toggles chosenStepVoltage while also changing the background color
        #of the two buttons to show which button/state is selected
        self.FORMSETVoltageStepChosenButton.config(command = lambda: self.changeFORMSETRESETVoltageStep('SET'))
        self.RESETVoltageStepChosenButton.config(command = lambda: self.changeFORMSETRESETVoltageStep('RESET'))

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #create buttons to let the user decide if the selected state voltage RISES from the
        #initial set amount to the maximum step voltage, does the inverse and FALLS, OR
        #does BOTH by rising then falling between the two voltages

        #prompt label
        self.voltageDirectionStepLabel = Label(self.pulseStepCanvas, text = \
            'Decide if the voltage should RISE, FALL or \ndo BOTH RISE THEN FALL between chosen \nstate voltage and maximum step voltage:', font = \
                       ('calibre', 10, 'normal'))
        self.voltageDirectionStepLabel.place(x = 50, y = 320)

        self.voltageDirectionStepLabel.update() #update to get position information of label

        #create the three buttons to toggle between the "direction" of the step voltage logic
        self.risingStepVoltageButton = Button(self.pulseStepCanvas, text = 'RISING', command = lambda: \
                                              self.changeStepVoltageDirectionStep('Rising'))
        self.risingStepVoltageButton.place(x = 75, y = 380)

        self.risingStepVoltageButton.update() #update to get position information of label
        
        self.fallingStepVoltageButton = Button(self.pulseStepCanvas, text = 'FALLING', command = lambda: \
                                              self.changeStepVoltageDirectionStep('Falling'))
        self.fallingStepVoltageButton.place(x = int(self.risingStepVoltageButton.place_info()['x']) + \
                                            int(self.risingStepVoltageButton.winfo_width()) + 5, y = \
                                            self.risingStepVoltageButton.place_info()['y'])

        self.fallingStepVoltageButton.update() #update to get position information of label
        
        self.riseAndFallStepVoltageButton = Button(self.pulseStepCanvas, text = 'RISE THEN FALL', command = lambda: \
                                              self.changeStepVoltageDirectionStep('Rise then Fall'))
        self.riseAndFallStepVoltageButton.place(x = int(self.fallingStepVoltageButton.place_info()['x']) + \
                                            int(self.fallingStepVoltageButton.winfo_width()) + 5, y = \
                                            self.risingStepVoltageButton.place_info()['y'])

        if(self.startRun): #set defaults by calling changeStepVoltageDirectionStep function
            self.changeStepVoltageDirectionStep('Rising')

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #"Unit" Button FOR PULSE TEST and Label to toggle between Current (uA)
        #and Resistance (KOhm) in an Ohm's Law relationship (V = IR) for output
        #display of non-Voltage units
        self.toggleOhmsLawUnitLabelStep = Label(self.pulseStepCanvas, text = 'Unit:')
        self.toggleOhmsLawUnitLabelStep.place(x = 350, y = 500)

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.toggleOhmsLawUnitLabelStep.update()

        #calls built-in "toggleOhmsLawUnit" function when pressed AND displays
        #the current/changed unit on the button
        self.toggleOhmsLawUnitButtonStep = Button(self.pulseStepCanvas, text = \
                                    self.toggledOhmsLawUnit.get(), command = lambda: \
                                    toggleOhmsLawUnit(self.toggledOhmsLawUnit, \
                                    self.toggleOhmsLawUnitButtonStep, self.rangeVerificationTitleLabel), \
                                    width = 5, padx = 2, pady = 1, \
                                    bg = 'light gray')
        
        self.toggleOhmsLawUnitButtonStep.place(x = int(self.toggleOhmsLawUnitLabelStep.place_info()['x']) + \
                                    int(self.toggleOhmsLawUnitLabelStep.winfo_width()), y = \
                                    int(self.toggleOhmsLawUnitLabelStep.place_info()['y']))

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #export to .csv file checkbox FOR PULSE STEP TEST
        self.exportCheckBoxButtonStep = Checkbutton(self.pulseStepCanvas, text = \
                                'Export to CSV', variable = self.csvControlVariable)
        self.exportCheckBoxButtonStep.place(x = 350, y = 465)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        
        #checkbox FOR PULSE STEP TEST to choose to print out the runtime of the
        #"pressedSubmitData" function
        self.runtimeCheckBoxButtonStep = Checkbutton(self.pulseStepCanvas, text = \
                                'Print RunTime', variable = self.showRunTime)
        self.runtimeCheckBoxButtonStep.place(x = 350, y = 440)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #PULSE STEP TEST generate/save plots checkbox
        self.createSavePlotsCheckBoxButtonStep = Checkbutton(self.pulseStepCanvas, text = \
                                'Create Plots', variable = self.createSavePlots)
        self.createSavePlotsCheckBoxButtonStep.place(x = 350, y = 415)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #message text box FOR PULSE STEP TEST (as a ListBox to have scrolling
        #functionality for this version)
        self.messageListBoxStep = Listbox(self.pulseStepCanvas, bd = 1, relief = SUNKEN, height = 4, \
                                 width = 44, bg = 'light gray', justify = CENTER)
        self.messageListBoxStep.place(x = 50, y = 520)

        self.messageListScrollLabelStep = Label(self.pulseStepCanvas, text = \
                                       'Output Display Window')
        self.messageListScrollLabelStep.place(x = 120, y = 500)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #clear button FOR PULSE STEP TEST

        #calls built-in "pressedClearOutput" function when button is pressed
        self.clearButtonStep = Button(self.pulseStepCanvas, text = 'Clear', command = lambda: \
                             pressedClearOutput(self.messageListBoxStep), padx = 8, \
                             pady = 15, bg = 'white')
        self.clearButtonStep.place(x = 330, y = 535)

        #------------------------------------------------------

        '''
        pulse test (NOT STEP VOLTAGE) for SET/RESET alternation per cycle
        '''
        
        self.pulseSETRESETSwitchCanvas = Canvas(self.ModeCanvasFrame, width = 450, height = 500)

        #separates canvases into N number of equally spaced columns/rows
        self.pulseSETRESETSwitchCanvas.grid(rowspan = 20, columnspan = 4)

        masterWindow.update() #update masterWindow to save Canvas dimensions

        # - - - - - - - - - - - - -

        #create and place title label
        self.titlePulseSETRESETSwitchLabel = Label(self.pulseSETRESETSwitchCanvas, text = 'Pulse Test - SET/RESET Switch', font = \
                       ('calibre', 20, 'bold'))
        self.titlePulseSETRESETSwitchLabel.place(x = 15, y = 25)

        # - - - - - - - - - - - - -

        #at Jeelka's request, she wants all Entry boxes to have the same
        #X position in their respective column, so the following variable
        #will be used to store the maximum X position of each of the
        #Entry boxes in this column before setting them all to this value
        self.maxEntryXPosFirstColumnSETRESETSwitch = 0
        self.maxEntryXPosSecondColumnSETRESETSwitch = 0
        self.foundFirstColumnEntryPosSETRESETSwitch = False
        self.foundSecondColumnEntryPosSETRESETSwitch = False

        #setup canvas for all adjustable byte values

        #gate voltages SEPARATE FOR SET AND RESET
        #SET variable label
        self.gateVoltageLabelSwitchSET = Label(self.pulseSETRESETSwitchCanvas, text = 'SET Gate Voltage:', font = \
                       ('calibre', 10, 'normal'))
        self.gateVoltageLabelSwitchSET.place(x = 5, y = 70)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.gateVoltageLabelSwitchSET.update()

        #SET entry widget to input data
        self.gateVoltageEntrySwitchSET = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.SETGateVoltage, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.gateVoltageEntrySwitchSET.place(x = int(self.gateVoltageLabelSwitchSET.place_info()['x']) + \
                                    int(self.gateVoltageLabelSwitchSET.winfo_width()), y = \
                                    self.gateVoltageLabelSwitchSET.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.gateVoltageEntrySwitchSET.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnSETRESETSwitch
        if(self.maxEntryXPosFirstColumnSETRESETSwitch < \
           int(self.gateVoltageEntrySwitchSET.place_info()['x'])):
            self.maxEntryXPosFirstColumnSETRESETSwitch = \
                int(self.gateVoltageEntrySwitchSET.place_info()['x'])

        # - - - - - - - - - -

        #RESET variable label
        self.gateVoltageLabelSwitchRESET = Label(self.pulseSETRESETSwitchCanvas, text = 'RESET Gate Voltage:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.gateVoltageLabelSwitchRESET.place(x = int(self.gateVoltageLabelSwitchSET.place_info()['x']), y = \
                                  int(self.gateVoltageLabelSwitchSET.place_info()['y']) + \
                                  int(self.gateVoltageLabelSwitchSET.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.gateVoltageLabelSwitchRESET.update()

        #RESET entry widget to input data
        self.gateVoltageEntrySwitchRESET = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.RESETGateVoltage, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.gateVoltageEntrySwitchRESET.place(x = int(self.gateVoltageLabelSwitchRESET.place_info()['x']) + \
                                    int(self.gateVoltageLabelSwitchRESET.winfo_width()), y = \
                                    self.gateVoltageLabelSwitchRESET.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.gateVoltageEntrySwitchRESET.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnSETRESETSwitch
        if(self.maxEntryXPosFirstColumnSETRESETSwitch < \
           int(self.gateVoltageEntrySwitchRESET.place_info()['x'])):
            self.maxEntryXPosFirstColumnSETRESETSwitch = \
                int(self.gateVoltageEntrySwitchRESET.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #SET voltage
        #variable label
        self.SETVoltageLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'SET Voltage:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.SETVoltageLabelSETRESETSwitch.place(x = int(self.gateVoltageLabelSwitchRESET.place_info()['x']), y = \
                                  int(self.gateVoltageLabelSwitchRESET.place_info()['y']) + \
                                  int(self.gateVoltageLabelSwitchRESET.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.SETVoltageLabelSETRESETSwitch.update()

        #entry widget to input data
        self.SETVoltageEntrySETRESETSwitch = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.FORMSETVoltage, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.SETVoltageEntrySETRESETSwitch.place(x = int(self.SETVoltageLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.SETVoltageLabelSETRESETSwitch.winfo_width()), y = \
                                    self.SETVoltageLabelSETRESETSwitch.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.SETVoltageEntrySETRESETSwitch.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnSETRESETSwitch
        if(self.maxEntryXPosFirstColumnSETRESETSwitch < \
           int(self.SETVoltageEntrySETRESETSwitch.place_info()['x'])):
            self.maxEntryXPosFirstColumnSETRESETSwitch = \
                int(self.SETVoltageEntrySETRESETSwitch.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #SET time
        #variable label
        self.SETTimeLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'SET Time:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.SETTimeLabelSETRESETSwitch.place(x = int(self.SETVoltageLabelSETRESETSwitch.place_info()['x']), y = \
                                  int(self.SETVoltageLabelSETRESETSwitch.place_info()['y']) + \
                                  int(self.SETVoltageLabelSETRESETSwitch.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.SETTimeLabelSETRESETSwitch.update()

        #entry widget to input data
        self.SETTimeEntrySETRESETSwitch = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.FORMSETTime, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.SETTimeEntrySETRESETSwitch.place(x = int(self.SETTimeLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.SETTimeLabelSETRESETSwitch.winfo_width()), y = \
                                    self.SETTimeLabelSETRESETSwitch.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.SETTimeEntrySETRESETSwitch.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnSETRESETSwitch
        if(self.maxEntryXPosFirstColumnSETRESETSwitch < \
           int(self.SETTimeEntrySETRESETSwitch.place_info()['x'])):
            self.maxEntryXPosFirstColumnSETRESETSwitch = \
                int(self.SETTimeEntrySETRESETSwitch.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #RESET voltage
        #variable label
        self.RESETVoltageLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'RESET Voltage:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.RESETVoltageLabelSETRESETSwitch.place(x = int(self.SETTimeLabelSETRESETSwitch.place_info()['x']), y = \
                                  int(self.SETTimeLabelSETRESETSwitch.place_info()['y']) + \
                                  int(self.SETTimeLabelSETRESETSwitch.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETVoltageLabelSETRESETSwitch.update()

        #entry widget to input data
        self.RESETVoltageEntrySETRESETSwitch = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.RESETVoltage, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.RESETVoltageEntrySETRESETSwitch.place(x = int(self.RESETVoltageLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.RESETVoltageLabelSETRESETSwitch.winfo_width()), y = \
                                    self.RESETVoltageLabelSETRESETSwitch.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETVoltageEntrySETRESETSwitch.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnSETRESETSwitch
        if(self.maxEntryXPosFirstColumnSETRESETSwitch < \
           int(self.RESETVoltageEntrySETRESETSwitch.place_info()['x'])):
            self.maxEntryXPosFirstColumnSETRESETSwitch = \
                int(self.RESETVoltageEntrySETRESETSwitch.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #RESET time
        #variable label
        self.RESETTimeLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'RESET Time:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.RESETTimeLabelSETRESETSwitch.place(x = int(self.RESETVoltageLabelSETRESETSwitch.place_info()['x']), y = \
                                  int(self.RESETVoltageLabelSETRESETSwitch.place_info()['y']) + \
                                  int(self.RESETVoltageLabelSETRESETSwitch.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETTimeLabelSETRESETSwitch.update()

        #entry widget to input data
        self.RESETTimeEntrySETRESETSwitch = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.RESETTime, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.RESETTimeEntrySETRESETSwitch.place(x = int(self.RESETTimeLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.RESETTimeLabelSETRESETSwitch.winfo_width()), y = \
                                    self.RESETTimeLabelSETRESETSwitch.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETTimeEntrySETRESETSwitch.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosFirstColumnSETRESETSwitch
        if(self.maxEntryXPosFirstColumnSETRESETSwitch < \
           int(self.RESETTimeEntrySETRESETSwitch.place_info()['x'])):
            self.maxEntryXPosFirstColumnSETRESETSwitch = \
                int(self.RESETTimeEntrySETRESETSwitch.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #delay time period
        #variable label
        #NOTE: new "column", hence the hard coded X value this time to shift to the right
        self.secondColumnXPosSETRESETSwitch = 220
        self.delayPeriodLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'Delay Period:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.delayPeriodLabelSETRESETSwitch.place(x = self.secondColumnXPosSETRESETSwitch, y = \
                        int(self.gateVoltageLabelSwitchSET.place_info()['y']))

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.delayPeriodLabelSETRESETSwitch.update()

        #entry widget to input data
        self.delayPeriodEntrySETRESETSwitch = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.delayPeriodTime, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.delayPeriodEntrySETRESETSwitch.place(x = int(self.delayPeriodLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.delayPeriodLabelSETRESETSwitch.winfo_width()), y = \
                                    self.delayPeriodLabelSETRESETSwitch.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.delayPeriodEntrySETRESETSwitch.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumnSETRESETSwitch
        if(self.maxEntryXPosSecondColumnSETRESETSwitch < \
           int(self.delayPeriodEntrySETRESETSwitch.place_info()['x'])):
            self.maxEntryXPosSecondColumnSETRESETSwitch = \
                int(self.delayPeriodEntrySETRESETSwitch.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #with the found maxEntryXPosFirstColumnSETRESETSwitch (ignored row and column
        #Entries above since they clearly aren't the longest), adjust
        #all entry and unit label positions for this row
        #NOTE: all unit label positions set HERE now

        #count the number of entries here to avoid having to worry
        #about repeating these through the same logic again
        entryCounterSETRESETSwitch = 0

        for widgetItem in self.pulseSETRESETSwitchCanvas.winfo_children():
            if(isinstance(widgetItem, tk.Entry)): #if an Entry, prepare to move position

                #IGNORE ANY SECOND COLUMN WIDGETS WITHIN THIS LOOP (specifically
                #the delay period widget, but keep this ambiguous for better coding
                #practices)
                if(int(widgetItem.place_info()['x']) >= self.maxEntryXPosSecondColumnSETRESETSwitch):
                    entryCounterSETRESETSwitch += 1
                    continue
                widgetItem.place(x = self.maxEntryXPosFirstColumnSETRESETSwitch, \
                                y = widgetItem.place_info()['y'])
                widgetItem.update()
                entryCounterSETRESETSwitch += 1

        self.foundFirstColumnEntryPosSETRESETSwitch = True

        #SET gate voltage unit label
        self.gateVoltageUnitLabelSwitchSET = Label(self.pulseSETRESETSwitchCanvas, text = 'V', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.gateVoltageUnitLabelSwitchSET.place(x = int(self.gateVoltageEntrySwitchSET.place_info()['x']) + \
                                    int(self.gateVoltageEntrySwitchSET.winfo_width()), y = \
                                    self.gateVoltageEntrySwitchSET.place_info()['y'])

        #RESET gate voltage unit label
        self.gateVoltageUnitLabelSwitchRESET = Label(self.pulseSETRESETSwitchCanvas, text = 'V', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.gateVoltageUnitLabelSwitchRESET.place(x = int(self.gateVoltageEntrySwitchRESET.place_info()['x']) + \
                                    int(self.gateVoltageEntrySwitchRESET.winfo_width()), y = \
                                    self.gateVoltageEntrySwitchRESET.place_info()['y'])

        #SET voltage unit label
        self.SETVoltageUnitLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'V', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.SETVoltageUnitLabelSETRESETSwitch.place(x = int(self.SETVoltageEntrySETRESETSwitch.place_info()['x']) + \
                                    int(self.SETVoltageEntrySETRESETSwitch.winfo_width()), y = \
                                    self.SETVoltageEntrySETRESETSwitch.place_info()['y'])

        #SET time unit label
        self.SETTimeUnitLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'us', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.SETTimeUnitLabelSETRESETSwitch.place(x = int(self.SETTimeEntrySETRESETSwitch.place_info()['x']) + \
                                    int(self.SETTimeEntrySETRESETSwitch.winfo_width()), y = \
                                    self.SETTimeEntrySETRESETSwitch.place_info()['y'])

        #RESET voltage unit label
        self.RESETVoltageUnitLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'V', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.RESETVoltageUnitLabelSETRESETSwitch.place(x = int(self.RESETVoltageEntrySETRESETSwitch.place_info()['x']) + \
                                    int(self.RESETVoltageEntrySETRESETSwitch.winfo_width()), y = \
                                    self.RESETVoltageEntrySETRESETSwitch.place_info()['y'])

        #RESET time unit label
        self.RESETTimeUnitLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'us', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.RESETTimeUnitLabelSETRESETSwitch.place(x = int(self.RESETTimeEntrySETRESETSwitch.place_info()['x']) + \
                                    int(self.RESETTimeEntrySETRESETSwitch.winfo_width()), y = \
                                    self.RESETTimeEntrySETRESETSwitch.place_info()['y'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #SET READ Voltage
        #variable label
        self.SETREADVoltageLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'SET READ Voltage:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.SETREADVoltageLabelSETRESETSwitch.place(x = int(self.delayPeriodLabelSETRESETSwitch.place_info()['x']), y = \
                                  int(self.delayPeriodLabelSETRESETSwitch.place_info()['y']) + \
                                  int(self.delayPeriodLabelSETRESETSwitch.winfo_height()) + 5)
        
        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.SETREADVoltageLabelSETRESETSwitch.update()

        #entry widget to input data
        self.SETREADVoltageEntrySETRESETSwitch = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.FORMSETREADVoltage, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.SETREADVoltageEntrySETRESETSwitch.place(x = int(self.SETREADVoltageLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.SETREADVoltageLabelSETRESETSwitch.winfo_width()), y = \
                                    self.SETREADVoltageLabelSETRESETSwitch.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.SETREADVoltageEntrySETRESETSwitch.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumnSETRESETSwitch
        if(self.maxEntryXPosSecondColumnSETRESETSwitch < \
           int(self.SETREADVoltageEntrySETRESETSwitch.place_info()['x'])):
            self.maxEntryXPosSecondColumnSETRESETSwitch = \
                int(self.SETREADVoltageEntrySETRESETSwitch.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #SET READ Time
        #variable label
        self.SETREADTimeLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'SET READ Time:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.SETREADTimeLabelSETRESETSwitch.place(x = int(self.SETREADVoltageLabelSETRESETSwitch.place_info()['x']), y = \
                                  int(self.SETREADVoltageLabelSETRESETSwitch.place_info()['y']) + \
                                  int(self.SETREADVoltageLabelSETRESETSwitch.winfo_height()) + 5)
        
        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.SETREADTimeLabelSETRESETSwitch.update()

        #entry widget to input data
        self.SETREADTimeEntrySETRESETSwitch = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.FORMSETREADTime, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.SETREADTimeEntrySETRESETSwitch.place(x = int(self.SETREADTimeLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.SETREADTimeLabelSETRESETSwitch.winfo_width()), y = \
                                    self.SETREADTimeLabelSETRESETSwitch.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.SETREADTimeEntrySETRESETSwitch.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumnSETRESETSwitch
        if(self.maxEntryXPosSecondColumnSETRESETSwitch < \
           int(self.SETREADTimeEntrySETRESETSwitch.place_info()['x'])):
            self.maxEntryXPosSecondColumnSETRESETSwitch = \
                int(self.SETREADTimeEntrySETRESETSwitch.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #RESET READ Voltage
        #variable label
        self.RESETREADVoltageLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'RESET READ Voltage:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.RESETREADVoltageLabelSETRESETSwitch.place(x = int(self.SETREADTimeLabelSETRESETSwitch.place_info()['x']), y = \
                                  int(self.SETREADTimeLabelSETRESETSwitch.place_info()['y']) + \
                                  int(self.SETREADTimeLabelSETRESETSwitch.winfo_height()) + 5)
        
        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETREADVoltageLabelSETRESETSwitch.update()

        #entry widget to input data
        self.RESETREADVoltageEntrySETRESETSwitch = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.RESETREADVoltage, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.RESETREADVoltageEntrySETRESETSwitch.place(x = int(self.RESETREADVoltageLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.RESETREADVoltageLabelSETRESETSwitch.winfo_width()), y = \
                                    self.RESETREADVoltageLabelSETRESETSwitch.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETREADVoltageEntrySETRESETSwitch.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumnSETRESETSwitch
        if(self.maxEntryXPosSecondColumnSETRESETSwitch < \
           int(self.RESETREADVoltageEntrySETRESETSwitch.place_info()['x'])):
            self.maxEntryXPosSecondColumnSETRESETSwitch = \
                int(self.RESETREADVoltageEntrySETRESETSwitch.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #RESET READ Time
        #variable label
        self.RESETREADTimeLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'RESET READ Time:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.RESETREADTimeLabelSETRESETSwitch.place(x = int(self.RESETREADVoltageLabelSETRESETSwitch.place_info()['x']), y = \
                                  int(self.RESETREADVoltageLabelSETRESETSwitch.place_info()['y']) + \
                                  int(self.RESETREADVoltageLabelSETRESETSwitch.winfo_height()) + 5)
        
        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETREADTimeLabelSETRESETSwitch.update()

        #entry widget to input data
        self.RESETREADTimeEntrySETRESETSwitch = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.RESETREADTime, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.RESETREADTimeEntrySETRESETSwitch.place(x = int(self.RESETREADTimeLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.RESETREADTimeLabelSETRESETSwitch.winfo_width()), y = \
                                    self.RESETREADTimeLabelSETRESETSwitch.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.RESETREADTimeEntrySETRESETSwitch.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumnSETRESETSwitch
        if(self.maxEntryXPosSecondColumnSETRESETSwitch < \
           int(self.RESETREADTimeEntrySETRESETSwitch.place_info()['x'])):
            self.maxEntryXPosSecondColumnSETRESETSwitch = \
                int(self.RESETREADTimeEntrySETRESETSwitch.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #Cycle Number
        #variable label
        self.cycleNumberLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'Cycle Number:', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.cycleNumberLabelSETRESETSwitch.place(x = int(self.RESETREADTimeLabelSETRESETSwitch.place_info()['x']), y = \
                                  int(self.RESETREADTimeLabelSETRESETSwitch.place_info()['y']) + \
                                  int(self.RESETREADTimeLabelSETRESETSwitch.winfo_height()) + 5)
        
        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.cycleNumberLabelSETRESETSwitch.update()

        #entry widget to input data
        self.cycleNumberEntrySETRESETSwitch = Entry(self.pulseSETRESETSwitchCanvas, width = 6, textvariable = self.cycleNumber, \
                        font = self.gateVoltageLabelSwitchSET['font'], bg = 'white')
        self.cycleNumberEntrySETRESETSwitch.place(x = int(self.cycleNumberLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.cycleNumberLabelSETRESETSwitch.winfo_width()), y = \
                                    self.cycleNumberLabelSETRESETSwitch.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.cycleNumberEntrySETRESETSwitch.update()

        #get current X position of Entry and store if it's bigger than
        #current maxEntryXPosSecondColumnSETRESETSwitch
        if(self.maxEntryXPosSecondColumnSETRESETSwitch < \
           int(self.cycleNumberEntrySETRESETSwitch.place_info()['x'])):
            self.maxEntryXPosSecondColumnSETRESETSwitch = \
                int(self.cycleNumberEntrySETRESETSwitch.place_info()['x'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #with the found maxEntryXPosSecondColumnSETRESETSwitch (ignored row and column
        #Entries above since they clearly aren't the longest), adjust
        #all entry and unit label positions for this row
        #NOTE: all unit label positions set HERE now

        for widgetItem in self.pulseSETRESETSwitchCanvas.winfo_children():
            if(isinstance(widgetItem, tk.Entry)): #if an Entry, prepare to move position

                #shift ONLY THE ENTRIES IN THE SECOND COLUMN BASED ON ASSIGNED
                #secondColumnXPos POSITION
                if(int(widgetItem.place_info()['x']) >= self.secondColumnXPosSETRESETSwitch):

                    widgetItem.place(x = self.maxEntryXPosSecondColumnSETRESETSwitch, \
                                y = widgetItem.place_info()['y'])
                    widgetItem.update()

        self.foundSecondColumnEntryPosSETRESETSwitch = True

        #delay period unit label
        self.delayPeriodUnitLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'us', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.delayPeriodUnitLabelSETRESETSwitch.place(x = int(self.delayPeriodEntrySETRESETSwitch.place_info()['x']) + \
                                    int(self.delayPeriodEntrySETRESETSwitch.winfo_width()), y = \
                                    self.delayPeriodEntrySETRESETSwitch.place_info()['y'])

        #SET READ Voltage unit label
        self.SETREADVoltageUnitLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'V', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.SETREADVoltageUnitLabelSETRESETSwitch.place(x = int(self.SETREADVoltageEntrySETRESETSwitch.place_info()['x']) + \
                                    int(self.SETREADVoltageEntrySETRESETSwitch.winfo_width()), y = \
                                    self.SETREADVoltageEntrySETRESETSwitch.place_info()['y'])

        #SET READ Time unit label
        self.SETREADTimeUnitLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'us', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.SETREADTimeUnitLabelSETRESETSwitch.place(x = int(self.SETREADTimeEntrySETRESETSwitch.place_info()['x']) + \
                                    int(self.SETREADTimeEntrySETRESETSwitch.winfo_width()), y = \
                                    self.SETREADTimeEntrySETRESETSwitch.place_info()['y'])

        #RESET READ Voltage unit label
        self.RESETREADVoltageUnitLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'V', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.RESETREADVoltageUnitLabelSETRESETSwitch.place(x = int(self.RESETREADVoltageEntrySETRESETSwitch.place_info()['x']) + \
                                    int(self.RESETREADVoltageEntrySETRESETSwitch.winfo_width()), y = \
                                    self.RESETREADVoltageEntrySETRESETSwitch.place_info()['y'])

        #RESET READ Time unit label
        self.RESETREADTimeUnitLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'us', font = \
                       self.gateVoltageLabelSwitchSET['font'])
        self.RESETREADTimeUnitLabelSETRESETSwitch.place(x = int(self.RESETREADTimeEntrySETRESETSwitch.place_info()['x']) + \
                                    int(self.RESETREADTimeEntrySETRESETSwitch.winfo_width()), y = \
                                    self.RESETREADTimeEntrySETRESETSwitch.place_info()['y'])

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #"Unit" Button FOR PULSE SET/REST SWITCH TEST and Label to toggle between Current (uA)
        #and Resistance (KOhm) in an Ohm's Law relationship (V = IR) for output
        #display of non-Voltage units
        self.toggleOhmsLawUnitLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = 'Unit:')
        self.toggleOhmsLawUnitLabelSETRESETSwitch.place(x = 350, y = 400)

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.toggleOhmsLawUnitLabelSETRESETSwitch.update()

        #calls built-in "toggleOhmsLawUnit" function when pressed AND displays
        #the current/changed unit on the button
        self.toggleOhmsLawUnitButtonSETRESETSwitch = Button(self.pulseSETRESETSwitchCanvas, text = \
                                    self.toggledOhmsLawUnit.get(), command = lambda: \
                                    toggleOhmsLawUnit(self.toggledOhmsLawUnit, \
                                    self.toggleOhmsLawUnitButtonSETRESETSwitch, self.rangeVerificationTitleLabel), \
                                    width = 5, padx = 2, pady = 1, \
                                    bg = 'light gray')
        
        self.toggleOhmsLawUnitButtonSETRESETSwitch.place(x = \
                                    int(self.toggleOhmsLawUnitLabelSETRESETSwitch.place_info()['x']) + \
                                    int(self.toggleOhmsLawUnitLabelSETRESETSwitch.winfo_width()), y = \
                                    int(self.toggleOhmsLawUnitLabelSETRESETSwitch.place_info()['y']))

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #export to .csv file checkbox FOR PULSE SET/REST SWITCH TEST
        self.exportCheckBoxButtonSETRESETSwitch = Checkbutton(self.pulseSETRESETSwitchCanvas, text = \
                                'Export to CSV', variable = self.csvControlVariable)
        self.exportCheckBoxButtonSETRESETSwitch.place(x = 350, y = 365)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #checkbox FOR PULSE SET/RESET SWITCH TEST to choose to print out the runtime of the
        #"pressedSubmitData" function
        self.runtimeCheckBoxButtonSETRESETSwitch = Checkbutton(self.pulseSETRESETSwitchCanvas, text = \
                                'Print RunTime', variable = self.showRunTime)
        self.runtimeCheckBoxButtonSETRESETSwitch.place(x = 350, y = 340)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #checkbox for PULSE SET/RESET SWITCH TEST that inverts the state order
        #of the two states from SET->RESET to RESET->SET
        self.invertSETRESETSwitchStateCheckBoxButton = Checkbutton(self.pulseSETRESETSwitchCanvas, text = \
                                'Invert States', variable = self.invertIVStates)
        self.invertSETRESETSwitchStateCheckBoxButton.place(x = 350, y = 315)

        #create text explaining the DEFAULT logic        
        self.defaultSETRESETSwitchStateLabel = Label(self.pulseSETRESETSwitchCanvas, text = \
                        'Default State Test Order: SET->RESET \n(inverse = RESET->SET)\n(SET state sets RESET V to 0 and vice versa)', \
                        font = self.gateVoltageLabelSwitchSET['font'])
        self.defaultSETRESETSwitchStateLabel.place(x = 48, y = 278) #position hard coded based on personal preference
        self.defaultSETRESETSwitchStateLabel.update()

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #PULSE SET/RESET SWITCH TEST generate/save plots checkbox
        self.createSavePlotsCheckBoxButtonSETRESETSwitch = Checkbutton(self.pulseSETRESETSwitchCanvas, text = \
                                'Create Plots', variable = self.createSavePlots)
        self.createSavePlotsCheckBoxButtonSETRESETSwitch.place(x = 350, y = 290)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #message text box FOR PULSE SET/REST SWITCH TEST (as a ListBox to have scrolling
        #functionality for this version)
        self.messageListBoxSETRESETSwitch = Listbox(self.pulseSETRESETSwitchCanvas, bd = 1, relief = SUNKEN, height = 4, \
                                 width = 44, bg = 'light gray', justify = CENTER)
        self.messageListBoxSETRESETSwitch.place(x = 50, y = 420)

        self.messageListScrollLabelSETRESETSwitch = Label(self.pulseSETRESETSwitchCanvas, text = \
                                       'Output Display Window')
        self.messageListScrollLabelSETRESETSwitch.place(x = 120, y = 400)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #clear button FOR PULSE SET/REST SWITCH TEST

        #calls built-in "pressedClearOutput" function when button is pressed
        self.clearButtonSETRESETSwitch = Button(self.pulseSETRESETSwitchCanvas, text = 'Clear', command = lambda: \
                             pressedClearOutput(self.messageListBoxSETRESETSwitch), padx = 8, \
                             pady = 15, bg = 'white')
        self.clearButtonSETRESETSwitch.place(x = 330, y = 435)

        #------------------------------------------------------

        '''
        IV testing canvas
        '''
        self.IVCanvas = Canvas(self.ModeCanvasFrame, width = 480, height = 750)

        #separates canvases into N number of equally spaced columns/rows
        self.IVCanvas.grid(rowspan = 20, columnspan = 4)

        masterWindow.update() #update masterWindow to save Canvas dimensions

        #for the sake of splitting four separate mode label frames equally, two in each row,
        #find out the what the minimum width of each one should be and round down to the
        #nearest "acceptableMultipler" pixels multiple for the sake of robustness
        self.acceptableXMultiplier = 25 #CHANGE IF NECESSARY
        self.splitLabelFrameXShift = math.floor(self.IVCanvas.winfo_width()/2) - \
            (math.floor(self.IVCanvas.winfo_width()/2 % self.acceptableXMultiplier)) #removes unwanted remainder

        #create and place title label
        self.titleIVLabel = Label(self.IVCanvas, text = 'IV Test Mode', font = \
                       ('calibre', 20, 'bold'))
        self.titleIVLabel.place(x = 45, y = 25)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #at Jeelka's request, this Canvas's functionality will involve the user
        #select 1 of 4 IV state modes and only make changes to the variables of that
        #corresponding mode

        self.FORMModeFrame = LabelFrame(self.IVCanvas, text = 'FORM Mode', \
                                labelanchor = 'n', font = ('calibre', 10, 'normal'))
        self.FORMModeFrame.place(x = 10, y = 60)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.FORMModeFrame.update()

        self.SETModeFrame = LabelFrame(self.IVCanvas, text = 'SET Mode', \
                                labelanchor = 'n', font = self.FORMModeFrame['font'])
        self.SETModeFrame.place(x = int(self.FORMModeFrame.place_info()['x']) + self.splitLabelFrameXShift, \
                                 y = self.FORMModeFrame.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.SETModeFrame.update()

        self.RESETModeFrame = LabelFrame(self.IVCanvas, text = 'RESET Mode', \
                                labelanchor = 'n', font = self.FORMModeFrame['font'])
        self.RESETModeFrame.place(x = self.FORMModeFrame.place_info()['x'], \
                                  y = int(self.FORMModeFrame.place_info()['y']) + \
                                  int(self.FORMModeFrame.winfo_height()) + 25)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.RESETModeFrame.update()

        self.IVModeFrame = LabelFrame(self.IVCanvas, text = 'IV Mode', \
                                labelanchor = 'n', font = self.FORMModeFrame['font'])
        self.IVModeFrame.place(x = int(self.FORMModeFrame.place_info()['x']) + self.splitLabelFrameXShift, \
                                 y = int(self.FORMModeFrame.place_info()['y']) + \
                                  int(self.FORMModeFrame.winfo_height()) + 25)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.IVModeFrame.update()

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #create the logic of the frames that affect one another now that all of the
        #IV Test mode frames have been created

        #FORM Frame
        #FORM Mode Button
        self.FORMModeButton = Button(self.FORMModeFrame, text = 'Select FORM', command = lambda: \
                             self.pressedIVStateChange(self.IVTestState, 'FORM'), bg = 'light gray')
        #NOTE: 3 columns span for a variable's description label, it's entry box,
        #and unit label
        self.FORMModeButton.grid(row = 0, column = 0, columnspan = 3, sticky= 'ew')

        #FORM Gate Voltage label
        self.FORMGateVoltageLabel = Label(self.FORMModeFrame, text = 'Gate Voltage:', font = \
                       self.FORMModeFrame['font'])
        self.FORMGateVoltageLabel.grid(row = 1, column = 0)

        #FORM Gate Voltage entry widget to input data
        self.FORMGateVoltageEntry = Entry(self.FORMModeFrame, width = 6, textvariable = self.gateVoltage, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.FORMGateVoltageEntry.grid(row = self.FORMGateVoltageLabel.grid_info()['row'], column =
                                       int(self.FORMGateVoltageLabel.grid_info()['column']) + 1)

        #FORM Gate Voltage unit label
        self.FORMGateVoltageUnitLabel = Label(self.FORMModeFrame, text = 'V', font = \
                       self.FORMModeFrame['font'])
        self.FORMGateVoltageUnitLabel.grid(row = self.FORMGateVoltageLabel.grid_info()['row'], column =
                                       int(self.FORMGateVoltageEntry.grid_info()['column']) + 1)

        #FORM Delay Period label
        self.FORMDelayPeriodLabel = Label(self.FORMModeFrame, text = 'Delay Period:', font = \
                       self.FORMModeFrame['font'])
        self.FORMDelayPeriodLabel.grid(row = 2, column = 0)

        #FORM Delay Period entry widget to input data
        self.FORMDelayPeriodEntry = Entry(self.FORMModeFrame, width = 6, textvariable = self.delayPeriodTime, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.FORMDelayPeriodEntry.grid(row = self.FORMDelayPeriodLabel.grid_info()['row'], column =
                                       int(self.FORMDelayPeriodLabel.grid_info()['column']) + 1)

        #FORM Delay Period unit label
        self.FORMDelayPeriodUnitLabel = Label(self.FORMModeFrame, text = 'us', font = \
                       self.FORMModeFrame['font'])
        self.FORMDelayPeriodUnitLabel.grid(row = self.FORMDelayPeriodLabel.grid_info()['row'], column =
                                       int(self.FORMDelayPeriodEntry.grid_info()['column']) + 1)

        #FORM READ Voltage label
        self.FORMREADVoltageLabel = Label(self.FORMModeFrame, text = 'READ Voltage:', font = \
                       self.FORMModeFrame['font'])
        self.FORMREADVoltageLabel.grid(row = 3, column = 0)

        #FORM READ Voltage entry widget to input data
        self.FORMREADVoltageEntry = Entry(self.FORMModeFrame, width = 6, textvariable = self.FORMSETREADVoltage, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.FORMREADVoltageEntry.grid(row = self.FORMREADVoltageLabel.grid_info()['row'], column =
                                       int(self.FORMREADVoltageLabel.grid_info()['column']) + 1)

        #FORM READ Voltage unit label
        self.FORMREADVoltageUnitLabel = Label(self.FORMModeFrame, text = 'V', font = \
                       self.FORMModeFrame['font'])
        self.FORMREADVoltageUnitLabel.grid(row = self.FORMREADVoltageLabel.grid_info()['row'], column =
                                       int(self.FORMREADVoltageEntry.grid_info()['column']) + 1)

        #FORM READ Time label
        self.FORMREADTimeLabel = Label(self.FORMModeFrame, text = 'READ Time:', font = \
                       self.FORMModeFrame['font'])
        self.FORMREADTimeLabel.grid(row = 4, column = 0)

        #FORM READ Time entry widget to input data
        self.FORMREADTimeEntry = Entry(self.FORMModeFrame, width = 6, textvariable = self.FORMSETREADTime, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.FORMREADTimeEntry.grid(row = self.FORMREADTimeLabel.grid_info()['row'], column =
                                       int(self.FORMREADTimeLabel.grid_info()['column']) + 1)

        #FORM READ Time unit label
        self.FORMREADTimeUnitLabel = Label(self.FORMModeFrame, text = 'us', font = \
                       self.FORMModeFrame['font'])
        self.FORMREADTimeUnitLabel.grid(row = self.FORMREADTimeLabel.grid_info()['row'], column =
                                       int(self.FORMREADTimeEntry.grid_info()['column']) + 1)

        #FORM Cycle Number label
        self.FORMCycleNumberLabel = Label(self.FORMModeFrame, text = 'Cycle #:', font = \
                       self.FORMModeFrame['font'])
        self.FORMCycleNumberLabel.grid(row = 5, column = 0)

        #FORM Cycle Number entry widget to input data
        self.FORMCycleNumberEntry = Entry(self.FORMModeFrame, width = 6, textvariable = self.cycleNumber, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.FORMCycleNumberEntry.grid(row = self.FORMCycleNumberLabel.grid_info()['row'], column =
                                       int(self.FORMCycleNumberLabel.grid_info()['column']) + 1)

        #FORM Step Number Label
        self.FORMStepNumberLabel = Label(self.FORMModeFrame, text = 'Step #:', font = \
                       self.FORMModeFrame['font'])
        self.FORMStepNumberLabel.grid(row = 6, column = 0)

        #FORM Step Number entry widget to input data
        self.FORMStepNumberEntry = Entry(self.FORMModeFrame, width = 6, textvariable = self.stepNumber, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.FORMStepNumberEntry.grid(row = self.FORMStepNumberLabel.grid_info()['row'], column =
                                       int(self.FORMStepNumberLabel.grid_info()['column']) + 1)

        self.FORMModeFrame.update()

        # - - - - -

        #SET Frame
        #SET Mode Button
        self.SETModeButton = Button(self.SETModeFrame, text = 'Select SET', command = lambda: \
                             self.pressedIVStateChange(self.IVTestState, 'SET'), bg = 'light gray')
        #NOTE: 3 columns span for a variable's description label, it's entry box,
        #and unit label
        self.SETModeButton.grid(row = 0, column = 0, columnspan = 3, sticky= 'ew')

        #SET Gate Voltage label
        self.SETGateVoltageLabel = Label(self.SETModeFrame, text = 'Gate Voltage:', font = \
                       self.FORMModeFrame['font'])
        self.SETGateVoltageLabel.grid(row = 1, column = 0)

        #SET Gate Voltage entry widget to input data
        self.SETGateVoltageEntry = Entry(self.SETModeFrame, width = 6, textvariable = self.gateVoltage, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.SETGateVoltageEntry.grid(row = self.SETGateVoltageLabel.grid_info()['row'], column =
                                       int(self.SETGateVoltageLabel.grid_info()['column']) + 1)

        #SET Gate Voltage unit label
        self.SETGateVoltageUnitLabel = Label(self.SETModeFrame, text = 'V', font = \
                       self.FORMModeFrame['font'])
        self.SETGateVoltageUnitLabel.grid(row = self.SETGateVoltageLabel.grid_info()['row'], column =
                                       int(self.SETGateVoltageEntry.grid_info()['column']) + 1)

        #SET Delay Period label
        self.SETDelayPeriodLabel = Label(self.SETModeFrame, text = 'Delay Period:', font = \
                       self.FORMModeFrame['font'])
        self.SETDelayPeriodLabel.grid(row = 2, column = 0)

        #SET Delay Period entry widget to input data
        self.SETDelayPeriodEntry = Entry(self.SETModeFrame, width = 6, textvariable = self.delayPeriodTime, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.SETDelayPeriodEntry.grid(row = self.SETDelayPeriodLabel.grid_info()['row'], column =
                                       int(self.SETDelayPeriodLabel.grid_info()['column']) + 1)

        #SET Delay Period unit label
        self.SETDelayPeriodUnitLabel = Label(self.SETModeFrame, text = 'us', font = \
                       self.FORMModeFrame['font'])
        self.SETDelayPeriodUnitLabel.grid(row = self.SETDelayPeriodLabel.grid_info()['row'], column =
                                       int(self.SETDelayPeriodEntry.grid_info()['column']) + 1)

        #SET READ Voltage label
        self.SETREADVoltageLabel = Label(self.SETModeFrame, text = 'READ Voltage:', font = \
                       self.FORMModeFrame['font'])
        self.SETREADVoltageLabel.grid(row = 3, column = 0)

        #SET READ Voltage entry widget to input data
        self.SETREADVoltageEntry = Entry(self.SETModeFrame, width = 6, textvariable = self.FORMSETREADVoltage, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.SETREADVoltageEntry.grid(row = self.SETREADVoltageLabel.grid_info()['row'], column =
                                       int(self.SETREADVoltageLabel.grid_info()['column']) + 1)

        #SET READ Voltage unit label
        self.SETREADVoltageUnitLabel = Label(self.SETModeFrame, text = 'V', font = \
                       self.FORMModeFrame['font'])
        self.SETREADVoltageUnitLabel.grid(row = self.SETREADVoltageLabel.grid_info()['row'], column =
                                       int(self.SETREADVoltageEntry.grid_info()['column']) + 1)

        #SET READ Time label
        self.SETREADTimeLabel = Label(self.SETModeFrame, text = 'READ Time:', font = \
                       self.FORMModeFrame['font'])
        self.SETREADTimeLabel.grid(row = 4, column = 0)

        #SET READ Time entry widget to input data
        self.SETREADTimeEntry = Entry(self.SETModeFrame, width = 6, textvariable = self.FORMSETREADTime, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.SETREADTimeEntry.grid(row = self.SETREADTimeLabel.grid_info()['row'], column =
                                       int(self.SETREADTimeLabel.grid_info()['column']) + 1)

        #SET READ Time unit label
        self.SETREADTimeUnitLabel = Label(self.SETModeFrame, text = 'us', font = \
                       self.FORMModeFrame['font'])
        self.SETREADTimeUnitLabel.grid(row = self.SETREADTimeLabel.grid_info()['row'], column =
                                       int(self.SETREADTimeEntry.grid_info()['column']) + 1)

        #SET Cycle Number label
        self.SETCycleNumberLabel = Label(self.SETModeFrame, text = 'Cycle #:', font = \
                       self.FORMModeFrame['font'])
        self.SETCycleNumberLabel.grid(row = 5, column = 0)

        #SET Cycle Number entry widget to input data
        self.SETCycleNumberEntry = Entry(self.SETModeFrame, width = 6, textvariable = self.cycleNumber, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.SETCycleNumberEntry.grid(row = self.SETCycleNumberLabel.grid_info()['row'], column =
                                       int(self.SETCycleNumberLabel.grid_info()['column']) + 1)

        #SET Step Number Label
        self.SETStepNumberLabel = Label(self.SETModeFrame, text = 'Step #:', font = \
                       self.FORMModeFrame['font'])
        self.SETStepNumberLabel.grid(row = 6, column = 0)

        #SET Step Number entry widget to input data
        self.SETStepNumberEntry = Entry(self.SETModeFrame, width = 6, textvariable = self.stepNumber, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.SETStepNumberEntry.grid(row = self.SETStepNumberLabel.grid_info()['row'], column =
                                       int(self.SETStepNumberLabel.grid_info()['column']) + 1)

        self.SETModeFrame.update()

        # - - - - -

        #RESET Frame

        #because of the fact that FORMModeFrame can adjust in height due to the addition/removal
        #of widget rows, RESETModeFrame will be placed and updated again to account for these
        #changes automatically
        self.RESETModeFrame.place(x = self.FORMModeFrame.place_info()['x'], \
                                  y = int(self.FORMModeFrame.place_info()['y']) + \
                                  int(self.FORMModeFrame.winfo_height()) + 25)
        self.RESETModeFrame.update()
        
        #RESET Mode Button
        self.RESETModeButton = Button(self.RESETModeFrame, text = 'Select RESET', command = lambda: \
                             self.pressedIVStateChange(self.IVTestState, 'RESET'), bg = 'light gray')
        #NOTE: 3 columns span for a variable's description label, it's entry box,
        #and unit label
        self.RESETModeButton.grid(row = 0, column = 0, columnspan = 3, sticky= 'ew')

        #RESET Gate Voltage label
        self.RESETGateVoltageLabel = Label(self.RESETModeFrame, text = 'Gate Voltage:', font = \
                       self.FORMModeFrame['font'])
        self.RESETGateVoltageLabel.grid(row = 1, column = 0)

        #RESET Gate Voltage entry widget to input data
        self.RESETGateVoltageEntry = Entry(self.RESETModeFrame, width = 6, textvariable = self.gateVoltage, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.RESETGateVoltageEntry.grid(row = self.RESETGateVoltageLabel.grid_info()['row'], column =
                                       int(self.RESETGateVoltageLabel.grid_info()['column']) + 1)

        #RESET Gate Voltage unit label
        self.RESETGateVoltageUnitLabel = Label(self.RESETModeFrame, text = 'V', font = \
                       self.FORMModeFrame['font'])
        self.RESETGateVoltageUnitLabel.grid(row = self.RESETGateVoltageLabel.grid_info()['row'], column =
                                       int(self.RESETGateVoltageEntry.grid_info()['column']) + 1)

        #RESET Delay Period label
        self.RESETDelayPeriodLabel = Label(self.RESETModeFrame, text = 'Delay Period:', font = \
                       self.FORMModeFrame['font'])
        self.RESETDelayPeriodLabel.grid(row = 2, column = 0)

        #RESET Delay Period entry widget to input data
        self.RESETDelayPeriodEntry = Entry(self.RESETModeFrame, width = 6, textvariable = self.delayPeriodTime, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.RESETDelayPeriodEntry.grid(row = self.RESETDelayPeriodLabel.grid_info()['row'], column =
                                       int(self.RESETDelayPeriodLabel.grid_info()['column']) + 1)

        #RESET Delay Period unit label
        self.RESETDelayPeriodUnitLabel = Label(self.RESETModeFrame, text = 'us', font = \
                       self.FORMModeFrame['font'])
        self.RESETDelayPeriodUnitLabel.grid(row = self.RESETDelayPeriodLabel.grid_info()['row'], column =
                                       int(self.RESETDelayPeriodEntry.grid_info()['column']) + 1)

        #RESET READ Voltage label
        self.RESETREADVoltageLabel = Label(self.RESETModeFrame, text = 'READ Voltage:', font = \
                       self.FORMModeFrame['font'])
        self.RESETREADVoltageLabel.grid(row = 3, column = 0)

        #RESET READ Voltage entry widget to input data
        self.RESETREADVoltageEntry = Entry(self.RESETModeFrame, width = 6, textvariable = self.RESETREADVoltage, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.RESETREADVoltageEntry.grid(row = self.RESETREADVoltageLabel.grid_info()['row'], column =
                                       int(self.RESETREADVoltageLabel.grid_info()['column']) + 1)

        #RESET READ Voltage unit label
        self.RESETREADVoltageUnitLabel = Label(self.RESETModeFrame, text = 'V', font = \
                       self.FORMModeFrame['font'])
        self.RESETREADVoltageUnitLabel.grid(row = self.RESETREADVoltageLabel.grid_info()['row'], column =
                                       int(self.RESETREADVoltageEntry.grid_info()['column']) + 1)

        #RESET READ Time label
        self.RESETREADTimeLabel = Label(self.RESETModeFrame, text = 'READ Time:', font = \
                       self.FORMModeFrame['font'])
        self.RESETREADTimeLabel.grid(row = 4, column = 0)

        #RESET READ Time entry widget to input data
        self.RESETREADTimeEntry = Entry(self.RESETModeFrame, width = 6, textvariable = self.RESETREADTime, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.RESETREADTimeEntry.grid(row = self.RESETREADTimeLabel.grid_info()['row'], column =
                                       int(self.RESETREADTimeLabel.grid_info()['column']) + 1)

        #RESET READ Time unit label
        self.RESETREADTimeUnitLabel = Label(self.RESETModeFrame, text = 'us', font = \
                       self.FORMModeFrame['font'])
        self.RESETREADTimeUnitLabel.grid(row = self.RESETREADTimeLabel.grid_info()['row'], column =
                                       int(self.RESETREADTimeEntry.grid_info()['column']) + 1)

        #RESET Cycle Number label
        self.RESETCycleNumberLabel = Label(self.RESETModeFrame, text = 'Cycle #:', font = \
                       self.FORMModeFrame['font'])
        self.RESETCycleNumberLabel.grid(row = 5, column = 0)

        #RESET Cycle Number entry widget to input data
        self.RESETCycleNumberEntry = Entry(self.RESETModeFrame, width = 6, textvariable = self.cycleNumber, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.RESETCycleNumberEntry.grid(row = self.RESETCycleNumberLabel.grid_info()['row'], column =
                                       int(self.RESETCycleNumberLabel.grid_info()['column']) + 1)

        #RESET Step Number Label
        self.RESETStepNumberLabel = Label(self.RESETModeFrame, text = 'Step #:', font = \
                       self.FORMModeFrame['font'])
        self.RESETStepNumberLabel.grid(row = 6, column = 0)

        #RESET Step Number entry widget to input data
        self.RESETStepNumberEntry = Entry(self.RESETModeFrame, width = 6, textvariable = self.stepNumber, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.RESETStepNumberEntry.grid(row = self.RESETStepNumberLabel.grid_info()['row'], column =
                                       int(self.RESETStepNumberLabel.grid_info()['column']) + 1)

        self.RESETModeFrame.update()

        # - - - - -

        #IV Frame

        #because of the fact that FORMModeFrame can adjust in height due to the addition/removal
        #of widget rows, IVModeFrame will be placed and updated again to account for these
        #changes automatically
        self.IVModeFrame.place(x = int(self.FORMModeFrame.place_info()['x']) + self.splitLabelFrameXShift, \
                                 y = int(self.FORMModeFrame.place_info()['y']) + \
                                  int(self.FORMModeFrame.winfo_height()) + 25)
        self.IVModeFrame.update()
        
        #IV Mode Button
        self.IVModeButton = Button(self.IVModeFrame, text = 'Select IV', command = lambda: \
                             self.pressedIVStateChange(self.IVTestState, 'IV'), bg = 'light gray')
        #NOTE: 3 columns span for a variable's description label, it's entry box,
        #and unit label
        self.IVModeButton.grid(row = 0, column = 0, columnspan = 3, sticky= 'ew')

        #IV SET Gate Voltage label
        self.IVSETGateVoltageLabel = Label(self.IVModeFrame, text = 'SET Gate Voltage:', font = \
                       self.FORMModeFrame['font'])
        self.IVSETGateVoltageLabel.grid(row = 1, column = 0)

        #IV SET Gate Voltage entry widget to input data
        self.IVSETGateVoltageEntry = Entry(self.IVModeFrame, width = 6, textvariable = self.SETGateVoltage, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.IVSETGateVoltageEntry.grid(row = self.IVSETGateVoltageLabel.grid_info()['row'], column =
                                       int(self.IVSETGateVoltageLabel.grid_info()['column']) + 1)

        #IV SET Gate Voltage unit label
        self.IVSETGateVoltageUnitLabel = Label(self.IVModeFrame, text = 'V', font = \
                       self.FORMModeFrame['font'])
        self.IVSETGateVoltageUnitLabel.grid(row = self.IVSETGateVoltageLabel.grid_info()['row'], column =
                                       int(self.IVSETGateVoltageEntry.grid_info()['column']) + 1)

        #IV RESET Gate Voltage label
        self.IVRESETGateVoltageLabel = Label(self.IVModeFrame, text = 'RESET Gate Voltage:', font = \
                       self.FORMModeFrame['font'])
        self.IVRESETGateVoltageLabel.grid(row = 2, column = 0)

        #IV RESET Gate Voltage entry widget to input data
        self.IVRESETGateVoltageEntry = Entry(self.IVModeFrame, width = 6, textvariable = self.RESETGateVoltage, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.IVRESETGateVoltageEntry.grid(row = self.IVRESETGateVoltageLabel.grid_info()['row'], column =
                                       int(self.IVRESETGateVoltageLabel.grid_info()['column']) + 1)

        #IV RESET Gate Voltage unit label
        self.IVRESETGateVoltageUnitLabel = Label(self.IVModeFrame, text = 'V', font = \
                       self.FORMModeFrame['font'])
        self.IVRESETGateVoltageUnitLabel.grid(row = self.IVRESETGateVoltageLabel.grid_info()['row'], column =
                                       int(self.IVRESETGateVoltageEntry.grid_info()['column']) + 1)


        #IV Delay Period label
        self.IVDelayPeriodLabel = Label(self.IVModeFrame, text = 'Delay Period:', font = \
                       self.FORMModeFrame['font'])
        self.IVDelayPeriodLabel.grid(row = 3, column = 0)

        #IV Delay Period entry widget to input data
        self.IVDelayPeriodEntry = Entry(self.IVModeFrame, width = 6, textvariable = self.delayPeriodTime, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.IVDelayPeriodEntry.grid(row = self.IVDelayPeriodLabel.grid_info()['row'], column =
                                       int(self.IVDelayPeriodLabel.grid_info()['column']) + 1)

        #IV Delay Period unit label
        self.IVDelayPeriodUnitLabel = Label(self.IVModeFrame, text = 'us', font = \
                       self.FORMModeFrame['font'])
        self.IVDelayPeriodUnitLabel.grid(row = self.IVDelayPeriodLabel.grid_info()['row'], column =
                                       int(self.IVDelayPeriodEntry.grid_info()['column']) + 1)

        #IV FORM/SET READ Voltage label
        self.IVFORMSETREADVoltageLabel = Label(self.IVModeFrame, text = 'FORM/SET READ Voltage:', font = \
                       self.FORMModeFrame['font'])
        self.IVFORMSETREADVoltageLabel.grid(row = 4, column = 0)

        #IV FORM/SET READ Voltage entry widget to input data
        self.IVFORMSETREADVoltageEntry = Entry(self.IVModeFrame, width = 6, textvariable = self.FORMSETREADVoltage, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.IVFORMSETREADVoltageEntry.grid(row = self.IVFORMSETREADVoltageLabel.grid_info()['row'], column =
                                       int(self.IVFORMSETREADVoltageLabel.grid_info()['column']) + 1)

        #IV FORM/SET READ Voltage unit label
        self.IVFORMSETREADVoltageUnitLabel = Label(self.IVModeFrame, text = 'V', font = \
                       self.FORMModeFrame['font'])
        self.IVFORMSETREADVoltageUnitLabel.grid(row = self.IVFORMSETREADVoltageLabel.grid_info()['row'], column =
                                       int(self.IVFORMSETREADVoltageEntry.grid_info()['column']) + 1)

        #IV FORM/SET READ Time label
        self.IVFORMSETREADTimeLabel = Label(self.IVModeFrame, text = 'FORM/SET READ Time:', font = \
                       self.FORMModeFrame['font'])
        self.IVFORMSETREADTimeLabel.grid(row = 5, column = 0)

        #IV FORM/SET READ Time entry widget to input data
        self.IVFORMSETREADTimeEntry = Entry(self.IVModeFrame, width = 6, textvariable = self.FORMSETREADTime, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.IVFORMSETREADTimeEntry.grid(row = self.IVFORMSETREADTimeLabel.grid_info()['row'], column =
                                       int(self.IVFORMSETREADTimeLabel.grid_info()['column']) + 1)

        #IV FORM/SET READ Time unit label
        self.IVFORMSETREADTimeUnitLabel = Label(self.IVModeFrame, text = 'us', font = \
                       self.FORMModeFrame['font'])
        self.IVFORMSETREADTimeUnitLabel.grid(row = self.IVFORMSETREADTimeLabel.grid_info()['row'], column =
                                       int(self.IVFORMSETREADTimeEntry.grid_info()['column']) + 1)

        #IV RESET READ Voltage label
        self.IVRESETREADVoltageLabel = Label(self.IVModeFrame, text = 'RESET READ Voltage:', font = \
                       self.FORMModeFrame['font'])
        self.IVRESETREADVoltageLabel.grid(row = 6, column = 0)

        #IV RESET READ Voltage entry widget to input data
        self.IVRESETREADVoltageEntry = Entry(self.IVModeFrame, width = 6, textvariable = self.RESETREADVoltage, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.IVRESETREADVoltageEntry.grid(row = self.IVRESETREADVoltageLabel.grid_info()['row'], column =
                                       int(self.IVRESETREADVoltageLabel.grid_info()['column']) + 1)

        #IV RESET READ Voltage unit label
        self.IVRESETREADVoltageUnitLabel = Label(self.IVModeFrame, text = 'V', font = \
                       self.FORMModeFrame['font'])
        self.IVRESETREADVoltageUnitLabel.grid(row = self.IVRESETREADVoltageLabel.grid_info()['row'], column =
                                       int(self.IVRESETREADVoltageEntry.grid_info()['column']) + 1)

        #IV RESET READ Time label
        self.IVRESETREADTimeLabel = Label(self.IVModeFrame, text = 'RESET READ Time:', font = \
                       self.FORMModeFrame['font'])
        self.IVRESETREADTimeLabel.grid(row = 7, column = 0)

        #IV RESET READ Time entry widget to input data
        self.IVRESETREADTimeEntry = Entry(self.IVModeFrame, width = 6, textvariable = self.RESETREADTime, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.IVRESETREADTimeEntry.grid(row = self.IVRESETREADTimeLabel.grid_info()['row'], column =
                                       int(self.IVRESETREADTimeLabel.grid_info()['column']) + 1)

        #IV RESET READ Time unit label
        self.IVRESETREADTimeUnitLabel = Label(self.IVModeFrame, text = 'us', font = \
                       self.FORMModeFrame['font'])
        self.IVRESETREADTimeUnitLabel.grid(row = self.IVRESETREADTimeLabel.grid_info()['row'], column =
                                       int(self.IVRESETREADTimeEntry.grid_info()['column']) + 1)

        #IV Cycle Number label
        self.IVCycleNumberLabel = Label(self.IVModeFrame, text = 'Cycle #:', font = \
                       self.FORMModeFrame['font'])
        self.IVCycleNumberLabel.grid(row = 8, column = 0)

        #IV Cycle Number entry widget to input data
        self.IVCycleNumberEntry = Entry(self.IVModeFrame, width = 6, textvariable = self.cycleNumber, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.IVCycleNumberEntry.grid(row = self.IVCycleNumberLabel.grid_info()['row'], column =
                                       int(self.IVCycleNumberLabel.grid_info()['column']) + 1)

        #IV Step Number Label
        self.IVStepNumberLabel = Label(self.IVModeFrame, text = 'Step #:', font = \
                       self.FORMModeFrame['font'])
        self.IVStepNumberLabel.grid(row = 9, column = 0)

        #IV Step Number entry widget to input data
        self.IVStepNumberEntry = Entry(self.IVModeFrame, width = 6, textvariable = self.stepNumber, \
                        font = self.FORMModeFrame['font'], bg = 'white')
        self.IVStepNumberEntry.grid(row = self.IVStepNumberLabel.grid_info()['row'], column =
                                       int(self.IVStepNumberLabel.grid_info()['column']) + 1)

        self.IVModeFrame.update()

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #export to .csv file checkbox FOR IV TEST
        self.exportCheckBoxButtonIV = Checkbutton(self.IVCanvas, text = \
                                'Export to CSV', variable = self.csvControlVariable)
        self.exportCheckBoxButtonIV.place(x = 370, y = 600)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        
        #checkbox FOR IV TEST to choose to print out the runtime of the
        #"pressedSubmitData" function
        self.runtimeCheckBoxButtonIV = Checkbutton(self.IVCanvas, text = \
                                'Print RunTime', variable = self.showRunTime)
        self.runtimeCheckBoxButtonIV.place(x = 370, y = 625)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #checkbox for IV TEST for IT STATE that inverts the state order
        #of the IV state from SET->RESET to RESET->SET
        self.invertIVStateCheckBoxButton = Checkbutton(self.IVCanvas, text = \
                                'Invert IV States', variable = self.invertIVStates)
        self.invertIVStateCheckBoxButton.place(x = 370, y = 575)

        #create text explaining the DEFAULT logic        
        self.defaultIVStateLabel = Label(self.IVCanvas, text = \
                        'Default IV State Test Order: SET->RESET \n(inverse = RESET->SET)', \
                        font = self.FORMModeFrame['font'])
        self.defaultIVStateLabel.place(x = 75, y = 550) #position hard coded based on personal preference
        self.defaultIVStateLabel.update()

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #IV TEST generate/save plots checkbox
        self.createSavePlotsCheckBoxButtonIV = Checkbutton(self.IVCanvas, text = \
                                'Create Plots', variable = self.createSavePlots)
        self.createSavePlotsCheckBoxButtonIV.place(x = 370, y = 550)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #message text box FOR IV TEST (as a ListBox to have scrolling
        #functionality for this version)
        self.messageListBoxIV = Listbox(self.IVCanvas, bd = 1, relief = SUNKEN, height = 4, \
                                 width = 44, bg = 'light gray', justify = CENTER)
        self.messageListBoxIV.place(x = 70, y = 670)

        self.messageListScrollLabelIV = Label(self.IVCanvas, text = \
                                       'Output Display Window')
        self.messageListScrollLabelIV.place(x = 140, y = 650)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #clear button FOR IV TEST

        #calls built-in "pressedClearOutput" function when button is pressed
        self.clearButtonIV = Button(self.IVCanvas, text = 'Clear', command = lambda: \
                             pressedClearOutput(self.messageListBoxIV), padx = 8, \
                             pady = 15, bg = 'white')
        self.clearButtonIV.place(x = 345, y = 680)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #update corresponding byte information upon changed Entry values
        #(since only the value that the two bytes represent gets changed
        #directly with the Entry box change)
        #NOTE: Boolean logic done to show when an input is VOLTAGE based
        #UPDATES BOTH THE PULSE TEST AND IV TEST CHANGES HERE, SEEING HOW BOTH
        #CANVAS ARE MADE AND MAINTAINED IN THE SAME FUNCTION
        self.gateVoltage.trace('w', lambda *args: updateEntryBytes(self.gateVoltage, \
                            self.byte3_GateVoltageMSB, self.byte4_GateVoltageLSB, True))

        self.FORMSETVoltage.trace('w', lambda *args: updateEntryBytes(self.FORMSETVoltage, \
                            self.byte5_FORMSETVoltageMSB, self.byte6_FORMSETVoltageLSB, True))

        self.FORMSETTime.trace('w', lambda *args: updateEntryBytes(self.FORMSETTime, \
                            self.byte7_FORMSETTimeMSB, self.byte8_FORMSETTimeLSB, False))

        self.delayPeriodTime.trace('w', lambda *args: updateEntryBytes(\
                            self.delayPeriodTime, self.byte9_delayPeriodTimeMSB, \
                            self.byte10_delayPeriodTimeLSB, False))

        self.FORMSETREADVoltage.trace('w', lambda *args: updateEntryBytes(\
                            self.FORMSETREADVoltage, self.byte11_FORMSETREADVoltageMSB, \
                            self.byte12_FORMSETREADVoltageLSB, True))

        self.FORMSETREADTime.trace('w', lambda *args: updateEntryBytes(self.FORMSETREADTime, \
                            self.byte13_FORMSETREADTimeMSB, self.byte14_FORMSETREADTimeLSB, False))

        self.RESETVoltage.trace('w', lambda *args: updateEntryBytes(self.RESETVoltage, \
                            self.byte15_RESETVoltageMSB, self.byte16_RESETVoltageLSB, True))

        self.RESETTime.trace('w', lambda *args: updateEntryBytes(self.RESETTime, \
                            self.byte17_RESETTimeMSB, self.byte18_RESETTimeLSB, False))

        self.RESETREADVoltage.trace('w', lambda *args: updateEntryBytes(\
                            self.RESETREADVoltage, self.byte19_RESETREADVoltageMSB, \
                            self.byte20_RESETREADVoltageLSB, True))

        self.RESETREADTime.trace('w', lambda *args: updateEntryBytes(\
                            self.RESETREADTime, self.byte21_RESETREADTimeMSB, \
                            self.byte22_RESETREADTimeLSB, False))

        self.cycleNumber.trace('w', lambda *args: updateEntryBytes(\
                            self.cycleNumber, self.byte25_CyclesNumberMSB, \
                            self.byte26_CyclesNumberLSB, False))

        self.stepNumber.trace('w', lambda *args: updateEntryBytes(\
                            self.stepNumber, self.byte27_StepNumberMSB, \
                            self.byte28_StepNumberLSB, False))

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #enable/disable the PULSE TEST range entry widgets based on the utilizeCurResRange
        #boolean state
        self.utilizeCurResRange.trace_add('write', lambda * args: toggleRangeEntries(self.utilizeCurResRange, \
                                            self.rangeMinEntry, self.rangeMaxEntry, self.rangeMaxCycleEntry))

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #update the IV test state and the corresponding options in the case of the IV
        #Test Canvas

        self.IVTestState.trace('w', lambda *args: self.updateIVTestState(self.IVTestState, \
                                self.IVCanvas))

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #Interactive Grid (Window)

        #NOTE: Since the inclusion of a scrollbar is desired should the grid exceed
        #the window dimensions (as the number of rows and columns for the grid are based
        #on user input), the following steps to include the scrollbars were from the following
        #(following "grid" logical since "grid" was already used for the main window instead of "pack"):
        #https://www.tutorialspoint.com/implementing-a-scrollbar-using-grid-manager-on-a-tkinter-window

        #open secondary window for cell grid
        cellGridWindow = tk.Toplevel(masterWindow) #create secondary window
        cellGridWindow.title('Cell/Device Selection Grid (White = False, Black = True)')

        #since this program is to be dependent on selecting individual cells, closing this
        #cell grid window and not the master one would be counterintuitive, so closing this
        #window will close the master one too
        cellGridWindow.protocol("WM_DELETE_WINDOW", lambda: closeMaster(masterWindow))

        #create the frame for the grid layout
        cellGridFrame = ttk.Frame(cellGridWindow)
        cellGridFrame.grid(row = 0, column = 0, sticky = 'nsew')

        #create the canvasand the scrollbars connected to the canvas
        #NOTE: xscrollcommand and yscrollcommand ensures the scrollbar controls
        #the canvas's horizontal and vertical scrolling respectively
        #NOTE: Recycling Canvas dimensions of masterWindow for this
        #window too, though this window will still be able to be adjusted
        #in terms of shape/size
        cellGridCanvas = tk.Canvas(cellGridFrame , width=700, height=600) #canvas of the FRAME

        #scrollbars for the FRAME that commands the CANVAS
        scrollBarVertY = ttk.Scrollbar(cellGridFrame, orient = 'vertical', \
                                       command = cellGridCanvas.yview) #vertical
        cellGridCanvas.configure(yscrollcommand = scrollBarVertY.set)
        scrollBarHorizX = ttk.Scrollbar(cellGridFrame, orient = 'horizontal', \
                                       command = cellGridCanvas.xview) #horizontal
        cellGridCanvas.configure(xscrollcommand = scrollBarHorizX.set)

        #create ANOTHER frame WITHIN the canvas to obtain the scrollable content
        #(as recommended in the web link that this structure is following above)
        cellGridContentFrame = ttk.Frame(cellGridCanvas)

        #use "bind" to adjust the canvas scroll region whenever the size of the new
        #frame changes
        #NOTE: "lambda" function is used to pass arguments to a command
        cellGridContentFrame.bind("<Configure>", lambda e: \
                                  cellGridCanvas.configure(scrollregion = \
                                                           cellGridCanvas.bbox("all")))

        #call built in "interactiveGrid" function to populate this new internal frame
        cellGrid = interactiveGrid(cellGridContentFrame)
        
        #perform window resizing configurations to make sure that the window and its components
        #expand proportionally when resized
        cellGridWindow.columnconfigure(0, weight = 1)
        cellGridWindow.rowconfigure(0, weight = 1)
        cellGridFrame.columnconfigure(0, weight = 1) #OUTER frame
        cellGridFrame.rowconfigure(0, weight = 1)

        #"pack" the canvas and scrollbar onto the window using "grid" version, with the scrollbar
        #being adjacent to the canvas
        cellGridCanvas.create_window((0, 0), window = cellGridContentFrame, anchor = "nw")
        cellGridCanvas.grid(row = 0, column = 0, sticky = 'nsew')
        scrollBarVertY.grid(row = 0, column = 1, sticky = 'ns')
        scrollBarHorizX.grid(row = 1, column = 0, sticky = 'ew')

        #-----------------------------------------------------------------------------------------

        #create the Grid "All True" and "All False" buttons for ALL PULSE AND IV TEST CANVASES
        #RECALL: self.pulseCanvas, self.pulseStepCanvas, self.IVCanvas

        #Pulse Canvas (NOT STEP)
        #buttons IN PULSE CANVAS added to make allow for the user to set/reset all cells in the grid
        #to "True" or "False" respectively to avoid having to manually set all the buttons to one state
        #after a select number of cells/devices were changed before this preference
        allFalseButtonPulse = Button(self.pulseCanvas, text = 'Grid - All False', \
                                     command = cellGrid.allFalse, padx = 8, \
                                     pady = 8, bg = 'white')
        allFalseButtonPulse.place(x = 70, y = 345) #position hard coded based on personal preference

        allFalseButtonPulse.update() #done to finalize widget dimensions for the winfo_width call below
        
        allTrueButtonPulse = Button(self.pulseCanvas, text = 'Grid - All True', \
                                    command = cellGrid.allTrue, padx = 8, \
                                    pady = 8, bg = 'white')
        
        allTrueButtonPulse.place(x = int(allFalseButtonPulse.place_info()['x']) + \
                                 int(allFalseButtonPulse.winfo_width()) + 25, y = \
                                 allFalseButtonPulse.place_info()['y']) #position hard coded based on personal preference

        #Pulse STEP Canvas
        #buttons IN PULSE STEP CANVAS added to make allow for the user to set/reset all cells in the grid
        #to "True" or "False" respectively to avoid having to manually set all the buttons to one state
        #after a select number of cells/devices were changed before this preference
        allFalseButtonPulseStep = Button(self.pulseStepCanvas, text = 'Grid - All False', \
                                     command = cellGrid.allFalse, padx = 8, \
                                     pady = 8, bg = 'white')
        allFalseButtonPulseStep.place(x = 70, y = 445) #position hard coded based on personal preference

        allFalseButtonPulseStep.update() #done to finalize widget dimensions for the winfo_width call below
        
        allTrueButtonPulseStep = Button(self.pulseStepCanvas, text = 'Grid - All True', \
                                    command = cellGrid.allTrue, padx = 8, \
                                    pady = 8, bg = 'white')
        
        allTrueButtonPulseStep.place(x = int(allFalseButtonPulseStep.place_info()['x']) + \
                                 int(allFalseButtonPulseStep.winfo_width()) + 25, y = \
                                 allFalseButtonPulseStep.place_info()['y']) #position hard coded based on personal preference

        #Pulse SET/RESET Switch Canvas
        #buttons IN PULSE CANVAS added to make allow for the user to set/reset all cells in the grid
        #to "True" or "False" respectively to avoid having to manually set all the buttons to one state
        #after a select number of cells/devices were changed before this preference
        allFalseButtonPulseSETRESETSwitch = Button(self.pulseSETRESETSwitchCanvas, text = 'Grid - All False', \
                                     command = cellGrid.allFalse, padx = 8, \
                                     pady = 8, bg = 'white')
        allFalseButtonPulseSETRESETSwitch.place(x = 70, y = 345) #position hard coded based on personal preference

        allFalseButtonPulseSETRESETSwitch.update() #done to finalize widget dimensions for the winfo_width call below
        
        allTrueButtonPulseSETRESETSwitch = Button(self.pulseSETRESETSwitchCanvas, text = 'Grid - All True', \
                                    command = cellGrid.allTrue, padx = 8, \
                                    pady = 8, bg = 'white')
        
        allTrueButtonPulseSETRESETSwitch.place(x = int(allFalseButtonPulseSETRESETSwitch.place_info()['x']) + \
                                 int(allFalseButtonPulseSETRESETSwitch.winfo_width()) + 25, y = \
                                 allFalseButtonPulseSETRESETSwitch.place_info()['y']) #position hard coded based on personal preference

        #IV Canvas
        #buttons IN IV CANVAS added to make allow for the user to set/reset all cells in the grid
        #to "True" or "False" respectively to avoid having to manually set all the buttons to one state
        #after a select number of cells/devices were changed before this preference
        allFalseButtonIV = Button(self.IVCanvas, text = 'Grid - All False', \
                                     command = cellGrid.allFalse, padx = 8, \
                                     pady = 8, bg = 'white')
        allFalseButtonIV.place(x = 90, y = 600) #position hard coded based on personal preference

        allFalseButtonIV.update() #done to finalize widget dimensions for the winfo_width call below
        
        allTrueButtonIV = Button(self.IVCanvas, text = 'Grid - All True', \
                                    command = cellGrid.allTrue, padx = 8, \
                                    pady = 8, bg = 'white')
        
        allTrueButtonIV.place(x = int(allFalseButtonIV.place_info()['x']) + \
                                 int(allFalseButtonIV.winfo_width()) + 25, y = \
                                 allFalseButtonIV.place_info()['y']) #position hard coded based on personal preference

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #submit button FOR PULSE TEST (put here AFTER CellGrid creation)

        #calls built-in "pressedSubmitData" function when button is pressed
        self.submitButton = Button(self.pulseCanvas, text = 'Send', command = lambda: \
                        pressedSubmitData(cellGrid, self.expectedPortDriverSearch, self.saveFileNameString, \
                        self.csvDirectoryString, self.toggledOhmsLawUnit, self.csvControlVariable, \
                        self.showRunTime, self.cycleNumber, self.FORMSETREADVoltage, self.RESETREADVoltage, \
                        self.byte3_GateVoltageMSB, self.byte4_GateVoltageLSB, self.byte5_FORMSETVoltageMSB, \
                        self.byte6_FORMSETVoltageLSB, self.byte7_FORMSETTimeMSB, \
                        self.byte8_FORMSETTimeLSB, self.byte9_delayPeriodTimeMSB, \
                        self.byte10_delayPeriodTimeLSB, self.byte11_FORMSETREADVoltageMSB, \
                        self.byte12_FORMSETREADVoltageLSB, self.byte13_FORMSETREADTimeMSB, \
                        self.byte14_FORMSETREADTimeLSB, self.byte15_RESETVoltageMSB, \
                        self.byte16_RESETVoltageLSB, self.byte17_RESETTimeMSB, self.byte18_RESETTimeLSB, \
                        self.byte19_RESETREADVoltageMSB, self.byte20_RESETREADVoltageLSB, \
                        self.byte21_RESETREADTimeMSB, self.byte22_RESETREADTimeLSB, \
                        self.byte25_CyclesNumberMSB, self.byte26_CyclesNumberLSB, \
                        self.byte27_StepNumberMSB, self.byte28_StepNumberLSB, self.byte29_modeState, \
                        self.messageListBox, self.IVTestState, self.FORMSETStateString, \
                        self.invertIVStates, self.maxStepVoltage, \
                        self.SETGateVoltage, self.RESETGateVoltage, self.chosenStepVoltage, \
                        self.stepVoltageDirection, self.createSavePlots, self.stepNumber, \
                        self.utilizeCurResRange, self.pulseTestRangeMin, self.pulseTestRangeMax, \
                        self.pulseTestRangeCycleCount, self.createHeatMap, self.hardCodeDevices), \
                        padx = 8, pady = 15, bg = 'white')
        self.submitButton.place(x = 390, y = 435)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #submit button FOR PULSE STEP TEST (put here AFTER CellGrid creation)

        #calls built-in "pressedSubmitData" function when button is pressed
        self.submitButtonStep = Button(self.pulseStepCanvas, text = 'Send', command = lambda: \
                        pressedSubmitData(cellGrid, self.expectedPortDriverSearch, self.saveFileNameString, \
                        self.csvDirectoryString, self.toggledOhmsLawUnit, self.csvControlVariable, \
                        self.showRunTime, self.cycleNumber, self.FORMSETREADVoltage, self.RESETREADVoltage, \
                        self.byte3_GateVoltageMSB, self.byte4_GateVoltageLSB, self.byte5_FORMSETVoltageMSB, \
                        self.byte6_FORMSETVoltageLSB, self.byte7_FORMSETTimeMSB, \
                        self.byte8_FORMSETTimeLSB, self.byte9_delayPeriodTimeMSB, \
                        self.byte10_delayPeriodTimeLSB, self.byte11_FORMSETREADVoltageMSB, \
                        self.byte12_FORMSETREADVoltageLSB, self.byte13_FORMSETREADTimeMSB, \
                        self.byte14_FORMSETREADTimeLSB, self.byte15_RESETVoltageMSB, \
                        self.byte16_RESETVoltageLSB, self.byte17_RESETTimeMSB, self.byte18_RESETTimeLSB, \
                        self.byte19_RESETREADVoltageMSB, self.byte20_RESETREADVoltageLSB, \
                        self.byte21_RESETREADTimeMSB, self.byte22_RESETREADTimeLSB, \
                        self.byte25_CyclesNumberMSB, self.byte26_CyclesNumberLSB, \
                        self.byte27_StepNumberMSB, self.byte28_StepNumberLSB, self.byte29_modeState, \
                        self.messageListBoxStep, self.IVTestState, self.FORMSETStateString, \
                        self.invertIVStates, self.maxStepVoltage, \
                        self.SETGateVoltage, self.RESETGateVoltage, self.chosenStepVoltage, \
                        self.stepVoltageDirection, self.createSavePlots, self.stepNumber, \
                        self.utilizeCurResRange, self.pulseTestRangeMin, self.pulseTestRangeMax, \
                        self.pulseTestRangeCycleCount, self.createHeatMap, self.hardCodeDevices), \
                        padx = 8, pady = 15, bg = 'white')
        self.submitButtonStep.place(x = 390, y = 535)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #submit button FOR PULSE SET/RESET SWITCH TEST (put here AFTER CellGrid creation)

        #calls built-in "pressedSubmitData" function when button is pressed
        self.submitButtonSETRESETSwitch = Button(self.pulseSETRESETSwitchCanvas, text = 'Send', command = lambda: \
                        pressedSubmitData(cellGrid, self.expectedPortDriverSearch, self.saveFileNameString, \
                        self.csvDirectoryString, self.toggledOhmsLawUnit, self.csvControlVariable, \
                        self.showRunTime, self.cycleNumber, self.FORMSETREADVoltage, self.RESETREADVoltage, \
                        self.byte3_GateVoltageMSB, self.byte4_GateVoltageLSB, self.byte5_FORMSETVoltageMSB, \
                        self.byte6_FORMSETVoltageLSB, self.byte7_FORMSETTimeMSB, \
                        self.byte8_FORMSETTimeLSB, self.byte9_delayPeriodTimeMSB, \
                        self.byte10_delayPeriodTimeLSB, self.byte11_FORMSETREADVoltageMSB, \
                        self.byte12_FORMSETREADVoltageLSB, self.byte13_FORMSETREADTimeMSB, \
                        self.byte14_FORMSETREADTimeLSB, self.byte15_RESETVoltageMSB, \
                        self.byte16_RESETVoltageLSB, self.byte17_RESETTimeMSB, self.byte18_RESETTimeLSB, \
                        self.byte19_RESETREADVoltageMSB, self.byte20_RESETREADVoltageLSB, \
                        self.byte21_RESETREADTimeMSB, self.byte22_RESETREADTimeLSB, \
                        self.byte25_CyclesNumberMSB, self.byte26_CyclesNumberLSB, \
                        self.byte27_StepNumberMSB, self.byte28_StepNumberLSB, self.byte29_modeState, \
                        self.messageListBoxSETRESETSwitch, self.IVTestState, self.FORMSETStateString, \
                        self.invertIVStates, self.maxStepVoltage, \
                        self.SETGateVoltage, self.RESETGateVoltage, self.chosenStepVoltage, \
                        self.stepVoltageDirection, self.createSavePlots, self.stepNumber, \
                        self.utilizeCurResRange, self.pulseTestRangeMin, self.pulseTestRangeMax, \
                        self.pulseTestRangeCycleCount, self.createHeatMap, self.hardCodeDevices), \
                        padx = 8, pady = 15, bg = 'white')
        self.submitButtonSETRESETSwitch.place(x = 390, y = 435)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #submit button FOR IV TEST (put here AFTER CellGrid creation)

        #calls built-in "pressedSubmitData" function when button is pressed
        self.submitButtonIV = Button(self.IVCanvas, text = 'Send', command = lambda: \
                        pressedSubmitData(cellGrid, self.expectedPortDriverSearch, self.saveFileNameString, \
                        self.csvDirectoryString, self.toggledOhmsLawUnit, self.csvControlVariable, \
                        self.showRunTime, self.cycleNumber, self.FORMSETREADVoltage, self.RESETREADVoltage, \
                        self.byte3_GateVoltageMSB, self.byte4_GateVoltageLSB, self.byte5_FORMSETVoltageMSB, \
                        self.byte6_FORMSETVoltageLSB, self.byte7_FORMSETTimeMSB, \
                        self.byte8_FORMSETTimeLSB, self.byte9_delayPeriodTimeMSB, \
                        self.byte10_delayPeriodTimeLSB, self.byte11_FORMSETREADVoltageMSB, \
                        self.byte12_FORMSETREADVoltageLSB, self.byte13_FORMSETREADTimeMSB, \
                        self.byte14_FORMSETREADTimeLSB, self.byte15_RESETVoltageMSB, \
                        self.byte16_RESETVoltageLSB, self.byte17_RESETTimeMSB, self.byte18_RESETTimeLSB, \
                        self.byte19_RESETREADVoltageMSB, self.byte20_RESETREADVoltageLSB, \
                        self.byte21_RESETREADTimeMSB, self.byte22_RESETREADTimeLSB, \
                        self.byte25_CyclesNumberMSB, self.byte26_CyclesNumberLSB, \
                        self.byte27_StepNumberMSB, self.byte28_StepNumberLSB, self.byte29_modeState, \
                        self.messageListBoxIV, self.IVTestState, self.FORMSETStateString, \
                        self.invertIVStates, self.maxStepVoltage, \
                        self.SETGateVoltage, self.RESETGateVoltage, self.chosenStepVoltage, \
                        self.stepVoltageDirection, self.createSavePlots, self.stepNumber, \
                        self.utilizeCurResRange, self.pulseTestRangeMin, self.pulseTestRangeMax, \
                        self.pulseTestRangeCycleCount, self.createHeatMap, self.hardCodeDevices), \
                        padx = 8, pady = 15, bg = 'white')
        self.submitButtonIV.place(x = 405, y = 680)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #using the following class function(s) further down, call built-in
        #"createPulseCanvas" function from the start to initialize the canvas frame
        #with the pulseCanvas information
        if(self.startRun): #if initial run, call createPulseCanvas to start with Pulse testing display
            self.createPulseCanvas()

        # - - - - - - - - - - - - - - - - - - - - - - - -

        # Drop Down Menu

        #for the sake of avoiding the use of globals, initialize the Export
        #window here when this function nears the end of its first run
        if(self.startRun): #if initial run, initialize drop down menu Export window
            self.fileSaveWindow = None
        
        self.menuBar = Menu(masterWindow)
        self.fileMenu = Menu(self.menuBar, tearoff = 0)
        
        self.fileMenu.add_command(label = 'Export', command = lambda: \
                             self.initExportSettings(masterWindow)) #calls "initExportSettings" function
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label = "Exit", command = \
                             lambda: closeMaster(masterWindow)) #calls "closeMaster" function
        self.fileMenu.add_command(label = 'Import Excel Binary Grid', command = \
                                  lambda: self.importBinaryCSVToGrid(masterWindow, cellGrid)) #calls "importBinaryCSVToGrid" function
        
        self.menuBar.add_cascade(label = "File", menu = self.fileMenu)
        masterWindow.config(menu = self.menuBar)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #after everything has been initialized,the "start" run is now over,
        #so set the startRun boolean to False
        self.startRun = False

        #seeing how the "startRun window" is the "Pulse Testing" window and the user should
        #NOT be faster than the GUI's system, create the pulseCanvas logic AGAIN of the FORM/SET
        #state variables AFTER all this is done in order to guarantee the correct variable positions
        self.changeFORMSETState('FORM', self.FORMSelectButton, \
                                self.SETSelectButton, self.startRun, \
                                self.maxEntryXPosFirstColumn, self.foundFirstColumnEntryPos, \
                                self.maxEntryXPosSecondColumn, self.foundSecondColumnEntryPos, \
                                self.FORMSETStateString)

        #seeing how the "startRun window" is the "Pulse Testing" window and the user should
        #NOT be faster than the GUI's system, create the pulseStepCanvas logic AGAIN of the FORM/SET
        #state variables AFTER all this is done rather than waiting for the startRun like the
        #pulseCanvas in order to guarantee the correct variable positions
        self.changeFORMSETStateStep('FORM', self.FORMSelectButtonStep, \
                                self.SETSelectButtonStep, self.startRun, \
                                self.maxEntryXPosFirstColumnStep, self.foundFirstColumnEntryPosStep, \
                                self.maxEntryXPosSecondColumnStep, self.foundSecondColumnEntryPosStep, \
                                self.FORMSETStateString)

    #-----------------------------------------------------------------------------

    #populate the canvas frame with the information specific to the pulse testing
    #mode
    def createPulseCanvas(self):
        self.pulseStepCanvas.grid_forget() #hide the pulse STEP canvas grid
        self.pulseSETRESETSwitchCanvas.grid_forget() #hide the SET/RESET pulse test switching canvas
        self.IVCanvas.grid_forget() #hide the IV canvas grid
        self.pulseCanvas.grid(row = 0, column = 0, sticky = 'nsew') #show the pulse canvas info in the frame

        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE IV
        #CANVAS TO THEIR PULSE TEST DEFAULTS
        self.IVTestState.set('None')

        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE IV
        #CANVAS TO THEIR PULSE TEST DEFAULTS
        #NOTE: These ones are automatically changed between
        #IV test modes and, should the user go back to the Pulse
        #Test window, NOT RESETTING THESE will have these set
        #to 0 and this is done to avoid tedium
        self.FORMSETVoltage.set(3.3)
        self.FORMSETTime.set(100)
        self.FORMSETREADVoltage.set(0.2) 
        self.FORMSETREADTime.set(500) 
        self.RESETVoltage.set(1)
        self.RESETTime.set(100)
        self.RESETREADVoltage.set(0.2) 
        self.RESETREADTime.set(500) 
        self.stepNumber.set(0)
        self.byte29_modeState.set('Pulse Test')

        self.maxStepVoltage.set(0) #FOR PULSE STEP TEST ONLY
        self.chosenStepVoltage.set('None')
        self.stepVoltageDirection.set('None')

        #reset current/resistance button to its default current mode
        self.toggledOhmsLawUnit.set('uA')
        self.toggleOhmsLawUnitButton.config(text = self.toggledOhmsLawUnit.get())

        #PULSE TEST ONLY range variables
        self.utilizeCurResRange.set(False)
        self.pulseTestRangeMin.set(0)
        self.pulseTestRangeMax.set(1000000)
        self.pulseTestRangeCycleCount.set(1)

        #other PULSE TEST ONLY toggles
        self.createHeatMap.set(False)
        self.hardCodeDevices.set(False)

    #-----------------------------------------------------------------------------

    #populate the canvas frame with the information specific to the pulse STEP testing
    #mode
    def createPulseStepCanvas(self):
        self.pulseCanvas.grid_forget() #hide the pulse canvas grid
        self.pulseSETRESETSwitchCanvas.grid_forget() #hide the SET/RESET pulse test switching canvas
        self.IVCanvas.grid_forget() #hide the IV canvas grid
        self.pulseStepCanvas.grid(row = 0, column = 0, sticky = 'nsew') #show the pulse canvas info in the frame

        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE IV
        #CANVAS TO THEIR PULSE TEST DEFAULTS
        self.IVTestState.set('None')

        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE IV
        #CANVAS TO THEIR PULSE TEST DEFAULTS
        #NOTE: These ones are automatically changed between
        #IV test modes and, should the user go back to the Pulse
        #Test window, NOT RESETTING THESE will have these set
        #to 0 and this is done to avoid tedium
        self.FORMSETVoltage.set(3.3)
        self.FORMSETTime.set(100)
        self.FORMSETREADVoltage.set(0.2) 
        self.FORMSETREADTime.set(500) 
        self.RESETVoltage.set(1)
        self.RESETTime.set(100)
        self.RESETREADVoltage.set(0.2) 
        self.RESETREADTime.set(500) 
        self.stepNumber.set(25)
        self.byte29_modeState.set('Pulse Test - Step')

        self.maxStepVoltage.set(2)
        self.chosenStepVoltage.set('SET')

        if(not self.startRun): #set entry and value defaults if not opened on startup
            self.changeFORMSETRESETVoltageStep(self.chosenStepVoltage.get())
        
        self.stepVoltageDirection.set('Rising')

        #reset current/resistance button to its default current mode
        self.toggledOhmsLawUnit.set('uA')
        self.toggleOhmsLawUnitButton.config(text = self.toggledOhmsLawUnit.get())

        #PULSE TEST ONLY range variables
        self.utilizeCurResRange.set(False)
        self.pulseTestRangeMin.set(0)
        self.pulseTestRangeMax.set(0)
        self.pulseTestRangeCycleCount.set(0)

        #other PULSE TEST ONLY toggles
        self.createHeatMap.set(False)
        self.hardCodeDevices.set(False)

    #-----------------------------------------------------------------------------

    #populate the canvas frame with the information specific to the pulse testing
    #mode that switches between SET and RESET states every cycle
    def createPulseSETRESETSwitchCanvas(self):
        self.pulseCanvas.grid_forget() #hide the pulse canvas grid
        self.pulseStepCanvas.grid_forget() #hide the pulse STEP canvas grid
        self.IVCanvas.grid_forget() #hide the IV canvas grid

        #show the SET/RESET switching pulse test canvas info in the frame
        self.pulseSETRESETSwitchCanvas.grid(row = 0, column = 0, sticky = 'nsew')

        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE IV
        #CANVAS TO THEIR PULSE TEST DEFAULTS
        self.IVTestState.set('None')

        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE IV
        #CANVAS TO THEIR PULSE TEST DEFAULTS
        #NOTE: These ones are automatically changed between
        #IV test modes and, should the user go back to the Pulse
        #Test window, NOT RESETTING THESE will have these set
        #to 0 and this is done to avoid tedium
        self.FORMSETVoltage.set(2) #SET voltage
        self.FORMSETTime.set(100)
        self.FORMSETREADVoltage.set(0.2) 
        self.FORMSETREADTime.set(500) 
        self.RESETVoltage.set(1)
        self.RESETTime.set(100)
        self.RESETREADVoltage.set(0.2) 
        self.RESETREADTime.set(500) 
        self.stepNumber.set(0)
        self.byte29_modeState.set('Pulse Test - SET/RESET Switch')

        self.maxStepVoltage.set(0) #FOR PULSE STEP TEST ONLY
        self.chosenStepVoltage.set('None')
        self.stepVoltageDirection.set('None')

        #reset current/resistance button to its default current mode
        self.toggledOhmsLawUnit.set('uA')
        self.toggleOhmsLawUnitButton.config(text = self.toggledOhmsLawUnit.get())

        #PULSE TEST ONLY range variables
        self.utilizeCurResRange.set(False)
        self.pulseTestRangeMin.set(0)
        self.pulseTestRangeMax.set(0)
        self.pulseTestRangeCycleCount.set(0)

        #other PULSE TEST ONLY toggles
        self.createHeatMap.set(False)
        self.hardCodeDevices.set(False)
        
    #-----------------------------------------------------------------------------

    #populate the canvas frame with the information specific to the IV testing
    #mode
    def createIVCanvas(self):
        self.pulseCanvas.grid_forget() #hide the pulse canvas grid
        self.pulseStepCanvas.grid_forget() #hide the pulse STEP canvas grid
        self.pulseSETRESETSwitchCanvas.grid_forget() #hide the SET/RESET pulse test switching canvas
        self.IVCanvas.grid(row = 0, column = 0, sticky = 'nsew') #show the IV canvas info in the frame

        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE PULSE
        #CANVAS TO THEIR IV TEST DEFAULTS
        self.FORMSETREADVoltage.set(2)
        self.RESETREADVoltage.set(1)
        self.IVTestState.set('FORM')
        self.stepNumber.set(25)
        self.byte29_modeState.set('IV Test')

        self.maxStepVoltage.set(0) #FOR PULSE STEP TEST ONLY
        self.chosenStepVoltage.set('None')
        self.stepVoltageDirection.set('None')

        #set to current her to avoid possible resistance toggle carried over from
        #previous Pulse test mode selection
        self.toggledOhmsLawUnit.set('uA')

        #PULSE TEST ONLY range variables
        self.utilizeCurResRange.set(False)
        self.pulseTestRangeMin.set(0)
        self.pulseTestRangeMax.set(0)
        self.pulseTestRangeCycleCount.set(0)

        #other PULSE TEST ONLY toggles
        self.createHeatMap.set(False)
        self.hardCodeDevices.set(False)

    #-----------------------------------------------------------------------------

    #to show which state between FORM and SET is selected, this function
    #will change the button color and change next input variable's string
    #alongside the byte information in the background
    def changeFORMSETState(self, stateString, FORMButton, SETButton, startRun, \
                           maxEntryXPosFirstColumn, foundFirstColumnEntryPos, \
                           maxEntryXPosSecondColumn, foundSecondColumnEntryPos, \
                           FORMSETStateString):

        #for the sake of avoiding any overlap, destroy any older instances of
        #these widgets when toggled (specifically the labels to avoid any staying
        #when the Entry box is shifted) if not the first instance of this function
        #being called
        if(not startRun): #if this function is called later than the code's first run, reset the visuals
            #FORM/SET voltage
            self.currentFORMSETVoltageLabel.destroy()
            self.currentFORMSETVoltageEntry.destroy()
            self.currentFORMSETVoltageUnitLabel.destroy()

            #FORM/SET time
            self.currentFORMSETTimeLabel.destroy()
            self.currentFORMSETTimeEntry.destroy()
            self.currentFORMSETTimeUnitLabel.destroy()

            #FORM/SET READ voltage
            self.currentFORMSETREADVoltageLabel.destroy()
            self.currentFORMSETREADVoltageEntry.destroy()
            self.currentFORMSETREADVoltageUnitLabel.destroy()

            #FORM/SET READ time
            self.currentFORMSETREADTimeLabel.destroy()
            self.currentFORMSETREADTimeEntry.destroy()
            self.currentFORMSETREADTimeUnitLabel.destroy()

            
        if(stateString == 'FORM'): #if FORM state, configure GUI to prepare for FORM inputs
            #change associated button color to green to show it's selected
            FORMButton.config(bg = 'lightgreen')
            SETButton.config(bg = 'light gray') #set other button color to the default

            #change which voltage string is being displayed next to the corresponding entry
            #AND set the Entry value to the default value of THIS specific state
            self.FORMSETVoltage.set(3.3) #voltage, CHANGE IF NECESSARY

            #variable label
            self.currentFORMSETVoltageLabel = Label(self.pulseCanvas, text = 'FORM Voltage:', font = \
                       ('calibre', 10, 'normal'))

            self.FORMSETStateString.set('FORM')

        else: #otherwise, SET state, configure GUI to prepare for SET inputs
            #change associated button color to green to show it's selected
            SETButton.config(bg = 'lightgreen')
            FORMButton.config(bg = 'light gray') #set other button color to the default

            #change which voltage string is being displayed next to the corresponding entry
            #AND set the Entry value to the default value of THIS specific state
            self.FORMSETVoltage.set(2) #voltage, CHANGE IF NECESSARY

            #variable label
            self.currentFORMSETVoltageLabel = Label(self.pulseCanvas, text = 'SET Voltage:', font = \
                       ('calibre', 10, 'normal'))

            self.FORMSETStateString.set('SET')

        #NOTE: All voltage values to be inputted to the PCB are in
        #MILLIVOLTS, so perform the conversion during the byte
        #splitting process (1000 millivolts = 1 volt)
        #NOTE: For the sake of all byte information being in "Int" format,
        #convert the floats to integers post multiplication
        self.MSBFORMSETVoltHexInt, self.LSBFORMSETVoltHexInt = \
                  twoByteComboSplit(int(self.FORMSETVoltage.get() * 1000))
        self.byte5_FORMSETVoltageMSB.set(str(self.MSBFORMSETVoltHexInt))
        self.byte6_FORMSETVoltageLSB.set(str(self.LSBFORMSETVoltHexInt))

        #variable label placement
        self.currentFORMSETVoltageLabel.place(x = int(self.FORMOrSETLabel.place_info()['x']), y = \
                              int(self.FORMSelectButton.place_info()['y']) + \
                              int(self.FORMSelectButton.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.currentFORMSETVoltageLabel.update()

        #entry widget to input data
        self.currentFORMSETVoltageEntry = Entry(self.pulseCanvas, width = 6, textvariable = \
                                                self.FORMSETVoltage, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.currentFORMSETVoltageEntry.place(x = \
                                    int(self.currentFORMSETVoltageLabel.place_info()['x']) + \
                                    int(self.currentFORMSETVoltageLabel.winfo_width()), y = \
                                    self.currentFORMSETVoltageLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.currentFORMSETVoltageEntry.update()
    
        # - - - - - - - - - - - - - -

        #create/toggle the widgets for the selected (non-read) state's time
        #information as well

        #variable label
        self.currentFORMSETTimeLabel = Label(self.pulseCanvas, text = ''.join([stateString, \
                                            ' Time:']), font = \
                       ('calibre', 10, 'normal'))
        self.currentFORMSETTimeLabel.place(x = int(self.currentFORMSETVoltageLabel.place_info()['x']), \
                            y = int(self.currentFORMSETVoltageLabel.place_info()['y']) + \
                            int(self.currentFORMSETVoltageLabel.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.currentFORMSETTimeLabel.update()

        #entry widget to input data
        self.currentFORMSETTimeEntry = Entry(self.pulseCanvas, width = 6, textvariable = \
                                                self.FORMSETTime, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.currentFORMSETTimeEntry.place(x = \
                                    int(self.currentFORMSETTimeLabel.place_info()['x']) + \
                                    int(self.currentFORMSETTimeLabel.winfo_width()), y = \
                                    self.currentFORMSETTimeLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.currentFORMSETTimeEntry.update()

        #if on a new cycle where the maximum first column
        #Entry position is found, set the Entry and corresponding
        #unit label positions based on that value
        if(foundFirstColumnEntryPos):
            self.currentFORMSETVoltageEntry.place(x = maxEntryXPosFirstColumn, \
                            y = self.currentFORMSETVoltageEntry.place_info()['y'])
            
            self.currentFORMSETTimeEntry.place(x = maxEntryXPosFirstColumn, \
                            y = self.currentFORMSETTimeEntry.place_info()['y'])

        #voltage unit label
        self.currentFORMSETVoltageUnitLabel = Label(self.pulseCanvas, text = 'V', font = \
                       self.gateVoltageLabel['font'])
        self.currentFORMSETVoltageUnitLabel.place(x = \
                                    int(self.currentFORMSETVoltageEntry.place_info()['x']) + \
                                    int(self.currentFORMSETVoltageEntry.winfo_width()), y = \
                                    self.currentFORMSETVoltageEntry.place_info()['y'])

        #time unit label
        self.currentFORMSETTimeUnitLabel = Label(self.pulseCanvas, text = 'us', font = \
                       self.gateVoltageLabel['font'])
        self.currentFORMSETTimeUnitLabel.place(x = \
                                    int(self.currentFORMSETTimeEntry.place_info()['x']) + \
                                    int(self.currentFORMSETTimeEntry.winfo_width()), y = \
                                    self.currentFORMSETTimeEntry.place_info()['y'])

        # - - - - - - - - - - - - - -

        #create/toggle the READ widgets for the selected state's voltage info

        #variable label        
        self.currentFORMSETREADVoltageLabel = Label(self.pulseCanvas, text = ''.join([stateString, \
                                            ' READ Voltage:']), font = ('calibre', 10, 'normal'))
        self.currentFORMSETREADVoltageLabel.place(x = int(self.delayPeriodLabel.place_info()['x']), y = \
                                  int(self.delayPeriodLabel.place_info()['y']) + \
                                  int(self.delayPeriodLabel.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.currentFORMSETREADVoltageLabel.update()

        #entry widget to input data
        self.currentFORMSETREADVoltageEntry = Entry(self.pulseCanvas, width = 6, textvariable = \
                                                self.FORMSETREADVoltage, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.currentFORMSETREADVoltageEntry.place(x = \
                                    int(self.currentFORMSETREADVoltageLabel.place_info()['x']) + \
                                    int(self.currentFORMSETREADVoltageLabel.winfo_width()), y = \
                                    self.currentFORMSETREADVoltageLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.currentFORMSETREADVoltageEntry.update()

        # - - - - - - - - - - - - - -

        #create/toggle the READ widgets for the selected state's time info

        #variable label
        self.currentFORMSETREADTimeLabel = Label(self.pulseCanvas, text = ''.join([stateString, \
                                            ' READ Time:']), font = ('calibre', 10, 'normal'))
        self.currentFORMSETREADTimeLabel.place(x = int(self.currentFORMSETREADVoltageLabel.place_info()['x']), \
                            y = int(self.currentFORMSETREADVoltageLabel.place_info()['y']) + \
                            int(self.currentFORMSETREADVoltageLabel.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.currentFORMSETREADTimeLabel.update()

        #entry widget to input data
        self.currentFORMSETREADTimeEntry = Entry(self.pulseCanvas, width = 6, textvariable = \
                                                self.FORMSETREADTime, \
                        font = self.gateVoltageLabel['font'], bg = 'white')
        self.currentFORMSETREADTimeEntry.place(x = \
                                    int(self.currentFORMSETREADTimeLabel.place_info()['x']) + \
                                    int(self.currentFORMSETREADTimeLabel.winfo_width()), y = \
                                    self.currentFORMSETREADTimeLabel.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.currentFORMSETREADTimeEntry.update()

        # - - - - -

        #if on a new cycle where the maximum second column
        #Entry position is found, set the Entry and corresponding
        #unit label positions based on that value
        if(foundSecondColumnEntryPos):
            self.currentFORMSETREADVoltageEntry.place(x = maxEntryXPosSecondColumn, \
                            y = self.currentFORMSETREADVoltageEntry.place_info()['y'])
            
            self.currentFORMSETREADTimeEntry.place(x = maxEntryXPosSecondColumn, \
                            y = self.currentFORMSETREADTimeEntry.place_info()['y'])

        #voltage unit label
        self.currentFORMSETREADVoltageUnitLabel = Label(self.pulseCanvas, text = 'V', font = \
                       self.gateVoltageLabel['font'])
        self.currentFORMSETREADVoltageUnitLabel.place(x = \
                                    int(self.currentFORMSETREADVoltageEntry.place_info()['x']) + \
                                    int(self.currentFORMSETREADVoltageEntry.winfo_width()), y = \
                                    self.currentFORMSETREADVoltageEntry.place_info()['y'])

        #time unit label
        self.currentFORMSETREADTimeUnitLabel = Label(self.pulseCanvas, text = 'us', font = \
                       self.gateVoltageLabel['font'])
        self.currentFORMSETREADTimeUnitLabel.place(x = \
                                    int(self.currentFORMSETREADTimeEntry.place_info()['x']) + \
                                    int(self.currentFORMSETREADTimeEntry.winfo_width()), y = \
                                    self.currentFORMSETREADTimeEntry.place_info()['y'])

    #-----------------------------------------------------------------------------

    #to show which state between FORM and SET is selected, this function
    #will change the button color and change next input variable's string
    #alongside the byte information in the background, STEP VOLTAGE ONLY
    def changeFORMSETStateStep(self, stateString, FORMButton, SETButton, startRun, \
                           maxEntryXPosFirstColumn, foundFirstColumnEntryPos, \
                           maxEntryXPosSecondColumn, foundSecondColumnEntryPos, \
                           FORMSETStateString):

        #for the sake of avoiding any overlap, destroy any older instances of
        #these widgets when toggled (specifically the labels to avoid any staying
        #when the Entry box is shifted) if not the first instance of this function
        #being called
        if(not startRun): #if this function is called later than the code's first run, reset the visuals
            #FORM/SET voltage
            self.currentFORMSETVoltageLabelStep.destroy()
            self.currentFORMSETVoltageEntryStep.destroy()
            self.currentFORMSETVoltageUnitLabelStep.destroy()

            #FORM/SET time
            self.currentFORMSETTimeLabelStep.destroy()
            self.currentFORMSETTimeEntryStep.destroy()
            self.currentFORMSETTimeUnitLabelStep.destroy()

            #FORM/SET READ voltage
            self.currentFORMSETREADVoltageLabelStep.destroy()
            self.currentFORMSETREADVoltageEntryStep.destroy()
            self.currentFORMSETREADVoltageUnitLabelStep.destroy()

            #FORM/SET READ time
            self.currentFORMSETREADTimeLabelStep.destroy()
            self.currentFORMSETREADTimeEntryStep.destroy()
            self.currentFORMSETREADTimeUnitLabelStep.destroy()

        if(stateString == 'FORM'): #if FORM state, configure GUI to prepare for FORM inputs
            #change associated button color to green to show it's selected
            FORMButton.config(bg = 'lightgreen')
            SETButton.config(bg = 'light gray') #set other button color to the default

            #change which voltage string is being displayed next to the corresponding entry
            #AND set the Entry value to the default value of THIS specific state
            self.FORMSETVoltage.set(3.3) #voltage, CHANGE IF NECESSARY

            #variable label
            self.currentFORMSETVoltageLabelStep = Label(self.pulseStepCanvas, text = 'Min FORM Voltage:', font = \
                       ('calibre', 10, 'normal'))

            self.FORMSETStateString.set('FORM')

        else: #otherwise, SET state, configure GUI to prepare for SET inputs
            #change associated button color to green to show it's selected
            SETButton.config(bg = 'lightgreen')
            FORMButton.config(bg = 'light gray') #set other button color to the default

            #change which voltage string is being displayed next to the corresponding entry
            #AND set the Entry value to the default value of THIS specific state
            self.FORMSETVoltage.set(2) #voltage, CHANGE IF NECESSARY

            #variable label
            self.currentFORMSETVoltageLabelStep = Label(self.pulseStepCanvas, text = 'Min SET Voltage:', font = \
                       ('calibre', 10, 'normal'))

            self.FORMSETStateString.set('SET')

        #NOTE: All voltage values to be inputted to the PCB are in
        #MILLIVOLTS, so perform the conversion during the byte
        #splitting process (1000 millivolts = 1 volt)
        #NOTE: For the sake of all byte information being in "Int" format,
        #convert the floats to integers post multiplication
        self.MSBFORMSETVoltHexInt, self.LSBFORMSETVoltHexInt = \
                  twoByteComboSplit(int(self.FORMSETVoltage.get() * 1000))
        self.byte5_FORMSETVoltageMSB.set(str(self.MSBFORMSETVoltHexInt))
        self.byte6_FORMSETVoltageLSB.set(str(self.LSBFORMSETVoltHexInt))

        #variable label placement
        self.currentFORMSETVoltageLabelStep.place(x = int(self.FORMOrSETLabelStep.place_info()['x']), y = \
                              int(self.FORMSelectButtonStep.place_info()['y']) + \
                              int(self.FORMSelectButtonStep.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.currentFORMSETVoltageLabelStep.update()

        #entry widget to input data
        self.currentFORMSETVoltageEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = \
                                                self.FORMSETVoltage, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.currentFORMSETVoltageEntryStep.place(x = \
                                    int(self.currentFORMSETVoltageLabelStep.place_info()['x']) + \
                                    int(self.currentFORMSETVoltageLabelStep.winfo_width()), y = \
                                    self.currentFORMSETVoltageLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.currentFORMSETVoltageEntryStep.update()
    
        # - - - - - - - - - - - - - -

        #create/toggle the widgets for the selected (non-read) state's time
        #information as well

        #variable label
        self.currentFORMSETTimeLabelStep = Label(self.pulseStepCanvas, text = ''.join([stateString, \
                                            ' Time:']), font = \
                       ('calibre', 10, 'normal'))
        self.currentFORMSETTimeLabelStep.place(x = int(self.currentFORMSETVoltageLabelStep.place_info()['x']), \
                            y = int(self.currentFORMSETVoltageLabelStep.place_info()['y']) + \
                            int(self.currentFORMSETVoltageLabelStep.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.currentFORMSETTimeLabelStep.update()

        #entry widget to input data
        self.currentFORMSETTimeEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = \
                                                self.FORMSETTime, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.currentFORMSETTimeEntryStep.place(x = \
                                    int(self.currentFORMSETTimeLabelStep.place_info()['x']) + \
                                    int(self.currentFORMSETTimeLabelStep.winfo_width()), y = \
                                    self.currentFORMSETTimeLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.currentFORMSETTimeEntryStep.update()

        #if on a new cycle where the maximum first column
        #Entry position is found, set the Entry and corresponding
        #unit label positions based on that value
        if(foundFirstColumnEntryPos):
            self.currentFORMSETVoltageEntryStep.place(x = maxEntryXPosFirstColumn, \
                            y = self.currentFORMSETVoltageEntryStep.place_info()['y'])
            
            self.currentFORMSETTimeEntryStep.place(x = maxEntryXPosFirstColumn, \
                            y = self.currentFORMSETTimeEntryStep.place_info()['y'])

        #voltage unit label
        self.currentFORMSETVoltageUnitLabelStep = Label(self.pulseStepCanvas, text = 'V', font = \
                       self.gateVoltageLabelStep['font'])
        self.currentFORMSETVoltageUnitLabelStep.place(x = \
                                    int(self.currentFORMSETVoltageEntryStep.place_info()['x']) + \
                                    int(self.currentFORMSETVoltageEntryStep.winfo_width()), y = \
                                    self.currentFORMSETVoltageEntryStep.place_info()['y'])

        #time unit label
        self.currentFORMSETTimeUnitLabelStep = Label(self.pulseStepCanvas, text = 'us', font = \
                       self.gateVoltageLabelStep['font'])
        self.currentFORMSETTimeUnitLabelStep.place(x = \
                                    int(self.currentFORMSETTimeEntryStep.place_info()['x']) + \
                                    int(self.currentFORMSETTimeEntryStep.winfo_width()), y = \
                                    self.currentFORMSETTimeEntryStep.place_info()['y'])

        # - - - - - - - - - - - - - -

        #create/toggle the READ widgets for the selected state's voltage info

        #variable label        
        self.currentFORMSETREADVoltageLabelStep = Label(self.pulseStepCanvas, text = ''.join([stateString, \
                                            ' READ Voltage:']), font = ('calibre', 10, 'normal'))
        self.currentFORMSETREADVoltageLabelStep.place(x = int(self.delayPeriodLabelStep.place_info()['x']), y = \
                                  int(self.delayPeriodLabelStep.place_info()['y']) + \
                                  int(self.delayPeriodLabelStep.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.currentFORMSETREADVoltageLabelStep.update()

        #entry widget to input data
        self.currentFORMSETREADVoltageEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = \
                                                self.FORMSETREADVoltage, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.currentFORMSETREADVoltageEntryStep.place(x = \
                                    int(self.currentFORMSETREADVoltageLabelStep.place_info()['x']) + \
                                    int(self.currentFORMSETREADVoltageLabelStep.winfo_width()), y = \
                                    self.currentFORMSETREADVoltageLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.currentFORMSETREADVoltageEntryStep.update()

        # - - - - - - - - - - - - - -

        #create/toggle the READ widgets for the selected state's time info

        #variable label
        self.currentFORMSETREADTimeLabelStep = Label(self.pulseStepCanvas, text = ''.join([stateString, \
                                            ' READ Time:']), font = ('calibre', 10, 'normal'))
        self.currentFORMSETREADTimeLabelStep.place(x = int(self.currentFORMSETREADVoltageLabelStep.place_info()['x']), \
                            y = int(self.currentFORMSETREADVoltageLabelStep.place_info()['y']) + \
                            int(self.currentFORMSETREADVoltageLabelStep.winfo_height()) + 5)

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.currentFORMSETREADTimeLabelStep.update()

        #entry widget to input data
        self.currentFORMSETREADTimeEntryStep = Entry(self.pulseStepCanvas, width = 6, textvariable = \
                                                self.FORMSETREADTime, \
                        font = self.gateVoltageLabelStep['font'], bg = 'white')
        self.currentFORMSETREADTimeEntryStep.place(x = \
                                    int(self.currentFORMSETREADTimeLabelStep.place_info()['x']) + \
                                    int(self.currentFORMSETREADTimeLabelStep.winfo_width()), y = \
                                    self.currentFORMSETREADTimeLabelStep.place_info()['y'])

        #update the widget to update the widget place and width info for
        #position calculations below for unit Label widget
        self.currentFORMSETREADTimeEntryStep.update()

        # - - - - -

        #if on a new cycle where the maximum second column
        #Entry position is found, set the Entry and corresponding
        #unit label positions based on that value
        if(foundSecondColumnEntryPos):
            self.currentFORMSETREADVoltageEntryStep.place(x = maxEntryXPosSecondColumn, \
                            y = self.currentFORMSETREADVoltageEntryStep.place_info()['y'])
            
            self.currentFORMSETREADTimeEntryStep.place(x = maxEntryXPosSecondColumn, \
                            y = self.currentFORMSETREADTimeEntryStep.place_info()['y'])

        #voltage unit label
        self.currentFORMSETREADVoltageUnitLabelStep = Label(self.pulseStepCanvas, text = 'V', font = \
                       self.gateVoltageLabelStep['font'])
        self.currentFORMSETREADVoltageUnitLabelStep.place(x = \
                                    int(self.currentFORMSETREADVoltageEntryStep.place_info()['x']) + \
                                    int(self.currentFORMSETREADVoltageEntryStep.winfo_width()), y = \
                                    self.currentFORMSETREADVoltageEntryStep.place_info()['y'])

        #time unit label
        self.currentFORMSETREADTimeUnitLabelStep = Label(self.pulseStepCanvas, text = 'us', font = \
                       self.gateVoltageLabelStep['font'])
        self.currentFORMSETREADTimeUnitLabelStep.place(x = \
                                    int(self.currentFORMSETREADTimeEntryStep.place_info()['x']) + \
                                    int(self.currentFORMSETREADTimeEntryStep.winfo_width()), y = \
                                    self.currentFORMSETREADTimeEntryStep.place_info()['y'])

        #if this function is called later than the code's first run, reset the visuals
        #of changeFORMSETRESETVoltageStep, as changing these values after switching the
        #changeFORMSETRESETVoltageStep buttons THEN the FORM/SET state buttons will
        #not maintain which buttons are disabled
        if(not startRun and self.byte29_modeState.get() == 'Pulse Test - Step'):
            self.changeFORMSETRESETVoltageStep(self.chosenStepVoltage.get())

    #-----------------------------------------------------------------------------

    #function for determining the "direction" between the starting voltage and maximum
    #step voltage IN THE PULSE STEP TEST the step voltage logic should proceed, be
    #it "rising" from the start V to the max step V, the "fall" inverse equivalent, or
    #BOTH "rising then falling"
    #this function is also responsible for changing the appearance of the corresponding
    #step voltage "direction" buttons within this mode's GUI to show which option is selected
    def changeStepVoltageDirectionStep(self, chosenDirection):

        #determine state logic for stepVoltageDirection variable and change button
        #color based on inputted chosenDirection string
        if(chosenDirection == 'Rising'): #if RISING button was selected

            #set the background of the corresponding direction's button to light green while
            #setting the background of the other buttons to the default light gray
            self.risingStepVoltageButton.config(bg = 'lightgreen')
            self.fallingStepVoltageButton.config(bg = 'light gray')
            self.riseAndFallStepVoltageButton.config(bg = 'light gray')
            
        elif(chosenDirection == 'Falling'): #if FALLING button was selected

            #set the background of the corresponding direction's button to light green while
            #setting the background of the other buttons to the default light gray
            self.risingStepVoltageButton.config(bg = 'light gray')
            self.fallingStepVoltageButton.config(bg = 'lightgreen')
            self.riseAndFallStepVoltageButton.config(bg = 'light gray')
            
        else: #otherwise, RISE THEN FALL button was selected

            #set the background of the corresponding direction's button to light green while
            #setting the background of the other buttons to the default light gray
            self.risingStepVoltageButton.config(bg = 'light gray')
            self.fallingStepVoltageButton.config(bg = 'light gray')
            self.riseAndFallStepVoltageButton.config(bg = 'lightgreen')

        #set stepVoltageDirection variable to corresponding direction decision
        self.stepVoltageDirection.set(chosenDirection)

    #-----------------------------------------------------------------------------

    #function between FORM/SET and RESET voltage selection buttons that will set the
    #chosenStepVoltage variable alongside changing the button colors to show which
    #state is selected
    def changeFORMSETRESETVoltageStep(self, chosenState):

        if(chosenState == 'SET'): #if FORM/SET state

            self.chosenStepVoltage.set('SET')

            #change button colors to show which one is selected
            self.FORMSETVoltageStepChosenButton.config(bg = 'lightgreen')
            self.RESETVoltageStepChosenButton.config(bg = 'light gray')

            #set the RESET voltage data to 0, including the READ voltage
            self.RESETVoltage.set(0)
            self.RESETREADVoltage.set(0)

            #return the FORM/SET voltages to their defaults, should this
            #chosenState be reselected after switching between them beforehand
            self.FORMSETVoltage.set(3.3)
            self.FORMSETREADVoltage.set(0.2)
            self.currentFORMSETVoltageEntryStep.config(state = 'normal')
            self.currentFORMSETREADVoltageEntryStep.config(state = 'normal')

            #disable the RESET voltage data entries to avoid changing these values
            self.RESETVoltageEntryStep.config(state = 'disabled')
            self.RESETREADVoltageEntryStep.config(state = 'disabled')

        else: #otherwise, RESET

            self.chosenStepVoltage.set('RESET')

            #change button colors to show which one is selected
            self.RESETVoltageStepChosenButton.config(bg = 'lightgreen')
            self.FORMSETVoltageStepChosenButton.config(bg = 'light gray')

            #set the FORM/SET voltage data to 0, including the READ voltage
            self.FORMSETVoltage.set(0)
            self.FORMSETREADVoltage.set(0)

            #return the RESET voltages to their defaults, should this
            #chosenState be reselected after switching between them beforehand
            self.RESETVoltage.set(1)
            self.RESETREADVoltage.set(0.2)
            self.RESETVoltageEntryStep.config(state = 'normal')
            self.RESETREADVoltageEntryStep.config(state = 'normal')

            #disable the FORM/SET voltage data entries to avoid changing these values
            self.currentFORMSETVoltageEntryStep.config(state = 'disabled')
            self.currentFORMSETREADVoltageEntryStep.config(state = 'disabled')

    #-----------------------------------------------------------------------------

    #update IVTestState with the newStateString that was selected via button press
    def pressedIVStateChange(self, IVTestState, newStateString):

        IVTestState.set(newStateString)

    #-----------------------------------------------------------------------------

    #function that will toggle off the widgets of the mode that is currently NOT
    #selected while highlighting which mode is selected by making its corresponding
    #button light green
    #also, any byte information expected to be set to 0 based on the selected mode
    #will be addressed here
    def updateIVTestState(self, newIVTestState, IVCanvas):

        if(newIVTestState.get() != 'None'): #if focusing STRICTLY on the IV Test

            for canvasWidget in IVCanvas.winfo_children(): #for all IV Canvas widgets

                #focus strictly on the labelFrame information
                if(isinstance(canvasWidget, tk.LabelFrame)):
                    
                    #look at the name of the labelFrame and, if it does NOT have an exact
                    #match as newIVTestState, DISABLE ALL ENTRY WIDGETS, also
                    #reset the color of the buttons to their defaults if one of the
                    #state buttons was previously selected
                    #NOTE: In the unique case of "SET" being within "RESET", this specific
                    #condition will also be checked in the following IF statement by checking
                    #if the newIVTestState string is an EXACT match for the FIRST FULL
                    #WORD of the labelFrame title
                    if(newIVTestState.get() != canvasWidget.cget('text').split()[0]):

                        #set all of the different state's Entry widgets to disabled
                        #and reset the button color
                        for differentIVStateWidget in canvasWidget.winfo_children():

                            if(isinstance(differentIVStateWidget, tk.Entry)):
                                differentIVStateWidget.config(state = 'disabled')
                            elif(isinstance(differentIVStateWidget, tk.Button)):
                                differentIVStateWidget.config(bg = 'light gray')

                    #also, if the labelFrame is the one selected, ENABLE all Entry
                    #widgets AND set its corresponding button color to showcase that
                    #it's selected
                    else:

                        #set all of the CORRECT state's Entry widgets to ENABLED
                        #and set the button color to light green
                        for correctIVStateWidget in canvasWidget.winfo_children():

                            if(isinstance(correctIVStateWidget, tk.Entry)):
                                correctIVStateWidget.config(state = 'normal')
                            elif(isinstance(correctIVStateWidget, tk.Button)):
                                correctIVStateWidget.config(bg = 'lightgreen')

        # - - - - - - - - - - - - - - - - - - -

        #now, based on the specific selected mode, any byte information NOT AVAILABLE
        #IN THE FRAME'S LIST OF ENTRIES WILL BE SET TO 0 REGARDLESS OF WHAT THEY WERE
        #NOTE: The selected bytes being set to 0 are defined in the GUI requireents doc
        #provided by Jeelka
        #NOTE: In the unique case of the "IV" state, the changes will be IGNORED here
        #and will instead by implemented in "pressedSubmitData" function with the alternating
        #FORM/SET and RESET byte information instances
        if(newIVTestState.get() == 'FORM'): #if the new state is the FORM state, set FORM bytes

            self.FORMSETVoltage.set(0)
            self.FORMSETTime.set(0)
            self.RESETVoltage.set(0)
            self.RESETTime.set(0)
            self.RESETREADVoltage.set(0)
            self.RESETREADTime.set(0)

            #set this state's used information that could be set to 0 in another state
            #back to its defaults
            self.FORMSETREADVoltage.set(3.3)
            self.FORMSETREADTime.set(500)

        elif(newIVTestState.get() == 'SET'): #if the new state is the SET state, set SET bytes

            self.FORMSETVoltage.set(0)
            self.FORMSETTime.set(0)
            self.RESETVoltage.set(0)
            self.RESETTime.set(0)
            self.RESETREADVoltage.set(0)
            self.RESETREADTime.set(0)

            #set this state's used information that could be set to 0 in another state
            #back to its defaults
            self.FORMSETREADVoltage.set(2)
            self.FORMSETREADTime.set(500)

        elif(newIVTestState.get() == 'RESET'): #if the new state is the RESET state, set RESET bytes

            self.FORMSETVoltage.set(0)
            self.FORMSETTime.set(0)
            self.FORMSETREADVoltage.set(0)
            self.FORMSETREADTime.set(0)
            self.RESETVoltage.set(0)
            self.RESETTime.set(0)

            #set this state's used information that could be set to 0 in another state
            #back to its defaults
            self.RESETREADVoltage.set(1)
            self.RESETREADTime.set(500)

        else: #otherwise, IV state, set IV bytes

            self.FORMSETVoltage.set(0)
            self.FORMSETTime.set(0)
            self.RESETVoltage.set(0)
            self.RESETTime.set(0)

            self.FORMSETREADVoltage.set(2)
            self.FORMSETREADTime.set(500)
            self.RESETREADVoltage.set(1)
            self.RESETREADTime.set(500)

    #-------------------------------------------------------------------------

    #initializes and opens import CSV file window
    def importBinaryCSVToGrid(self, masterWindow, cellGrid):

        #get the file to be imported by finding the file path (.csv files ONLY)
        CSVFilePath = tk.filedialog.askopenfilename(title = "Select CSV File", \
                                                 filetypes = (("CSV files", "*.csv"), ("All files", "*.*")))

        #extra print statement to show that a file was selected for arbitrary reassurance
        if CSVFilePath:
            print("Selected file:", CSVFilePath)

        # - - - - - - - - - - - - - - - - - - - - - - -

        #extract the binary information of the import .csv file
        importedGrid = []

        #open the file in a read format as a means of getting the data
        with open(CSVFilePath, mode = 'r', encoding = 'utf-8-sig') as readFile:

            readerData = csv.reader(readFile) #use csv.reader to get the file data

            #NOTE: this will change with the CellGrid dimensions
            startRow = 0
            startColumn = 0
            maxRow = cellGrid.returnRowNum()
            maxColumn = cellGrid.returnColumnNum()

            #since this is a 2D grid, enumerate through the rows and columns of individual cells
            for column, row in enumerate(readerData):
                
                if(column >= startRow + maxRow): #break enumeration logic, will loop otherwise
                    break

                #get full row with all (maxColumn) # of columns
                currentRow = row[startColumn:startColumn + maxColumn]

                #save the currentRow information before going to the next column in importedGrid list
                importedGrid.append(currentRow)

        # - - - - - - - - - - - - - - - - - - - - - - -

        #now that the Excel data has all been imported, change the boolean/grid logic
        #of the cellGrid

        #first, set all of the cells to False to reset the grid before adding the logic
        cellGrid.allFalse()

        #iterate though entire importedGrid using the two FOR loops based on the grid dimensions
        for row in range(maxRow):
            for column in range(maxColumn):

                #if the importedGrid cell has a 1, set the corresponding
                #cellGrid to pressed
                if(int(importedGrid[row][column]) == 1):
                    cellGrid.clickedButton(row, column)
        
    #-------------------------------------------------------------------------

    #opens import CSV file for grid binary window
    def openCSVFileWindow(self, masterWindow):

        #create the fileSaveWindow and assign dimensions
        self.fileSaveWindow = Toplevel(masterWindow)
        self.fileSaveWindow.title('Export Settings')
        self.fileSaveWindowCanvas = Canvas(self.fileSaveWindow, width = 450, height = 130)

        #separate window in N number of equally spaced columns/rows
        self.fileSaveWindowCanvas.grid(rowspan = 20, columnspan = 4)

        self.fileSaveWindow.resizable(False, False)

        # - - - - - - - - - - - - - - - -
        
    #-------------------------------------------------------------------------      

    #initializes and opens export setting window
    def initExportSettings(self, masterWindow):

        try: #check if already open, call "openFileSaveWindow" if not

            if(self.fileSaveWindow.state() == 'normal'): #if currently open (state = normal means it's open)
                print('already open') #state that it's open already
                self.fileSaveWindow.focus()

        except:
            self.openFileSaveWindow(masterWindow) #calls built in "openFileSaveWindow" function

    #-------------------------------------------------------------------------

    #opens export settings window
    def openFileSaveWindow(self, masterWindow):

        #create the fileSaveWindow and assign dimensions
        self.fileSaveWindow = Toplevel(masterWindow)
        self.fileSaveWindow.title('Export Settings')
        self.fileSaveWindowCanvas = Canvas(self.fileSaveWindow, width = 450, height = 130)

        #separate window in N number of equally spaced columns/rows
        self.fileSaveWindowCanvas.grid(rowspan = 20, columnspan = 4)

        self.fileSaveWindow.resizable(False, False)

        # - - - - - - - - - - - - - - - -

        #declare the variables that will be shared between widgets
        self.saveFileName = StringVar()
        self.saveDirectory = StringVar()

        # - - - - - - - - - - - - - - - -

        #create the widgets for this window

        #labels
        self.nameOfFileLabel = Label(self.fileSaveWindow, text = 'Name of file:', font = \
                                ('calibre', 10, 'normal')).place(relx = 0.05, rely = 0.6)
        self.csvFileExtensionLabel = Label(self.fileSaveWindow, text = '.csv', font = \
                                      ('calibre', 10, 'normal')).place(relx = 0.65, rely = 0.6)
        self.currentFolderLabel = Label(self.fileSaveWindow, text = 'Current Export Folder:', font = \
                                   ('calibre', 12, 'bold')).place(relx = 0.05, rely = 0.06)

        # - - - - - - - - - - - - - - - -

        #message box (Entry)

        #saveDirectoryBox takes saveDirectory user input
        self.saveDirectoryBox = Entry(self.fileSaveWindow, width = 45, textvariable = self.saveDirectory, font = \
                                 ('calibre', 10, 'normal'), bg = 'white')
        self.saveDirectoryBox.place(relx = 0.245, rely = 0.31)

        # - - - - - - - - - - - - - - - -

        #file name Entry

        #saveFileNameEntry takes saveFileName user input
        self.saveFileNameEntry = Entry(self.fileSaveWindow, width = 25, textvariable = self.saveFileName, font = \
                                  ('calibre', 10, 'normal'), bg = 'white')
        self.saveFileNameEntry.place(relx = 0.25, rely = 0.6)

        # - - - - - - - - - - - - - - - -

        #file directory buttons

        #calls built in "chooseExportDirectory" function when pressed
        self.changeDirectoryButton = Button(self.fileSaveWindow, text = 'Change Dir', command = \
                                     lambda: self.chooseExportDirectory(), height = 1, width = 10, bg = 'white')
        self.changeDirectoryButton.place(relx=0.05,rely=0.28)

        #calls built in "saveExportSettings" function when pressed
        self.saveExportButton = Button(self.fileSaveWindow, text = 'Save', command = \
                                  lambda: self.saveExportSettings(), height = 2, width = 6, bg = 'white')
        self.saveExportButton.place(relx = 0.86,rely = 0.62)

        # - - - - - - - - - - - - - - - -

        #display current save settings (to match the user inputs)
        self.saveFileNameEntry.delete(0, END)
        self.saveFileNameEntry.insert(0, self.saveFileNameString.get())
        self.saveDirectoryBox.delete(0, END)
        self.saveDirectoryBox.insert(0, self.csvDirectoryString.get())

    #-------------------------------------------------------------------------

    #function that allows the user to change export directory folder
    def chooseExportDirectory(self):

        #select new directory using "promptlib" library
        self.prompter = promptlib.Files()
        self.selectedDirectory = self.prompter.dir()

        #set default
        if(self.selectedDirectory == ''):
            self.selectedDirectory = os.getcwd()

        self.saveDirectoryBox.delete(0, END)
        self.saveDirectoryBox.insert(0, self.selectedDirectory)

    #-------------------------------------------------------------------------

    #saves export settings chosen in fileSaveWindow until changed or reset
    def saveExportSettings(self):

        #get the string information inputs
        self.saveFileNameString.set(self.saveFileName.get())
        self.csvDirectoryString.set(self.saveDirectory.get())

        #set default
        if(self.csvDirectoryString.get() == ''):
            self.csvDirectoryString.set(os.getcwd())

#-------------------------------------------------------------------------

#function is called when the user closes the main window
def closeMaster(masterWindow):
    masterWindow.destroy()
    quit()

#-------------------------------------------------------------------------  

#function to split an integer (to be interpreted as a hexidecimal equivalent)
#that is the equivalent of two bytes into two separate bytes for
#"most significant byte" (MSB) and "least significant byte" (LSB) respectively
#using "divmod" (returns 2 values, quotient and remainder)
#logic from the following website:
#https://stackoverflow.com/questions/15036551/best-way-to-split-a-hexadecimal
def twoByteComboSplit(hexCombo):
    return divmod(hexCombo, 0x100)

#-------------------------------------------------------------------------        

#function to toggle the inputted Ohm's Law unit between current (uA) and
#resistance (kOhm) for both the display and output (converted if need be)
#values
def toggleOhmsLawUnit(OhmsLawUnit, OhmsLawUnitButton, rangeVerificationTitleLabel):

    #change the inputted unit and thus the corresponding labels to whichever
    #unit type is NOT the inputted one (between current and resistance)

    #if inputted unit is current, change to resistance
    if(OhmsLawUnit.get() == 'uA'):
        OhmsLawUnit.set('kOhm')

    #otherwise (only toggled between two units), change from resistance
    #to current
    else:
        OhmsLawUnit.set('uA')

    #set the text of the OhmsLawUnitButton to the new OhmsLawUnit text
    OhmsLawUnitButton.config(text = OhmsLawUnit.get())
    rangeVerificationTitleLabel.config(text = ''.join(['Read-Write Range (', OhmsLawUnit.get(), ')']))

#-------------------------------------------------------------------------

#function to enable/disable range entries based on utilizeCurResRange  boolean
def toggleRangeEntries(utilizeCurResRange, rangeMinEntry, rangeMaxEntry, \
                       rangeMaxCycleEntry):

    if(utilizeCurResRange.get()): #if set, (re/)enable all the range entry boxes

        rangeMinEntry.config(state = 'normal')
        rangeMaxEntry.config(state = 'normal')
        rangeMaxCycleEntry.config(state = 'normal')

    else: #otherwise, disable all range entry boxes

        rangeMinEntry.config(state = 'disabled')
        rangeMaxEntry.config(state = 'disabled')
        rangeMaxCycleEntry.config(state = 'disabled')
        
#-------------------------------------------------------------------------

#function tied to 'Clear' button in master GUI, clears output box
def pressedClearOutput(messageListBox):

    #list box display resets
    messageListBox.delete(0, END)

#-------------------------------------------------------------------------

#separate board output data into state lists based on their associated
#pulse information/order
def splitSetResetData(boardOutChannels, boardOutCurrent, boardOutStates):

    SETCurrentList = []
    RESETCurrentList = []
    SETChannelList = []
    RESETChannelList = []

    #for all data, separate the data into lists based on the SET or RESET
    #strings in boardOutStates
    for dataPoint in range(len(boardOutStates)):

        #if SET state, store this index's boardOut logic in SET arrays
        if(boardOutStates[dataPoint] == 'SET'):
            SETCurrentList.append(boardOutCurrent[dataPoint])
            SETChannelList.append(boardOutChannels[dataPoint])
        else: #otherwise, RESET state, store this index's boardOut logic in RESET arrays
            RESETCurrentList.append(boardOutCurrent[dataPoint])
            RESETChannelList.append(boardOutChannels[dataPoint])            

    return SETCurrentList, RESETCurrentList, SETChannelList, RESETChannelList

#-------------------------------------------------------------------------

#perform all serial communications between the GUI and connected
#microcontroller PCB (printed circuit board)
#NOTE: Input to PCB is a list of byte information, the input to this
#function has said information as integer values initially
def serialExecution(inputDataList, expectedPortDriverSearch, IVTestState):

    #initialize list for serial port outputs
    serialPortOutputList  = []
    
    #find serial COM port using custom "findPort" function within this program
    foundPort = findPort(expectedPortDriverSearch)
   
    baudRate = 115200 #initialize Baudrate variable (value carried over from previous version)

    print(inputDataList)
    print([hex(x) for x in inputDataList])
    #set the serial native port device (class)
    #Information here: https://pyserial.readthedocs.io/en/latest/pyserial_api.html
    setSerialDevice = serial.Serial(foundPort, baudRate, timeout = 0, \
                                    bytesize = serial.EIGHTBITS) # Define serial device

    setSerialDevice.write(bytearray(inputDataList)) #write the byte data to the PCB port

    boardData = '' #since the outputted data will be read in as strings/characters, this will be appended to

    combinedCycleNumber = inputDataList[25] + (inputDataList[24] << 8) #get the current number of cycles for loop calculations
    lineCounter = 0 #initialize integer to count number of "\n" characters (i.e. new lines of outputs based on current output format)

    '''
    Given the following output formats that are expected:
    Pulse Test Mode: SET and RESET outputs (2 lines) PER CYCLE
    Pulse Step Test Mode: same as Pulse Test
    Pulse SET/RESET Switch Test Mode: same as Pulse Test
    IV Mode: Rising THEN FALLING (2 lines) x  NUMBER OF STEPS

    CHOOSE A MULTIPLIER DEPENDENT ON THE CHOSEN MODE AND, IF THE IV MODE, IV STATE UNDER TEST
    '''
    
    if(inputDataList[28] == 1): #if the IV mode was selected, prepare testModeMultiplier based on STEP NUMBERS

        #get the number of steps from the provided byte information
        combinedStepByteAmount = inputDataList[27] + (inputDataList[26] << 8)

        #seeing how the unique IV test for the IV mode has its cycles done individually to account
        #for the SET and RESET instances PER CYCLE but NOT for the other IV mode states, check
        #if the unique IV test mode is what was run to determine if the cycle number is included
        #in the testModeMultiplier equation (it would be for the non-unique IV mode states)
        
        if(IVTestState.get() == 'IV'): #if the unique IV mode state, exclude cycle number
            testModeMultiplier = 2 * combinedStepByteAmount            
        else: #otherwise, other IV mode states, include the cycle number in the equation
            testModeMultiplier = 2 * combinedStepByteAmount * combinedCycleNumber
            
    else: #otherwise, prepare testModeMultiplier based on DOUBLE THE CYCLE NUMBER
        testModeMultiplier = 2 * combinedCycleNumber

    #continue to loop while the expected number of lines based on expected length based on cycle numbers
    #or step numbers hasn't been reached/found
    while(lineCounter < testModeMultiplier):

        if(setSerialDevice.in_waiting > 0): #if there is data waiting to be read out

            #read said available data and append it to the boardData string (that's
            #used in the WHILE loop condition)
            boardData += setSerialDevice.read(setSerialDevice.in_waiting).decode('utf-8')

            #add small delay to avoid busy-waiting to reduce CPU usage
            time.sleep(0.025)

        #check how many lines there are within boardData currently WITHOUT changing it
        lineCounter = boardData.count('\n')

    #with the board data collected, close the current setSerialDevice (to avoid having too many remain
    #open in the case of multiple devices being selected or if serialExecution is called per cycle)
    setSerialDevice.close()
    print(boardData)
    #check the read data from the board to see if an error is thrown, the
    #data outputted from the board has finished compiling, or if the reset
    #switch is pressed (if one of the latter two, the code will wait for
    #the user to re-submit the input list)  
    while True:
        
        #either prepare the outputted data, break the WHILE loop,
        #or continue past any "OutOfRange" data

        #if an error with the inputted list tells the user to hit
        #the reset switch, hitthe reset switch to resubmit the data
        if(boardData == 'Received Frame Error'):
            return 'Reset Switch', [], []

        #else if, once the data is finished being read or the reset switch is pressed,
        #end the WHILE loop and wait for user to re-submit the input list
        elif(boardData == 'Waiting for command'):
            break

        #else if the data the value is "OutOfRange", ignore it
        elif(boardData == 'Value is OutOfRange'):
            continue

        #else if the data is not empty, append the outputted data to the
        #list that returns all the data at the end of this function
        elif(boardData != ''):

            #remove all non-numeric (excluding decimal point between numbers) characters
            #and create an array with the corresponding channel/voltage (depends on which mode
            #is run) number in the first list, the current in the second list, and a string showing
            #the state of the data in the third list
            #NOTE: Current (raw) format of boardData is the following (when not an error):
            #PULSE TEST:
            #(Set only): Ch No:  #, Set-Read I = #.# uA
            #(Reset only):  Ch No:  #, Reset-Read I = #.# uA

            #IV TEST:
            #(when rising) RISING-Read1 V = # mV ; I = # uA

            #(when falling) FALLING-Read1 V = # mV ; I = # uA


            # - - - - - - - - - - - 

            #first, check what lines (if multiple) are associated with SET or RESET
            boardDataLines = boardData.splitlines() #if multiple lines, get each line individually
            stateStringArray = []

            #check each line
            for lineIndex, lineContents in enumerate(boardDataLines):

                #since the outputs are expected to be different depending on whether or not the
                #input is for a "Pulse Test" or "IV Test" (byte 29 of 31 is selected mode), the following
                #IF statement logic will be incorporated into this to decide which state information
                #to append
                #CHANGE STRING SEARCH TERMS/LOGIC IF NECESSARY
                if(inputDataList[28] == 0): #if modeStateNum = 0 -> Pulse Test

                    #store strings to represent what lines are associated with what state
                    #in stateStringArray
                    if 'Reset' in lineContents: #if the string "Reset" is found in the lineContents string
                        stateStringArray.append('RESET')

                    #if the string "Set" is found in the lineContents string and "Set"
                    #is NOT part of the word "Reset"
                    elif 'Set' in lineContents and 'Reset' not in lineContents:
                        stateStringArray.append('SET')
                    
                else: #otherwise modeStateNum = 1 -> IV TEST

                    #store strings to represent what lines are associated with what state
                    #in stateStringArray
                    
                    if 'RISING' in lineContents: #if the string "Rising" is found in the lineContents string
                        stateStringArray.append('RISING')

                    elif 'FALLING' in lineContents: #if the string "Falling" is found in the lineContents string
                        stateStringArray.append('FALLING')

            # - - - - - - - - - - -
        
            #IGNORE all non-numeric characters while sorting any numerical data into an
            #array if there's more than one separate numerical value (which there is
            #as showcased above in the format comment)
            #NOTE: "Exception" being the "-" character for the NEGATIVE SIGN
            curCharIndex = 0
            boardDataNumbersList = []

            #since Jeelka's board output includes a standalone number character before reading off the voltage
            #for the IV test outputs AFTER the string "read", remove such instances of this otherwise
            #aesthetic number
            if(inputDataList[28] == 1): #if modeStateNum = 1 -> IV TEST

                searchedStringWithNumberAtEnd = 'Read' #CHANGE IF NECESSARY
                
                #check each line
                for lineIndex, lineContents in enumerate(boardDataLines):
                    readStringFinalCharIndex = lineContents.rfind(searchedStringWithNumberAtEnd) + \
                        len(searchedStringWithNumberAtEnd) - 1 #get the final character string index
                    unwantedNumberCharIndex = readStringFinalCharIndex + 1
                    boardDataLines[lineIndex] = lineContents[:unwantedNumberCharIndex] + \
                        lineContents[unwantedNumberCharIndex + 1:] #remove the unwanted numerical string

                #recombine boardDataLines with removed unwanted numerical strings
                boardData = "\n".join(boardDataLines)
            
            while(curCharIndex < len(boardData)):

                #if the current string is numeric OR the "negative sign" (-)
                if(boardData[curCharIndex].isnumeric() or boardData[curCharIndex] == '-'):

                    # - - - - - - - - - - -
                    
                    #EXCEPTIONS BASED ON DEBUGGING LOGIC

                    #if the NEXT character is NOT numeric and the CURRENT character is the
                    #NEGATIVE SIGN, don't bother with the incorrectly assumed negative sign
                    #and continue past it
                    if(boardData[curCharIndex] == '-' and not \
                       boardData[curCharIndex + 1].isnumeric()):
                        curCharIndex += 1 #increment curCharIndex to check next character
                        continue

                    # - - - - - -

                    #if the (odd) event the outputted "numerical" data has the following format,
                    #SET THIS ILLOGICAL OUTPUT TO 0 (as recommended by Jeelka)
                    #Ch No:  #, Set-Read I = #.-# uA
                    #check if boardData[curCharIndex] is a NUMBER
                    if(boardData[curCharIndex + 1] == '.' and \
                       boardData[curCharIndex + 2] == '-' and
                       boardData[curCharIndex + 3].isnumeric()):
                        boardDataNumbersList.append('0')
                        curCharIndex += 4 #jump past this illogical data
                        continue

                    #check if boardData[curCharIndex] is a NEGATIVE SIGN
                    if(boardData[curCharIndex + 1].isnumeric() and \
                       boardData[curCharIndex + 2] == '.' and \
                       boardData[curCharIndex + 3] == '-' and
                       boardData[curCharIndex + 4].isnumeric()):
                        boardDataNumbersList.append('0')
                        curCharIndex += 5 #jump past this illogical data
                        continue

                    # - - - - - - - - - - -

                    #since this still is a string format, get the full string
                    #by checking future characters to see if this is a float, let
                    #alone how many digits afterwards there are for this single
                    #float value
                    currentNumberString = boardData[curCharIndex]

                    curCharIndex += 1 #increment curCharIndex to check next character

                    #check if the NEXT character is either numeric or a decimal point (with
                    #another number after it)
                    while(curCharIndex < len(boardData) and \
                          (boardData[curCharIndex].isnumeric() or \
                           ((curCharIndex + 1) < len(boardData) and \
                            boardData[curCharIndex] == '.' and \
                            boardData[curCharIndex + 1].isnumeric()))):

                        #append to the current numerical string with the continuing number
                        #characters
                        currentNumberString += boardData[curCharIndex]

                        curCharIndex += 1 #increment curCharIndex to check next character

                    #append the found "full" number to the array to output
                    boardDataNumbersList.append(currentNumberString)

                else: #otherwise, proceed to the next character (index)

                    curCharIndex += 1 #increment curCharIndex to check next character

            #since the first number in the current format is expected to be the channel number
            #(integer) while the remainder is the current value (float), split boardDataNumbersList
            #by the even and odd indices respectively
            otherNumberList = [int(outputData) for outputData \
                                         in boardDataNumbersList[::2]] #even indices, (channel or voltage) numbers
            currentOutputList = [float(outputData) for outputData \
                                         in boardDataNumbersList[1::2]] #odd indices, current values [SET, RESET]

            return otherNumberList, currentOutputList, stateStringArray

#-------------------------------------------------------------------------

# Looks for the PCB (printed circuit board) port that is plugged into the board
def findPort(expectedPortDriverSearch):

    #retrieve list of "ListPortInfo" objects
    #links for this information:
    #https://pyserial.readthedocs.io/en/latest/tools.html#module-serial.tools.list_ports
    #https://pyserial.readthedocs.io/en/latest/tools.html#serial.tools.list_ports.ListPortInfo
    portsList = serial.tools.list_ports.comports()
    
    #initialize empty "ListPortInfo" object to return the found (desired) port
    desiredPortInfo = None

    #search for the desired port among all the ports obtained above
    for currentPort in portsList:

        #perform the search by converting the "ListPortInfo" object into a string
        portString = str(currentPort)

        #if the expected port information is within the current port string
        if expectedPortDriverSearch.get() in portString:
            
            #split the found port string information up with the space delimiter
            splitDesiredPortInfo = portString.split(' ')
            
            #get the device name/path (first object element in "ListPortInfo")
            #in string format from the split port string above
            desiredPortInfo = splitDesiredPortInfo[0]

    #return desired port information
    return desiredPortInfo

#-------------------------------------------------------------------------

#create and export the list of values read from the PCB board in a .csv
#file within the provided directory (with the directory being defined
#in the "csvDirectoryString" variable that is an expected input)

def exportPCBToCSV(dataToExport, exportFileName, directory):

    #in the event a file name isn't directly provided (is empty), create
    #a file name strictly around the datetime of the file's creation
    if(exportFileName == ''):

        currentTime = datetime.now() #get current datetime information
        
        #adjust datetime format to custom format
        #https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        dateTimeFormatted = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

        #set the directory with the file name/extension
        csvNameDirectory = ''.join([directory, '\\', dateTimeFormatted, '.csv'])

    #else, find and set the directory based on the input strings
    else:

        #call built-in "getFileTitleNum" function should the user try to export
        #a file with a pre-existing name
        titleNumToExport = getFileTitleNum(exportFileName, directory)

        #set the directory with the file name/extension
        csvNameDirectory = ''.join([directory, '\\', exportFileName, titleNumToExport, '.csv'])

    # - - - - - - - - - - - - - - -

    #using the set directory/file name, write the inputted data into the
    #created .csv file

    #open the .csv file set as the "dir" variable and return it as a file object
    #https://docs.python.org/3/library/csv.html#csv.writer
    with open(csvNameDirectory, 'w', newline = '') as csvFileObject:

        #create writer object of the .csv file to be written to
        writerCSVObject = csv.writer(csvFileObject)

        #export all the inputted data into the .csv file/writer object
        for dataSnippet in dataToExport:
            writerCSVObject.writerow(dataSnippet)

#-------------------------------------------------------------------------

#return the next (new/incremented) index of a file name if shared or start
#at 1 for the file name if the name wasn't pre-existing
#NOTE: this is only called in "exportPCBToCSV", which is focusing
#strictly on .csv files, so this extension is the only extension that will
#be looked at
def getFileTitleNum(exportFileName, directory):

    #create list to store all numbers of the otherwise same file name,
    #with 0 being the default that isn't expected in the file names
    fileNameNumList = [0]

    #within the inputted directory, find all the .csv files with the same
    #file name, get the numbers associated with them if found, and store those
    #numbers to find the maximum listed number to increment past

    #get each string representation of the file names obtained within the list
    #that os.listdir(directory) provides
    for foundFile in os.listdir(directory):

        #start by seeing if exportFileName is within the foundFile's name at all
        #AND is the correct extension (.csv)
        if(exportFileName in foundFile) and (foundFile.endswith('.csv')):

            #NOTE: since it's possible that the exportFileName could be in
            #the name of files that aren't associated with the correct program (with
            #extra text before or after the exportFileName that aren't expected),
            #this will be looking for EXACT same names aside from the expected
            #different number at the end of the file name before the .csv extension

            #get file name without the extension
            #https://docs.python.org/3/library/os.path.html#os.path.splitext
            fileNameNoExtension = os.path.splitext(foundFile)[0]

            #string to append the numerical character data to with each number removal
            #NOTE: string will be appended using "+" instead "join()" for convenience
            #in a loop
            numberAsChars = ''

            #while still looking for file name (so long as the final number isn't completely removed
            #AND doesn't match the exportFileName while doing the number removals (with the chance of
            #exportFileName having numbers at the end for whatever reason as part of the direct input))
            while(fileNameNoExtension[-1].isdigit()) and (fileNameNoExtension != exportFileName):
                numberAsChars += fileNameNoExtension[-1] #save the number information at the end before removal
                fileNameNoExtension = fileNameNoExtension[:-1] #remove last character that is a number

            #if numberAsChars has more than 1 character, the string will need to be reversed,
            #as the numbers were being removed from the end of the string individually and thus
            #will be in the reverse order
            #Ex: filename410 -> first removed number = 0, second = 1, third = 4
            if(len(numberAsChars) > 1):
                numberAsChars = numberAsChars[::-1]

            #final check post WHILE loop, if the inputted file name matches ALL
            #characters ASIDE from the number before the extension (should any
            #characters before the exportFileName be different)
            if(exportFileName == fileNameNoExtension):

                #append the number associated with the file to fileNameNumList
                fileNameNumList.append(int(numberAsChars))

    #return the next incremented number based on the maximum number within
    #the shared file names (or return 1 if no similar title was found)
    return str(max(fileNameNumList) + 1)

#-------------------------------------------------------------------------        

#function that updates an Entry widget's associated most and least significant
#bytes when the integer that's split between the two bytes changes
def updateEntryBytes(newEntryValue, correspondingByteMSB, \
                     correspondingByteLSB, voltageBoolCheck):

    #only perform the following code if there's a numerical value in the
    #"newEntryValue" Entry box (the Entry box being empty will go into the "except"
    #case)
    #NOTE: try/except included here to address the Entry (IntVar)
    #breaking the code if empty when this function is called with "trace"
    try:
        if(isinstance(newEntryValue.get(), (int, float))):

            #get new byte values

            #check if the input is VOLTAGE, as the Entry expects VOLTS but
            #the PCB board input must be MILLIVOLTS, so make the conversion here
            #(1000 millivolts = 1 volt)
            #NOTE: For the sake of all byte information being in "Int" format,
            #convert the floats to integers post multiplication
            if(voltageBoolCheck): #if voltage
                newValueMSB, newValueLSB = twoByteComboSplit(int(newEntryValue.get() * 1000))
            else: #otherwise, not voltage unit
                newValueMSB, newValueLSB = twoByteComboSplit(newEntryValue.get())

            #set the new byte values
            correspondingByteMSB.set(str(newValueMSB))
            correspondingByteLSB.set(str(newValueLSB))

    except:
        print('Changed Entry box input is NOT numerical, change it before running\n' + \
              '(NOTE: the previous number was kept in the meantime)')
        return

#-------------------------------------------------------------------------

#function to convert current inputs (to be board outputs) to their resistance
#equivalents using inputted voltages (V = IR -> R = V/I)
def convertIToR(boardOutputCurrent, boardOutStates, SETREADVoltage, RESETREADVoltage):

    #sift through all outputBoard data
    for boardOutputIndex in range(len(boardOutputCurrent)):

        #convert outputBoard data (as current) to resistance if not 0
        #(to avoid dividing by 0)
        if(boardOutputCurrent[boardOutputIndex] != 0):

            #since the two READ voltages (SET/RESET) are split by even/odd
            #indices in the boardOutput, use the indices to determine which
            #inputted voltage to use in the new output's equation

            if(boardOutStates[boardOutputIndex] == 'SET'): #if SET voltage

                #calculate the new resistance (R = V/I) and convert to
                #KOhm by multiplying by 1000 from uA
                newSETResistance = abs(float(SETREADVoltage) / \
                                    float(boardOutputCurrent[boardOutputIndex])) * 1000

                #change the current (I) output to its resistance equivalent
                #in the boardOutput at the same index
                #round to 2 decimal places for better visual output later
                boardOutputCurrent[boardOutputIndex] = round(newSETResistance, 2)
                
            else: #otherwise, index is odd, RESET voltage

                #calculate the new resistance (R = V/I) and convert to
                #KOhm by multiplying by 1000 from uA
                newRESETResistance = abs(float(RESETREADVoltage) / \
                                    float(boardOutputCurrent[boardOutputIndex])) * 1000

                #change the current (I) output to its resistance equivalent
                #in the boardOutput at the same index
                #round to 2 decimal places for better visual output later
                boardOutputCurrent[boardOutputIndex] = round(newRESETResistance, 2)

#-------------------------------------------------------------------------

#function that arranges the raw data from the board to have it be exportable
#in the correct format
def arrangeGridExport(boardOutOther, boardOutIcurRes, boardOutStates, cycleNumber, \
                      FORMSETREADVoltage, RESETREADVoltage, toggledOhmsLawUnit, \
                      ModeStateStringVar, IVTestState, IVStateBool, FORMSETStateString, \
                      inputByteList, cellGrid, maxStepVoltage, \
                      pulseTestStepVoltagesList, invertIVStates, SETGateVoltage, RESETGateVoltage, \
                      deviceNumber, stepVoltageDirection, rangeCycleList, rangeCycleBoolean, \
                      rangeCycleDeviceList, failedRangeCycleDataListOther, failedRangeCycleDataListCurrent, \
                      failedRangeCycleDataListStates, failedDeviceList, failedCycleMax, \
                      pulseTestRangeMin, pulseTestRangeMax, hardCodeDevices):

    #recalculate the other information that was included in the inputByteList but wasn't already directly
    #provided as an input (and recombining MSBs with shifting and LSBs)
    gateVoltage = inputByteList[3] + (inputByteList[2] << 8)
    FORMSETVoltage = inputByteList[5] + (inputByteList[4] << 8)
    RESETVoltage = inputByteList[15] + (inputByteList[14] << 8)
    FORMSETTime = inputByteList[7] + (inputByteList[6] << 8)
    RESETTime = inputByteList[17] + (inputByteList[16] << 8)
    FORMSETREADTime = inputByteList[13] + (inputByteList[12] << 8)
    RESETREADTime = inputByteList[21] + (inputByteList[20] << 8)
    delayPeriodTime = inputByteList[9] + (inputByteList[8] << 8)
    stepNumber = inputByteList[27] + (inputByteList[26] << 8)

    #prepare string to showcase whether the data is the Current (uA) or Reistance (kOhm)
    #format as chosen upon pressing the 'Send' button
    outputUnit = ''
    if(toggledOhmsLawUnit.get() == 'uA'):
        outputUnit = 'Current (uA)'
    else:
        outputUnit = 'Resistance (kOhm)'

    #create unique lists to export of information to add to the .csv file
    exportDataList = []
    exportDataListFAILED = []
    exportDataListSET = []
    exportDataListRESET = []

    #call "splitSetResetData" function to split up the SET/RESET data IF PULSE TEST
    #WAS RUN
    if(ModeStateStringVar.get() == 'Pulse Test'):

        #split the data here normally when not inputting data from the ranged cycling
        #logic, as the split will be done further down
        if(not rangeCycleBoolean.get()):
            FORMSETIcurResList, RESETIcurResList, FORMSETChannelList, RESETChannelList = \
                            splitSetResetData(boardOutOther, boardOutIcurRes, boardOutStates)

        #create basic headers with single instances of information
        if(not rangeCycleBoolean.get() and not hardCodeDevices.get()):
            exportDataList.append([''.join([ModeStateStringVar.get(), ' Run, Output Unit: ', outputUnit])]) #"title" header
        elif(hardCodeDevices.get()):
            exportDataList.append([''.join([ModeStateStringVar.get(), 'SET/RESET Hard Coded Run, Output Unit: ', outputUnit])]) #"title" header
        else:
            exportDataList.append([''.join([ModeStateStringVar.get(), ' Read-Write Verification Run, Output Unit: ', outputUnit])]) #"title" header
        
        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataList.append([''.join(['State(s) Under Test: ', FORMSETStateString.get(), ' and RESET'])])
        exportDataList.append([''.join(['Gate Voltage (V):  ', str(gateVoltage/1000)])])
        exportDataList.append([''.join([FORMSETStateString.get(), ' Voltage (V):  ', str(FORMSETVoltage/1000)])])
        exportDataList.append([''.join(['RESET Voltage (V):  ', str(RESETVoltage/1000)])])
        exportDataList.append([''.join([FORMSETStateString.get(), ' READ Voltage (V):  ', str(FORMSETREADVoltage.get())])])
        exportDataList.append([''.join(['RESET READ Voltage (V):  ', str(RESETREADVoltage.get())])])

        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataList.append([''.join([FORMSETStateString.get(), ' Time (us):  ', str(FORMSETTime)])])
        exportDataList.append([''.join(['RESET Time (us):  ', str(RESETTime)])])
        exportDataList.append([''.join([FORMSETStateString.get(), ' READ Time (us):  ', str(FORMSETREADTime)])])
        exportDataList.append([''.join(['RESET READ Time (us):  ', str(RESETREADTime)])])
        exportDataList.append([''.join(['Delay Period (us):  ', str(delayPeriodTime)])])

        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        # - - - - - - - - - - - - - - - - - - - -

        #create loop logic to showcase the total number of cycles PER DEVICE/CELL with the associated
        #device/cell information next to the number (done to add clarity should a large list of devices
        #be selected, as having to manually count to figure out which cycle number is associated with
        #what device is a pain)
        if(rangeCycleBoolean.get()):

            fullDeviceRangeCycleList = [] #initialize the list to store all of the string information
            fullDeviceRangeCycleList.append('[')

            #loop to get all of the associated device/cell row, column and cycle numbers done when
            #iterating to find a value within the desired range here
            for deviceInfo in range(len(rangeCycleDeviceList)):
                fullDeviceRangeCycleList.append(''.join([str(rangeCycleDeviceList[deviceInfo][0]), '/', \
                                                         str(rangeCycleDeviceList[deviceInfo][1]), ': ', \
                                                         str(rangeCycleList[deviceInfo])]))

                #for visual clarity, add a comma to split the device/cell data when printed
                if(deviceInfo < len(rangeCycleDeviceList) - 1):
                    fullDeviceRangeCycleList.append(', ')

            fullDeviceRangeCycleList.append(']')
                    
            fullCycleDeviceString = ''.join(fullDeviceRangeCycleList) #join all of the strings together for the final full string
            
            exportDataList.append([''.join(['Number of Cycles for all Devices:  ', str(fullCycleDeviceString)])])
        else:
            exportDataList.append([''.join(['Number of Cycles for all Devices:  ', str(cycleNumber.get())])])

        # - - - - - - - - - - - - - - - - - - - -

        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        if(rangeCycleBoolean.get()): #if the unique range read-write verification test, include the range min and max

            exportDataList.append([''.join(['Range Min (', outputUnit, '): ', str(pulseTestRangeMin.get())])])
            exportDataList.append([''.join(['Range Max (', outputUnit, '): ', str(pulseTestRangeMax.get())])])

            exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)
            
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        #create the header for the corresponding multiple columns for the data within said header
        #and loop through the data to append to the exportDataList

        #row header with all column titles
        if(hardCodeDevices.get()): #add another column to have the SET or RESET state listed if hard coded
            loopDataRowHeader = ['Device [row, column]', 'Cycle Number', ''.join(['Channel Numbers [', FORMSETStateString.get(), \
                                ', RESET]']), ''.join([FORMSETStateString.get(), ' ', outputUnit]), \
                             ''.join(['RESET ', outputUnit]), 'Device State']
        else:
            loopDataRowHeader = ['Device [row, column]', 'Cycle Number', ''.join(['Channel Numbers [', FORMSETStateString.get(), \
                                    ', RESET]']), ''.join([FORMSETStateString.get(), ' ', outputUnit]), \
                                 ''.join(['RESET ', outputUnit])]
        
        exportDataList.append(loopDataRowHeader)

        # - - - - - - - -

        #if the range cycling logic was done, there is the chance that the number of
        #iterations, i.e. cycles, per device to finish its run can vary, so the shared
        #cycleNumber will NOT work
        #NOTE: the length of rangeCycleList will ONLY potentially change when the ranged cycle
        #mode is activated
        if(rangeCycleBoolean.get()):

            for rangeCycleDeviceIndex in range(len(rangeCycleList)):

                FORMSETIcurResList, RESETIcurResList, FORMSETChannelList, RESETChannelList = \
                    splitSetResetData(boardOutOther[rangeCycleDeviceIndex], boardOutIcurRes[rangeCycleDeviceIndex], \
                                      boardOutStates[rangeCycleDeviceIndex])

                #loop through all cycles to get said cycle's data to append with
                #the expected information (and order) based on the loopDataRowHeader list
                for cycleIndex in range(rangeCycleList[rangeCycleDeviceIndex]):

                    #currently working around the logic of having the SET and RESET operations
                    #be on SEPARATE rows, so create and append the row data for each operation
                    #into the exportDataList separately

                    #prepare this row's data
                    cycleNewRowList = [] #list to store the row data

                    #save the device/cell information
                    cycleNewRowList.append(''.join([str(rangeCycleDeviceList[rangeCycleDeviceIndex][0]), \
                                                    ',', str(rangeCycleDeviceList[rangeCycleDeviceIndex][1])]))

                    #record the current cycle number
                    cycleNewRowList.append(str(cycleIndex + 1)) #for the 'Cycle Number' colum

                    #get the channel number from either the SET or RESET data if either of them
                    #are not empty
                    #if BOTH are NOT empty, output the [FORM/SET, RESET], otherwise have the
                    #empty list return nothing for its respective part)
                    if(FORMSETChannelList[0] != '' and RESETChannelList[0] != ''): #if BOTH lists are NOT empty
                        combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[cycleIndex]), ', ', \
                                                            str(RESETChannelList[cycleIndex]), ']'])
                        cycleNewRowList.append(combinedListChannelsString)
                    elif(FORMSETChannelList[0] != '' and RESETChannelList[0] == ''): #else if ONLY FORM/SET channel list isn't empty
                        combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[cycleIndex]), \
                                                              ', EMPTY]'])
                        cycleNewRowList.append(combinedListChannelsString)
                    elif(FORMSETChannelList[0] == '' and RESETChannelList[0] != ''): #else if ONLY RESET channel list isn't empty
                        combinedListChannelsString = ''.join(['[EMPTY, ', str(RESETChannelList[cycleIndex]), \
                                                              ']'])
                        cycleNewRowList.append(combinedListChannelsString)
                    else: #otherwise, append empty cell info
                        cycleNewRowList.append('')

                    #get the current/resistance data from FORM/SET and/or RESET
                    if(FORMSETIcurResList[0] != ''): #checking FORM/SET list if it isn't empty

                        #record the FORM/SET current or resistance
                        cycleNewRowList.append(str(FORMSETIcurResList[cycleIndex]))

                    else: #otherwise (i.e. if empty), append empty cell info
                        cycleNewRowList.append('')

                    if(RESETIcurResList[0] != ''): #checking RESET list if it isn't empty

                        #record the FORM/SET current or resistance
                        cycleNewRowList.append(str(RESETIcurResList[cycleIndex]))

                    else: #otherwise (i.e. if empty), append empty cell info
                        cycleNewRowList.append('')
                
                    #append to exportDataList in the FOR loop for each cycle's data
                    exportDataList.append(cycleNewRowList)

        else: #else, proceed normally

            #append the data FOR EACH DEVICE/CELL THAT WAS SET TO TRUE

            dataIndex = 0

            for currentRow in range(cellGrid.returnRowNum()): #for all rows
                for currentColumn in range(cellGrid.returnColumnNum()): #for all columns

                    if(hardCodeDevices.get()): #for ALL devices

                        #reformat the data into 2D arrays before reconverting back to lists
                        FORMSETChannelListArray = np.array(FORMSETChannelList).reshape(cellGrid.returnRowNum(), \
                                                                           cellGrid.returnColumnNum())
                        FORMSETChannelList = FORMSETChannelListArray.tolist()
                        FORMSETIcurResListArray = np.array(FORMSETIcurResList).reshape(cellGrid.returnRowNum(), \
                                                                           cellGrid.returnColumnNum())
                        FORMSETIcurResList = FORMSETIcurResListArray.tolist()
                        RESETChannelListArray = np.array(RESETChannelList).reshape(cellGrid.returnRowNum(), \
                                                                           cellGrid.returnColumnNum())
                        RESETChannelList = FORMSETChannelListArray.tolist()
                        RESETIcurResListArray = np.array(RESETIcurResList).reshape(cellGrid.returnRowNum(), \
                                                                           cellGrid.returnColumnNum())
                        RESETIcurResList = RESETIcurResListArray.tolist()

                        #loop through all cycles to get said cycle's data to append with
                        #the expected information (and order) based on the loopDataRowHeader list
                        for cycleIndex in range(cycleNumber.get()):

                            #currently working around the logic of having the SET and RESET operations
                            #be on SEPARATE rows, so create and append the row data for each operation
                            #into the exportDataList separately

                            #prepare this row's data
                            cycleNewRowList = [] #list to store the row data

                            #save the device/cell information
                            cycleNewRowList.append(''.join([str(currentRow + 1), ',', str(currentColumn + 1)]))

                            #record the current cycle number
                            cycleNewRowList.append(str(cycleIndex + 1)) #for the 'Cycle Number' colum

                            #get the channel number from either the SET or RESET data if either of them
                            #are not empty
                            #if BOTH are NOT empty, output the [FORM/SET, RESET], otherwise have the
                            #empty list return nothing for its respective part)
                            if(FORMSETChannelList[0] != '' and RESETChannelList[0] != ''): #if BOTH lists are NOT empty
                                combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[currentRow][currentColumn]), ', ', \
                                                                    str(RESETChannelList[currentRow][currentColumn]), ']'])
                                cycleNewRowList.append(combinedListChannelsString)
                            elif(FORMSETChannelList[0] != '' and RESETChannelList[0] == ''): #else if ONLY FORM/SET channel list isn't empty
                                combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[currentRow][currentColumn]), ', EMPTY]'])
                                cycleNewRowList.append(combinedListChannelsString)
                            elif(FORMSETChannelList[0] == '' and RESETChannelList[0] != ''): #else if ONLY RESET channel list isn't empty
                                combinedListChannelsString = ''.join(['[EMPTY, ', str(RESETChannelList[currentRow][currentColumn]), ']'])
                                cycleNewRowList.append(combinedListChannelsString)
                            else: #otherwise, append empty cell info
                                cycleNewRowList.append('')

                            #get the current/resistance data from FORM/SET and/or RESET
                            if(FORMSETIcurResList[0] != ''): #checking FORM/SET list if it isn't empty

                                #record the FORM/SET current or resistance
                                cycleNewRowList.append(str(FORMSETIcurResList[currentRow][currentColumn]))

                            else: #otherwise (i.e. if empty), append empty cell info
                                cycleNewRowList.append('')

                            if(RESETIcurResList[0] != ''): #checking RESET list if it isn't empty

                                #record the FORM/SET current or resistance
                                cycleNewRowList.append(str(RESETIcurResList[currentRow][currentColumn]))

                            else: #otherwise (i.e. if empty), append empty cell info
                                cycleNewRowList.append('')

                            #return device/cell state
                            if(cellGrid.returnBooleans()[currentRow][currentColumn]): #if pressed = RESET
                                cycleNewRowList.append('RESET')
                            else: #if not pressed = SET
                                cycleNewRowList.append('SET')
                        
                            #append to exportDataList in the FOR loop for each cycle's data
                            exportDataList.append(cycleNewRowList)
                        
                    else:

                        #CHECK IF SELECTED IN THE INTERACTIVE GRID
                        if(cellGrid.returnBooleans()[currentRow][currentColumn]): #if selected

                            #loop through all cycles to get said cycle's data to append with
                            #the expected information (and order) based on the loopDataRowHeader list
                            for cycleIndex in range(cycleNumber.get()):

                                #currently working around the logic of having the SET and RESET operations
                                #be on SEPARATE rows, so create and append the row data for each operation
                                #into the exportDataList separately

                                #prepare this row's data
                                cycleNewRowList = [] #list to store the row data

                                #save the device/cell information
                                cycleNewRowList.append(''.join([str(currentRow + 1), ',', str(currentColumn + 1)]))

                                #record the current cycle number
                                cycleNewRowList.append(str(cycleIndex + 1)) #for the 'Cycle Number' colum

                                #get the channel number from either the SET or RESET data if either of them
                                #are not empty
                                #if BOTH are NOT empty, output the [FORM/SET, RESET], otherwise have the
                                #empty list return nothing for its respective part)
                                if(FORMSETChannelList[0] != '' and RESETChannelList[0] != ''): #if BOTH lists are NOT empty
                                    combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[dataIndex]), ', ', \
                                                                        str(RESETChannelList[dataIndex]), ']'])
                                    cycleNewRowList.append(combinedListChannelsString)
                                elif(FORMSETChannelList[0] != '' and RESETChannelList[0] == ''): #else if ONLY FORM/SET channel list isn't empty
                                    combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[dataIndex]), ', EMPTY]'])
                                    cycleNewRowList.append(combinedListChannelsString)
                                elif(FORMSETChannelList[0] == '' and RESETChannelList[0] != ''): #else if ONLY RESET channel list isn't empty
                                    combinedListChannelsString = ''.join(['[EMPTY, ', str(RESETChannelList[dataIndex]), ']'])
                                    cycleNewRowList.append(combinedListChannelsString)
                                else: #otherwise, append empty cell info
                                    cycleNewRowList.append('')

                                #get the current/resistance data from FORM/SET and/or RESET
                                if(FORMSETIcurResList[0] != ''): #checking FORM/SET list if it isn't empty

                                    #record the FORM/SET current or resistance
                                    cycleNewRowList.append(str(FORMSETIcurResList[dataIndex]))

                                else: #otherwise (i.e. if empty), append empty cell info
                                    cycleNewRowList.append('')

                                if(RESETIcurResList[0] != ''): #checking RESET list if it isn't empty

                                    #record the FORM/SET current or resistance
                                    cycleNewRowList.append(str(RESETIcurResList[dataIndex]))

                                else: #otherwise (i.e. if empty), append empty cell info
                                    cycleNewRowList.append('')                                
                            
                                #append to exportDataList in the FOR loop for each cycle's data
                                exportDataList.append(cycleNewRowList)

                                dataIndex += 1

    #----------------------------------------------------------------

    #else if PULSE STEP TEST
    elif(ModeStateStringVar.get() == 'Pulse Test - Step'):

        FORMSETIcurResList, RESETIcurResList, FORMSETChannelList, RESETChannelList = \
                        splitSetResetData(boardOutOther, boardOutIcurRes, boardOutStates)

        #in the event multiple DEVICES are selected, split the data into smaller lists of equal
        #value that represent that device's specific outputs
        FORMSETIcurResListSplitByDeviceNPArrays = np.array_split(FORMSETIcurResList, deviceNumber)
        RESETIcurResListSplitByDeviceNPArrays = np.array_split(RESETIcurResList, deviceNumber)
        FORMSETChannelListSplitByDeviceNPArrays = np.array_split(FORMSETChannelList, deviceNumber)
        RESETChannelListSplitByDeviceNPArrays = np.array_split(RESETChannelList, deviceNumber)

        #since pulseTestStepVoltagesList will have the same format for all device/cycle combinations,
        #just get the minimum list information without worrying about by device/by cycle case by
        #case basis
        pulseTestStepVoltagesListSplitDeviceCycle = np.array_split(pulseTestStepVoltagesList, \
                                                                   (deviceNumber * cycleNumber.get()))
        pulseTestStepVoltagesList = pulseTestStepVoltagesListSplitDeviceCycle[0].tolist()

        #split the data into FORM/SET/RESET (device) lists PER CYCLE using Numpy.array_split
        #before converting the Numpy arrays back into lists for simplicity

        #first, split the FORM/SET/RESET data into equal length lists that represent the
        #outputs for their respective cycles (NOTE: channel information not necessary for
        #current plots), PERFORM CONVERSION OF ALL NUMPY ARRAYS TO LIST HERE WITHIN 2D ARRAY/LIST LOGIC
        FORMSETIcurResListSplitNPArrays = [np.array_split(deviceList, cycleNumber.get()) for \
                                           deviceList in FORMSETIcurResListSplitByDeviceNPArrays]
        FORMSETIcurResList = [[(item.tolist() if isinstance(item, np.ndarray) else item) \
                               for item in row] for row in FORMSETIcurResListSplitNPArrays]
        RESETIcurResListSplitNPArrays = [np.array_split(deviceList, cycleNumber.get()) for \
                                           deviceList in RESETIcurResListSplitByDeviceNPArrays]
        RESETIcurResList = [[(item.tolist() if isinstance(item, np.ndarray) else item) \
                               for item in row] for row in RESETIcurResListSplitNPArrays]
        FORMSETChannelListSplitNPArrays = [np.array_split(deviceList, cycleNumber.get()) for \
                                           deviceList in FORMSETChannelListSplitByDeviceNPArrays]
        FORMSETChannelList = [[(item.tolist() if isinstance(item, np.ndarray) else item) \
                               for item in row] for row in FORMSETChannelListSplitNPArrays]
        RESETChannelListSplitNPArrays  = [np.array_split(deviceList, cycleNumber.get()) for \
                                           deviceList in RESETChannelListSplitByDeviceNPArrays]
        RESETChannelList = [[(item.tolist() if isinstance(item, np.ndarray) else item) \
                               for item in row] for row in RESETChannelListSplitNPArrays]

        #prepare string to showcase whether the data is the Current (uA) or Reistance (kOhm)
        #format as chosen upon pressing the 'Send' button
        outputUnit = ''
        if(toggledOhmsLawUnit.get() == 'uA'):
            outputUnit = 'Current (uA)'
        else:
            outputUnit = 'Resistance (kOhm)'

        #create basic headers with single instances of information
        exportDataList.append([''.join([ModeStateStringVar.get(), ' Run, Output Unit: ', outputUnit])]) #"title" header
        
        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataList.append([''.join(['State(s) Under Test: ', FORMSETStateString.get(), ' and RESET'])])
        exportDataList.append([''.join(['Gate Voltage (V):  ', str(gateVoltage/1000)])])
        exportDataList.append([''.join([FORMSETStateString.get(), ' Voltage (V):  ', str(FORMSETVoltage/1000)])])
        exportDataList.append([''.join(['RESET Voltage (V):  ', str(RESETVoltage/1000)])])
        exportDataList.append([''.join([FORMSETStateString.get(), ' READ Voltage (V):  ', str(FORMSETREADVoltage.get())])])
        exportDataList.append([''.join(['RESET READ Voltage (V):  ', str(RESETREADVoltage.get())])])

        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataList.append([''.join([FORMSETStateString.get(), ' Time (us):  ', str(FORMSETTime)])])
        exportDataList.append([''.join(['RESET Time (us):  ', str(RESETTime)])])
        exportDataList.append([''.join([FORMSETStateString.get(), ' READ Time (us):  ', str(FORMSETREADTime)])])
        exportDataList.append([''.join(['RESET READ Time (us):  ', str(RESETREADTime)])])
        exportDataList.append([''.join(['Delay Period (us):  ', str(delayPeriodTime)])])

        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataList.append([''.join(['Maximum Step Voltage (V):  ', str(maxStepVoltage.get())])])
        exportDataList.append([''.join(['Number of Steps for all Devices:  ', str(stepNumber)])])

        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataList.append([''.join(['Number of Cycles for all Devices:  ', str(cycleNumber.get())])])

        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        #create the header for the corresponding multiple columns for the data within said header
        #and loop through the data to append to the exportDataList

        #row header with all column titles
        loopDataRowHeader = ['Device [row, column]', 'Cycle Number', ''.join(['Channel Numbers [', FORMSETStateString.get(), \
                                ', RESET]']), ''.join([FORMSETStateString.get(), ' ', outputUnit]), \
                             ''.join(['RESET ', outputUnit]), 'Current Step Voltage (mV)']
        
        exportDataList.append(loopDataRowHeader)

        # - - - - - - - -

        #append the data FOR EACH DEVICE/CELL THAT WAS SET TO TRUE

        currentDevice = 0

        for currentRow in range(cellGrid.returnRowNum()): #for all rows
            for currentColumn in range(cellGrid.returnColumnNum()): #for all columns

                #CHECK IF SELECTED IN THE INTERACTIVE GRID
                if(cellGrid.returnBooleans()[currentRow][currentColumn]): #if selected

                    #loop through all cycles to get said cycle's data to append with
                    #the expected information (and order) based on the loopDataRowHeader list
                    for cycleIndex in range(cycleNumber.get()):

                        #for another loop based on the number of voltage steps
                        for stepIndex in range(len(FORMSETIcurResList[0][0])):

                            #currently working around the logic of having the SET and RESET operations
                            #be on SEPARATE rows, so create and append the row data for each operation
                            #into the exportDataList separately

                            #prepare this row's data
                            cycleNewRowList = [] #list to store the row data

                            #save the device/cell information
                            cycleNewRowList.append(''.join([str(currentRow + 1), ',', str(currentColumn + 1)]))

                            #record the current cycle number
                            cycleNewRowList.append(str(cycleIndex + 1)) #for the 'Cycle Number' colum

                            #get the channel number from either the SET or RESET data if either of them
                            #are not empty
                            #if BOTH are NOT empty, output the [FORM/SET, RESET], otherwise have the
                            #empty list return nothing for its respective part)
                            if(FORMSETChannelList[currentDevice][cycleIndex][0] != '' and \
                               RESETChannelList[currentDevice][cycleIndex][0] != ''): #if BOTH lists are NOT empty
                                combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[currentDevice][cycleIndex][stepIndex]), ', ', \
                                                                    str(RESETChannelList[currentDevice][cycleIndex][stepIndex]), ']'])
                                cycleNewRowList.append(combinedListChannelsString)
                            elif(FORMSETChannelList[currentDevice][cycleIndex][0] != '' and \
                                 RESETChannelList[currentDevice][cycleIndex][0] == ''): #else if ONLY FORM/SET channel list isn't empty
                                combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[currentDevice][cycleIndex][stepIndex]), ', EMPTY]'])
                                cycleNewRowList.append(combinedListChannelsString)
                            elif(FORMSETChannelList[currentDevice][cycleIndex][0] == '' and \
                                 RESETChannelList[currentDevice][cycleIndex][0] != ''): #else if ONLY RESET channel list isn't empty
                                combinedListChannelsString = ''.join(['[EMPTY, ', str(RESETChannelList[currentDevice][cycleIndex][stepIndex]), ']'])
                                cycleNewRowList.append(combinedListChannelsString)
                            else: #otherwise, append empty cell info
                                cycleNewRowList.append('')

                            #get the current/resistance data from FORM/SET and/or RESET
                            if(FORMSETIcurResList[currentDevice][cycleIndex][0] != ''): #checking FORM/SET list if it isn't empty

                                #record the FORM/SET current or resistance
                                cycleNewRowList.append(str(FORMSETIcurResList[currentDevice][cycleIndex][stepIndex]))

                            else: #otherwise (i.e. if empty), append empty cell info
                                cycleNewRowList.append('')

                            if(RESETIcurResList[currentDevice][cycleIndex][0] != ''): #checking RESET list if it isn't empty

                                #record the FORM/SET current or resistance
                                cycleNewRowList.append(str(RESETIcurResList[currentDevice][cycleIndex][stepIndex]))

                            else: #otherwise (i.e. if empty), append empty cell info
                                cycleNewRowList.append('')

                            #get the step voltage at the time this row's data was obtained
                            cycleNewRowList.append(str(pulseTestStepVoltagesList[stepIndex]))
                        
                            #append to exportDataList in the FOR loop for each cycle's data
                            exportDataList.append(cycleNewRowList)

                    currentDevice += 1

    #----------------------------------------------------------------

    #otherwise, ModeStateStringVar states that the run was for an IV test OR pulse SET/RESET switch test,
    #prepare these test specific outputs
    else:

        #NOTE: Contents of "boardOutOther" are the OUTPUTTED VOLTAGES from the board

        #create basic headers with single instances of information
        #if the unique instance of running BOTH SET AND RESET BACK TO BACK was done, create unique title
        if(IVStateBool or ModeStateStringVar.get() == 'Pulse Test - SET/RESET Switch'):

            if(invertIVStates.get()): #if inverted run, reflect in title
                exportDataList.append([''.join([ModeStateStringVar.get(), ' Run, RESET/SET Consecutive Sequence'])]) #"title" header
            else: #otherwise, normal IV state title
                exportDataList.append([''.join([ModeStateStringVar.get(), ' Run, SET/RESET Consecutive Sequence'])]) #"title" header
                
        else: #otherwise, normal title
            exportDataList.append([''.join([ModeStateStringVar.get(), ' Run'])]) #"title" header
        
        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy)

        if(ModeStateStringVar.get() == 'IV Test'):
            exportDataList.append([''.join(['State under Test:  ', IVTestState.get()])])

        if(ModeStateStringVar.get() == 'Pulse Test - SET/RESET Switch'):
            FORMSETIcurResList, RESETIcurResList, FORMSETChannelList, RESETChannelList = \
                        splitSetResetData(boardOutOther, boardOutIcurRes, boardOutStates)

        if(IVStateBool or ModeStateStringVar.get() == 'Pulse Test - SET/RESET Switch'):
            exportDataList.append([''.join(['SET Gate Voltage (V):  ', str(SETGateVoltage.get())])])
            exportDataList.append([''.join(['RESET Gate Voltage (V):  ', str(RESETGateVoltage.get())])])
        else:
            exportDataList.append([''.join(['Gate Voltage (V):  ', str(gateVoltage/1000)])])

        if(ModeStateStringVar.get() == 'Pulse Test - SET/RESET Switch'):
            exportDataList.append([''.join(['SET Voltage (V):  ', str(FORMSETVoltage/1000)])])
            exportDataList.append([''.join(['RESET Voltage (V):  ', str(RESETVoltage/1000)])])

        exportDataList.append([''.join(['SET READ Voltage (V):  ', str(FORMSETREADVoltage.get())])])
        exportDataList.append([''.join(['RESET READ Voltage (V):  ', str(RESETREADVoltage.get())])])

        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        if(ModeStateStringVar.get() == 'Pulse Test - SET/RESET Switch'):
            exportDataList.append([''.join(['SET Time (us):  ', str(FORMSETTime)])])
            exportDataList.append([''.join(['RESET Time (us):  ', str(RESETTime)])])

        exportDataList.append([''.join(['SET READ Time (us):  ', str(FORMSETREADTime)])])
        exportDataList.append([''.join(['RESET READ Time (us):  ', str(RESETREADTime)])])
        exportDataList.append([''.join(['Delay Period (us):  ', str(delayPeriodTime)])])

        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy)

        exportDataList.append([''.join(['Number of Cycles for all Devices:  ', str(cycleNumber.get())])])

        if(ModeStateStringVar.get() == 'IV Test'):
            exportDataList.append([''.join(['Number of Steps for all Devices:  ', str(stepNumber)])])

        exportDataList.append(['']) #skip to next cell row (.csv file logic terminlogy)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        #create the header for the corresponding multiple columns for the data within said header
        #and loop through the data to append to the exportDataList

        #row header with all column titles
        if(ModeStateStringVar.get() == 'IV Test'):
            loopDataRowHeader = ['Device [row, column]', 'Cycle/Step Number', 'Edge Operation', 'Voltage (mV)', 'Current (uA)']
        else: #if for pulse SET/RESET switch, which allows for changeable current/resistance units
            loopDataRowHeader = ['Device [row, column]', 'Cycle Number', 'Channel Numbers [SET, RESET]', ''.join(['SET ', outputUnit]), \
                             ''.join(['RESET ', outputUnit])]
            
        exportDataList.append(loopDataRowHeader)

        #append the data FOR EACH DEVICE/CELL THAT WAS SET TO TRUE

        dataIndex = 0

        for currentRow in range(cellGrid.returnRowNum()): #for all rows
            for currentColumn in range(cellGrid.returnColumnNum()): #for all columns

                #CHECK IF SELECTED IN THE INTERACTIVE GRID
                if(cellGrid.returnBooleans()[currentRow][currentColumn]): #if selected

                    #given the unique fact that the 'IV' state test AND the SET/RESET Pulse Tests do BOTH SET AND RESET runs,
                    #the amount of outputs are expected to be doubled, so such logic will be done in a separate sequence
                    #compared to the rest also logically works for the pulse SET/RESET switch test

                    #if not this unique IVStateBool case (IV state, IV test mode) OR not the Pulse Test SET/RESET case overall,
                    #proceed below (keeping normal instance in first position this time) 
                    #NOTE: this is done because the stepNumber needs to be QUADRUPLE the range for the unique IVStateBool
                    #case, NOT JUST DOUBLE
                    if(not (IVStateBool or ModeStateStringVar.get() == 'Pulse Test - SET/RESET Switch')):

                        #other 3 IV state modes
                        
                        #loop through all cycles AND steps to get said cycle's/step's data to append with
                        #the expected information (and order) based on the loopDataRowHeader list
                        for cycleIndex in range(cycleNumber.get()):

                            #NOTE: steps for BOTH rising AND falling instances (lists have double stepNumber length)
                            for stepIndex in range(stepNumber * 2):

                                cycleNewRowList = [] #list to store the row data

                                #save the device/cell information
                                cycleNewRowList.append(''.join([str(currentRow + 1), ',', str(currentColumn + 1)]))

                                #record the current cycle AND step number
                                cycleNewRowList.append([''.join([str(cycleIndex + 1), '/', str(stepIndex + 1)])])

                                #record the corresponding edge operation (in boardOutStates)
                                cycleNewRowList.append(str(boardOutStates[dataIndex]))
                                
                                #record the voltage (in boardOutOther)
                                #RECALL: Voltage data ALREADY converted to milliVolts
                                cycleNewRowList.append(str(boardOutOther[dataIndex]))

                                #record the current/resistance
                                cycleNewRowList.append(str(boardOutIcurRes[dataIndex]))

                                #append to exportDataList in the FOR loop for each cycle's data
                                exportDataList.append(cycleNewRowList)

                                dataIndex += 1

                    else: #otherwise, THE UNIQUE 'IV' STATE CASE IS MET OR Pulse Test SET/RESET mode

                        #perform the same as above, only this time there are DOUBLE the 'normal' number of steps

                        #loop through all cycles AND steps to get said cycle's/step's data to append with
                        #the expected information (and order) based on the loopDataRowHeader list
                        for cycleIndex in range(cycleNumber.get()):

                            if(ModeStateStringVar.get() == 'IV Test'): #this has step number logic

                                #NOTE: steps for BOTH rising AND falling instances (lists have double stepNumber length)
                                #DIFFERENCE FROM OTHER VERSION HERE WITH * 4 INSTEAD OF * 2
                                for stepIndex in range(stepNumber * 4):

                                    cycleNewRowList = [] #list to store the row data

                                    #save the device/cell information
                                    cycleNewRowList.append(''.join([str(currentRow + 1), ',', str(currentColumn + 1)]))

                                    #record the current cycle AND step number
                                    cycleNewRowList.append([''.join([str(cycleIndex + 1), '/', str(stepIndex + 1)])])

                                    #record the corresponding edge operation (in boardOutStates)
                                    cycleNewRowList.append(str(boardOutStates[dataIndex]))
                                    
                                    #record the voltage (in boardOutOther)
                                    cycleNewRowList.append(str(boardOutOther[dataIndex]))

                                    #record the current
                                    cycleNewRowList.append(str(boardOutIcurRes[dataIndex]))

                                    #append to exportDataList in the FOR loop for each cycle's data
                                    exportDataList.append(cycleNewRowList)

                                    dataIndex += 1

                            else: #otherwise, pulse SET/RESET switch logic

                                #currently working around the logic of having the SET and RESET operations
                                #be on SEPARATE rows, so create and append the row data for each operation
                                #into the exportDataList separately

                                #prepare this row's data
                                cycleNewRowList = [] #list to store the row data

                                #save the device/cell information
                                cycleNewRowList.append(''.join([str(currentRow + 1), ',', str(currentColumn + 1)]))

                                #record the current cycle number
                                cycleNewRowList.append(str(cycleIndex + 1)) #for the 'Cycle Number' colum

                                #get the channel number from either the SET or RESET data if either of them
                                #are not empty
                                #if BOTH are NOT empty, output the [FORM/SET, RESET], otherwise have the
                                #empty list return nothing for its respective part)
                                if(FORMSETChannelList[0] != '' and RESETChannelList[0] != ''): #if BOTH lists are NOT empty
                                    combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[dataIndex]), ', ', \
                                                                        str(RESETChannelList[dataIndex]), ']'])
                                    cycleNewRowList.append(combinedListChannelsString)
                                elif(FORMSETChannelList[0] != '' and RESETChannelList[0] == ''): #else if ONLY FORM/SET channel list isn't empty
                                    combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[dataIndex]), ', EMPTY]'])
                                    cycleNewRowList.append(combinedListChannelsString)
                                elif(FORMSETChannelList[0] == '' and RESETChannelList[0] != ''): #else if ONLY RESET channel list isn't empty
                                    combinedListChannelsString = ''.join(['[EMPTY, ', str(RESETChannelList[dataIndex]), ']'])
                                    cycleNewRowList.append(combinedListChannelsString)
                                else: #otherwise, append empty cell info
                                    cycleNewRowList.append('')

                                #get the current/resistance data from FORM/SET and/or RESET
                                if(FORMSETIcurResList[0] != ''): #checking FORM/SET list if it isn't empty

                                    #record the FORM/SET current or resistance
                                    cycleNewRowList.append(str(FORMSETIcurResList[dataIndex]))

                                else: #otherwise (i.e. if empty), append empty cell info
                                    cycleNewRowList.append('')

                                if(RESETIcurResList[0] != ''): #checking RESET list if it isn't empty

                                    #record the FORM/SET current or resistance
                                    cycleNewRowList.append(str(RESETIcurResList[dataIndex]))

                                else: #otherwise (i.e. if empty), append empty cell info
                                    cycleNewRowList.append('')
                            
                                #append to exportDataList in the FOR loop for each cycle's data
                                exportDataList.append(cycleNewRowList)

                                dataIndex += 1

    #----------------------------------------------------------------

    #at Jeelka's request, for a PULSE TEST read-write verification run,
    #create a separate Excel file that stores ALL the data of the FAILED
    #devices that did not find any RESET outputs within the specified range
    if(len(failedDeviceList) > 0): #if ANY failed devices were found, proceed

        FORMSETIcurResList, RESETIcurResList, FORMSETChannelList, RESETChannelList = \
                            splitSetResetData(failedRangeCycleDataListOther, failedRangeCycleDataListCurrent, \
                                failedRangeCycleDataListStates)

        #create basic headers with single instances of information
        exportDataListFAILED.append([''.join([ModeStateStringVar.get(), \
                                              ' FAILED Read-Write Verification Run, Output Unit: ', outputUnit])]) #"title" header
        
        exportDataListFAILED.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataListFAILED.append([''.join(['State(s) Under Test: ', FORMSETStateString.get(), ' and RESET'])])
        exportDataListFAILED.append([''.join(['Gate Voltage (V):  ', str(gateVoltage/1000)])])
        exportDataListFAILED.append([''.join([FORMSETStateString.get(), ' Voltage (V):  ', str(FORMSETVoltage/1000)])])
        exportDataListFAILED.append([''.join(['RESET Voltage (V):  ', str(RESETVoltage/1000)])])
        exportDataListFAILED.append([''.join([FORMSETStateString.get(), ' READ Voltage (V):  ', str(FORMSETREADVoltage.get())])])
        exportDataListFAILED.append([''.join(['RESET READ Voltage (V):  ', str(RESETREADVoltage.get())])])

        exportDataListFAILED.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataListFAILED.append([''.join([FORMSETStateString.get(), ' Time (us):  ', str(FORMSETTime)])])
        exportDataListFAILED.append([''.join(['RESET Time (us):  ', str(RESETTime)])])
        exportDataListFAILED.append([''.join([FORMSETStateString.get(), ' READ Time (us):  ', str(FORMSETREADTime)])])
        exportDataListFAILED.append([''.join(['RESET READ Time (us):  ', str(RESETREADTime)])])
        exportDataListFAILED.append([''.join(['Delay Period (us):  ', str(delayPeriodTime)])])

        exportDataListFAILED.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataListFAILED.append([''.join(['Number of Cycles for all Devices:  ', str(failedCycleMax)])])

        exportDataListFAILED.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataListFAILED.append([''.join(['Range Min (', outputUnit, '): ', str(pulseTestRangeMin.get())])])
        exportDataListFAILED.append([''.join(['Range Max (', outputUnit, '): ', str(pulseTestRangeMax.get())])])

        exportDataListFAILED.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        #create the header for the corresponding multiple columns for the data within said header
        #and loop through the data to append to the exportDataList

        #row header with all column titles
        loopDataRowHeader = ['Device [row, column]', 'Cycle Number', ''.join(['Channel Numbers [', FORMSETStateString.get(), \
                                ', RESET]']), ''.join([FORMSETStateString.get(), ' ', outputUnit]), \
                             ''.join(['RESET ', outputUnit])]
        
        exportDataListFAILED.append(loopDataRowHeader)

        # - - - - - - - -

        dataIndex = 0

        #loop through all cycles to get said cycle's data to append with
        #the expected information (and order) based on the loopDataRowHeader list
        for failedDeviceIndex in range(len(failedDeviceList)):
            
            for cycleIndex in range(failedCycleMax):

                #currently working around the logic of having the SET and RESET operations
                #be on SEPARATE rows, so create and append the row data for each operation
                #into the exportDataList separately

                #prepare this row's data
                cycleNewRowList = [] #list to store the row data

                #save the device/cell information
                cycleNewRowList.append(''.join([str(failedDeviceList[failedDeviceIndex][0]), ',', \
                                                str(failedDeviceList[failedDeviceIndex][1])]))

                #record the current cycle number
                cycleNewRowList.append(str(cycleIndex + 1)) #for the 'Cycle Number' colum

                #get the channel number from either the SET or RESET data if either of them
                #are not empty
                #if BOTH are NOT empty, output the [FORM/SET, RESET], otherwise have the
                #empty list return nothing for its respective part)
                if(FORMSETChannelList[0] != '' and RESETChannelList[0] != ''): #if BOTH lists are NOT empty
                    combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[dataIndex]), ', ', \
                                                        str(RESETChannelList[dataIndex]), ']'])
                    cycleNewRowList.append(combinedListChannelsString)
                elif(FORMSETChannelList[0] != '' and RESETChannelList[0] == ''): #else if ONLY FORM/SET channel list isn't empty
                    combinedListChannelsString = ''.join(['[', str(FORMSETChannelList[dataIndex]), ', EMPTY]'])
                    cycleNewRowList.append(combinedListChannelsString)
                elif(FORMSETChannelList[0] == '' and RESETChannelList[0] != ''): #else if ONLY RESET channel list isn't empty
                    combinedListChannelsString = ''.join(['[EMPTY, ', str(RESETChannelList[dataIndex]), ']'])
                    cycleNewRowList.append(combinedListChannelsString)
                else: #otherwise, append empty cell info
                    cycleNewRowList.append('')

                #get the current/resistance data from FORM/SET and/or RESET
                if(FORMSETIcurResList[0] != ''): #checking FORM/SET list if it isn't empty

                    #record the FORM/SET current or resistance
                    cycleNewRowList.append(str(FORMSETIcurResList[dataIndex]))

                else: #otherwise (i.e. if empty), append empty cell info
                    cycleNewRowList.append('')

                if(RESETIcurResList[0] != ''): #checking RESET list if it isn't empty

                    #record the FORM/SET current or resistance
                    cycleNewRowList.append(str(RESETIcurResList[dataIndex]))

                else: #otherwise (i.e. if empty), append empty cell info
                    cycleNewRowList.append('')
            
                #append to exportDataList in the FOR loop for each cycle's data
                exportDataListFAILED.append(cycleNewRowList)

                dataIndex += 1
                
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #at Jeelka's request, for PULSE TEST exclusively for SINGLE CYCLES when ALL
    #devices/cells are selected, she wants two Excel outputs in a format where
    #the grid columns are outputted in row format and separated for SET and RESET
    #respectively between the two files
    if(ModeStateStringVar.get() == 'Pulse Test' and cycleNumber.get() == 1 and not \
       hardCodeDevices.get()):

        #split the data here to their SET/RESET exclusive equivalents
        #NOTE: While this is done above for normal pulse testing, best to keep this
        #here regardless for the sake of not having to worry about potential changes
        #between splitSetResetData function calls
        FORMSETIcurResList, RESETIcurResList, FORMSETChannelList, RESETChannelList = \
                        splitSetResetData(boardOutOther, boardOutIcurRes, boardOutStates)

        # - - - - - - - - - - - - - - - - - - - -

        #create basic headers with single instances of information

        #FORM/SET
        exportDataListSET.append([''.join([ModeStateStringVar.get(), ' Single Cycle ', FORMSETStateString.get(), \
                                           ' Run, Output Unit: ', outputUnit])]) #"title" header
        
        exportDataListSET.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataListSET.append([''.join(['Gate Voltage (V):  ', str(gateVoltage/1000)])])
        exportDataListSET.append([''.join([FORMSETStateString.get(), ' Voltage (V):  ', str(FORMSETVoltage/1000)])])
        exportDataListSET.append([''.join(['RESET Voltage (V):  ', str(RESETVoltage/1000)])])
        exportDataListSET.append([''.join([FORMSETStateString.get(), ' READ Voltage (V):  ', str(FORMSETREADVoltage.get())])])
        exportDataListSET.append([''.join(['RESET READ Voltage (V):  ', str(RESETREADVoltage.get())])])

        exportDataListSET.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataListSET.append([''.join([FORMSETStateString.get(), ' Time (us):  ', str(FORMSETTime)])])
        exportDataListSET.append([''.join(['RESET Time (us):  ', str(RESETTime)])])
        exportDataListSET.append([''.join([FORMSETStateString.get(), ' READ Time (us):  ', str(FORMSETREADTime)])])
        exportDataListSET.append([''.join(['RESET READ Time (us):  ', str(RESETREADTime)])])
        exportDataListSET.append([''.join(['Delay Period (us):  ', str(delayPeriodTime)])])

        exportDataListSET.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        # - - - - - - - - -

        #RESET
        exportDataListRESET.append([''.join([ModeStateStringVar.get(), ' Single Cycle RESET Run, Output Unit: ', outputUnit])]) #"title" header
        
        exportDataListRESET.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataListRESET.append([''.join(['Gate Voltage (V):  ', str(gateVoltage/1000)])])
        exportDataListRESET.append([''.join([FORMSETStateString.get(), ' Voltage (V):  ', str(FORMSETVoltage/1000)])])
        exportDataListRESET.append([''.join(['RESET Voltage (V):  ', str(RESETVoltage/1000)])])
        exportDataListRESET.append([''.join([FORMSETStateString.get(), ' READ Voltage (V):  ', str(FORMSETREADVoltage.get())])])
        exportDataListRESET.append([''.join(['RESET READ Voltage (V):  ', str(RESETREADVoltage.get())])])

        exportDataListRESET.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)

        exportDataListRESET.append([''.join([FORMSETStateString.get(), ' Time (us):  ', str(FORMSETTime)])])
        exportDataListRESET.append([''.join(['RESET Time (us):  ', str(RESETTime)])])
        exportDataListRESET.append([''.join([FORMSETStateString.get(), ' READ Time (us):  ', str(FORMSETREADTime)])])
        exportDataListRESET.append([''.join(['RESET READ Time (us):  ', str(RESETREADTime)])])
        exportDataListRESET.append([''.join(['Delay Period (us):  ', str(delayPeriodTime)])])

        exportDataListRESET.append(['']) #skip to next cell row (.csv file logic terminlogy for aesthetic)
            
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        #create the header for the corresponding multiple columns for the data within said header
        #and loop through the data to append to the exportDataList

        #row header with all Excel column titles, which will be for the device/cell
        #ROWS at Jeelka's request
        deviceCellFullGridRange = range(1, cellGrid.returnRowNum() + 1)
        colHeader = ['']
        colHeader.extend([''.join(['Column ', str(rangeNum)]) for rangeNum in deviceCellFullGridRange])
        
        exportDataListSET.append(colHeader)
        exportDataListRESET.append(colHeader)

        # - - - - - - - -

        #seeing how Jeelka wants an option where the full 64 x 64 grid is outputted but
        #any devices/cells NOT selected should be empty, this requires recreating the
        #list with the empty devices wherever buttons were not pressed, though luckily
        #maintaining the searching format in other areas of the code should maintain the
        #split SET/RESET data indices relative to the selected grid buttons
        foundDeviceNum = 0
        for gridRow in range(cellGrid.returnRowNum()):

            recreatedGridRowSET = []
            recreatedGridRowRESET = []

            #initialize current data list with column number
            recreatedGridRowSET = [''.join(['Row ', str(gridRow + 1)])]
            recreatedGridRowRESET = [''.join(['Row ', str(gridRow + 1)])]
            
            for gridCol in range(cellGrid.returnColumnNum()):
                if(cellGrid.returnBooleans()[gridRow][gridCol]): #if the device was selected

                    #retrieve the data for that corresponding device and append to the
                    #SET and RESET two separate Excel files
                    recreatedGridRowSET.append(str(FORMSETIcurResList[foundDeviceNum]))
                    recreatedGridRowRESET.append(str(RESETIcurResList[foundDeviceNum]))

                    foundDeviceNum += 1

                else: #otherwise, make an Excel cell empty for the sake of moving to new spots
                    recreatedGridRowSET.append('')
                    recreatedGridRowRESET.append('')

            #append the full row's data to the list to be returned
            #before proceeding to the next row
            exportDataListSET.append(recreatedGridRowSET)
            exportDataListRESET.append(recreatedGridRowRESET)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #return all created lists of data
    return exportDataList, exportDataListFAILED, exportDataListSET, \
           exportDataListRESET

#-------------------------------------------------------------------------

#call the serialExecution function and organize the outputted data based
#on the number of cycles
def serialConnectAndExecute(cycleNumber, inputByteList, expectedPortDriverSearch, \
                            toggledOhmsLawUnit, SETREADVoltage, RESETREADVoltage, \
                            messageListBox, IVTestState):

    #initialized lists to store "serialExecution" output(s)
    #boardOutOther for storing channel numbers for Pulse Test OR
    #voltage for IV test corresponding to the current outputs
    boardOutOther = []
    boardOutCurrent = [] #for storing electric current values
    boardOutStates = [] #for storing channel states

    #since the following logic has loop conditions based around the cycle number,
    #"cycleNumber" from the main GUI function has been included here to avoid
    #having to recombine the split byte information of byte25_CyclesNumberMSB and
    #byte26_CyclesNumberLSB respectively

    #perform try/except block test to check if the board connection is maintained

    try: #perform "serialExecution" function loop while connected

        #send byte list to board through serial

        #first, determine number of times "serialExecution" function needs
        #to be called depending on the number of cycles (with the number 125 being
        #the set number of cycles set in the previous code)
        if(cycleNumber.get() <= 125): #if number of cycles inputted is LTE 125

            #run normal serial execution
            boardOutOther, boardOutCurrent, boardOutStates = \
                             serialExecution(inputByteList, expectedPortDriverSearch, IVTestState)

        #otherwise, number of cycles inputted exceeds 125, so loop through
        #serial executions in cycle iterations of 125 with the final loop
        #addressing the remainder
        else:

            #reset boardOutOther and boardOutCurrent list for
            #appending to deviceOutputList
            boardOutOther = []
            boardOutCurrent = []
            boardOutStates = []

            #while still looping through the data, including one loop
            #for the remainder (if any), call built in "serialExecution"
            #function with cycle iterations of (at most) 125
            
            cycleWHILENum = cycleNumber.get() #initialize iterative number for WHILE loop

            #for the following, the MSB of the cycle number will ALWAYS be 0
            #since it won't change with the total amount per "serialExceution"
            #call being 125 or below (must be at least 256 for the MSB to change,
            #0x0100 = 256)
            inputByteList[24] = int(0) #byte 25, number of cycles MSB

            while(cycleWHILENum > 0):
                if(cycleWHILENum - 125 >= 0): #if 125 cycles still remain

                    #call "serialExecution" function for 125 cycles
                    
                    inputByteList[25] = int(125) #byte 26, number of cycles LSB
                    
                    loopOutputOther, loopOutputCurrent, loopOutputStates = \
                                       serialExecution(inputByteList, expectedPortDriverSearch, IVTestState)

                    #"extend()" boardOutputs with both loopOutput data
                    boardOutOther += loopOutputOther
                    boardOutCurrent += loopOutputCurrent
                    boardOutStates += loopOutputStates

                    cycleWHILENum -= 125 #remove 125 cycles and WHILE loop again

                else: #otherwise, perform one last "serialExecution" for remainder

                    inputByteList[25] = int(cycleWHILENum) #byte 26, number of cycles LSB
                    
                    loopOutputOther, loopOutputCurrent, loopOutputStates = \
                                       serialExecution(inputByteList, expectedPortDriverSearch, IVTestState)

                    #"extend()" boardOutputs with both loopOutput data
                    boardOutOther += loopOutputOther
                    boardOutCurrent += loopOutputCurrent
                    boardOutStates += loopOutputStates
                    
                    cycleWHILENum -= cycleWHILENum #remove remaining cycles to break the WHILE loop

        #if necessary, change the obtained current units to resistance depending on
        #the current "toggledOhmsLawUnit" string
        #NOTE: the "convertIToR" function only works for Pulse Test, with only the Pulse Test
        #GUI window being able to convert the toggledOhmsLawUnit using the corresponding unit button
        if(toggledOhmsLawUnit.get() == 'kOhm'): #if resistance string, change current to resistance
                convertIToR(boardOutCurrent, boardOutStates, SETREADVoltage.get(), \
                            RESETREADVoltage.get())
        
    except Exception as e: #exception found, connection issue occurred
        messageListBox.insert(END, 'Board connection issue')
        messageListBox.insert(END, 'Check if board is plugged in or')
        messageListBox.insert(END, 'if drivers not installed')

    return boardOutOther, boardOutCurrent, boardOutStates

#-------------------------------------------------------------------------

#function that will generate the plots based on the mode run
def createPlots(boardOutOther, boardOutCurrent, boardOutStates, cellGrid, cycleNumber, \
                toggledOhmsLawUnit, IVTestState, byte29_modeState, rowNumber, columnNumber, \
                SETREADVoltage, RESETREADVoltage, FORMSETStateString, messageListBox, \
                invertStates, stepVoltageDirection, maxStepVoltage, \
                chosenStepVoltage, pulseTestStepVoltagesList, gateVoltage, FORMSETVoltage, \
                RESETVoltage, SETGateVoltage, RESETGateVoltage, saveDirectory, permitPlotDisplayFlag, \
                heatMapFlag, hardCodeDevices):

    if(not heatMapFlag): #if NOT the full data heatmap choice

        #create plots of the obtained information depending on the run test
        #RECALL: boardOutOther for storing channel numbers for Pulse Test OR
        #voltage for IV test corresponding to the current outputs
        #RECALL: For the PULSE TEST specifically, the non-Voltage value can
        #be EITHER CURRENT OR RESISTANCE (incorporate toggledOhmsLawUnit)

        #NOTE: At Jeelka's request, she wants the directory where the plots are stored to be the
        #same directory where the outputted .csv files are located

        # - - - - - - - - - - - -

        #set x-axis ticks to whole numbers AND CHANGE X AXIS SPACING BETWEEN POINTS
        #IF THE NUMBER OF INPUTTED CYCLES ARE LARGER THAN A SET AMOUNT THAT THE PLOT CAN
        #VISIBLY SHOW WITHOUT CLUTTER (limiter numbers based on personal preference after
        #testing)
        #NOTE: For the sake of "simplicity", the MultipleLocator below will be determined by the
        #(cycle number / xAxisPointNumber) value, THIS GUARANTEES A MAX OF ONLY xAxisPointNumber POINTS
        #ON THE X-AXIS
        #maxSinglePointLimit chosen based on personal preference and previous testing (seeing how 20 works to have the
        #intervals use this logic and be 2+ onwards), CHANGE IF NECESSARY
        maxSinglePointLimit = 19
        xAxisPointNumber = 10 #chosen based on personal preference and previous testing, CHANGE IF NECESSARY

        # - - - - - - - - - - - -

        #NOTE: For pulse test, this will only generate a plot IF THE CYCLE NUMBER EXCEEDS 1
        #For IV test, no data will be outputted if the STEP NUMBER IS 1, BUT IT'S
        #POSSIBLE TO STILL HAVE ONE FULL CYCLE ALONE WITH MULTIPLE STEPS

        if(byte29_modeState.get() == 'Pulse Test'): #create the Pulse Test specific plot output(s)

            #ONLY PLOT FOR SET/RESET COMBINATION, NOT FOR FORM
            if(not FORMSETStateString.get() == 'FORM'):

                #ONLY PERFORM THE FOLLOWING IF THE CYCLE NUMBER EXCEEDS ONE, AS PLOTTING
                #A SINGLE POINT ON A PLOT WON'T MAKE AN INFORMATIVE PLOT
                if(cycleNumber.get() > 1):
                    
                    #call "splitSetResetData" function to split up the SET/RESET data
                    FORMSETIcurResList, RESETIcurResList, FORMSETChannelList, RESETChannelList = \
                                    splitSetResetData(boardOutOther, boardOutCurrent, boardOutStates)

                    # - - - - - - - - - - - - - - - - - - - - - - -

                    #BOTH FORM/SET AND RESET PLOTS ON THE SAME GRAPH

                    #create cycle number (x-axis) vs FORMSETIcurResList (y-axis) plot

                    #create the x-axis list (cycle number) based off the FORMSETIcurResList list length
                    cycleList = list(range(1, len(FORMSETIcurResList) + 1))

                    #create and populate two separate subplots, one for SET and the other for RESET
                    #NOTE: the logic for the "num = 1, clear = True" as a means of addressing memory
                    #issues with too many plots being opened was obtained from the following link:
                    #https://stackoverflow.com/questions/28757348/how-to-clear-memory-completely-of-all-matplotlib-plots
                    if(permitPlotDisplayFlag):
                        fig, ax = plt.subplots()
                    else:
                        fig, ax = plt.subplots(num = 1, clear = True)
                    
                    ax.set_xlabel('Cycle Number') #SHARED x-axis

                    #set y-axis label and generate plot types based on inputted toggledOhmsLawUnit
                    if(toggledOhmsLawUnit.get() == 'uA'): #if current, not resistance
                        ax.set_ylabel(''.join([FORMSETStateString.get(), ' Current (uA)'])) #y-axis
                        
                    else: #otherwise, resistance
                        ax.set_ylabel(''.join([FORMSETStateString.get(), ' Resistance (KOhms)'])) #y-axis

                    if(toggledOhmsLawUnit.get() == 'uA'): #if current, not resistance

                        #create SCATTER plots  
                        ax.scatter(cycleList, FORMSETIcurResList, color = 'red', label = 'Low Current State (uA)', \
                                   marker = 'p')
                        ax.scatter(cycleList, RESETIcurResList, color = 'blue', label = 'High Current State (uA)', \
                                   marker = '^')
                        ax.set_yscale('log') #have y-axis show values in "log" format

                        #place the legend outside the plot using bbox_to_anchor
                        plt.legend(bbox_to_anchor = (1.05, 0.5), loc = 'center left', \
                                   borderaxespad = 0., title = 'Current Legend', fontsize = '7')

                    else:

                        #create SCATTER plots  
                        ax.scatter(cycleList, FORMSETIcurResList, color = 'red', label = 'Low Resistance State (kOhms)', \
                                   marker = 'p')
                        ax.scatter(cycleList, RESETIcurResList, color = 'blue', label = 'High Current State (kOhms)', \
                                   marker = '^')
                        ax.set_yscale('log') #have y-axis show values in "log" format

                        #place the legend outside the plot using bbox_to_anchor
                        plt.legend(bbox_to_anchor = (1.05, 0.5), loc = 'center left', \
                                   borderaxespad = 0., title = 'Resistance Legend', fontsize = '7')

                    ax.set_title(''.join(['Pulse Testing, Device: (R:', \
                                str(rowNumber), '/C:', str(columnNumber), ')\n(Gate Voltage: ', str(gateVoltage/1000), \
                                ' V, ', FORMSETStateString.get(), ' Voltage: ', str(FORMSETVoltage/1000),  ' V, \nRESET Voltage: ', \
                                str(RESETVoltage/1000), ' V, ', FORMSETStateString.get(), ' READ Voltage: ', \
                                str(SETREADVoltage.get()), ' V, \nRESET READ Voltage: ', str(RESETREADVoltage.get()), ' V)'])) #title

                    if(len(cycleList) > maxSinglePointLimit): #if more cycles than visibly permitted based on maxSinglePointLimit

                        #get the (number of cycles / xAxisPointNumber) and iterate the x-axis points by that number
                        #for better visual clarity
                        ax.xaxis.set_major_locator(plt.MultipleLocator(math.floor(len(cycleList)/xAxisPointNumber)))
                        
                    else: #otherwise, increment x-axis points by 1 since it should be acceptable according to user preference in maxSinglePointLimit
                        ax.xaxis.set_major_locator(plt.MultipleLocator(1))

                    #perform tight_layout to avoid title cutoff
                    plt.tight_layout()

                    #maximize the plot window for better visual clarity (mostly to address legibility
                    #for larger cycle number plots on the x-axis)
                    manager = plt.get_current_fig_manager()
                    manager.window.state('zoomed')

                    # - - - - - - - - - - - - - - - - - - - - - - -

                    #CREATE PNG IMAGE OF PLOT AND SAVE TO CURRENT DIRECTORY

                    currentTime = datetime.now() #get current datetime information
                
                    #adjust datetime format to custom format
                    #https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
                    dateTimeFormatted = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                    fileNameString = ''.join(['Pulse', FORMSETStateString.get(), 'RESETPlot_Device', str(rowNumber), \
                                         '-', str(columnNumber), '_', toggledOhmsLawUnit.get(), '_', \
                                         dateTimeFormatted, '.png'])

                    filePath = os.path.join(saveDirectory.get(), fileNameString)                 
                    
                    fig.savefig(filePath, dpi = 300, bbox_inches = 'tight')

                    # - - - - - - - - - - - - - - - - - - - - - - -

                    #if allowed to show ALL the plots (based on decided max plot limit)
                    if(permitPlotDisplayFlag):
                        
                        #show ALL newly created plots
                        plt.show(block = False)

                    else: #otherwise, clear the memory
                        fig.clear()                    

                else: #otherwise, cycle number <= 1, output message saying no plot is generated for this reason

                    messageListBox.insert(END, 'Cycle Number <= 1, which is used for')
                    messageListBox.insert(END, 'plot X-axis, no plot displayed')
                    messageListBox.insert(END, '')

                    return

            else: #otherwise, FORM was selected, don't plot

                messageListBox.insert(END, 'This program will not plot for FORM mode')
                messageListBox.insert(END, '')

                return
                
        #----------------------------------------------------------------------------------

        elif(byte29_modeState.get() == 'Pulse Test - Step'): #create the Pulse STEP Test specific plot output(s)

            #only plot when there's multiple steps, so if the data length is equivalent to the number
            #of cycles, this concludes that there was only ONE STEP PER CYCLE (since the data is inputted
            #for both SET and RESET combined, check if the length of the inputted data is DOUBLE the
            #number of cycles)

            #ONLY PLOT FOR SET/RESET COMBINATION, NOT FOR FORM
            if(not FORMSETStateString.get() == 'FORM'):

                if(len(boardOutOther) > (2 * cycleNumber.get()) or stepVoltageDirection.get() == 'Rise then Fall'):

                    #call "splitSetResetData" function to split up the SET/RESET data
                    FORMSETIcurResList, RESETIcurResList, FORMSETChannelList, RESETChannelList = \
                                    splitSetResetData(boardOutOther, boardOutCurrent, boardOutStates)

                    # - - - - - - - - - - - - - - - - - - - - - - -

                    #split the data into FORM/SET/RESET plots PER CYCLE using Numpy.array_split
                    #before converting the Numpy arrays back into lists for simplicity

                    #first, split the FORM/SET/RESET data into equal length lists that represent the
                    #outputs for their respective cycles (NOTE: channel information not necessary for
                    #current plots)
                    FORMSETIcurResListSplitNPArrays = np.array_split(FORMSETIcurResList, cycleNumber.get())
                    FORMSETIcurResListSplit = [npArray.tolist() for npArray in FORMSETIcurResListSplitNPArrays]
                    RESETIcurResListSplitNPArrays = np.array_split(RESETIcurResList, cycleNumber.get())
                    RESETIcurResListSplit = [npArray.tolist() for npArray in RESETIcurResListSplitNPArrays]

                    # - - - - - - - - - - - - - - - - - - - - - - -

                    for cycleIteration in range(cycleNumber.get()): #loop through every cycle to output the FORM/SET/RESET data

                        if(chosenStepVoltage.get() == 'SET'): #ONLY plot what chosenStepVoltage has selected

                            #FORM/SET PLOT
                            #RECALL: the inputted FORMSETIcurResListSplit has the step logic incorporated into the list

                            #create pulseTestStepVoltagesList (x-axis) vs FORMSETIcurResListSplit (y-axis) plot
                            #first, get the number of steps (not importing step number of device number into the plot
                            #given the various locations in "pressedSubmitData" that call this function)
                            stepListLength = len(FORMSETIcurResListSplit[cycleIteration])

                            #create the plot with the expected information
                            #creates figure INDEPENDENT OF OTHER FIGURES (to allow multiple plot outputs at once)
                            #NOTE: the logic for the "num = 1, clear = True" as a means of addressing memory
                            #issues with too many plots being opened was obtained from the following link:
                            #https://stackoverflow.com/questions/28757348/how-to-clear-memory-completely-of-all-matplotlib-plots
                            if(permitPlotDisplayFlag):
                                fig = plt.figure()
                            else:
                                fig = plt.figure(num = 1, clear = True)
                    
                            # - - - - - - - - - - - - - - - - - - - - - - -

                            #set y-axis label and generate plot based on inputted toggledOhmsLawUnit

                            if(toggledOhmsLawUnit.get() == 'uA'): #if current, not resistance
                                plt.ylabel('Current (uA)') #y-axis
                                
                            else: #otherwise, resistance
                                plt.ylabel('Resistance (KOhms)') #y-axis

                            #create SCATTER plot
                            plt.scatter(pulseTestStepVoltagesList[slice(stepListLength)], FORMSETIcurResListSplit[cycleIteration])

                            # - - - - - - - - - - - - - - - - - - - - - - -
                            
                            ax = plt.gca()

                            if(len(FORMSETIcurResList) > maxSinglePointLimit): #if more data points than visibly permitted based on maxSinglePointLimit
                                ax.xaxis.set_major_locator(plt.MultipleLocator(abs(pulseTestStepVoltagesList[1] - \
                                                            pulseTestStepVoltagesList[0]) * \
                                                            math.floor(len(FORMSETIcurResList)/xAxisPointNumber))) #increment x-axis points by whole numbers equal to the step interval amount
                            else:
                                ax.xaxis.set_major_locator(plt.MultipleLocator(abs(pulseTestStepVoltagesList[1] - \
                                                            pulseTestStepVoltagesList[0])))

                            if(stepVoltageDirection.get() == 'Falling'): #if falling, invert x-axis direction for logic simplicity
                                ax.invert_xaxis()
                                
                            ax.set_yscale('log') #have y-axis show values in "log" format

                            # - - - - - - - - - - - - - - - - - - - - - - -

                            #add plot labels and title
                            plt.xlabel('Step Voltage (mV)') #x-axis
                            
                            plt.title(''.join(['Pulse Step Testing - SET ', stepVoltageDirection.get(), \
                                               ' Device: (R:', str(rowNumber), '/C:', str(columnNumber), ')\n(', FORMSETStateString.get(), \
                                               ' READ Voltage: ', str(SETREADVoltage.get()), ' V)(Cycle: ', str(cycleIteration + 1), ')'])) #title

                            #perform tight_layout to avoid title cutoff
                            plt.tight_layout()

                            #maximize the plot window for better visual clarity (mostly to address legibility
                            #for larger cycle number plots on the x-axis)
                            manager = plt.get_current_fig_manager()
                            manager.window.state('zoomed')

                            # - - - - - - - - - - - - - - - - - - - - - - -

                            #CREATE PNG IMAGE OF PLOT AND SAVE TO CURRENT DIRECTORY

                            currentTime = datetime.now() #get current datetime information
                        
                            #adjust datetime format to custom format
                            #https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
                            dateTimeFormattedFORMSET = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                            if(stepVoltageDirection.get() == 'Rise then Fall'): #for the sake of having "stepVoltageDirection" without spaces if "Rise then Fall"

                                fileNameString = ''.join(['Pulse', FORMSETStateString.get(),  'RiseThenFallStepPlot_Device', \
                                                 str(rowNumber), '-', str(columnNumber), '_', toggledOhmsLawUnit.get(), '_Cycle', \
                                                 str(cycleIteration + 1), '_', dateTimeFormattedFORMSET, '.png'])

                            else: #either rising only or falling only, doesn't need special string format above

                                fileNameString = ''.join(['Pulse', FORMSETStateString.get(),  stepVoltageDirection.get(), 'StepPlot_Device', \
                                                     str(rowNumber), '-', str(columnNumber), '_', toggledOhmsLawUnit.get(), '_Cycle', \
                                                     str(cycleIteration + 1), '_', dateTimeFormattedFORMSET, '.png'])

                            filePath = os.path.join(saveDirectory.get(), fileNameString)                 
                    
                            fig.savefig(filePath, dpi = 300, bbox_inches = 'tight')

                        # - - - - - - - - - - - - - - - - - - - - - - -

                        else:

                            #RESET PLOT
                            #RECALL: the inputted RESETIcurResListSplit has the step logic incorporated into the list

                            #create pulseTestStepVoltagesList (x-axis) vs RESETIcurResListSplit (y-axis) plot

                            #first, get the number of steps (not importing step number of device number into the plot
                            #given the various locations in "pressedSubmitData" that call this function)
                            stepListLength = len(RESETIcurResListSplit[cycleIteration])

                            #create the plot with the expected information
                            #creates figure INDEPENDENT OF OTHER FIGURES (to allow multiple plot outputs at once)
                            #NOTE: the logic for the "num = 1, clear = True" as a means of addressing memory
                            #issues with too many plots being opened was obtained from the following link:
                            #https://stackoverflow.com/questions/28757348/how-to-clear-memory-completely-of-all-matplotlib-plots
                            if(permitPlotDisplayFlag):
                                fig = plt.figure()
                            else:
                                fig = plt.figure(num = 1, clear = True)
                                
                            # - - - - - - - - - - - - - - - - - - - - - - -

                            #set y-axis label and generate plot based on inputted toggledOhmsLawUnit

                            if(toggledOhmsLawUnit.get() == 'uA'): #if current, not resistance
                                plt.ylabel('Current (uA)') #y-axis

                            else: #otherwise, resistance
                                plt.ylabel('Resistance (KOhms)') #y-axis

                            #create SCATTER plot
                            plt.scatter(pulseTestStepVoltagesList[slice(stepListLength)], RESETIcurResListSplit[cycleIteration])

                            # - - - - - - - - - - - - - - - - - - - - - - -

                            ax = plt.gca()

                            if(len(RESETIcurResListSplit) > maxSinglePointLimit): #if more data points than visibly permitted based on maxSinglePointLimit
                                ax.xaxis.set_major_locator(plt.MultipleLocator(abs(pulseTestStepVoltagesList[1] - \
                                                            pulseTestStepVoltagesList[0]) * \
                                                            math.floor(len(RESETIcurResListSplit)/xAxisPointNumber))) #increment x-axis points by whole numbers equal to the step interval amount
                            else:
                                ax.xaxis.set_major_locator(plt.MultipleLocator(abs(pulseTestStepVoltagesList[1] - \
                                                            pulseTestStepVoltagesList[0])))

                            if(stepVoltageDirection.get() == 'Falling'): #if falling, invert x-axis direction for logic simplicity
                                ax.invert_xaxis()

                            ax.set_yscale('log') #have y-axis show values in "log" format

                            # - - - - - - - - - - - - - - - - - - - - - - -

                            #add plot labels and title
                            plt.xlabel('Step Voltage (mV)') #x-axis

                            if(toggledOhmsLawUnit.get() == 'uA'): #if current, not resistance
                                plt.ylabel('Current (uA)') #y-axis
                            else: #otherwise, resistance
                                plt.ylabel('Resistance (KOhms)') #y-axis
                            
                            plt.title(''.join(['Pulse Step Testing - RESET ', stepVoltageDirection.get(), \
                                               ' Device: (R:', str(rowNumber), '/C:', str(columnNumber), ')\n(RESET READ Voltage: ', \
                                               str(RESETREADVoltage.get()), ' V)(Cycle: ', str(cycleIteration + 1), ')'])) #title

                            #perform tight_layout to avoid title cutoff
                            plt.tight_layout()

                            #maximize the plot window for better visual clarity (mostly to address legibility
                            #for larger cycle number plots on the x-axis)
                            manager = plt.get_current_fig_manager()
                            manager.window.state('zoomed')

                            # - - - - - - - - - - - - - - - - - - - - - - -

                            #CREATE PNG IMAGE OF PLOT AND SAVE TO CURRENT DIRECTORY

                            currentTime = datetime.now() #get current datetime information
                        
                            #adjust datetime format to custom format
                            #https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
                            dateTimeFormattedRESET = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")
                            
                            if(stepVoltageDirection.get() == 'Rise then Fall'): #for the sake of having "stepVoltageDirection" without spaces if "Rise then Fall"
                                fileNameString = ''.join(['PulseRESETRiseThenFallStepPlot_Device', \
                                                 str(rowNumber), '-', str(columnNumber), '_', toggledOhmsLawUnit.get(), '_Cycle', \
                                                 str(cycleIteration + 1), '_', dateTimeFormattedRESET, '.png'])

                            else: #either rising only or falling only, doesn't need special string format above
                                fileNameString = ''.join(['PulseRESET',  stepVoltageDirection.get(), 'StepPlot_Device', \
                                                     str(rowNumber), '-', str(columnNumber), '_', toggledOhmsLawUnit.get(), '_Cycle', \
                                                     str(cycleIteration + 1), '_', dateTimeFormattedRESET, '.png'])

                            filePath = os.path.join(saveDirectory.get(), fileNameString)                 
                    
                            fig.savefig(filePath, dpi = 300, bbox_inches = 'tight')

                        # - - - - - - - - - - - - - - - - - - - - - - -

                        #if allowed to show ALL the plots (based on decided max plot limit)
                        if(permitPlotDisplayFlag):
                            
                            #show ALL newly created plots
                            plt.show(block = False)

                        else: #otherwise, clear the memory
                            fig.clear()

                else: #otherwise, number of steps <= 1, output message saying no plot is generated for this reason

                    messageListBox.insert(END, 'Step Number <= 1, which is used for')
                    messageListBox.insert(END, 'plot X-axis, no plot displayed')
                    messageListBox.insert(END, '')

                    return

            else: #otherwise, FORM was selected, don't plot

                messageListBox.insert(END, 'This program will not plot for FORM mode')
                messageListBox.insert(END, '')

                return

        #----------------------------------------------------------------------------------
            
        elif(byte29_modeState.get() == 'Pulse Test - SET/RESET Switch'): #create the Pulse SET/RESET SWITCH Test specific plot output(s)

            #ONLY PERFORM THE FOLLOWING IF THE CYCLE NUMBER EXCEEDS ONE, AS PLOTTING
            #A SINGLE POINT ON A PLOT WON'T MAKE AN INFORMATIVE PLOT
            if(cycleNumber.get() > 1):
                
                #call "splitSetResetData" function to split up the SET/RESET data
                FORMSETIcurResList, RESETIcurResList, FORMSETChannelList, RESETChannelList = \
                                splitSetResetData(boardOutOther, boardOutCurrent, boardOutStates)

                # - - - - - - - - - - - - - - - - - - - - - - -

                #create string assigning SET/RESET order based on invertStates BooleanVar
                if(invertStates.get()): #if inverted, RESET->SET
                    orderString = 'RESET-SET'
                else: #otherwise, default order, SET->RESET
                    orderString = 'SET-RESET'

                #BOTH FORM/SET AND RESET PLOTS ON THE SAME GRAPH

                #create cycle number (x-axis) vs FORMSETIcurResList (y-axis) plot

                #create the x-axis list (cycle number) based off the FORMSETIcurResList list length
                cycleList = list(range(1, len(FORMSETIcurResList) + 1))

                #create and populate two separate subplots, one for SET and the other for RESET
                #NOTE: the logic for the "num = 1, clear = True" as a means of addressing memory
                #issues with too many plots being opened was obtained from the following link:
                #https://stackoverflow.com/questions/28757348/how-to-clear-memory-completely-of-all-matplotlib-plots
                if(permitPlotDisplayFlag):
                    fig, ax = plt.subplots()
                else:
                    fig, ax = plt.subplots(num = 1, clear = True)
                
                ax.set_xlabel('Cycle Number') #SHARED x-axis

                #set y-axis label and generate plot types based on inputted toggledOhmsLawUnit
                if(toggledOhmsLawUnit.get() == 'uA'): #if current, not resistance
                    ax.set_ylabel(''.join([orderString, ' Current (uA)'])) #y-axis
                    
                else: #otherwise, resistance
                    ax.set_ylabel(''.join([FORMSETStateString.get(), ' Resistance (KOhms)'])) #y-axis

                if(toggledOhmsLawUnit.get() == 'uA'): #if current, not resistance

                    #create SCATTER plots  
                    ax.scatter(cycleList, FORMSETIcurResList, color = 'red', label = 'Low Current State (uA)', \
                               marker = 'p')
                    ax.scatter(cycleList, RESETIcurResList, color = 'blue', label = 'High Current State (uA)', \
                               marker = '^')
                    ax.set_yscale('log') #have y-axis show values in "log" format
                                
                    #place the legend outside the plot using bbox_to_anchor
                    plt.legend(bbox_to_anchor = (1.05, 0.5), loc = 'center left', \
                               borderaxespad = 0., title = 'Current Legend', fontsize = '7')

                else:

                    #create SCATTER plots  
                    ax.scatter(cycleList, FORMSETIcurResList, color = 'red', label = 'Low Resistance State (kOhms)', \
                               marker = 'p')
                    ax.scatter(cycleList, RESETIcurResList, color = 'blue', label = 'High Resistance State (kOhms)', \
                               marker = '^')
                    ax.set_yscale('log') #have y-axis show values in "log" format
                                
                    #place the legend outside the plot using bbox_to_anchor
                    plt.legend(bbox_to_anchor = (1.05, 0.5), loc = 'center left', \
                               borderaxespad = 0., title = 'Resistance Legend', fontsize = '7')

                ax.set_title(''.join([orderString, ' Switch Pulse Testing, Device: (R:', \
                            str(rowNumber), '/C:', str(columnNumber), ')\n(SET Gate Voltage: ', str(SETGateVoltage.get()), \
                            ' V, RESET Gate Voltage: ', str(RESETGateVoltage.get()), ', SET Voltage: ', str(FORMSETVoltage/1000),  \
                            ' V, \nRESET Voltage: ', str(RESETVoltage/1000), ' V, ', 'SET READ Voltage: ', \
                            str(SETREADVoltage.get()), ' V, \nRESET READ Voltage: ', str(RESETREADVoltage.get()), ' V)'])) #title

                if(len(cycleList) > maxSinglePointLimit): #if more cycles than visibly permitted based on maxSinglePointLimit

                    #get the (number of cycles / xAxisPointNumber) and iterate the x-axis points by that number
                    #for better visual clarity
                    ax.xaxis.set_major_locator(plt.MultipleLocator(math.floor(len(cycleList)/xAxisPointNumber)))
                    
                else: #otherwise, increment x-axis points by 1 since it should be acceptable according to user preference in maxSinglePointLimit
                    ax.xaxis.set_major_locator(plt.MultipleLocator(1))

                #perform tight_layout to avoid title cutoff
                plt.tight_layout()

                #maximize the plot window for better visual clarity (mostly to address legibility
                #for larger cycle number plots on the x-axis)
                manager = plt.get_current_fig_manager()
                manager.window.state('zoomed')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #CREATE PNG IMAGE OF PLOT AND SAVE TO CURRENT DIRECTORY

                currentTime = datetime.now() #get current datetime information
            
                #adjust datetime format to custom format
                #https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
                dateTimeFormatted = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                fileNameString = ''.join(['Pulse', orderString, 'SwitchPlot_Device', str(rowNumber), \
                                     '-', str(columnNumber), '_', toggledOhmsLawUnit.get(), '_', \
                                     dateTimeFormatted, '.png'])

                filePath = os.path.join(saveDirectory.get(), fileNameString)                 
                    
                fig.savefig(filePath, dpi = 300, bbox_inches = 'tight')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #if allowed to show ALL the plots (based on decided max plot limit)
                if(permitPlotDisplayFlag):
                    
                    #show ALL newly created plots
                    plt.show(block = False)

                else: #otherwise, clear the memory
                    fig.clear()

            else: #otherwise, cycle number <= 1, output message saying no plot is generated for this reason

                messageListBox.insert(END, 'Cycle Number <= 1, which is used for')
                messageListBox.insert(END, 'plot X-axis, no plot displayed')
                messageListBox.insert(END, '')

                return

        #----------------------------------------------------------------------------------

        else: #otherwise, IV mode, create the IV MODE Test specific plot output(s)

            #create plots based on IVTestState selection, as the IV state test has a unique
            #design involving both SET then RESET data within the same cycle

            #NOTE: boardOutOther contains the list of step voltages associated with each current value

            #NOTE: Jeelka wants ALL cycles on the IV mode plots

            if(len(boardOutStates) < 2): #if number of steps < 2, output message saying no plot is generated for this reason

                messageListBox.insert(END, 'Step Number <= 1, which is used for')
                messageListBox.insert(END, 'plot X-axis, no plot displayed')
                messageListBox.insert(END, '')

                return
            
            #if the FORM, SET or RESET modes (i.e. not IV State mode), proceed with normal logic
            if(not IVTestState.get() == 'IV'):

                #plot step voltage in x-axis against the outputted current in boardOutCurrent for the y-axis

                #create the plot with the expected information
                #creates figure INDEPENDENT OF OTHER FIGURES (to allow multiple plot outputs at once)
                #NOTE: the logic for the "num = 1, clear = True" as a means of addressing memory
                #issues with too many plots being opened was obtained from the following link:
                #https://stackoverflow.com/questions/28757348/how-to-clear-memory-completely-of-all-matplotlib-plots
                if(permitPlotDisplayFlag):
                    fig = plt.figure()
                else:
                    fig = plt.figure(num = 1, clear = True)

                #NOTE: since this is only for current, not resistance, sticking with LINE plot
                plt.xlabel('Step Voltage (mV)') #x-axis
                plt.ylabel('Current (uA)') #y-axis

                #create unique title string information based on (FORM/)SET or RESET state selection
                if(IVTestState.get() == 'RESET'):
                    READVoltageString = ' V, RESET READ Voltage: '
                    READVoltage = str(RESETREADVoltage.get())
                else:
                    READVoltageString = ' V, SET READ Voltage: '
                    READVoltage = str(SETREADVoltage.get())

                plt.title(''.join(['IV ', IVTestState.get(),' Test, Device: (R:', str(rowNumber), '/C:', str(columnNumber), \
                            ')\n(Gate Voltage: ', str(gateVoltage/1000), READVoltageString, READVoltage, \
                            ' V, \nNumber of Cycles: ', str(cycleNumber.get()), ', Steps per Cycle: ', \
                            str(int(len(boardOutStates)/cycleNumber.get())), ')'])) #title

                plt.plot(boardOutOther, boardOutCurrent) #create the line plot

                # - - - - - - - - - - - - - - - - - - - - - - -
                    
                ax = plt.gca()

                #get the step voltage increment amount and iterate the x-axis points by that number
                #for better visual clarity
                #NOTE: Seeing how this data will showcase ALL cycle outputs on the same plot, which
                #affects the inputted board data output length, this is incorporated into the division
                #process
                if(len(boardOutOther) > maxSinglePointLimit): #if more data points than visibly permitted based on maxSinglePointLimit
                    ax.xaxis.set_major_locator(plt.MultipleLocator(abs(boardOutOther[1] - \
                                                    boardOutOther[0]) * math.floor(len(boardOutOther)/\
                                                    (xAxisPointNumber * cycleNumber.get())))) #increment x-axis points by whole numbers equal to the step interval amount
                else:
                    ax.xaxis.set_major_locator(plt.MultipleLocator(abs(boardOutOther[1] - \
                                                    boardOutOther[0])))

                # - - - - - - - - - - - - - - - - - - - - - - -

                #perform tight_layout to avoid title cutoff
                plt.tight_layout()

                #maximize the plot window for better visual clarity (mostly to address legibility
                #for larger cycle number plots on the x-axis)
                manager = plt.get_current_fig_manager()
                manager.window.state('zoomed')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #CREATE PNG IMAGE OF PLOT AND SAVE TO CURRENT DIRECTORY

                currentTime = datetime.now() #get current datetime information
            
                #adjust datetime format to custom format
                #https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
                dateTimeFormattedFORMSET = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                fileNameString = ''.join(['IV', IVTestState.get(), 'Plot_Device', str(rowNumber), '-', str(columnNumber), \
                                     '_CycleNumber', str(cycleNumber.get()), '_stepNumber', \
                                     str(int(len(boardOutStates)/cycleNumber.get())), '_', dateTimeFormattedFORMSET, \
                                     '.png'])

                filePath = os.path.join(saveDirectory.get(), fileNameString)                 
                    
                fig.savefig(filePath, dpi = 300, bbox_inches = 'tight')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #if allowed to show ALL the plots (based on decided max plot limit)
                if(permitPlotDisplayFlag):
                    
                    #show ALL newly created plots
                    plt.show(block = False)

                else: #otherwise, clear the memory
                    fig.clear()

            else: #otherwise, IV state mode, proceed with plot creation with both SET and RESET data

                #plot step voltage in x-axis against the outputted current in boardOutCurrent for the y-axis

                #NOTE: for the IV state mode specifically, have BOTH THE SET AND RESET DATA ON THE SAME PLOT,
                #WITH ONE PLOT HAVING BOTH IN THE FIRST COORDINATE PLANE/QUADRANT AND THE OTHER PLOT HAVING
                #THE RESET DATA WITHIN THE THIRD COORDINATE PLANE/QUADRANT

                # - - - - - - - - - - - - - -

                #first, since the inputted data has an equal amount of SET data points as RESET, split the inputted
                #board data lists in half PER CYCLE, with whichever one being determined by the invertStates BooleanVar

                #first, split the data into (cycle # x 2) in order to get all the cycle SET and RESET data split,
                #THEN determine which data subsets are SET and which are RESET based on even and odd indices (even first
                #when starting at 0) (rising/falling/state strings are NOT necessary)
                #NOTE:
                splitByCycleBoardOutOtherArrays = np.array_split(boardOutOther, int(cycleNumber.get()) * 2)
                splitByCycleBoardOutOtherLists = [sub_array.tolist() for sub_array in splitByCycleBoardOutOtherArrays]
                splitByCycleBoardOutCurrentArrays = np.array_split(boardOutCurrent, int(cycleNumber.get()) * 2)
                splitByCycleBoardOutCurrentLists = [sub_array.tolist() for sub_array in splitByCycleBoardOutCurrentArrays]

                testStateArray = np.array_split(boardOutStates, int(cycleNumber.get()) * 2)
                testStateList = [sub_array.tolist() for sub_array in testStateArray]

                #create the lists to store all corresponding other and current data values based on their
                #SET or RESET listing (based on even or odd indices)
                SETIVStepListAllCyclesOther = []
                RESETIVStepListAllCyclesOther = []
                SETIVStepListAllCyclesCurrent = []
                RESETIVStepListAllCyclesCurrent = []
                
                if(not invertStates.get()): #if default order, first half of each cycle's data is SET (EVEN), the second half is RESET (ODD)

                    #get the "other" list data split by getting the two halves of data for each cycle's
                    #list within splitByCycleBoardOutOtherLists (split by cycle) based on even/odd indices
                    otherCycleStateCounter = 0
                    for otherList in splitByCycleBoardOutOtherLists:
                        if(otherCycleStateCounter % 2 == 0): #if even, SET
                            SETIVStepListAllCyclesOther.append(otherList) #first half
                        else: #otherwise, it's odd, RESET
                            RESETIVStepListAllCyclesOther.append(otherList) #second half
                        otherCycleStateCounter += 1

                    #get the current list data split by getting the even/odd numbered indices of data for each cycle's
                    #list within splitByCycleBoardOutCurrentLists (split by cycle)based on even/odd indices
                    currentCycleStateCounter = 0
                    for currentList in splitByCycleBoardOutCurrentLists:
                        if(currentCycleStateCounter % 2 == 0): #if even, SET
                            SETIVStepListAllCyclesCurrent.append(currentList) #first half
                        else: #otherwise, it's odd, RESET
                            RESETIVStepListAllCyclesCurrent.append(currentList) #second half
                        currentCycleStateCounter += 1

                else: #otherwise, inverted, first half of each cycle's data is RESET, the second half is SET

                    #get the "other" list data split by getting the two halves of data for each cycle's
                    #list within splitByCycleBoardOutOtherLists (split by cycle) based on even/odd indices
                    otherCycleStateCounter = 0
                    for otherList in splitByCycleBoardOutOtherLists:
                        if(otherCycleStateCounter % 2 == 1): #if odd, SET
                            SETIVStepListAllCyclesOther.append(otherList) #second half
                        else: #otherwise, it's even, RESET
                            RESETIVStepListAllCyclesOther.append(otherList) #first half
                        otherCycleStateCounter += 1

                    #get the current list data split by getting the even/odd numbered indices of data for each cycle's
                    #list within splitByCycleBoardOutCurrentLists (split by cycle)based on even/odd indices
                    currentCycleStateCounter = 0
                    for currentList in splitByCycleBoardOutCurrentLists:
                        if(currentCycleStateCounter % 2 == 1): #if odd, SET
                            SETIVStepListAllCyclesCurrent.append(currentList) #second half
                        else: #otherwise, it's even, RESET
                            RESETIVStepListAllCyclesCurrent.append(currentList) #first half
                        currentCycleStateCounter += 1

                # - - - - - - - - - - - - - -

                #create the FIRST (SET order doesn't really matter here) plot with the expected information

                #create the plot with the expected information
                #creates figure INDEPENDENT OF OTHER FIGURES (to allow multiple plot outputs at once)
                #NOTE: the logic for the "num = 1, clear = True" as a means of addressing memory
                #issues with too many plots being opened was obtained from the following link:
                #https://stackoverflow.com/questions/28757348/how-to-clear-memory-completely-of-all-matplotlib-plots
                if(permitPlotDisplayFlag):
                    fig = plt.figure()
                else:
                    fig = plt.figure(num = 1, clear = True)
                
                #NOTE: since this is only for current, not resistance, sticking with LINE plot
                plt.xlabel('Step Voltage (mV)') #x-axis
                plt.ylabel('Current (uA)') #y-axis

                if(invertStates.get()): #add string to showcase order for the sake of clarity
                    orderString = 'RESET-SET'
                else:
                    orderString = 'SET-RESET'

                plt.title(''.join(['IV State ', orderString, ' Test, Device: (R:', str(rowNumber), '/C:', \
                            str(columnNumber), ')\n(SET Gate Voltage: ', str(SETGateVoltage.get()), \
                            ' V, RESET Gate Voltage: ', str(RESETGateVoltage.get()), ' V, SET READ Voltage: ', \
                            str(SETREADVoltage.get()), ' V,\nRESET READ Voltage: ', str(RESETREADVoltage.get()), \
                            ' V, Number of Cycles: ', str(cycleNumber.get()), ', Steps per Cycle: ', \
                            str(int(len(SETIVStepListAllCyclesOther[0]))), ')'])) #title

                #create the line plots for the SET and RESET data in the first coordinate plane/quadrant

                #sift through all of the list indices and plot each cycle's data one by one
                for cycleIndex in range(len(SETIVStepListAllCyclesOther)):
                    plt.plot(SETIVStepListAllCyclesOther[cycleIndex], SETIVStepListAllCyclesCurrent[cycleIndex], \
                             color = 'red', label = 'SET IV (uA)', marker = 'p')

                    #add line that connects the two plots at the end of the SET data and the beginning of the
                    #RESET data plots
                    connectingOtherList = [SETIVStepListAllCyclesOther[cycleIndex][-1], \
                                             RESETIVStepListAllCyclesOther[cycleIndex][0]]
                    connectingCurrentList = [SETIVStepListAllCyclesCurrent[cycleIndex][-1], \
                                             RESETIVStepListAllCyclesCurrent[cycleIndex][0]]
                    plt.plot(connectingOtherList, connectingCurrentList, color = 'black')

                    plt.plot(RESETIVStepListAllCyclesOther[cycleIndex], RESETIVStepListAllCyclesCurrent[cycleIndex], \
                             color = 'blue', label = 'RESET IV (uA)', marker = '^')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #get handles and labels (to address the same labels getting added multiple times into
                #the legend due to the FOR loop above)
                handles, labels = plt.gca().get_legend_handles_labels()

                #create a dictionary to group handles by label
                by_label = dict(zip(labels, handles))

                #place the legend outside the plot using bbox_to_anchor
                plt.legend(by_label.values(), by_label.keys(), bbox_to_anchor = (1.05, 0.5), \
                           loc = 'center left', borderaxespad = 0., title = 'IV Current Legend', fontsize = '7')

                # - - - - - - - - - - - - - - - - - - - - - - -
                    
                ax = plt.gca()

                #get the step voltage increment amount and iterate the x-axis points by that number
                #for better visual clarity
                #NOTE: Seeing how this data will showcase ALL cycle outputs on the same plot, which
                #affects the inputted board data output length, this is incorporated into the division
                #process
                if(len(SETIVStepListAllCyclesOther[0]) > maxSinglePointLimit): #if more data points than visibly permitted based on maxSinglePointLimit
                    ax.xaxis.set_major_locator(plt.MultipleLocator(abs(SETIVStepListAllCyclesOther[0][1] - \
                                                    SETIVStepListAllCyclesOther[0][0]) * \
                                                    math.floor(len(boardOutOther)/\
                                                    (xAxisPointNumber * cycleNumber.get() * 2)))) #increment x-axis points by whole numbers equal to the step interval amount
                else:
                    ax.xaxis.set_major_locator(plt.MultipleLocator(abs(SETIVStepListAllCyclesOther[0][1] - \
                                                    SETIVStepListAllCyclesOther[0][0])))

                # - - - - - - - - - - - - - - - - - - - - - - -

                #perform tight_layout to avoid title cutoff
                plt.tight_layout()

                #maximize the plot window for better visual clarity (mostly to address legibility
                #for larger cycle number plots on the x-axis)
                manager = plt.get_current_fig_manager()
                manager.window.state('zoomed')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #CREATE PNG IMAGE OF PLOT AND SAVE TO CURRENT DIRECTORY

                currentTime = datetime.now() #get current datetime information
            
                #adjust datetime format to custom format
                #https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
                dateTimeFormattedFORMSET = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                fileNameString = ''.join(['IVState', orderString, 'Plot_Device', str(rowNumber), '-', str(columnNumber), \
                                     '_Cycles', str(cycleNumber.get()), '_stepNumber', \
                                     str(int(len(SETIVStepListAllCyclesOther[0]))), '_', dateTimeFormattedFORMSET, \
                                     '.png'])

                filePath = os.path.join(saveDirectory.get(), fileNameString)                 
                    
                fig.savefig(filePath, dpi = 300, bbox_inches = 'tight')

                #if allowed to show ALL the plots (based on decided max plot limit)
                if(permitPlotDisplayFlag):
                    
                    #show ALL newly created plots
                    plt.show(block = False)

                else: #otherwise, clear the memory
                    fig.clear()

                # - - - - - - - - - - - - - - - - - - - - - - -

                #create the SECOND (SET order doesn't really matter here) plot with the expected information
                #with the RESET data in the THIRD COORDINATE PLANE/QUADRANT by inverting all data point
                #x and y axes directions

                RESETIVStepListAllCyclesOtherNegative = [[-element for element in row] for \
                                                         row in RESETIVStepListAllCyclesOther]
                RESETIVStepListAllCyclesCurrentNegative = [[-element for element in row] for \
                                                           row in RESETIVStepListAllCyclesCurrent]
                
                #create the plot with the expected information
                #creates figure INDEPENDENT OF OTHER FIGURES (to allow multiple plot outputs at once)
                #NOTE: the logic for the "num = 1, clear = True" as a means of addressing memory
                #issues with too many plots being opened was obtained from the following link:
                #https://stackoverflow.com/questions/28757348/how-to-clear-memory-completely-of-all-matplotlib-plots
                if(permitPlotDisplayFlag):
                    fig = plt.figure()
                else:
                    fig = plt.figure(num = 1, clear = True)
                    
                #NOTE: since this is only for current, not resistance, sticking with LINE plot
                plt.xlabel('Step Voltage (mV)') #x-axis
                plt.ylabel('Current (uA)') #y-axis

                if(invertStates.get()): #add string to showcase order for the sake of clarity
                    orderString = 'RESET-SET'
                else:
                    orderString = 'SET-RESET'

                plt.title(''.join(['IV State ', orderString, ' Test, Negative RESET, Device: (R:', str(rowNumber), '/C:', \
                            str(columnNumber), ')\n(SET Gate Voltage: ', str(SETGateVoltage.get()), \
                            ' V, RESET Gate Voltage: ', str(RESETGateVoltage.get()), ' V, SET READ Voltage: ', \
                            str(SETREADVoltage.get()), ' V,\nRESET READ Voltage: ', str(RESETREADVoltage.get()), \
                            ' V, Number of Cycles: ', str(cycleNumber.get()), ', Steps per Cycle: ', \
                            str(int(len(SETIVStepListAllCyclesOther[0]))), ')'])) #title

                #create the line plots for the SET and RESET data in the first coordinate plane/quadrant

                #sift through all of the list indices and plot each cycle's data one by one
                for cycleIndex in range(len(SETIVStepListAllCyclesOther)):
                    plt.plot(SETIVStepListAllCyclesOther[cycleIndex], SETIVStepListAllCyclesCurrent[cycleIndex], \
                             color = 'red', label = 'SET IV (uA)', marker = 'p')

                    plt.plot(RESETIVStepListAllCyclesOtherNegative[cycleIndex], RESETIVStepListAllCyclesCurrentNegative[cycleIndex], \
                             color = 'blue', label = 'RESET IV (uA)', marker = '^')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #get handles and labels (to address the same labels getting added multiple times into
                #the legend due to the FOR loop above)
                handles, labels = plt.gca().get_legend_handles_labels()

                #create a dictionary to group handles by label
                by_label = dict(zip(labels, handles))

                #place the legend outside the plot using bbox_to_anchor
                plt.legend(by_label.values(), by_label.keys(), bbox_to_anchor = (1.05, 0.5), \
                           loc = 'center left', borderaxespad = 0., title = 'IV Current Legend', fontsize = '7')

                # - - - - - - - - - - - - - - - - - - - - - - -
                    
                ax = plt.gca()

                #get the step voltage increment amount and iterate the x-axis points by that number
                #for better visual clarity
                #NOTE: Seeing how this data will showcase ALL cycle outputs on the same plot, which
                #affects the inputted board data output length, this is incorporated into the division
                #process
                if(len(SETIVStepListAllCyclesOther[0]) > maxSinglePointLimit): #if more data points than visibly permitted based on maxSinglePointLimit
                    ax.xaxis.set_major_locator(plt.MultipleLocator((abs(SETIVStepListAllCyclesOther[0][1]) - \
                                                    abs(SETIVStepListAllCyclesOther[0][0])) * \
                                                    math.floor(len(boardOutOther)/\
                                                    (xAxisPointNumber * cycleNumber.get() * 2)))) #increment x-axis points by whole numbers equal to the step interval amount
                else:
                    ax.xaxis.set_major_locator(plt.MultipleLocator(abs(SETIVStepListAllCyclesOther[0][1] - \
                                                    SETIVStepListAllCyclesOther[0][0])))

                #seeing how this plot is expected to show two opposite coordinate planes/quadrants,
                #lines for where x and y are 0 are added for visual clarity
                ax.axvline(x = 0, color = 'k')
                ax.axhline(y = 0, color = 'k')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #perform tight_layout to avoid title cutoff
                plt.tight_layout()

                #maximize the plot window for better visual clarity (mostly to address legibility
                #for larger cycle number plots on the x-axis)
                manager = plt.get_current_fig_manager()
                manager.window.state('zoomed')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #CREATE PNG IMAGE OF PLOT AND SAVE TO CURRENT DIRECTORY

                currentTime = datetime.now() #get current datetime information
            
                #adjust datetime format to custom format
                #https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
                dateTimeFormattedFORMSET = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                fileNameString = ''.join(['IVState', orderString, 'PlotNegativeRESET_Device', str(rowNumber), '-', str(columnNumber), \
                                     '_Cycles', str(cycleNumber.get()), '_stepNumber', \
                                     str(int(len(SETIVStepListAllCyclesOther[0]))), '_', dateTimeFormattedFORMSET, \
                                     '.png'])

                filePath = os.path.join(saveDirectory.get(), fileNameString)                 
                    
                fig.savefig(filePath, dpi = 300, bbox_inches = 'tight')

                #if allowed to show ALL the plots (based on decided max plot limit)
                if(permitPlotDisplayFlag):
                    
                    #show ALL newly created plots
                    plt.show(block = False)

                else: #otherwise, clear the memory
                    fig.clear()

    #----------------------------------------------------------------------------------

    #at Dr. Cady's request, in the event the unique PULSE TEST heatmap generation checkbutton
    #is set upon this function's call, this expects ALL of the grid to be sifted through, so
    #generate a heatmap plot for all of the devices that were selected
    else:

        if(cycleNumber.get() == 1):

            #call "splitSetResetData" function to split up the SET/RESET data
            FORMSETIcurResList, RESETIcurResList, FORMSETChannelList, RESETChannelList = \
                            splitSetResetData(boardOutOther, boardOutCurrent, boardOutStates)

            #given how the inputted board data lists didn't keep their corresponding device information,
            #recreate the 2D grid, only this time have the devices that were not selected be given a
            #NaN value to remove them from the grid's heatmap entirely
            #OR, if hardCodeDevices is set, have the arrays have ONLY their respective data and NaNs
            #for the other state's data for ALL devices
            FORMSETHeatGridList = []
            RESETHeatGridList = []

            #for the sake of simplicity, have the hardCodeDevices grid already be formatted while
            #just setting the incorrect states based on button press (SET = not pressed, RESET = pressed)
            #below
            if(hardCodeDevices.get()):
                FORMSETHeatGridList = np.array(FORMSETIcurResList).reshape(cellGrid.returnRowNum(), \
                                                                           cellGrid.returnColumnNum()).tolist()
                RESETHeatGridList = np.array(RESETIcurResList).reshape(cellGrid.returnRowNum(), \
                                                                           cellGrid.returnColumnNum()).tolist()

            foundDeviceNum = 0 #used for counting for devices that were selected in one approach without hardCodeDevices
            
            for gridRow in range(cellGrid.returnRowNum()):

                recreatedGridRowSET = []
                recreatedGridRowRESET = []
                
                for gridCol in range(cellGrid.returnColumnNum()):
                    if(cellGrid.returnBooleans()[gridRow][gridCol]): #if the device was selected

                        #retrieve the data for that corresponding device and append to the
                        #SET and RESET two separate Excel files
                        #OR, in the case of the hard coded device/cell logic, get RESET ONLY data
                        if(hardCodeDevices.get()):
                            FORMSETHeatGridList[gridRow][gridCol] = np.nan
                        else:
                            recreatedGridRowSET.append(FORMSETIcurResList[foundDeviceNum])
                            recreatedGridRowRESET.append(RESETIcurResList[foundDeviceNum])

                        foundDeviceNum += 1

                    else: #otherwise, make an Excel cell NaN for the sake of moving to new spots OR get SET ONLY data

                        if(hardCodeDevices.get()):
                            RESETHeatGridList[gridRow][gridCol] = np.nan
                        else:
                            recreatedGridRowSET.append(np.nan)
                            recreatedGridRowRESET.append(np.nan)

                #append the full row's data to the list to be returned
                #before proceeding to the next row
                if(not hardCodeDevices.get()):
                    FORMSETHeatGridList.append(recreatedGridRowSET)
                    RESETHeatGridList.append(recreatedGridRowRESET)

            #for generating the heatmap, change the lists to Numpy arrays
            FORMSETHeatGridArray = np.array(FORMSETHeatGridList)
            RESETHeatGridArray = np.array(RESETHeatGridList)

            # - - - - - - - - - - - - - -

            #prepare string to showcase whether the data is the Current (uA) or Reistance (kOhm)
            #format as chosen upon pressing the 'Send' button
            if(toggledOhmsLawUnit.get() == 'uA'):
                outputUnit = 'Current (uA)'
            else:
                outputUnit = 'Resistance (kOhm)'

            # - - - - - - - - - - - - - -

            #at Jeelka's request, have the heatmap have both the SET and RESET data in the same heatmap
            #if using the hardCodeDevices setting, seeing how all devices are run with its state based
            #on which devices/cells were selected
            if(hardCodeDevices.get()):

                fig, ax = plt.subplots()
                RESETImage = ax.imshow(RESETHeatGridArray, cmap = 'autumn') #RESET plot (with selected device/cell format)
                FORMSETImage = ax.imshow(FORMSETHeatGridArray, cmap = 'cool') #SET plot (for "background" otherwise)
                ax.set_title(''.join([FORMSETStateString.get(), '/RESET Heatmap']))
                fig.colorbar(FORMSETImage, ax = ax, label = ''.join([FORMSETStateString.get(), ' ', \
                                                                     outputUnit]), orientation = 'vertical', pad = 0.05)
                fig.colorbar(RESETImage, ax = ax, label = ''.join(['RESET ', outputUnit]), \
                             orientation = 'vertical', pad = 0.15)

                # - - - - - - - - - - - - - - - - - - - - - - -

                #perform tight_layout to avoid title cutoff
                plt.tight_layout()

                #maximize the plot window for better visual clarity (mostly to address legibility
                #for larger cycle number plots on the x-axis)
                manager = plt.get_current_fig_manager()
                manager.window.state('zoomed')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #CREATE PNG IMAGE OF PLOT AND SAVE TO CURRENT DIRECTORY

                currentTime = datetime.now() #get current datetime information
            
                #adjust datetime format to custom format
                #https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
                dateTimeFormatted = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                fileNameString = ''.join([FORMSETStateString.get(), 'RESET_HardCodedHeatmap_', dateTimeFormatted, \
                                     '.png'])

                filePath = os.path.join(saveDirectory.get(), fileNameString)
                    
                fig.savefig(filePath, dpi = 300, bbox_inches = 'tight')

                fig.clear()

            else: #otherwise, not hard coded, proceed to create two separate heatmaps for SET and RESET specifically

                #FORM/SET heatmap
                figFORMSET, axFORMSET = plt.subplots()
                heatFORMSETImage = axFORMSET.imshow(FORMSETHeatGridArray, cmap = 'cool')
                axFORMSET.set_title(''.join([FORMSETStateString.get(), ' Heatmap']))
                figFORMSET.colorbar(heatFORMSETImage, ax = axFORMSET, label = outputUnit)

                figRESET, axRESET = plt.subplots()
                heatRESETImage = axRESET.imshow(RESETHeatGridArray, cmap = 'cool')
                axRESET.set_title('RESET Heatmap')
                figRESET.colorbar(heatRESETImage, ax = axRESET, label = outputUnit)

                # - - - - - - - - - - - - - - - - - - - - - - -

                #perform tight_layout to avoid title cutoff
                plt.tight_layout()

                #maximize the plot window for better visual clarity (mostly to address legibility
                #for larger cycle number plots on the x-axis)
                manager = plt.get_current_fig_manager()
                manager.window.state('zoomed')

                # - - - - - - - - - - - - - - - - - - - - - - -

                #CREATE PNG IMAGE OF PLOT AND SAVE TO CURRENT DIRECTORY

                currentTime = datetime.now() #get current datetime information
            
                #adjust datetime format to custom format
                #https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
                dateTimeFormattedFORMSET = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                fileNameStringFORMSET = ''.join([FORMSETStateString.get(), '_Heatmap_', dateTimeFormattedFORMSET, \
                                     '.png'])
                fileNameStringRESET = ''.join(['RESET_Heatmap_', dateTimeFormattedFORMSET, '.png'])

                filePathFORMSET = os.path.join(saveDirectory.get(), fileNameStringFORMSET)
                filePathRESET = os.path.join(saveDirectory.get(), fileNameStringRESET)
                    
                figFORMSET.savefig(filePathFORMSET, dpi = 300, bbox_inches = 'tight')
                figRESET.savefig(filePathRESET, dpi = 300, bbox_inches = 'tight')

                figFORMSET.clear()
                figRESET.clear()
        
        # - - - - - - - - - - - - - - -

        else:

            messageListBox.insert(END, 'Cycle Number != 1, current logic will')
            messageListBox.insert(END, 'not work for heatmap plotting')
            messageListBox.insert(END, '')

            return

#-------------------------------------------------------------------------

#function that will submit all parameters for checking and ordering
#(calls built-in "checkAndOrder" function) before sending the
#parameters to the PCB board (by calling the built-in "serialExecution"
#function)
def pressedSubmitData(cellGrid, expectedPortDriverSearch, saveFileNameString, csvDirectoryString, \
                    toggledOhmsLawUnit, csvControlVariable, showRunTime, cycleNumber, \
                    SETREADVoltage, RESETREADVoltage, byte3_GateVoltageMSB, byte4_GateVoltageLSB, byte5_FORMSETVoltageMSB, \
                    byte6_FORMSETVoltageLSB, byte7_FORMSETTimeMSB, byte8_FORMSETTimeLSB, byte9_sharedDelayPeriodMSB, \
                    byte10_sharedDelayPeriodLSB, byte11_FORMSETREADVoltageMSB, \
                    byte12_FORMSETREADVoltageLSB, byte13_FORMSETREADTimeMSB, byte14_FORMSETREADTimeLSB, byte15_RESETVoltageMSB, \
                    byte16_RESETVoltageLSB, byte17_RESETTimeMSB, byte18_RESETTimeLSB, \
                    byte19_RESETREADVoltageMSB, byte20_RESETREADVoltageLSB, \
                    byte21_RESETREADTimeMSB, byte22_RESETREADTimeLSB, \
                    byte25_CyclesNumberMSB, byte26_CyclesNumberLSB, \
                    byte27_StepNumberMSB, byte28_StepNumberLSB, byte29_modeState, \
                    messageListBox, IVTestState, FORMSETStateString, invertIVStates, \
                    maxStepVoltage, SETGateVoltage, RESETGateVoltage, chosenStepVoltage,\
                    stepVoltageDirection, createSavePlots, stepNumber, utilizeCurResRange, \
                    pulseTestRangeMin, pulseTestRangeMax, pulseTestRangeCycleCount, createHeatMap, hardCodeDevices):

    #if showRunTime is set, get run time information to display
    #once this program is completed
    if(showRunTime.get()): #if showRunTime Checkbutton checked/set to True

        #get starting time to find the difference between this time
        #and the final time at the end of this function
        startSendTime = datetime.now()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #clear text boxes should they already be populated with any text
    messageListBox.delete(0, END)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #if the button for this function is pressed without any interactive
    #grid cells/devices being set to true, no data will be submitted to
    #the PCB board, so a message will be sent to the message text box
    #telling the user to set a cell/device state to true

    #if all button booleans are False (when counting instances of True
    #in a 2D (or possibly 1D, this still works) list)
    if(sum(row.count(True) for row in cellGrid.returnBooleans()) == 0):
        messageListBox.insert(END, 'No cells/devices selected in the Grid window,')
        messageListBox.insert(END, 'choose at least one and Send again')

        #leave the function from here, as proceeding further isn't necessary without
        #any cells/devices to analyze
        return

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #if the "maxStepVoltage" or "stepVoltage" are NOT NUMERIC
    #OR ARE LESS THAN 0, no data will be submitted and this function
    #will end here, PULSE TEST ONLY
    if(byte29_modeState.get() == 'Pulse Test - Step'):

        try: #used to catch instance of empty/not numeric Entry widget input
            
            #if any unwanted conditions are met (i.e. <= 0)
            if(maxStepVoltage.get() <= 0):

                messageListBox.insert(END, 'Max Step Voltage <= 0')
                messageListBox.insert(END, 'Change these to meet these conditions')
                messageListBox.insert(END, 'and Send again')

                #leave the function from here, as proceeding further for the pulse test
                #isn't necessary
                return

            #ALS0, check if the selected state voltage to be tested already exceeds the
            #set maxStepVoltage
            if(chosenStepVoltage.get() == 'SET'): #if FORM/SET state selected, set currentStateVoltage to FORM/SET voltage
                currentStateVoltage = int(byte6_FORMSETVoltageLSB.get()) + (int(byte5_FORMSETVoltageMSB.get()) << 8)
            else: #otherwise, RESET state selected, set currentStateVoltage to RESET voltage
                currentStateVoltage = int(byte16_RESETVoltageLSB.get()) + (int(byte15_RESETVoltageMSB.get()) << 8)

            if(int(maxStepVoltage.get() * 1000) < currentStateVoltage): #NOTE: x1000 to convert from V to mV like the byte format
                messageListBox.insert(END, 'Max Step Voltage < Chosen State Voltage')
                messageListBox.insert(END, 'Change this to meet the expected conditions')
                messageListBox.insert(END, 'and Send again')

                #leave the function from here, as proceeding further for the pulse test
                #isn't necessary
                return
            
        except: #if either of the two Entry widgets are empty, throw exception

            messageListBox.insert(END, 'Max Step Voltage, or Chosen State')
            messageListBox.insert(END, 'Voltage inputs are not numeric')
            messageListBox.insert(END, 'Change these to meet these conditions')
            messageListBox.insert(END, 'and Send again')

            #leave the function from here, as proceeding further for the pulse test
            #isn't necessary
            return

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #at Jeelka's request, it's required that all inputted times NOT be
    #set to 0 (microseconds) FOR PULSE TEST(S) ONLY
    if(byte29_modeState.get() == 'Pulse Test' or byte29_modeState.get() == 'Pulse Test - Step' or \
       byte29_modeState.get() == 'Pulse Test - SET/RESET Switch'): #if one of the PULSE TESTS
        combinedFORMSETTime = int(byte8_FORMSETTimeLSB.get()) + (int(byte7_FORMSETTimeMSB.get()) << 8)
        combinedRESETTime = int(byte18_RESETTimeLSB.get()) + (int(byte17_RESETTimeMSB.get()) << 8)
        combinedFORMSETREADTime = int(byte14_FORMSETREADTimeLSB.get()) + (int(byte13_FORMSETREADTimeMSB.get()) << 8)
        combinedRESETREADTime = int(byte22_RESETREADTimeLSB.get()) + (int(byte21_RESETREADTimeMSB.get()) << 8)
        combinedDelayPeriod = int(byte10_sharedDelayPeriodLSB.get()) + (int(byte9_sharedDelayPeriodMSB.get()) << 8)

        if(any(timeVar <= 0 for timeVar in [combinedFORMSETTime, \
                combinedRESETTime, combinedFORMSETREADTime, \
                combinedRESETREADTime, combinedDelayPeriod]) and byte29_modeState.get() == \
                'Pulse Test'): #if ANY of the times <= 0 FOR PULSE TEST, leave this function now
            messageListBox.insert(END, 'ERROR: One of the PULSE TEST times set to <= 0,')
            messageListBox.insert(END, 'change and Send again')

            #leave the function from here, as proceeding further for the pulse test
            #isn't necessary
            return

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #throw an error should the number of steps be less than 1 for any modes
    #that utilize steps

    try:

       if((byte29_modeState.get() == 'Pulse Test - Step' or byte29_modeState.get() == 'IV Test') and \
          stepNumber.get() < 1):
       
           messageListBox.insert(END, 'ERROR: Step number < 1, change and Send again')
           #leave the function from here, as proceeding further for the pulse step/IV test
           #isn't necessary
           return

    except: #if this exception is reached, combinedStepNumber was not numeric, throw error

        messageListBox.insert(END, 'Step number is not numeric')
        messageListBox.insert(END, 'Change this to meet the expected conditions')
        messageListBox.insert(END, 'and Send again')

        #leave the function from here, as proceeding further for the pulse step/IV test
        #isn't necessary
        return

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #for the pulse test mode specifically, throw an error if any of the range
    #entries are not numeric, the range amounts are <0, the cycle number is <1,
    #the min and max are the same, or the min is greater

    try:
        if(byte29_modeState.get() == 'Pulse Test' and utilizeCurResRange.get()):

            if(pulseTestRangeMin.get() < 0 or pulseTestRangeMax.get() < 0):
                messageListBox.insert(END, 'ERROR: One of the ranges is < 0, change')
                messageListBox.insert(END, 'then send again')
                #leave the function from here, as proceeding further for the pulse step/IV test
                #isn't necessary
                return

            elif(pulseTestRangeCycleCount.get() < 1):
                messageListBox.insert(END, 'ERROR: Range Cycle Count < 1, change')
                messageListBox.insert(END, 'then send again')
                #leave the function from here, as proceeding further for the pulse step/IV test
                #isn't necessary
                return

            elif(pulseTestRangeMin.get() == pulseTestRangeMax.get()):
                messageListBox.insert(END, 'ERROR: Min = Max, no range, change')
                messageListBox.insert(END, 'then send again')
                #leave the function from here, as proceeding further for the pulse step/IV test
                #isn't necessary
                return

            elif(pulseTestRangeMin.get() > pulseTestRangeMax.get()):
                messageListBox.insert(END, 'ERROR: Min > Max, no range, change')
                messageListBox.insert(END, 'then send again')
                #leave the function from here, as proceeding further for the pulse step/IV test
                #isn't necessary
                return

    #if this exception is reached, at least one of the range values is not numeric,
    #throw error
    except:
        messageListBox.insert(END, 'One range entry value is not numeric')
        messageListBox.insert(END, 'Change this to meet the expected conditions')
        messageListBox.insert(END, 'and Send again')

        #leave the function from here, as proceeding further for the pulse step/IV test
        #isn't necessary
        return

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #for pulse test only, if the hard code device option is selected but the selected
    #state between FORM and SET is NOT SET (i.e. FORM), throw an error
    if(byte29_modeState.get() == 'Pulse Test' and hardCodeDevices.get() and \
       FORMSETStateString.get() == 'FORM'):
        messageListBox.insert(END, 'Hard coded devices need SET state values,')
        messageListBox.insert(END, 'change FORM state to SET and Send again')

        #leave the function from here, as proceeding further isn't necessary without
        #any cells/devices to analyze
        return

    elif(byte29_modeState.get() == 'Pulse Test' and hardCodeDevices.get() and \
         utilizeCurResRange.get()):
        messageListBox.insert(END, 'Hard coded devices currently do not work')
        messageListBox.insert(END, 'with Read-Write Verify range,')
        messageListBox.insert(END, 'uncheck and Send again')

        #leave the function from here, as proceeding further isn't necessary without
        #any cells/devices to analyze
        return

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #proceed to send byte sequence to PCB board
    #NOTE: The first and last two bytes of the inputByteList to be sent
    #are HARDCODED based on provided byte sequence in the "GUI
    #requirements doc", CHANGE IF NECESSARY
    #NOTE: Hex 0x55 = 85, Hex 0xAA = 170
    #NOTE: Current byte count (/inputByteList length) = 31

    #since byte29_modeState is a STRING, get the numerical equivalent (0 = Pulse Test,
    #1 = IV Test) as defined in the GUI requirements document
    modeStateNum = 0 #set to default "Pulse Test"
    if(byte29_modeState.get() == 'IV Test'): #if "IV Test", change modeStateNum to 1
        modeStateNum = 1

    #initialized lists to store "serialExecution" output(s)
    #boardOutOther for storing channel numbers for Pulse Test OR
    #voltage for IV test corresponding to the current outputs
    boardOutOther = []
    boardOutCurrent = [] #for storing electric current values
    boardOutStates = [] #for storing channel states

    #---------------------------------------------------------------------------

    #BASED ON INTERACTIVE GRID SET BUTTONS AT THE TIME THIS FUNCTION IS CALLED,
    #CALL BUILT IN "serialConnectAndExecute" FUNCTION ON ALL CELLS THAT ARE SET TO
    #BE UTILIZED

    #get interactive grid boolean logic
    cellGridBooleans = cellGrid.returnBooleans()

    #to avoid letting the user mess with the submitted button combinations while
    #the code is running, disable the ability to press the buttons while the code
    #is running
    cellGrid.changeGridButtonStates('disabled')

    #array for storing PULSE TEST STEP VOLTAGES (put here for all instances if needed
    #within the "arrangeGridExport" function but only filled for Pulse Test)
    pulseTestStepVoltagesList = []

    #for plotting purposes, get the combined amounts for the following voltage information
    gateVoltageCombinedBytes = int(byte4_GateVoltageLSB.get()) + (int(byte3_GateVoltageMSB.get()) << 8)
    FORMSETVoltageCombinedBytes = int(byte6_FORMSETVoltageLSB.get()) + (int(byte5_FORMSETVoltageMSB.get()) << 8)
    RESETVoltageCombinedBytes = int(byte16_RESETVoltageLSB.get()) + (int(byte15_RESETVoltageMSB.get()) << 8)

    # - - - - - - - - - - - - - - - - - -

    #calculate the number of devices BEFORE running any PCB/plotting related
    #logic further down

    deviceNum = 0

    #only bother with these lists and variables IF the range read-write verification
    #checkbox is clicked for the PULSE TEST
    rangeCycleIterations = IntVar()
    rangeCycleList = []
    rangeCycleDeviceList = []

    #only filled if a device doesn't find a value within
    #range within the cycle limit
    failedRangeCycleDataListOther = []
    failedRangeCycleDataListCurrent = []
    failedRangeCycleDataListStates = []
    failedDeviceList = []
    failedCycleMax = pulseTestRangeCycleCount.get()
    
    #iterate though entire grid using the two FOR loops based on the grid dimensions
    for row in range(cellGrid.returnRowNum()):
        for column in range(cellGrid.returnColumnNum()):

            #IF GRID BUTTON AT CURRENT ROW/COLUMN COMBINATION
            #IS SET TO TRUE WHEN PRESSED
            if(cellGridBooleans[row][column]):

                deviceNum += 1

                #for the PULSE TEST read-write verification mode, save the device
                #information here (or anywhere that does this cellGridBooleans check really)
                if(utilizeCurResRange.get()):
                    rangeCycleDeviceList.append([row + 1, column + 1])

    # - - - - - - - - - - - - - - - - - -

    #for the sake of avoiding taking up too much memory when generating the plots,
    #decide the maximum number of plots to be generated below without worrying about
    #closing/not showing the plots while the code runs
    #if the chosen maximum is exceeded, DO NOT SHOW THE PLOTS while the code runs
    maxPlotsPermitted = 20 #CHANGE IF NECESSARY
    permitPlotDisplayFlag = True

    #if too many plots are to be outputted, set flag telling the code not
    #to show all the plots, as it risks taking up too much memory and
    #crashing the code
    if(deviceNum > maxPlotsPermitted):

        permitPlotDisplayFlag = False

    # - - - - - - - - - - - - - - - - - -

    #iterate though entire grid using the two FOR loops based on the grid dimensions
    for row in range(cellGrid.returnRowNum()):
        for column in range(cellGrid.returnColumnNum()):

            #if the hard coded device option is selected, this will be for ALL DEVICES/CELLS
            #BUT the devices/cells NOT selected will be hard coded to hard coded SET state values
            #while the selected devices/cells will be hard coded to RESET state values
            #all hard coded SET and RESET values are hard coded HERE, CHANGE IF NECESSARY
            if(hardCodeDevices.get()):

                if(cellGridBooleans[row][column]): #if selected, hard code to chosen RESET values

                    inputByteList = [85, 170, 
                                    int(byte3_GateVoltageMSB.get()), int(byte4_GateVoltageLSB.get()), \
                                    int(byte5_FORMSETVoltageMSB.get()), int(byte6_FORMSETVoltageLSB.get()), \
                                    int(byte7_FORMSETTimeMSB.get()), int(byte8_FORMSETTimeLSB.get()), \
                                    int(byte9_sharedDelayPeriodMSB.get()), int(byte10_sharedDelayPeriodLSB.get()), 
                                    0, 0, \
                                    int(byte13_FORMSETREADTimeMSB.get()), int(byte14_FORMSETREADTimeLSB.get()), \
                                    int(byte15_RESETVoltageMSB.get()), int(byte16_RESETVoltageLSB.get()), \
                                    int(byte17_RESETTimeMSB.get()), int(byte18_RESETTimeLSB.get()), \
                                    int(byte19_RESETREADVoltageMSB.get()), int(byte20_RESETREADVoltageLSB.get()), \
                                    int(byte21_RESETREADTimeMSB.get()), int(byte22_RESETREADTimeLSB.get()), \
                                    column, row, int(byte25_CyclesNumberMSB.get()), \
                                    int(byte26_CyclesNumberLSB.get()), int(byte27_StepNumberMSB.get()), \
                                    int(byte28_StepNumberLSB.get()), modeStateNum, 170, 85]

                else: #otherwise, not selected, hard code to chosen SET values

                    inputByteList = [85, 170, \
                                        int(byte3_GateVoltageMSB.get()), int(byte4_GateVoltageLSB.get()), \
                                        int(byte5_FORMSETVoltageMSB.get()), int(byte6_FORMSETVoltageLSB.get()), \
                                        int(byte7_FORMSETTimeMSB.get()), int(byte8_FORMSETTimeLSB.get()), \
                                        int(byte9_sharedDelayPeriodMSB.get()), int(byte10_sharedDelayPeriodLSB.get()), \
                                        int(byte11_FORMSETREADVoltageMSB.get()), int(byte12_FORMSETREADVoltageLSB.get()), \
                                        int(byte13_FORMSETREADTimeMSB.get()), int(byte14_FORMSETREADTimeLSB.get()), 
                                        0, 0, \
                                        int(byte17_RESETTimeMSB.get()), int(byte18_RESETTimeLSB.get()), \
                                        0, 0, \
                                        int(byte21_RESETREADTimeMSB.get()), int(byte22_RESETREADTimeLSB.get()), \
                                        column, row, int(byte25_CyclesNumberMSB.get()), \
                                        int(byte26_CyclesNumberLSB.get()), int(byte27_StepNumberMSB.get()), \
                                        int(byte28_StepNumberLSB.get()), modeStateNum, 170, 85]

                #call "serialConnectAndExecute" for each input byte list
                boardOutOtherNew, boardOutCurrentNew, boardOutStatesNew = \
                                    serialConnectAndExecute(cycleNumber, inputByteList, \
                                        expectedPortDriverSearch, toggledOhmsLawUnit, \
                                        SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)

                #generate output plots by calling the "createPlots" function if createSavePlots checkbutton is selected
                if(createSavePlots.get() and not utilizeCurResRange):
                            
                    createPlots(boardOutOtherNew, boardOutCurrentNew, boardOutStatesNew, cellGrid, cycleNumber, \
                        toggledOhmsLawUnit, IVTestState, byte29_modeState, row + 1, column + 1, \
                        SETREADVoltage, RESETREADVoltage, FORMSETStateString, messageListBox, \
                        invertIVStates, stepVoltageDirection, maxStepVoltage, \
                        chosenStepVoltage, pulseTestStepVoltagesList, gateVoltageCombinedBytes, \
                        FORMSETVoltageCombinedBytes, RESETVoltageCombinedBytes, SETGateVoltage, \
                        RESETGateVoltage, csvDirectoryString, permitPlotDisplayFlag, False, hardCodeDevices)

                # - - - - - - - - - - - - - - - - - - -

                #"extend()" boardOutputs with both input byte list data
                boardOutOther += boardOutOtherNew
                boardOutCurrent += boardOutCurrentNew
                boardOutStates += boardOutStatesNew

            #IF GRID BUTTON AT CURRENT ROW/COLUMN COMBINATION
            #IS SET TO TRUE WHEN PRESSED
            if(cellGridBooleans[row][column] and not hardCodeDevices.get()):

                inputByteList = [85, 170, int(byte3_GateVoltageMSB.get()), int(byte4_GateVoltageLSB.get()), \
                     int(byte5_FORMSETVoltageMSB.get()), int(byte6_FORMSETVoltageLSB.get()), \
                     int(byte7_FORMSETTimeMSB.get()), int(byte8_FORMSETTimeLSB.get()), \
                     int(byte9_sharedDelayPeriodMSB.get()), int(byte10_sharedDelayPeriodLSB.get()), \
                     int(byte11_FORMSETREADVoltageMSB.get()), int(byte12_FORMSETREADVoltageLSB.get()), \
                     int(byte13_FORMSETREADTimeMSB.get()), int(byte14_FORMSETREADTimeLSB.get()), \
                     int(byte15_RESETVoltageMSB.get()), int(byte16_RESETVoltageLSB.get()), \
                     int(byte17_RESETTimeMSB.get()), int(byte18_RESETTimeLSB.get()), \
                     int(byte19_RESETREADVoltageMSB.get()), int(byte20_RESETREADVoltageLSB.get()), \
                     int(byte21_RESETREADTimeMSB.get()), int(byte22_RESETREADTimeLSB.get()), \
                     column, row, int(byte25_CyclesNumberMSB.get()), \
                     int(byte26_CyclesNumberLSB.get()), int(byte27_StepNumberMSB.get()), \
                     int(byte28_StepNumberLSB.get()), modeStateNum, 170, 85]

                #in the case of the "IV" state of IVTestState, it was required in the GUI
                #requirements documentation to have the SET and RESET instances done
                #SEPARATELY, so this will call the "serialConnectAndExecute" function
                #because of this, a new function involving calling the serialExecution function
                #was created, with the inputs being the differing SET/RESET inputByteList lists
                if((IVTestState.get() == 'IV' and byte29_modeState.get() == 'IV Test') or \
                   byte29_modeState.get() == 'Pulse Test - SET/RESET Switch'):

                    #initializing lists for looping purposes specific for the SET and RESET
                    #outputs per device for the Pulse SET/RESET Switch and IV State/IV Mode
                    #tests, as this is an approach to only have a single device's data be
                    #outputted when calling the "createPlots" function with these lists
                    #instead of the "boardOut" lists above with data of all devices
                    boardOutDeviceOther = []
                    boardOutDeviceCurrent = []
                    boardOutDeviceStates = []

                    #seeing how inputting any one state input with multiple cycles within the inputByteData
                    #leads to that state being cycled through multiple times DESPITE Jeelka INSISTING
                    #that the code should instead do SET THEN RESET PER CYCLE, the following logic
                    #where a loop for the set number of cycles must be done to have each of the two states
                    #be run PER CYCLE is incorporated
                    combinedByteCycleNumber = int(byte26_CyclesNumberLSB.get()) + (int(byte25_CyclesNumberMSB.get()) << 8)

                    #set the inputByteList cycle numbers to 1, seeing how the logic will apparently break
                    #when inputting multiple cycles of 1 state when Jeelka wants the two states to alternate per cycle
                    inputByteList[24] = 0 #MSB, byte25_CyclesNumberMSB
                    inputByteList[25] = 1 #LSB, byte26_CyclesNumberLSB

                    #create the inputByteList equivalents for ONLY SET and RESET specifically
                    #to run through the "serialConnectAndExecute" separately

                    #SET only version, initialize before making changes, CREATING COPY TO AVOID CHANGING ORIGINAL
                    SETOnlyInputByteList = inputByteList.copy()

                    #RESET only version, initialize before making changes, CREATING COPY TO AVOID CHANGING ORIGINAL
                    RESETOnlyInputByteList = inputByteList.copy()

                    #depending on the chosen mode, set the expected "opposite" state bytes to 0
                    if(byte29_modeState.get() == 'Pulse Test - SET/RESET Switch'):

                        #if SET/RESET Switch mode, only set opposite voltage and READ voltage
                        #to 0 (ignoring the times)
                        
                        SETOnlyInputByteList[14] = 0 #MSB, byte15_RESETVoltageMSB
                        SETOnlyInputByteList[15] = 0 #LSB, byte16_RESETVoltageLSB
                        SETOnlyInputByteList[18] = 0 #MSB, byte19_RESETREADVoltageMSB
                        SETOnlyInputByteList[19] = 0 #LSB, byte20_RESETREADVoltageLSB

                        RESETOnlyInputByteList[4] = 0 #MSB, byte5_FORMSETVoltageMSB
                        RESETOnlyInputByteList[5] = 0 #LSB, byte6_FORMSETVoltageLSB
                        RESETOnlyInputByteList[10] = 0 #MSB, byte11_FORMSETREADVoltageMSB
                        RESETOnlyInputByteList[11] = 0 #LSB, byte12_FORMSETREADVoltageLSB

                    else: #otherwise, IV test mode, IV state

                        #for SET only version of input byte list, set all RESET READ voltage
                        #and time bytes to 0 (set normal SET/RESET voltage/time bytes should
                        #already be 0)
                        SETOnlyInputByteList[18] = 0
                        SETOnlyInputByteList[19] = 0
                        SETOnlyInputByteList[20] = 0
                        SETOnlyInputByteList[21] = 0

                        #for RESET only version of input byte list, set all SET READ voltage
                        #and time bytes to 0 (set normal SET/RESET voltage/time bytes should
                        #already be 0)
                        RESETOnlyInputByteList[10] = 0
                        RESETOnlyInputByteList[11] = 0
                        RESETOnlyInputByteList[12] = 0
                        RESETOnlyInputByteList[13] = 0

                    # - - - - - - - - - - - - - - - - - -

                    #given the inclusion of different gate voltages for this specific IV test (mode) for SET and
                    #RESET respectively alongside the SET/RESET Switch test, set the bytes for gate voltage to
                    #these values for the respective duplicate lists before cycling through the bytes into the board
                    #Recall: byte3_GateVoltageMSB, byte4_GateVoltageLSB

                    #SETGateVoltage
                    MSBSETGateVoltHexInt, LSBSETGateVoltHexInt = \
                          twoByteComboSplit(int(SETGateVoltage.get() * 1000))
                    SETOnlyInputByteList[2] = MSBSETGateVoltHexInt
                    SETOnlyInputByteList[3] = LSBSETGateVoltHexInt
                    

                    #RESETGateVoltage
                    MSBRESETGateVoltHexInt, LSBRESETGateVoltHexInt = \
                          twoByteComboSplit(int(RESETGateVoltage.get() * 1000))
                    RESETOnlyInputByteList[2] = MSBRESETGateVoltHexInt
                    RESETOnlyInputByteList[3] = LSBRESETGateVoltHexInt

                    # - - - - - - - - - - - - - - - - - -

                    #loop through the two states calling the "serialConnectAndExecute" PER CYCLE
                    for cycleIteration in range(combinedByteCycleNumber):

                        #perform IV/SET-RESET test calls to "serialConnectAndExecute" with the ORDER being
                        #based on whether or not the invertIVStates boolean is set
                        #NOTE: The PCB board will have the possibility of changing behavior
                        #based on the order of inputted states, hence this logic's inclusion
                        if(invertIVStates.get()): #if INVERSE order

                            #call "serialConnectAndExecute" for each input byte list
                            RESETBoardOutOther, RESETBoardOutCurrent, RESETBoardOutStates = \
                                                serialConnectAndExecute(cycleNumber, RESETOnlyInputByteList, \
                                                    expectedPortDriverSearch, toggledOhmsLawUnit, \
                                                    SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)
                            
                            SETBoardOutOther, SETBoardOutCurrent, SETBoardOutStates = \
                                                serialConnectAndExecute(cycleNumber, SETOnlyInputByteList, \
                                                    expectedPortDriverSearch, toggledOhmsLawUnit, \
                                                    SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)

                            # - - - - - - - - - - - - - - - - - - -

                            #GIVEN HOW THE WHICHEVER STATE THAT ISN'T THE FOCUS OF ANY SPECIFIC "serialConnectAndExecute"
                            #CALL IS SET TO 0 BEFORE THIS MOMENT, THAT INFORMATION IS UNNECESSARY AND JUST "EXTENDS"
                            #THE LENGTH OF THE DATA WITH EMPTY RESULTS, SO REMOVE THE STATE THAT ISN'T THE FOCUS FROM
                            #EACH OF THE OUTPUTTED LISTS ABOVE (i.e. remove RESET data from SET output lists and vice versa)
                            #seeing how the data gets recombined further down to the expected format anyways, this shouldn't
                            #be an issue

                            #NOTE: since the current code works for SINGLE cycles, and the outputs are in the [SET, RESET] format
                            #for SET/RESET Switch respectively, then the code can simply remove the other index's data between the
                            #two, but the code below is incorporated for long term better coding practices with larger data outputs

                            if(byte29_modeState.get() == 'Pulse Test - SET/RESET Switch'):

                                #for SET ONLY list, get indices where RESET is found
                                RESETIndicesData = SETBoardOutStates.index('RESET')

                                #make sure that RESETIndicesList is a LIST, so if RESETIndicesData is returned as a single variable
                                #and not a list, save that variable within a list
                                if(not isinstance(RESETIndicesData, list)):
                                    RESETIndicesList = [RESETIndicesData]
                                else:
                                    RESETIndicesList = RESETIndicesData

                                #remove the RESET data from the SET lists
                                #NOTE: in REVERSE order to allow for deletion to not remove data and shift their indices when
                                #deleting in the normal order
                                for RESETIndex in sorted(RESETIndicesList, reverse = True):
                                    SETBoardOutOther.pop(RESETIndex)
                                    SETBoardOutCurrent.pop(RESETIndex)
                                    SETBoardOutStates.pop(RESETIndex)

                                # - - - - - - - - - -

                                #for RESET only list, get indices where SET is found
                                SETIndicesData = [RESETBoardOutStates.index('SET')]

                                #make sure that SETIndicesList is a LIST, so if SETIndicesData is returned as a single variable
                                #and not a list, save that variable within a list
                                if(not isinstance(SETIndicesData, list)):
                                    SETIndicesList = [SETIndicesData]
                                else:
                                    SETIndicesList = SETIndicesData

                                #remove the SET data from the RESET lists
                                #NOTE: in REVERSE order to allow for deletion to not remove data and shift their indices when
                                #deleting in the normal order
                                for SETIndex in sorted(SETIndicesList, reverse = True):
                                    RESETBoardOutOther.pop(SETIndex)
                                    RESETBoardOutCurrent.pop(SETIndex)
                                    RESETBoardOutStates.pop(SETIndex)

                            # - - - - - - - - - - - - - - - - - - -

                            #"extend()" boardOutputs with both input byte list data
                            #NOTE: given the previous deletion of "unnecessary data", REORDING
                            #THE DATA IF DONE FOR MORE THAN A SINGLE CYCLE WOULD HAVE BEEN REQUIRED,
                            #but since the current version is for one cycle and the order is addressed
                            #here, this isn't an issue, LONG TERM "OVERSIGHT" TO ADDRESS
                            boardOutDeviceOther += RESETBoardOutOther
                            boardOutDeviceOther += SETBoardOutOther
                            boardOutDeviceCurrent += RESETBoardOutCurrent
                            boardOutDeviceCurrent += SETBoardOutCurrent
                            boardOutDeviceStates += RESETBoardOutStates
                            boardOutDeviceStates += SETBoardOutStates
                            
                            boardOutOther += boardOutDeviceOther
                            boardOutCurrent += boardOutDeviceCurrent
                            boardOutStates += boardOutDeviceStates

                        else: #otherwise, DEFAULT IV/SET-RESET TEST ORDER

                            #call "serialConnectAndExecute" for each input byte list
                            SETBoardOutOther, SETBoardOutCurrent, SETBoardOutStates = \
                                                serialConnectAndExecute(cycleNumber, SETOnlyInputByteList, \
                                                    expectedPortDriverSearch, toggledOhmsLawUnit, \
                                                    SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)
                            
                            RESETBoardOutOther, RESETBoardOutCurrent, RESETBoardOutStates = \
                                                serialConnectAndExecute(cycleNumber, RESETOnlyInputByteList, \
                                                    expectedPortDriverSearch, toggledOhmsLawUnit, \
                                                    SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)

                            # - - - - - - - - - - - - - - - - - - -

                            #GIVEN HOW THE WHICHEVER STATE THAT ISN'T THE FOCUS OF ANY SPECIFIC "serialConnectAndExecute"
                            #CALL IS SET TO 0 BEFORE THIS MOMENT, THAT INFORMATION IS UNNECESSARY AND JUST "EXTENDS"
                            #THE LENGTH OF THE DATA WITH EMPTY RESULTS, SO REMOVE THE STATE THAT ISN'T THE FOCUS FROM
                            #EACH OF THE OUTPUTTED LISTS ABOVE (i.e. remove RESET data from SET output lists and vice versa)
                            #seeing how the data gets recombined further down to the expected format anyways, this shouldn't
                            #be an issue

                            #NOTE: since the current code works for SINGLE cycles, and the outputs are in the [SET, RESET] format
                            #for SET/RESET Switch respectively, then the code can simply remove the other index's data between the
                            #two, but the code below is incorporated for long term better coding practices with larger data outputs

                            if(byte29_modeState.get() == 'Pulse Test - SET/RESET Switch'):

                                #for SET ONLY list, get indices where RESET is found
                                RESETIndicesData = SETBoardOutStates.index('RESET')

                                #make sure that RESETIndicesList is a LIST, so if RESETIndicesData is returned as a single variable
                                #and not a list, save that variable within a list
                                if(not isinstance(RESETIndicesData, list)):
                                    RESETIndicesList = [RESETIndicesData]
                                else:
                                    RESETIndicesList = RESETIndicesData
                                    
                                for RESETIndex in sorted(RESETIndicesList, reverse = True): #remove the RESET data from the SET lists
                                    SETBoardOutOther.pop(RESETIndex)
                                    SETBoardOutCurrent.pop(RESETIndex)
                                    SETBoardOutStates.pop(RESETIndex)

                                # - - - - - - - - - -

                                #for RESET only list, get indices where SET is found
                                SETIndicesData = [RESETBoardOutStates.index('SET')]

                                #make sure that SETIndicesList is a LIST, so if SETIndicesData is returned as a single variable
                                #and not a list, save that variable within a list
                                if(not isinstance(SETIndicesData, list)):
                                    SETIndicesList = [SETIndicesData]
                                else:
                                    SETIndicesList = SETIndicesData
                               
                                for SETIndex in sorted(SETIndicesList, reverse = True): #remove the SET data from the RESET lists
                                    RESETBoardOutOther.pop(SETIndex)
                                    RESETBoardOutCurrent.pop(SETIndex)
                                    RESETBoardOutStates.pop(SETIndex)

                            # - - - - - - - - - - - - - - - - - - -

                            #"extend()" boardOutputs with both input byte list data
                            #NOTE: given the previous deletion of "unnecessary data", REORDING
                            #THE DATA IF DONE FOR MORE THAN A SINGLE CYCLE WOULD HAVE BEEN REQUIRED,
                            #but since the current version is for one cycle and the order is addressed
                            #here, this isn't an issue, LONG TERM "OVERSIGHT" TO ADDRESS
                            boardOutDeviceOther += SETBoardOutOther
                            boardOutDeviceOther += RESETBoardOutOther
                            boardOutDeviceCurrent += SETBoardOutCurrent
                            boardOutDeviceCurrent += RESETBoardOutCurrent
                            boardOutDeviceStates += SETBoardOutStates
                            boardOutDeviceStates += RESETBoardOutStates
                            
                            boardOutOther += boardOutDeviceOther
                            boardOutCurrent += boardOutDeviceCurrent
                            boardOutStates += boardOutDeviceStates

                    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

                    #generate output plots by calling the "createPlots" function if createSavePlots checkbutton is selected
                    if(createSavePlots.get()):

                        createPlots(boardOutDeviceOther, boardOutDeviceCurrent, boardOutDeviceStates, cellGrid, cycleNumber, \
                                toggledOhmsLawUnit, IVTestState, byte29_modeState, row + 1, column + 1, \
                                SETREADVoltage, RESETREADVoltage, FORMSETStateString, messageListBox, \
                                invertIVStates, stepVoltageDirection, maxStepVoltage, \
                                chosenStepVoltage, pulseTestStepVoltagesList, gateVoltageCombinedBytes, \
                                FORMSETVoltageCombinedBytes, RESETVoltageCombinedBytes, SETGateVoltage, \
                                RESETGateVoltage, csvDirectoryString, permitPlotDisplayFlag, False, hardCodeDevices)

                else: #otherwise, DEFAULT order (done by default for pulse test)

                    if(byte29_modeState.get() == 'Pulse Test - Step'): #if PULSE STEP TEST, PREPARE STEP LOGIC

                        #NOTE: the step voltage is meant to change the SET or RESET voltages, NOT THEIR
                        #READ VOLTAGE EQUIVALENTS
                        
                        if(chosenStepVoltage.get() == 'SET'): #if FORM/SET state selected, set currentStateVoltage to FORM/SET voltage
                            currentStateVoltage = int(byte6_FORMSETVoltageLSB.get()) + (int(byte5_FORMSETVoltageMSB.get()) << 8)

                        else: #otherwise, RESET state selected, set currentStateVoltage to RESET voltage
                            currentStateVoltage = int(byte16_RESETVoltageLSB.get()) + (int(byte15_RESETVoltageMSB.get()) << 8)

                        #since the inputted byte values are in mV, convert max step and step
                        #voltages to mV
                        maxVoltagemV = int(maxStepVoltage.get() * 1000)
                        voltageMVByStepNumber = int((abs(maxVoltagemV - currentStateVoltage) / stepNumber.get()))

                        #for rising and falling exclusively, Jeelka wants the steps to be done per cycle, so the
                        #following conditional logic is to set up another loop logic per cycle
                        if(stepVoltageDirection.get() == 'Rising' or stepVoltageDirection.get() == 'Falling'):

                            #loop through each cycle, completing each step sequence per cycle before proceeding
                            #to the next one (currently ignoring the cycle number input for the inputByteList)

                            combinedByteCycleNumber = int(byte26_CyclesNumberLSB.get()) + (int(byte25_CyclesNumberMSB.get()) << 8)

                            #set the inputByteList cycle numbers to 1, seeing how the logic will apparently break
                            #when inputting multiple cycles of 1 state whe  step voltage to iterate per cycle
                            inputByteList[24] = 0 #MSB, byte25_CyclesNumberMSB
                            inputByteList[25] = 1 #LSB, byte26_CyclesNumberLSB

                            startingStateVoltage = currentStateVoltage #saving to reset per cycle
                            
                            #reset the changing voltages at the start of each cycle
                            #NOTE: All voltage values to be inputted to the PCB are in
                            #MILLIVOLTS, so perform the conversion during the byte
                            #splitting process (1000 millivolts = 1 volt)
                            #NOTE: For the sake of all byte information being in "Int" format,
                            #convert the floats to integers post multiplication
                            MSBStateVoltHexInt, LSBStateVoltHexInt = \
                                               twoByteComboSplit(startingStateVoltage)

                            if(chosenStepVoltage.get() == 'SET'):
                                inputByteList[4] = int(MSBStateVoltHexInt) #byte5_FORMSETVoltageMSB
                                inputByteList[5] = int(LSBStateVoltHexInt) #byte6_FORMSETVoltageLSB
                            else:
                                inputByteList[14] = int(MSBStateVoltHexInt) #byte15_RESETVoltageMSB
                                inputByteList[15] = int(LSBStateVoltHexInt) #byte16_RESETVoltageLSB

                            #loop through the selected set mode calling the "serialConnectAndExecute" PER CYCLE
                            for cycleIteration in range(combinedByteCycleNumber):

                                currentStateVoltage = startingStateVoltage + voltageMVByStepNumber #reset for each cycle iteration

                                #DEPENDING ON stepVoltageDirection CHOICE, HAVE THE WHILE LOOP LOGIC INCREMENT OR
                                #DECREMENT RESPECTIVELY TO SIMULATE THE STEP VOLTAGE LOGIC

                                #if rising logic is selected, prepare the WHILE loop logic for incrementing each step voltage
                                if(stepVoltageDirection.get() == 'Rising'):

                                    #continue to call the board through "serialConnectAndExecute" function
                                    #while the selected voltage is still below the maximum voltage with each
                                    #incremental step voltage increase
                                    while(currentStateVoltage <= maxVoltagemV):

                                        #call "serialConnectAndExecute" for each input byte list
                                        boardOutOtherNew, boardOutCurrentNew, boardOutStatesNew = \
                                                            serialConnectAndExecute(cycleNumber, inputByteList, \
                                                                expectedPortDriverSearch, toggledOhmsLawUnit, \
                                                                SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)

                                        # - - - - - - - - - - - - - - - - - - -
                                        
                                        #"extend()" boardOutputs with both input byte list data
                                        boardOutOther += boardOutOtherNew
                                        boardOutCurrent += boardOutCurrentNew
                                        boardOutStates += boardOutStatesNew

                                        #save "currentFORMSETREADVoltage" in the "pulseTestStepVoltagesList"
                                        pulseTestStepVoltagesList += [currentStateVoltage]

                                        #set the FORM/SET READ voltage to the next value in the WHILE loop increment
                                        currentStateVoltage += voltageMVByStepNumber

                                        #depending on the selected chosenStepVoltage state, change the inputByteList
                                        #bytes corresponding to the chosen voltage using the adjusted currentStateVoltage

                                        #NOTE: All voltage values to be inputted to the PCB are in
                                        #MILLIVOLTS, so perform the conversion during the byte
                                        #splitting process (1000 millivolts = 1 volt)
                                        #NOTE: For the sake of all byte information being in "Int" format,
                                        #convert the floats to integers post multiplication
                                        MSBStateVoltHexInt, LSBStateVoltHexInt = \
                                                           twoByteComboSplit(currentStateVoltage)

                                        if(chosenStepVoltage.get() == 'SET'):
                                            inputByteList[4] = int(MSBStateVoltHexInt) #byte5_FORMSETVoltageMSB
                                            inputByteList[5] = int(LSBStateVoltHexInt) #byte6_FORMSETVoltageLSB
                                        else:
                                            inputByteList[14] = int(MSBStateVoltHexInt) #byte15_RESETVoltageMSB
                                            inputByteList[15] = int(LSBStateVoltHexInt) #byte16_RESETVoltageLSB

                                #if falling logic is selected, prepare the WHILE loop logic for decrementing each step voltage
                                elif(stepVoltageDirection.get() == 'Falling'):

                                    #save the previous byte state voltage information as well as starting the upcoming
                                    #WHILE loop at the MAXIMUM selected step voltage
                                   
                                    minStateVoltage = currentStateVoltage #save byte voltage information as separate variable 
                                    currentStateVoltage = maxVoltagemV - voltageMVByStepNumber

                                    #continue to call the board through "serialConnectAndExecute" function
                                    #while the current voltage is still above the minimum selected voltage with each
                                    #decremental step voltage decrease
                                    while(currentStateVoltage >= minStateVoltage):

                                        #call "serialConnectAndExecute" for each input byte list
                                        boardOutOtherNew, boardOutCurrentNew, boardOutStatesNew = \
                                                            serialConnectAndExecute(cycleNumber, inputByteList, \
                                                                expectedPortDriverSearch, toggledOhmsLawUnit, \
                                                                SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)

                                        # - - - - - - - - - - - - - - - - - - -
                                        
                                        #"extend()" boardOutputs with both input byte list data
                                        boardOutOther += boardOutOtherNew
                                        boardOutCurrent += boardOutCurrentNew
                                        boardOutStates += boardOutStatesNew

                                        #save "currentFORMSETREADVoltage" in the "pulseTestStepVoltagesList"
                                        pulseTestStepVoltagesList += [currentStateVoltage]

                                        #set the FORM/SET READ voltage to the next value in the WHILE loop decrement
                                        currentStateVoltage -= voltageMVByStepNumber

                                        #depending on the selected chosenStepVoltage state, change the inputByteList
                                        #bytes corresponding to the chosen voltage using the adjusted currentStateVoltage

                                        #NOTE: All voltage values to be inputted to the PCB are in
                                        #MILLIVOLTS, so perform the conversion during the byte
                                        #splitting process (1000 millivolts = 1 volt)
                                        #NOTE: For the sake of all byte information being in "Int" format,
                                        #convert the floats to integers post multiplication
                                        MSBStateVoltHexInt, LSBStateVoltHexInt = \
                                                           twoByteComboSplit(currentStateVoltage)

                                        if(chosenStepVoltage.get() == 'SET'):
                                            inputByteList[4] = int(MSBStateVoltHexInt) #byte5_FORMSETVoltageMSB
                                            inputByteList[5] = int(LSBStateVoltHexInt) #byte6_FORMSETVoltageLSB
                                        else:
                                            inputByteList[14] = int(MSBStateVoltHexInt) #byte15_RESETVoltageMSB
                                            inputByteList[15] = int(LSBStateVoltHexInt) #byte16_RESETVoltageLSB

                        else: #otherwise, "Rise then Fall" case

                            #NOTE: The logic expects that the rising and falling step voltage instances be done
                            #in succession PER CYCLE, NOT all cycles of one direction back to back, so the byte
                            #information for the cycle number will be set to 1 while the two directional runs
                            #are done in order for (cycle number) loops

                            #seeing how inputting any one state input with multiple cycles within the inputByteData
                            #leads to that state being cycled through multiple times, the following logic
                            #where a loop for the set number of cycles must be done to have each of the two states
                            #be run PER CYCLE is incorporated
                            combinedByteCycleNumber = int(byte26_CyclesNumberLSB.get()) + (int(byte25_CyclesNumberMSB.get()) << 8)

                            #set the inputByteList cycle numbers to 1, seeing how the logic will apparently break
                            #when inputting multiple cycles of 1 state when Jeelka wants the two states to alternate per cycle
                            inputByteList[24] = 0 #MSB, byte25_CyclesNumberMSB
                            inputByteList[25] = 1 #LSB, byte26_CyclesNumberLSB

                            minStateVoltage = currentStateVoltage #save byte voltage information as separate variable for falling post rising

                            # - - - - - - - - - - - - - - - - - -

                            #loop through the two states calling the "serialConnectAndExecute" PER CYCLE
                            for cycleIteration in range(combinedByteCycleNumber):

                                currentStateVoltage = minStateVoltage + voltageMVByStepNumber #reset upon each new cycle iteration

                                #continue to call the board through "serialConnectAndExecute" function
                                #while the selected voltage is still below the maximum voltage with each
                                #incremental step voltage increase
                                while(currentStateVoltage <= maxVoltagemV):

                                    #call "serialConnectAndExecute" for each input byte list
                                    boardOutOtherNew, boardOutCurrentNew, boardOutStatesNew = \
                                                        serialConnectAndExecute(cycleNumber, inputByteList, \
                                                            expectedPortDriverSearch, toggledOhmsLawUnit, \
                                                            SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)

                                    # - - - - - - - - - - - - - - - - - - -
                                    
                                    #"extend()" boardOutputs with both input byte list data
                                    boardOutOther += boardOutOtherNew
                                    boardOutCurrent += boardOutCurrentNew
                                    boardOutStates += boardOutStatesNew

                                    #save "currentFORMSETREADVoltage" in the "pulseTestStepVoltagesList"
                                    pulseTestStepVoltagesList += [currentStateVoltage]

                                    #set the FORM/SET READ voltage to the next value in the WHILE loop increment
                                    currentStateVoltage += voltageMVByStepNumber

                                    #depending on the selected chosenStepVoltage state, change the inputByteList
                                    #bytes corresponding to the chosen voltage using the adjusted currentStateVoltage

                                    #NOTE: All voltage values to be inputted to the PCB are in
                                    #MILLIVOLTS, so perform the conversion during the byte
                                    #splitting process (1000 millivolts = 1 volt)
                                    #NOTE: For the sake of all byte information being in "Int" format,
                                    #convert the floats to integers post multiplication
                                    MSBStateVoltHexInt, LSBStateVoltHexInt = \
                                                       twoByteComboSplit(currentStateVoltage)

                                    if(chosenStepVoltage.get() == 'SET'):
                                        inputByteList[4] = int(MSBStateVoltHexInt) #byte5_FORMSETVoltageMSB
                                        inputByteList[5] = int(LSBStateVoltHexInt) #byte6_FORMSETVoltageLSB
                                    else:
                                        inputByteList[14] = int(MSBStateVoltHexInt) #byte15_RESETVoltageMSB
                                        inputByteList[15] = int(LSBStateVoltHexInt) #byte16_RESETVoltageLSB

                                # - - - - - - - - -

                                #proceed to perform falling step process after the rising step process above is finished

                                currentStateVoltage = maxVoltagemV - voltageMVByStepNumber

                                #NOTE: All voltage values to be inputted to the PCB are in
                                #MILLIVOLTS, so perform the conversion during the byte
                                #splitting process (1000 millivolts = 1 volt)
                                #NOTE: For the sake of all byte information being in "Int" format,
                                #convert the floats to integers post multiplication
                                MSBStateVoltHexInt, LSBStateVoltHexInt = \
                                                   twoByteComboSplit(currentStateVoltage)

                                if(chosenStepVoltage.get() == 'SET'):
                                    inputByteList[4] = int(MSBStateVoltHexInt) #byte5_FORMSETVoltageMSB
                                    inputByteList[5] = int(LSBStateVoltHexInt) #byte6_FORMSETVoltageLSB
                                else:
                                    inputByteList[14] = int(MSBStateVoltHexInt) #byte15_RESETVoltageMSB
                                    inputByteList[15] = int(LSBStateVoltHexInt) #byte16_RESETVoltageLSB

                                #continue to call the board through "serialConnectAndExecute" function
                                #while the current voltage is still above the minimum selected voltage with each
                                #decremental step voltage decrease
                                while(currentStateVoltage >= minStateVoltage):

                                    #call "serialConnectAndExecute" for each input byte list
                                    boardOutOtherNew, boardOutCurrentNew, boardOutStatesNew = \
                                                        serialConnectAndExecute(cycleNumber, inputByteList, \
                                                            expectedPortDriverSearch, toggledOhmsLawUnit, \
                                                            SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)

                                    # - - - - - - - - - - - - - - - - - - -
                                    
                                    #"extend()" boardOutputs with both input byte list data
                                    boardOutOther += boardOutOtherNew
                                    boardOutCurrent += boardOutCurrentNew
                                    boardOutStates += boardOutStatesNew

                                    #save "currentFORMSETREADVoltage" in the "pulseTestStepVoltagesList"
                                    pulseTestStepVoltagesList += [currentStateVoltage]

                                    #set the FORM/SET READ voltage to the next value in the WHILE loop decrement
                                    currentStateVoltage -= voltageMVByStepNumber

                                    #depending on the selected chosenStepVoltage state, change the inputByteList
                                    #bytes corresponding to the chosen voltage using the adjusted currentStateVoltage

                                    #NOTE: All voltage values to be inputted to the PCB are in
                                    #MILLIVOLTS, so perform the conversion during the byte
                                    #splitting process (1000 millivolts = 1 volt)
                                    #NOTE: For the sake of all byte information being in "Int" format,
                                    #convert the floats to integers post multiplication
                                    MSBStateVoltHexInt, LSBStateVoltHexInt = \
                                                       twoByteComboSplit(currentStateVoltage)

                                    if(chosenStepVoltage.get() == 'SET'):
                                        inputByteList[4] = int(MSBStateVoltHexInt) #byte5_FORMSETVoltageMSB
                                        inputByteList[5] = int(LSBStateVoltHexInt) #byte6_FORMSETVoltageLSB
                                    else:
                                        inputByteList[14] = int(MSBStateVoltHexInt) #byte15_RESETVoltageMSB
                                        inputByteList[15] = int(LSBStateVoltHexInt) #byte16_RESETVoltageLSB

                    else: #otherwise, NORMAL Pulse test or other non-IV STATE IV test, proceed normally

                        #at Jeelka's request, the PULSE TEST mode does have a unique test design
                        #involving counting the number of iteration instances within a selectable range
                        #to find how long it takes for an output range to be found per device
                        #NOTE: perform the following unique Pulse Test method if the Pulse Test mode
                        #is selected AND the utilizeCurResRange boolean is set
                        if(byte29_modeState.get() == 'Pulse Test' and utilizeCurResRange.get()):

                            #create lists to be appended to check the most recent outputs of the
                            #serialConnectAndExecute function without losing the data between
                            #instances
                            cycledDataOther = []
                            cycledDataCurrent = []
                            cycledDataStates = []

                            #with the cycling logic being dependent on the pulseTestRangeCycleCount,
                            #loop pulseTestRangeCycleCount number of times with the cycle number
                            #of each inputByteList being set to 1 for each serialConnectAndExecute call
                            inputByteList[24] = 0 #byte25_CyclesNumberMSB
                            inputByteList[25] = 1 #byte26_CyclesNumberLSB

                            rangeCycleIterations.set(0) #initialize iteration counter for messaging purposes

                            #loop a maximum of pulseTestRangeCycleCount number of times to see if
                            #a final value within range is found
                            for rangeCycleIndex in range(pulseTestRangeCycleCount.get()):

                                #call "serialConnectAndExecute" for each input byte list
                                boardOutOtherNew, boardOutCurrentNew, boardOutStatesNew = \
                                                  serialConnectAndExecute(cycleNumber, inputByteList, \
                                                    expectedPortDriverSearch, toggledOhmsLawUnit, \
                                                    SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)

                                #append the data of each cycle to their corresponding lists above
                                cycledDataOther += boardOutOtherNew
                                cycledDataCurrent += boardOutCurrentNew
                                cycledDataStates += boardOutStatesNew

                                #check the final (RESET) value that was appended to cycledDataCurrent,
                                #seeing how this holds the current/resistance values that the range
                                #logic is built around
                                #if within range, break the FOR loop, as a value to end the search
                                #has been found
                                RESETRangeCycleCurrentVal = cycledDataCurrent[-1]

                                if(RESETRangeCycleCurrentVal >= pulseTestRangeMin.get() and \
                                   RESETRangeCycleCurrentVal <= pulseTestRangeMax.get()):

                                    #ending found, save the number of iterations to meet the range requirement
                                    rangeCycleIterations.set(rangeCycleIndex + 1)
                                    rangeCycleList.append(rangeCycleIterations.get())
                                    break

                                #as an extra precaution, simply return a message stating that the attempt
                                #to find a RESET output value within the provided range failed if the
                                #final cycle doesn't break before this moment
                                #ALSO, at Jeelka's request, the failed data will be saved for exporting
                                #purposes only
                                if(rangeCycleIndex == pulseTestRangeCycleCount.get() - 1):

                                    '''
                                    messageListBox.insert(END, ''.join(['No RESET value in range for device ', \
                                                                     str(row + 1), '/', str(column + 1)]))
                                    '''
                                    
                                    rangeCycleList.append(0)
                                    boardOutOther.append([])
                                    boardOutCurrent.append([])
                                    boardOutStates.append([])

                                    #save the failed data information for the ranged cycle search
                                    failedRangeCycleDataListOther += cycledDataOther
                                    failedRangeCycleDataListCurrent += cycledDataCurrent
                                    failedRangeCycleDataListStates += cycledDataStates
                                    failedDeviceList.append([row + 1, column + 1])

                            #ONLY bother saving the device's data if the rangeCycleIterations number is found, i.e. not 0
                            if(rangeCycleIterations.get() > 0):

                                #save the cycled data regardless of range successes/failures
                                boardOutOther.append(cycledDataOther)
                                boardOutCurrent.append(cycledDataCurrent)
                                boardOutStates.append(cycledDataStates)

                                '''
                                messageListBox.insert(END, ''.join(['It took ', str(rangeCycleIterations.get()), ' iterations to']))
                                messageListBox.insert(END, ''.join(['finish for device ', str(row + 1), '/', str(column + 1)]))
                                messageListBox.insert(END, '')
                                '''

                                #generate output plots by calling the "createPlots" function if createSavePlots checkbutton is selected
                                if(createSavePlots.get() and rangeCycleIterations.get() > 1):
                                            
                                    createPlots(cycledDataOther, cycledDataCurrent, cycledDataStates, cellGrid, rangeCycleIterations, \
                                        toggledOhmsLawUnit, IVTestState, byte29_modeState, row + 1, column + 1, \
                                        SETREADVoltage, RESETREADVoltage, FORMSETStateString, messageListBox, \
                                        invertIVStates, stepVoltageDirection, maxStepVoltage, \
                                        chosenStepVoltage, pulseTestStepVoltagesList, gateVoltageCombinedBytes, \
                                        FORMSETVoltageCombinedBytes, RESETVoltageCombinedBytes, SETGateVoltage, \
                                        RESETGateVoltage, csvDirectoryString, permitPlotDisplayFlag, False, hardCodeDevices)

                                elif(createSavePlots.get() and rangeCycleIterations.get() == 1):
                                    messageListBox.insert(END, 'Only one cycle/iteration, cannot create plot')
                                    messageListBox.insert(END, '')

                        else: #otherwise, proceed normally for either the other Pulse Test case or non_IV State IV Test

                            #call "serialConnectAndExecute" for each input byte list
                            boardOutOtherNew, boardOutCurrentNew, boardOutStatesNew = \
                                                serialConnectAndExecute(cycleNumber, inputByteList, \
                                                    expectedPortDriverSearch, toggledOhmsLawUnit, \
                                                    SETREADVoltage, RESETREADVoltage, messageListBox, IVTestState)

                            # - - - - - - - - - - - - - - - - - - -

                            #generate output plots by calling the "createPlots" function if createSavePlots checkbutton is selected
                            #ONLY DO THIS FOR NORMAL PULSE TEST HERE, AS NON-IV STATE IV TEST PLOTS ARE DONE FURTHER DOWN
                            if(createSavePlots.get() and byte29_modeState.get() == 'Pulse Test' and not utilizeCurResRange):
                                        
                                createPlots(boardOutOtherNew, boardOutCurrentNew, boardOutStatesNew, cellGrid, cycleNumber, \
                                    toggledOhmsLawUnit, IVTestState, byte29_modeState, row + 1, column + 1, \
                                    SETREADVoltage, RESETREADVoltage, FORMSETStateString, messageListBox, \
                                    invertIVStates, stepVoltageDirection, maxStepVoltage, \
                                    chosenStepVoltage, pulseTestStepVoltagesList, gateVoltageCombinedBytes, \
                                    FORMSETVoltageCombinedBytes, RESETVoltageCombinedBytes, SETGateVoltage, \
                                    RESETGateVoltage, csvDirectoryString, permitPlotDisplayFlag, False, hardCodeDevices)

                            # - - - - - - - - - - - - - - - - - - -

                            #"extend()" boardOutputs with both input byte list data
                            boardOutOther += boardOutOtherNew
                            boardOutCurrent += boardOutCurrentNew
                            boardOutStates += boardOutStatesNew

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #for plotting purposes, the Pulse Step and "NON-IV TEST" IV Mode Tests need
    #to have their device information accumulated all together BEFORE the
    #"createPlots" function is called, so call here after all devices are
    #sifted through
    if((byte29_modeState.get() == 'Pulse Test - Step' or (byte29_modeState.get() == 'IV Test' and \
        not IVTestState.get() == 'IV')) and createSavePlots.get()):

        #if Pulse Step Test, call "createPlots" for each individual device and have the board data
        #be separated by device at this point
        #iterate though entire grid using the two FOR loops based on the grid dimensions
        #RECALL: deviceNum variable for total number of devices found
        currentDevice = 0

        #split data before createPlots function call
        #NOTE: ORDER IN WHICH DEVICES ARE FOUND IS THE SAME AS ABOVE WHEN THE DATA WAS INPUT INTO
        #THE BOARD
        splitByDeviceBoardOutOtherArrays = np.array_split(boardOutOther, deviceNum)
        splitByDeviceBoardOutOtherLists = [sub_array.tolist() for sub_array in splitByDeviceBoardOutOtherArrays]

        splitByDeviceBoardOutCurrentArrays = np.array_split(boardOutCurrent, deviceNum)
        splitByDeviceBoardOutCurrentLists = [sub_array.tolist() for sub_array in splitByDeviceBoardOutCurrentArrays]

        splitByDeviceBoardOutStatesArrays = np.array_split(boardOutStates, deviceNum)
        splitByDeviceBoardOutStatesLists = [sub_array.tolist() for sub_array in splitByDeviceBoardOutStatesArrays]

        for row in range(cellGrid.returnRowNum()):
            for column in range(cellGrid.returnColumnNum()):

                #IF GRID BUTTON AT CURRENT ROW/COLUMN COMBINATION
                #IS SET TO TRUE WHEN PRESSED
                if(cellGridBooleans[row][column]):

                    #call the plot creation function FOR THE CURRENT DEVICE DATA ONLY
                    createPlots(splitByDeviceBoardOutOtherLists[currentDevice], \
                                splitByDeviceBoardOutCurrentLists[currentDevice], \
                                splitByDeviceBoardOutStatesLists[currentDevice], cellGrid, cycleNumber, \
                                toggledOhmsLawUnit, IVTestState, byte29_modeState, row + 1, column + 1, \
                                SETREADVoltage, RESETREADVoltage, FORMSETStateString, messageListBox, \
                                invertIVStates, stepVoltageDirection, maxStepVoltage, \
                                chosenStepVoltage, pulseTestStepVoltagesList, gateVoltageCombinedBytes, \
                                FORMSETVoltageCombinedBytes, RESETVoltageCombinedBytes, SETGateVoltage, \
                                RESETGateVoltage, csvDirectoryString, permitPlotDisplayFlag, False, hardCodeDevices)

                    currentDevice += 1 #increment for next device (if there is one)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #since the heatmap requires all devices to have their data generated, this calls
    #the createPlots function after all data has been generated
    if(createHeatMap.get()):

        #at Jeelka's request, she also wants this option available for the read-write
        #verification approach for the Pulse Test mode, with the logic being that the
        #values selected are the found values within the specified range
        if(utilizeCurResRange.get()): #if the read-write verification checkbutton is selected
            print(rangeCycleList)
            print(rangeCycleDeviceList)
            print(boardOutOther)
            print(boardOutCurrent)
            print(boardOutStates)
            print(failedRangeCycleDataListOther)
            print(failedRangeCycleDataListCurrent)
            print(failedRangeCycleDataListStates)
            print(failedDeviceList)

            #since the "last/found" data of each attempt per selected device would be at the
            #end of that device's amount of data, pull from the rangeCycleList to get the
            #associated final iteration's data's index based on length/range
            for deviceNum in range(len(rangeCycleList)):

                if(rangeCycleList[deviceNum] > 0): #if an ending verifcation RESET output was found

                    print('testing')

                    #save the device's LAST indices associated with this found RESET output
                    #RECALL: [SET, RESET] format, so RESET is last indice while SET is second to last

        else: #otherwise, normal pulse test, proceed normally
            createPlots(boardOutOther, boardOutCurrent, boardOutStates, cellGrid, cycleNumber, \
                        toggledOhmsLawUnit, IVTestState, byte29_modeState, row + 1, column + 1, \
                        SETREADVoltage, RESETREADVoltage, FORMSETStateString, messageListBox, \
                        invertIVStates, stepVoltageDirection, maxStepVoltage, \
                        chosenStepVoltage, pulseTestStepVoltagesList, gateVoltageCombinedBytes, \
                        FORMSETVoltageCombinedBytes, RESETVoltageCombinedBytes, SETGateVoltage, \
                        RESETGateVoltage, csvDirectoryString, permitPlotDisplayFlag, True, hardCodeDevices)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #if the board requires resetting, display this request in the message window, otherwise
    #print the output data and export if enabled by the csvControlVariable toggle

    if(boardOutOther == 'reset switch'): #if serialExecution board throws 'reset switch' request
        
        #display message to prompt the user to follow these instructions
        messageListBox.insert(END, 'Press reset switch to submit pulse')

    #otherwise, output/export all data as desired (lengths of all boardOutput
    #arrays are expected to be the same)
    elif(len(boardOutOther) > 0):

        #give confirmation that the run completed without issue
        messageListBox.insert(END, ''.join([byte29_modeState.get(), ' Run has completed']))

        # - - - - - - - - - - - - - - - - - - -

        #return FINAL CYCLE information of the PULSE TEST (related) run, NOT the IV test outputs
        if(byte29_modeState.get() != 'IV Test'):

            messageListBox.insert(END, '') #first, add empty line for better visibility

            #display the SET information on the FIRST line, THEN the RESET information on the second
            if 'SET' in boardOutStates: #check first if there is a 'SET' state should the board not output one otherwise

                #find the index of the LAST 'SET' instance
                lastSETIndex = next(i for i in reversed(range(len(boardOutStates))) if boardOutStates[i] == 'SET')

                #since the index should be shared with the other board output arrays of the same length,
                #get the corresponding channel numbers and non-voltage (either current or resistance) amounts
                messageListBox.insert(END, ''.join(['SET READ: Ch: ', str(boardOutOther[lastSETIndex]), \
                        ', ', str(boardOutCurrent[lastSETIndex]), ' ', toggledOhmsLawUnit.get()]))

            if 'RESET' in boardOutStates: #check first if there is a 'RESET' state should the board not output one otherwise

                #find the index of the LAST 'RESET' instance
                lastRESETIndex = next(i for i in reversed(range(len(boardOutStates))) if boardOutStates[i] == 'RESET')

                #since the index should be shared with the other board output arrays of the same length,
                #get the corresponding channel numbers and non-voltage (either current or resistance) amounts
                messageListBox.insert(END, ''.join(['RESET READ: Ch: ', str(boardOutOther[lastRESETIndex]), \
                        ', ', str(boardOutCurrent[lastRESETIndex]), ' ', toggledOhmsLawUnit.get()]))
        
        # - - - - - - - - - - - - - - - - - - -

        #if csvControlVariable toggle is set, call built in "arrangeGridExport" function
        #to prepare the data and export the data with the built in "exportPCBToCSV" function 
        if(csvControlVariable.get()): #if set

            #given the unique setup for the 'IV' state for IV testing, a boolean will be set depending on whether or
            #not it's done in order for the unique logic in arrangeGridExport to be activated
            IVStateBool = False
            if(IVTestState.get() == 'IV' and byte29_modeState.get() == 'IV Test'): #if this combination of conditions is met
                IVStateBool = True

            #call "arrangeGridExport" function to arrange the data before exporting, with
            #the final input "rangeCycleBoolean" being set based on whether or not the
            #utilizeCurResRange was set
            arrangedData, arrangedDataFAILED, arrangedDataPTSingleCycleSET, arrangedDataPTSingleCycleRESET = \
                          arrangeGridExport(boardOutOther, boardOutCurrent, boardOutStates, cycleNumber, \
                                            SETREADVoltage, RESETREADVoltage, toggledOhmsLawUnit, byte29_modeState, \
                                            IVTestState, IVStateBool, FORMSETStateString, inputByteList, cellGrid, \
                                            maxStepVoltage, pulseTestStepVoltagesList, invertIVStates, \
                                            SETGateVoltage, RESETGateVoltage, deviceNum, stepVoltageDirection, \
                                            rangeCycleList, utilizeCurResRange, rangeCycleDeviceList, failedRangeCycleDataListOther, \
                                            failedRangeCycleDataListCurrent, failedRangeCycleDataListStates, failedDeviceList, \
                                            failedCycleMax, pulseTestRangeMin, pulseTestRangeMax, hardCodeDevices)

            #for the sake of having the output file name be more informative, append to the string saying that
            #the code used hard coded data
            if(hardCodeDevices.get()):
                currentString = saveFileNameString.get()
                saveFileNameString.set(''.join([currentString, 'HardCodedPulseTest']))

            #call "exportPCBToCSV" if arrangedData has any data to export
            #NOTE: conditional logic checks to see if the boardOutOther (and boardOutCurrent and boardOutStates)
            #list(s) is COMPLETELY EMPTY, which would imply that all devices failed if so, meaning there is no
            #point in returning the arrangedData if no data beyond the general Excel header information
            #was saved/generated
            if(not all(not generatedList for generatedList in boardOutOther)):
                #call "exportPCBToCSV" to export the obtained arrangedData
                exportPCBToCSV(arrangedData, saveFileNameString.get(), csvDirectoryString.get())

            #call "exportPCBToCSV" if arrangeDataFAILED has any data to export
            if(len(arrangedDataFAILED) > 0): #if anything is exported from arrangeGridExport for arrangeDataFAILED, proceed

                #create failed read-write verification file string with date time
                currentTime = datetime.now() #get current datetime information
                dateTimeFormatted = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                exportPCBToCSV(arrangedDataFAILED, ''.join([saveFileNameString.get(), 'FAILED_RWVerif_Data', \
                                                            dateTimeFormatted]), csvDirectoryString.get())

            #call "exportPCBToCSV" if arrangedDataPTSingleCycleSET has any data to export
            if(len(arrangedDataPTSingleCycleSET) > 0): #if anything is exported from arrangeGridExport for arrangedDataPTSingleCycleSET, proceed

                #create failed read-write verification file string with date time
                currentTime = datetime.now() #get current datetime information
                dateTimeFormatted = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                exportPCBToCSV(arrangedDataPTSingleCycleSET, ''.join([saveFileNameString.get(), 'Pulse_Test_SETONLY', \
                                                            dateTimeFormatted]), csvDirectoryString.get())

            #call "exportPCBToCSV" if arrangedDataPTSingleCycleRESET has any data to export
            if(len(arrangedDataPTSingleCycleRESET) > 0): #if anything is exported from arrangeGridExport for arrangedDataPTSingleCycleRESET, proceed

                #create failed read-write verification file string with date time
                currentTime = datetime.now() #get current datetime information
                dateTimeFormatted = currentTime.strftime("%d-%m-%Y %Hh_%Mm_%Ss")

                exportPCBToCSV(arrangedDataPTSingleCycleRESET, ''.join([saveFileNameString.get(), 'Pulse_Test_RESETONLY', \
                                                            dateTimeFormatted]), csvDirectoryString.get())

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #print out the total run time of this function if showRunTime is set
    if(showRunTime.get()): #if True

        #for better visual clarity, add an extra line between the extra text
        #within the messageListBox and this Runtime output IF there is text
        #within the messageListBox already
        if(messageListBox.size() > 0): #if not empty, add empty extra line
            messageListBox.insert(END, '')

        #print out the difference in times for the full runtime
        messageListBox.insert(END, 'Runtime: '+ str(datetime.now() - startSendTime))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #reenable the option to toggle buttons now that the code is done
    cellGrid.changeGridButtonStates('normal')
    
#-------------------------------------------------------------------------

#main (top-level) startup
if __name__ == '__main__':
    masterTkRoot = Tk()
    programClassApp = masterWindowClass(masterTkRoot, True)
    masterTkRoot.mainloop()
