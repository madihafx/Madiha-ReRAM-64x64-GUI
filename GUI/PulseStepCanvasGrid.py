from tkinter import BooleanVar, Canvas,  Label, Button, Entry, Listbox,LabelFrame, Frame, Checkbutton, Scrollbar, CENTER, SUNKEN, StringVar

from .BaseCanvas import BaseCanvas

# Stacia's note: in the GUI, this window is referred to as "Potentiation Testing."
# However, this change was made long after many variables and functions referenced it as
# "Pulse Step Testing." Therefore, in the code, it is mostly called "Pulse Step Testing,"
# even though on the GUI the text says "Potentiation Testing."

class PulseStepCanvasGrid(BaseCanvas):

    def __init__(self, canvasFrame:Frame):
        BaseCanvas.__init__(self, canvasFrame)
        canvasFrame.grid_rowconfigure(0, weight=1)
        canvasFrame.grid_columnconfigure(0, weight=1)

        self.pulseStepCanvas = Canvas(canvasFrame)
        self.pulseStepCanvas.grid(row=0, column=0, sticky='nsew')
        self.startRun:bool = True
        self.modeState.set('pulse_step_test')

        self.setDefaultValues()
        self.createPulseStepCanvas()
        self.startRun = False
    
    def setDefaultValues(self):
        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE IV
        #CANVAS TO THEIR PULSE TEST DEFAULTS
        self.IvTestState.set('None')

        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE BASE
        #CANVAS TO THEIR PULSE STEP TEST DEFAULTS
        #NOTE: These ones are automatically changed between
        #IV test modes and, should the user go back to the Pulse
        #Test window, NOT RESETTING THESE will have these set
        #to 0 and this is done to avoid tedium
        self.gateVoltage.set(2)
        self.gateCycleVoltage.set(0)
        self.formSetStateString.set('')
        self.formSetVoltage.set(3.3)
        self.formSetTime.set(100)
        self.formSetReadVoltage.set(0.2) 
        self.formSetReadTime.set(500) 
        self.resetVoltage.set(1.8)
        self.resetTime.set(100)
        self.resetReadVoltage.set(0.2) 
        self.resetReadTime.set(500) 
        self.stepNumber.set(25)
        self.cycleNumber.set(1)
        self.delayPeriodTime.set(500)

        #FOR PULSE STEP TEST ONLY
        self.maxFormSetVoltage.set(2)
        self.maxResetVoltage.set(1.8)
        self.chosenStepVoltage.set('SET')
        self.stepVoltageDirection.set('Rising')
        self.incrementVoltage.set(True)

        #reset current/resistance button to its default current mode
        self.toggledOhmsLawUnit.set('uA')
        self.saveFileName.set('New Test')

        #PULSE TEST ONLY range variables
        self.utilizeCurResRange.set(False)
        self.pulseTestRangeMin.set(0)
        self.pulseTestRangeMax.set(0)
        self.hrsRangeMin.set(0)
        self.hrsRangeMax.set(0)
        self.lrsRangeMin.set(0)
        self.lrsRangeMax.set(0)
        self.pulseTestRangeCycleCount.set(0)
        self.minGateVoltage.set(0)
        self.minResetVoltage.set(0)

        #other PULSE TEST ONLY toggles
        self.createHeatMap.set(False)
        self.applyToAllDevices.set(False)

        self.retentionTest.set(False)
        self.retentionTime.set(0)
        self.retentionCycles.set(0)

        self.gateRangeTest.set(False)
        self.gateRangeMin.set(0)
        self.gateRangeMax.set(0)

        self.readImage.set(True)
        self.writeImage.set(False)

        self.verifyCycles.set(0)
        self.gateRangeThreshold.set(0)
        self.gateVoltageMin.set(0)
        self.gateVoltageMax.set(0)
        self.gateStepVoltage.set(0)
        self.resetVoltageMin.set(0)
        self.resetVoltageMax.set(0)

        self.levelTolerance.set(0)

        self.binaryMode.set(True)
        # self.rangeValuesStr.set(' 0.06, 0.2, 0.7, 1')
        # self.rangeLevelsStr.set(' 80, 30, 15, 7')

        self.rangeValuesStr.set('0')
        self.rangeLevelsStr.set('0')

        self.kernelProcessingTest.set(False)
        self.kernelMatStr.set('[]')

        rangeValues = []
        rangeLevels = []


        self.rowColumnVariable.set('Col')

    def createPulseStepCanvas(self):
        
        self.pulseStepCanvas.grid_columnconfigure(0, weight=4) #first column
        self.pulseStepCanvas.grid_columnconfigure(1, weight=2)
        self.pulseStepCanvas.grid_columnconfigure(2, weight=0)
        self.pulseStepCanvas.grid_columnconfigure(3, weight=2)
        self.pulseStepCanvas.grid_columnconfigure(4, weight=4) #last column

        
        pulseStepCanvasRow = 0
        # Title
        self.titlePulseStepLabel = Label(self.pulseStepCanvas, text='Potentiation Testing', font=('calibre', 20, 'bold'))
        self.titlePulseStepLabel.grid(row=pulseStepCanvasRow, column=0, columnspan=5, pady=(10, 5), sticky='nsew')

        pulseStepCanvasRow += 1
        TestNameFrame = Frame(self.pulseStepCanvas)
        TestNameFrame.grid(row=pulseStepCanvasRow, column=0, columnspan=5, padx=10, pady=(10, 5), sticky='nsew')

        # Configure TestNameFrame's columns
        TestNameFrame.grid_columnconfigure(0, weight=1)  # left spacer
        TestNameFrame.grid_columnconfigure(1, weight=0)  # label
        TestNameFrame.grid_columnconfigure(2, weight=1)  # entry (this will expand)
        TestNameFrame.grid_columnconfigure(3, weight=1)  # right spacer

        # Label
        Label(TestNameFrame, text='Test Name:', font=('calibre', 12, 'normal')).grid(
            row=0, column=1, padx=5, sticky='e')

        # Entry (expandable)
        self.testNameEntry = Entry(
            TestNameFrame,
            textvariable=self.saveFileName,
            font=('calibre', 10),
            bg='white'
        )
        self.testNameEntry.grid(row=0, column=2, padx=5, sticky='ew')  # Expand east-west

        labelFont = ('calibre', 12, 'normal')
        labelWidth = 13
        padX = 5
        padY = 2
        
        pulseStepCanvasRow += 1
        row = 0

        # column 2: middle column
        entryFrame = LabelFrame(self.pulseStepCanvas, text='Pulse Step Parameters', font=labelFont, labelanchor = 'nw')
        entryFrame.grid(row=pulseStepCanvasRow, column=2, sticky='nsew')

        # Store widgets in case you want to reference them later
        self.entryWidgets = {}

        # Only the mid column should expand
        # entryFrame.grid_columnconfigure(1, weight=1)

        fields = [
            (row + 1, 0, 'Gate Voltage:', self.gateVoltage, 'V'),
            (row + 1, 2, 'Delay Period:', self.delayPeriodTime, 'us'),
            # leave space for the buttons.
            (row + 3, 0, 'Form Voltage:', self.formSetVoltage, 'V'),
            (row + 2, 2, 'Read 1 Voltage:', self.formSetReadVoltage, 'V'),
            (row + 4, 0, 'Form Time:', self.formSetTime, 'us'),
            (row + 3, 2, 'Read 1 Time:', self.formSetReadTime, 'us'),
            (row + 5, 0, 'Min Reset Volt:', self.resetVoltage, 'V'),
            (row + 4, 2, 'Read 2 Voltage:', self.resetReadVoltage, 'V'),
            (row + 6, 0, 'Reset Time:', self.resetTime, 'us'),
            (row + 5, 2, 'Read 2 Time:', self.resetReadTime, 'us'),
            (row + 6, 2, 'Cycles:', self.cycleNumber, ''),
            (row + 7, 0, 'Max Form Volt:', self.maxFormSetVoltage, 'V'),
            (row + 7, 2, 'Step Number:', self.stepNumber, ''),
            (row + 8, 0, 'Max Reset Volt:', self.maxResetVoltage, 'V')
        ]

        for row, col, label_text, var, unit in fields:
            frame = Frame(entryFrame)
            frame.grid(row=row, column=col, padx=5, pady=padY, sticky='ew')

            # frame.grid_columnconfigure(0, weight=1)
            # frame.grid_columnconfigure(1, weight=2)
            # frame.grid_columnconfigure(2, weight=1)

            label = Label(frame, text=label_text, width=labelWidth, font=labelFont, anchor='w')
            label.grid(row=0, column=0, padx=(padX, 1), pady=padY, sticky='ew')

            entryUnitFrame = Frame(frame)
            entryUnitFrame.grid(row=0, column=1, padx=(1,padX), pady=padY, sticky='ew')

            entry = Entry(entryUnitFrame, textvariable=var, width=7, font=labelFont, bg='white')
            entry.grid(row=0, column=0, padx=padX, pady=padY, sticky='ew')

            unit_label = Label(entryUnitFrame, text=unit, width=3, font=labelFont, anchor='w')
            unit_label.grid(row=0, column=1, padx=(1,padX),  pady=padY, sticky='ew')

            self.entryWidgets[label_text.strip(':')] = {'Label':label, 'Entry':entry}

        self.formSetVoltageLabel:Label = self.entryWidgets['Form Voltage']['Label']
        self.formSetTimeLabel:Label = self.entryWidgets['Form Time']['Label']
        self.maxFormSetVoltageLabel:Label = self.entryWidgets['Max Form Volt']['Label']
        self.cycleNumberEntry = self.entryWidgets['Cycles']['Entry']

        self.maxInitialLabel = Label(entryFrame, text='Max voltages used for initial set/reset', font=labelFont, anchor='w')
        self.maxInitialLabel.grid(row=8, column=2, padx=padX, pady=padY, sticky='ew')

        #create the two buttons associated with the two states of interest and have them
        #call the same function to change the state information accordingly
        self.setFormButtonFrame = Frame(entryFrame)
        self.setFormButtonFrame.grid(row = 2, column = 0, padx = padX, pady = padY, sticky='w')

        self.setFormModeLabel = Label(self.setFormButtonFrame, text = 'FORM/SET Mode:', font=labelFont, anchor='w')
        self.setFormModeLabel.grid(row = 0, column = 0, padx = padX, pady = padY, sticky='w')

        self.FORMSelectButton = Button(self.setFormButtonFrame, text = 'FORM')
        self.FORMSelectButton.config(command = lambda: self.changeFORMSETState('FORM'), padx=1, pady=2, bg='light gray')
        self.FORMSelectButton.grid(row = 0, column = 1, padx = padX, pady = padY, sticky='w')

        self.SETSelectButton = Button(self.setFormButtonFrame, text = 'SET')
        self.SETSelectButton.config(command = lambda: self.changeFORMSETState('SET'), padx=1, pady=2, bg='light gray')
        self.SETSelectButton.grid(row = 0, column = 2, padx = padX, pady = padY, sticky='w')

        # pulseStepCanvasRow += 1

        # --------------------------------------------------------------------------------------
        # spaceLabel = Label(self.pulseStepCanvas, text = ' ', font=labelFont, anchor='w')
        # spaceLabel.grid(row = pulseStepCanvasRow, column = 0, columnspan=5, padx = padX, pady = 1, sticky='nsew')
        # --------------------------------------------------------------------------------------
        

        pulseStepCanvasRow += 1

        # column 1, 2, 3
        optionsFrame = LabelFrame(self.pulseStepCanvas, text='Options', font=labelFont, labelanchor = 'nw')
        optionsFrame.grid(row = pulseStepCanvasRow, column = 1, columnspan=3, padx = padX, pady=(20, 10), sticky='ew')
        # only expand the middle column
        optionsFrame.grid_columnconfigure(0, weight=3)
        optionsFrame.grid_columnconfigure(1, weight=3)
        optionsFrame.grid_columnconfigure(2, weight=1)

        row = 0
        checkButtonFrame = Frame(optionsFrame)
        checkButtonFrame.grid(row=row, column=0, columnspan=2, padx=padX, pady=padY, sticky='ew')
        checkButtonFrame.grid_columnconfigure(0, weight=3)
        checkButtonFrame.grid_columnconfigure(1, weight=3)

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #the following READ and WRITE check boxes are created to utilize the trace_add logic
        #before being removed
        self.readImageCheckBox = Checkbutton(checkButtonFrame, text = 'Read', font=labelFont, anchor='w', variable = self.readImage)
        self.readImageCheckBox.grid(row = 0, column = 0, padx=10, pady=(padY, 1), sticky='ew')
        self.readImage.trace_add('write', lambda * args: self.toggleReadImageFrame(self.readImage.get()))
        self.readImageCheckBox.grid_forget()

        self.writeImageCheckBox = Checkbutton(checkButtonFrame, text = 'Write', font=labelFont, anchor='w', variable = self.writeImage)
        self.writeImageCheckBox.grid(row = 1, column = 0, padx=10, pady=(padY, 1), sticky='ew')
        self.writeImage.trace_add('write', lambda * args: self.toggleWriteImageFrame( self.writeImage.get(), args))
        self.writeImageCheckBox.grid_forget()

        # - - - - - - - - - - - - - - - - - - - - - - - -

        self.exportCheckBox = Checkbutton(checkButtonFrame, text='Export to CSV', 
                                          font=labelFont, anchor='w', variable=self.csvControlVariable)
        self.exportCheckBox.grid(row=0, column=0, padx=padX, pady=padY, sticky='ew')

        self.createPlots = Checkbutton(checkButtonFrame, text='Create Plots', 
                                       font=labelFont, anchor='w', variable = self.createSavePlots)
        self.createPlots.grid(row=0, column=1, padx=padX, pady=padY, sticky='ew')

        unitButtonFrame = Frame(checkButtonFrame)
        unitButtonFrame.grid(row=0, column=2, padx=(20, 1), pady=(padY, 2), sticky='ew')
        # unitButtonFrame.grid_columnconfigure(0, weight=1)

        #display of non-Voltage units
        self.unitButtonLabel = Label(unitButtonFrame, text = 'Unit:', font=labelFont, anchor='w')
        self.unitButtonLabel.grid(row = 0, column = 0, padx=2, pady=(padY, 1), sticky='e')

        self.unitList = [] #initialize unitList to store all label widgets to be changed that have the toggleable Ohms Law units

        #calls built-in "toggleOhmsLawUnit" function when pressed AND displays
        #the current/changed unit on the button
        self.unitButton = Button(unitButtonFrame, text=self.toggledOhmsLawUnit.get(), 
                            command = lambda:self.toggleUnitButton(self.toggledOhmsLawUnit,self.unitButton, self.unitList),
                            width = 5, padx = 2, pady = 1, 
                            bg = 'lightgreen')
        self.unitButton.grid(row = 0, column = 1, padx=1, pady=(padY, 1), sticky='e')

        pulseStepCanvasRow += 1
