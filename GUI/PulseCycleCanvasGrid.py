from tkinter import BooleanVar, Canvas,  Label, Button, Entry, Listbox,LabelFrame, Frame, Checkbutton, Scrollbar, CENTER, SUNKEN, StringVar

from .BaseCanvas import BaseCanvas

class PulseCycleCanvasGrid(BaseCanvas):

    def __init__(self, canvasFrame:Frame):
        BaseCanvas.__init__(self, canvasFrame)
        canvasFrame.grid_rowconfigure(0, weight=1)
        canvasFrame.grid_columnconfigure(0, weight=1)

        self.pulseCycleCanvas = Canvas(canvasFrame)
        self.pulseCycleCanvas.grid(row=0, column=0, sticky='nsew')
        self.startRun:bool = True
        self.modeState.set('pulse_cycle_test')

        self.setDefaultValues()
        self.createPulseCycleCanvas()
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
        self.gateVoltage.set(1.5)
        self.gateCycleVoltage.set(3.3)
        self.formSetStateString.set('')
        self.formSetVoltage.set(3.3)
        self.formSetTime.set(100)
        self.formSetReadVoltage.set(0.2) 
        self.formSetReadTime.set(500) 
        self.resetVoltage.set(1.8)
        self.resetTime.set(100)
        self.resetReadVoltage.set(0.2) 
        self.resetReadTime.set(500) 
        self.stepNumber.set(0)
        self.cycleNumber.set(1)
        self.delayPeriodTime.set(500)

        #FOR PULSE STEP TEST ONLY
        self.maxFormSetVoltage.set(0)
        self.maxResetVoltage.set(0)
        self.chosenStepVoltage.set('None')
        self.stepVoltageDirection.set('None')
        self.incrementVoltage.set(False)

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

    def createPulseCycleCanvas(self):
        
        self.pulseCycleCanvas.grid_columnconfigure(0, weight=4) #first column
        self.pulseCycleCanvas.grid_columnconfigure(1, weight=2)
        self.pulseCycleCanvas.grid_columnconfigure(2, weight=0)
        self.pulseCycleCanvas.grid_columnconfigure(3, weight=2)
        self.pulseCycleCanvas.grid_columnconfigure(4, weight=4) #last column

        
        pulseCycleCanvasRow = 0
        # Title
        self.titlePulseCycleLabel = Label(self.pulseCycleCanvas, text='Pulse Test - SET/RESET Switch', font=('calibre', 20, 'bold'))
        self.titlePulseCycleLabel.grid(row = pulseCycleCanvasRow, column=0, columnspan=5, pady=(10, 5), sticky='nsew')

        pulseCycleCanvasRow += 1
        TestNameFrame = Frame(self.pulseCycleCanvas)
        TestNameFrame.grid(row = pulseCycleCanvasRow, column=0, columnspan=5, padx=10, pady=(10, 5), sticky='nsew')

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
        
        pulseCycleCanvasRow += 1
        row = 0

        # column 2: middle column
        entryFrame = LabelFrame(self.pulseCycleCanvas, text='Pulse Cycle Parameters', font=labelFont, labelanchor = 'nw')
        entryFrame.grid(row=pulseCycleCanvasRow, column=2, sticky='nsew')

        # Store widgets in case you want to reference them later
        self.entryWidgets = {}

        # Only the mid column should expand
        # entryFrame.grid_columnconfigure(1, weight=1)

        fields = [
            (row + 1, 0, 'SET Gate Volt:', self.gateVoltage, 'V'),
            (row + 2, 0, 'RESET Gate V:', self.gateCycleVoltage, 'V'),
            (row + 3, 0, 'SET Voltage:', self.formSetVoltage, 'V'),
            (row + 4, 0, 'SET Time:', self.formSetTime, 'us'),
            (row + 5, 0, 'RESET Voltage:', self.resetVoltage, 'V'),
            (row + 6, 0, 'RESET Time:', self.resetTime, 'us'),
            (row + 1, 2, 'Delay Period:', self.delayPeriodTime, 'us'),            
            (row + 2, 2, 'Read 1 Voltage:', self.formSetReadVoltage, 'V'),
            (row + 3, 2, 'Read 1 Time:', self.formSetReadTime, 'us'),
            (row + 4, 2, 'Read 2 Voltage:', self.resetReadVoltage, 'V'),
            (row + 5, 2, 'Read 2 Time:', self.resetReadTime, 'us'),
            (row + 6, 2, 'Cycles:', self.cycleNumber, '')
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

        self.cycleNumberEntry = self.entryWidgets['Cycles']['Entry']

        # pulseStepCanvasRow += 1

        # --------------------------------------------------------------------------------------
        # spaceLabel = Label(self.pulseStepCanvas, text = ' ', font=labelFont, anchor='w')
        # spaceLabel.grid(row = pulseStepCanvasRow, column = 0, columnspan=5, padx = padX, pady = 1, sticky='nsew')
        # --------------------------------------------------------------------------------------
        

        pulseCycleCanvasRow += 1

        # column 1, 2, 3
        optionsFrame = LabelFrame(self.pulseCycleCanvas, text='Options', font=labelFont, labelanchor = 'nw')
        optionsFrame.grid(row = pulseCycleCanvasRow, column = 1, columnspan=3, padx = padX, pady=(20, 10), sticky='ew')
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

        self.invertStates = Checkbutton(checkButtonFrame, text='Invert States', 
                                       font=labelFont, anchor='w', variable = self.invertIVStates)
        self.invertStates.grid(row=1, column=0, padx=padX, pady=padY, sticky='ew')

        unitButtonFrame = Frame(checkButtonFrame)
        unitButtonFrame.grid(row=1, column=1, padx=(20, 1), pady=(padY, 2), sticky='ew')
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

        pulseCycleCanvasRow += 1
# --------------------------------------------------------------------------------------
        # spaceLabel = Label(self.pulseStepCanvas, text = ' ', font=labelFont, anchor='w')
        # spaceLabel.grid(row = pulseStepCanvasRow, column = 0, columnspan=5, padx = padX, pady = 1, sticky='nsew')
# --------------------------------------------------------------------------------------
        
        pulseCycleCanvasRow += 1
        
        # --------------------------------------------------------------------------------------


        # ----- Pulse Control Frame -----
        pulseCycleCanvasRow += 4
        self.pulseCycleCanvas.grid_rowconfigure(pulseCycleCanvasRow, weight=1)
        controlFrame = Frame(self.pulseCycleCanvas)
        controlFrame.grid(row=pulseCycleCanvasRow, column=0, rowspan=3, columnspan=5, padx=(10, 10), pady=(2, 2), sticky='nsew')

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