# --------------------------------------------------------------------------------------
        # spaceLabel = Label(self.pulseStepCanvas, text = ' ', font=labelFont, anchor='w')
        # spaceLabel.grid(row = pulseStepCanvasRow, column = 0, columnspan=5, padx = padX, pady = 1, sticky='nsew')
# --------------------------------------------------------------------------------------
        

        pulseStepCanvasRow += 1

        #the following section will create and populate the PULSE STEP EXCLUSIVE frame to determine
        #if the inputted byte sequence will be SET or RESET focused as well as the direction of the
        #steps
        self.stepFrameRow = pulseStepCanvasRow
        self.stepFrame = LabelFrame(self.pulseStepCanvas, text = 'Step Voltage Direction', \
                                    labelanchor = 'nw', font = labelFont)
        self.stepFrame.grid(row = self.stepFrameRow, column = 2, padx = (10, 10), pady = (10, 2), \
                            sticky = 'ew') #grid format

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #create buttons to let the user toggle between whether the SET or RESET voltage incorporates
        #the step voltage logic

        #prompt label
        self.FORMOrSETVoltageLabelStep = Label(self.stepFrame, text = 'Select Voltage to use step logic:', font = \
                       labelFont)
        self.FORMOrSETVoltageLabelStep.grid(row = 0, column = 0, padx = (20, padX), pady = padY, sticky = 'w')

        #update the widget to update the widget place and width info for
        #position calculations below for Entry widget
        self.FORMOrSETVoltageLabelStep.update()

        #create the two buttons to toggle between the selected state being chosen for
        #using the step logic
        self.FORMSETVoltageStepChosenButton = Button(self.stepFrame, text = 'SET')
        self.RESETVoltageStepChosenButton = Button(self.stepFrame, text = 'RESET')

        #default will have FORM/SET chosen first in earlier initialized/set variables, so have the FORM/SET button
        #have the green "selected" visual color
        self.FORMSETVoltageStepChosenButton.config(bg = 'lightgreen')

        #place the buttons
        self.FORMSETVoltageStepChosenButton.grid(row = 0, column = 1, padx = (20, padX), pady = padY, sticky = 'w')
        self.RESETVoltageStepChosenButton.grid(row = 0, column = 2, padx = (20, padX), pady = padY, sticky = 'w')
        
        #create the button command logic that toggles chosenStepVoltage while also changing the background color
        #of the two buttons to show which button/state is selected
        self.FORMSETVoltageStepChosenButton.config(command = lambda: self.changeFORMSETRESETVoltageStep('SET'))
        self.RESETVoltageStepChosenButton.config(command = lambda: self.changeFORMSETRESETVoltageStep('RESET'))

        #for the creation of this pulse step canvas, initialize the logic by clicking
        #on the SET button by default
        self.changeFORMSETRESETVoltageStep('SET')

        #for initial pulse canvas creation, set the
        #FORM/SET button logic to the default FORM state
        #AFTER the RESETVoltageStepChosenButton is created, given
        #how this button effects the logic within
        self.changeFORMSETState('FORM')

        # create a checkbox for whether voltage increments
        # if selected, voltage will increment from MIN to MAX voltage in STEPS number of steps
        # if not selected, MIN voltage will be applied STEPS number of times
        # for both, MAX voltage will be used in initial set/reset operations before running step test
        self.IncrementVoltage = Checkbutton(self.stepFrame, text='Increment Voltage', 
                                          font=labelFont, anchor='w', variable=self.incrementVoltage)
        self.IncrementVoltage.grid(row=0, column=3, padx=(20, padX), pady=padY, sticky='ew')

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #create buttons to let the user decide if the selected state voltage RISES from the
        #initial set amount to the maximum step voltage, does the inverse and FALLS, OR
        #does BOTH by rising then falling between the two voltages

        #prompt label
        self.voltageDirectionStepLabel = Label(self.stepFrame, text = 'Voltage Direction:', \
                                               font = labelFont)
        self.voltageDirectionStepLabel.grid(row = 1, column = 0, padx = (20, padX), pady = padY, sticky = 'w')

        #create the three buttons to toggle between the "direction" of the step voltage logic
        self.risingStepVoltageButton = Button(self.stepFrame, text = 'RISING', command = lambda: \
                                              self.changeStepVoltageDirectionStep('Rising'))
        self.risingStepVoltageButton.grid(row = 1, column = 1, padx = (20, padX), pady = padY, sticky = 'w')
        
        self.fallingStepVoltageButton = Button(self.stepFrame, text = 'FALLING', command = lambda: \
                                              self.changeStepVoltageDirectionStep('Falling'))
        self.fallingStepVoltageButton.grid(row = 1, column = 2, padx = (20, padX), pady = padY, sticky = 'w')
        
        self.riseAndFallStepVoltageButton = Button(self.stepFrame, text = 'RISE THEN FALL', command = lambda: \
                                              self.changeStepVoltageDirectionStep('Rise then Fall'))
        self.riseAndFallStepVoltageButton.grid(row = 1, column = 3, padx = (20, padX), pady = padY, sticky = 'w')

        #do the following voltage direction by default upon startup
        self.changeStepVoltageDirectionStep('Rising')
        
        # --------------------------------------------------------------------------------------
        
        pulseStepCanvasRow += 1
        
        # --------------------------------------------------------------------------------------


        # ----- Pulse Control Frame -----
        pulseStepCanvasRow += 4
        self.pulseStepCanvas.grid_rowconfigure(pulseStepCanvasRow, weight=1)
        controlFrame = Frame(self.pulseStepCanvas)
        controlFrame.grid(row=pulseStepCanvasRow, column=0, rowspan=3, columnspan=5, padx=(10, 10), pady=(2, 2), sticky='nsew')

        controlFrame.grid_columnconfigure(0, weight=1)
        controlFrame.grid_rowconfigure(1, weight=1)

        row=0
        # Output label
        self.messageListLabel = Label(controlFrame, text='Output Display Window :', font=labelFont, anchor='w')
        self.messageListLabel.grid(row=row, column=0, columnspan=2, pady=(10, 2), sticky='w')

        
        row += 1
        # Frame to hold Listbox and Scrollbar
        console_frame = Frame(controlFrame, bd=1, relief=SUNKEN)
        console_frame.grid(row=row, column=0, padx=(15, 2), pady=(5, 15), sticky='nsew')

        # Make console_frame expandable
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        # Listbox
        self.console = Listbox(console_frame, bg='#1e1e1e', font=10, fg='white', yscrollcommand=True)
        self.console.grid(row=0, column=0, sticky='nsew')
        self.console.insert(0, '>>> ' + '\n')


        # Scrollbar
        self.scrollbar = Scrollbar(console_frame, orient="vertical", command=self.console.yview)
        self.scrollbar.grid(row=0, column=1, sticky='e')
        self.console.config(yscrollcommand=self.scrollbar.set)

        buttonsFrame = Frame(controlFrame)
        buttonsFrame.grid(row=row, column=1, padx=(10, 10), pady=5, sticky='new')

        #calls built-in "pressedSubmitData" function when button is pressed
        self.submitButton = Button(buttonsFrame, width=6, height=2, text = 'Send', font=labelFont, bg="lightgreen")
        self.submitButton.grid(row = 0, column = 0, padx = padX, pady = padY, sticky='nsew')

        self.stopButton = Button(buttonsFrame, width=6, height=2, text = 'Stop', font=labelFont, bg="white")
        self.stopButton.grid(row = 1, column = 0, padx = padX, pady = padY)

        self.clearButton = Button(buttonsFrame, width=6, height=2, text='Clear', 
                                  font=labelFont, command=lambda:self.pressedClearOutput(self.console),
                                  bg = 'white')
        self.clearButton.grid(row=2, column=0, padx=padX, pady=padY, sticky='nsew')

    def toggleBinaryMode(self, state, *args):
        self.binaryMode.set(state)

    def resetCycle(self, reset, args):
        if(reset):
            self.cycleNumber.set(1)
            self.cycleNumberEntry.config(state = 'disabled')
        else:
            self.cycleNumberEntry.config(state = 'normal')
            
    def setResetVoltages(self, state):
        if state:
            self.entryWidgets['Form Voltage']['Entry'].config(state = 'normal')
            self.entryWidgets['Form Time']['Entry'].config(state = 'normal')
            self.entryWidgets['Reset Voltage']['Entry'].config(state = 'normal')
            self.entryWidgets['Reset Time']['Entry'].config(state = 'normal')
            self.entryWidgets['Read 1 Voltage']['Entry'].config(state = 'normal')
            self.entryWidgets['Read 1 Time']['Entry'].config(state = 'normal')
            self.formSetVoltage.set(2)
            self.formSetReadVoltage.set(0.2)
            self.resetVoltage.set(1.8)

        else:
            self.entryWidgets['Form Voltage']['Entry'].config(state = 'disabled')
            self.entryWidgets['Form Time']['Entry'].config(state = 'disabled')
            self.entryWidgets['Reset Voltage']['Entry'].config(state = 'disabled')
            self.entryWidgets['Reset Time']['Entry'].config(state = 'disabled')
            self.entryWidgets['Read 1 Voltage']['Entry'].config(state = 'disabled')
            self.entryWidgets['Read 1 Time']['Entry'].config(state = 'disabled')
            self.formSetVoltage.set(0)
            self.formSetReadVoltage.set(0)
            self.resetVoltage.set(0)

    def toggleWriteImageFrame(self, state, *args):
        
        if state or self.binaryMode.get():
            self.writeImageFrame.grid(row=self.WriteImageFrameRow, column=2, padx=(10, 10), pady=(10, 2), sticky='ew')
            self.setResetVoltages(True)
            if self.readImage.get():
                self.readImage.set(False)

        else:
            self.writeImageFrame.grid_forget()
            self.setResetVoltages(False)
            if not self.readImage.get():
                self.readImage.set(True)
        

    def toggleReadImageFrame(self, state, *args):
        if state:
            if self.writeImage.get():
                self.writeImage.set(False)

        else:
           if not self.writeImage.get():
                self.writeImage.set(True)
   
    def toggleRowColButton(self, var: StringVar, button: Button):
        if(var.get() == 'Row'):
            var.set('Col')
        else:
            var.set('Row')

        button.config(text = var.get())

    #-----------------------------------------------------------------------------

    def changeFORMSETState(self, stateString):
        self.formSetVoltageLabel.config(text = ''.join(['Min ', stateString, ' Volt:']))
        self.formSetTimeLabel.config(text = ''.join([stateString, ' Time:']))
        self.maxFormSetVoltageLabel.config(text = ''.join(['Max ', stateString, ' Volt: ']))
        self.formSetStateString.set(stateString)
            
        if(stateString == 'FORM'): #if FORM state, configure GUI to prepare for FORM inputs
            #change associated button color to green to show it's selected
            self.FORMSelectButton.config(bg = 'lightgreen')
            self.SETSelectButton.config(bg = 'light gray') #set other button color to the default

            #change which voltage string is being displayed next to the corresponding entry
            #AND set the Entry value to the default value of THIS specific state

            #NOTE: If the RESETVoltageStepChosenButton is pressed (i.e. highlighted as "light green")
            # and the voltage direction is not RISE THEN FALL,
            #the FORM/SET voltages should be 0 V, so check the state of the button
            if(self.RESETVoltageStepChosenButton.cget('background') == 'lightgreen' and \
               self.stepVoltageDirection.get() != 'Rise then Fall'):
                self.formSetVoltage.set(0)
            else:
                self.formSetVoltage.set(2) #voltage, CHANGE IF NECESSARY

        else: #otherwise, SET state, configure GUI to prepare for SET inputs
            #change associated button color to green to show it's selected
            self.SETSelectButton.config(bg = 'lightgreen')
            self.FORMSelectButton.config(bg = 'light gray') #set other button color to the default

            #change which voltage string is being displayed next to the corresponding entry
            #AND set the Entry value to the default value of THIS specific state

            #NOTE: If the RESETVoltageStepChosenButton is pressed (i.e. highlighted as "light green")
            # and the voltage direction is not RISE THEN FALL,
            #the FORM/SET voltages should be 0 V, so check the state of the button
            if(self.RESETVoltageStepChosenButton.cget('background') == 'lightgreen' and \
               self.stepVoltageDirection.get() != 'Rise then Fall'):
                self.formSetVoltage.set(0)
            else:
                self.formSetVoltage.set(2) #voltage, CHANGE IF NECESSARY

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

            # if RISING or FALLING is selected, the min field of the non-selected step voltage is disabled
            # if RISE THEN FALL is selected, both should remain enabled
            if(self.stepVoltageDirection.get() != 'Rise then Fall'):
                #set the RESET voltage data to 0, including the READ voltage
                self.resetVoltage.set(0)
                #self.resetReadVoltage.set(0)

                #return the FORM/SET voltages to their defaults, should this
                #chosenState be reselected after switching between them beforehand
                self.formSetVoltage.set(2)
                #self.formSetReadVoltage.set(0.2)
                self.entryWidgets['Form Voltage']['Entry'].config(state = 'normal')
                #self.entryWidgets['Read 1 Voltage']['Entry'].config(state = 'normal')

                #disable the RESET voltage data entries to avoid changing these values
                self.entryWidgets['Min Reset Volt']['Entry'].config(state = 'disabled')
                #self.entryWidgets['Read 2 Voltage']['Entry'].config(state = 'disabled')

        else: #otherwise, RESET

            self.chosenStepVoltage.set('RESET')

            #change button colors to show which one is selected
            self.RESETVoltageStepChosenButton.config(bg = 'lightgreen')
            self.FORMSETVoltageStepChosenButton.config(bg = 'light gray')

            # if RISING or FALLING is selected, the min field of the non-selected step voltage is disabled
            # if RISE THEN FALL is selected, both should remain enabled
            if(self.stepVoltageDirection.get() != 'Rise then Fall'):
                #set the FORM/SET voltage data to 0, including the READ voltage
                self.formSetVoltage.set(0)
                #self.formSetReadVoltage.set(0)

                #return the RESET voltages to their defaults, should this
                #chosenState be reselected after switching between them beforehand
                self.resetVoltage.set(1.8)
                #self.resetReadVoltage.set(0.2)
                self.entryWidgets['Min Reset Volt']['Entry'].config(state = 'normal')
                #self.entryWidgets['Read 2 Voltage']['Entry'].config(state = 'normal')

                #disable the FORM/SET voltage data entries to avoid changing these values
                self.entryWidgets['Form Voltage']['Entry'].config(state = 'disabled')
                #self.entryWidgets['Read 1 Voltage']['Entry'].config(state = 'disabled')

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
            if(self.chosenStepVoltage.get() == 'SET'):
                # enable the min SET voltage data entry, disable the min RESET voltage data entry
                self.entryWidgets['Form Voltage']['Entry'].config(state = 'normal')
                self.entryWidgets['Min Reset Volt']['Entry'].config(state = 'disabled')
                self.formSetVoltage.set(2)
                self.resetVoltage.set(0)
            else:   # RESET mode
                # disable the min SET voltage data entry, enable the min RESET voltage data entry
                self.entryWidgets['Form Voltage']['Entry'].config(state = 'disabled')
                self.entryWidgets['Min Reset Volt']['Entry'].config(state = 'normal')
                self.formSetVoltage.set(0)
                self.resetVoltage.set(1.8)
            
        elif(chosenDirection == 'Falling'): #if FALLING button was selected

            #set the background of the corresponding direction's button to light green while
            #setting the background of the other buttons to the default light gray
            self.risingStepVoltageButton.config(bg = 'light gray')
            self.fallingStepVoltageButton.config(bg = 'lightgreen')
            self.riseAndFallStepVoltageButton.config(bg = 'light gray')
            if(self.chosenStepVoltage.get() == 'SET'):
                # enable the min SET voltage data entry, disable the min RESET voltage data entry
                self.entryWidgets['Form Voltage']['Entry'].config(state = 'normal')
                self.entryWidgets['Min Reset Volt']['Entry'].config(state = 'disabled')
                self.formSetVoltage.set(2)
                self.resetVoltage.set(0)
            else:   # RESET mode
                # disable the min SET voltage data entry, enable the min RESET voltage data entry
                self.entryWidgets['Form Voltage']['Entry'].config(state = 'disabled')
                self.entryWidgets['Min Reset Volt']['Entry'].config(state = 'normal')
                self.formSetVoltage.set(0)
                self.resetVoltage.set(1.8)
            
        else: #otherwise, RISE THEN FALL button was selected

            #set the background of the corresponding direction's button to light green while
            #setting the background of the other buttons to the default light gray
            self.risingStepVoltageButton.config(bg = 'light gray')
            self.fallingStepVoltageButton.config(bg = 'light gray')
            self.riseAndFallStepVoltageButton.config(bg = 'lightgreen')
            # enable both the min RESET and min FORM/SET voltage data entries
            self.entryWidgets['Min Reset Volt']['Entry'].config(state = 'normal')
            self.entryWidgets['Form Voltage']['Entry'].config(state = 'normal')
            self.formSetVoltage.set(2)
            self.resetVoltage.set(1.8)

        #set stepVoltageDirection variable to corresponding direction decision
        self.stepVoltageDirection.set(chosenDirection)
