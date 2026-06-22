from tkinter import BooleanVar, Canvas,  Label, Button, Entry, Listbox,LabelFrame, Frame, Checkbutton, Scrollbar, CENTER, SUNKEN, StringVar

from .BaseCanvas import BaseCanvas

class PulseCanvasGrid(BaseCanvas):

    def __init__(self, canvasFrame:Frame):
        BaseCanvas.__init__(self, canvasFrame)
        canvasFrame.grid_rowconfigure(0, weight=1)
        canvasFrame.grid_columnconfigure(0, weight=1)

        self.pulseCanvas = Canvas(canvasFrame)
        
        self.pulseCanvas.grid(row=0, column=0, sticky='nsew')
        self.startRun:bool = True
        self.modeState.set('pulse_test')

        self.setDefaultValues()
        self.createPulseCanvas()
        self.startRun = False
    
    def setDefaultValues(self):
        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE IV
        #CANVAS TO THEIR PULSE TEST DEFAULTS
        self.IvTestState.set('None')

        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE BASE
        #CANVAS TO THEIR PULSE TEST DEFAULTS
        #NOTE: These ones are automatically changed between
        #test modes and, should the user go back to the Pulse
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
        self.pulseTestRangeMax.set(1000000)
        self.hrsRangeMin.set(10)
        self.hrsRangeMax.set(100)
        self.lrsRangeMin.set(0)
        self.lrsRangeMax.set(10)
        self.pulseTestRangeCycleCount.set(10)
        self.minGateVoltage.set(1)
        self.minResetVoltage.set(1)

        #other PULSE TEST ONLY toggles
        self.createHeatMap.set(False)
        self.applyToAllDevices.set(False)

        self.retentionTest.set(False)
        self.retentionTime.set(100-000)
        self.retentionCycles.set(1)

        self.gateRangeTest.set(False)
        self.gateRangeMin.set(0.5)
        self.gateRangeMax.set(2)

        self.readImage.set(True)
        self.writeImage.set(False)

        self.verifyCycles.set(20)
        self.gateRangeThreshold.set(40)
        self.gateVoltageMin.set(0.5)
        self.gateVoltageMax.set(2.0)
        self.gateStepVoltage.set(0.01)
        self.resetVoltageMin.set(0.5)
        self.resetVoltageMax.set(2.0)

        self.levelTolerance.set(10.0)

        self.binaryMode.set(True)
        # self.rangeValuesStr.set(' 0.06, 0.2, 0.7, 1')
        # self.rangeLevelsStr.set(' 80, 30, 15, 7')

        #self.rangeValuesStr.set('0.25, 0.50, 0.75, 1')
        #self.rangeLevelsStr.set('7,  9, 11.5, 15, 19.5, 25, 32, 40.15')

        self.kernelProcessingTest.set(False)
        self.kernelMatStr.set('[0, -0.1, 0; -0.1, 0.4, -0.1; 0, -0.1, 0]')

        self.rangeValuesStr.set('0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1')
        self.rangeLevelsStr.set('7, 12, 20, 30, 40, 50, 60, 80, 100, 120')


        self.rowColumnVariable.set('Col')

    def createPulseCanvas(self):
        # Configure the grid layout in the pulseCanvas for resizability
        # for r in range(20):
        #     self.pulseCanvas.grid_rowconfigure(r, weight=0)
        
        self.pulseCanvas.grid_columnconfigure(0, weight=4) #first column
        self.pulseCanvas.grid_columnconfigure(1, weight=2)
        self.pulseCanvas.grid_columnconfigure(2, weight=0)
        self.pulseCanvas.grid_columnconfigure(3, weight=2)
        self.pulseCanvas.grid_columnconfigure(4, weight=4) #last column

        
        pulseCanvasRow = 0
        # Title
        self.titlePulseLabel = Label(self.pulseCanvas, text='Pulse Test Mode', font=('calibre', 20, 'bold'))
        self.titlePulseLabel.grid(row=pulseCanvasRow, column=0, columnspan=5, pady=(10, 5), sticky='nsew')

        pulseCanvasRow += 1
        TestNameFrame = Frame(self.pulseCanvas)
        TestNameFrame.grid(row=pulseCanvasRow, column=0, columnspan=5, padx=10, pady=(10, 5), sticky='nsew')

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
        
        pulseCanvasRow += 1
        row = 0

        # column 2: middle column
        entryFrame = LabelFrame(self.pulseCanvas, text='Pulse Parameters', font=labelFont, labelanchor = 'nw')
        entryFrame.grid(row=pulseCanvasRow, column=2, sticky='nsew')

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
            (row + 5, 0, 'Reset Voltage:', self.resetVoltage, 'V'),
            (row + 4, 2, 'Read 2 Voltage:', self.resetReadVoltage, 'V'),
            (row + 6, 0, 'Reset Time:', self.resetTime, 'us'),
            (row + 5, 2, 'Read 2 Time:', self.resetReadTime, 'us'),
            (row + 6, 2, 'Cycles:', self.cycleNumber, ''),
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
        self.cycleNumberEntry = self.entryWidgets['Cycles']['Entry']

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

        #for initial pulse canvas creation, set the
        #FORM/SET button logic to the default FORM state
        self.changeFORMSETState('FORM')

        # pulseCanvasRow += 1

        # --------------------------------------------------------------------------------------
        # spaceLabel = Label(self.pulseCanvas, text = ' ', font=labelFont, anchor='w')
        # spaceLabel.grid(row = pulseCanvasRow, column = 0, columnspan=5, padx = padX, pady = 1, sticky='nsew')
        # --------------------------------------------------------------------------------------
        

        pulseCanvasRow += 1

        # column 1, 2, 3
        optionsFrame = LabelFrame(self.pulseCanvas, text='Options', font=labelFont, labelanchor = 'nw')
        optionsFrame.grid(row = pulseCanvasRow, column = 1, columnspan=3, padx = padX, pady=(20, 10), sticky='ew')
        # only expand the middle column
        optionsFrame.grid_columnconfigure(0, weight=3)
        optionsFrame.grid_columnconfigure(1, weight=3)
        optionsFrame.grid_columnconfigure(2, weight=1)

        row = 0
        checkButtonFrame = Frame(optionsFrame)
        checkButtonFrame.grid(row=row, column=0, columnspan=3, padx=padX, pady=padY, sticky='ew')
        checkButtonFrame.grid_columnconfigure(0, weight=3)
        checkButtonFrame.grid_columnconfigure(1, weight=3)
        checkButtonFrame.grid_columnconfigure(2, weight=1)

        #PULSE TEST current/resistance range checkbox
        self.allDevicesCheckBox = Checkbutton(checkButtonFrame, text='Hard Code Full Grid', 
                                              font=labelFont, anchor='w', variable=self.applyToAllDevices)
        self.applyToAllDevices.trace_add('write',
                                         lambda * args: self.resetCycle(self.applyToAllDevices.get(), args))
        self.allDevicesCheckBox.grid(row=0, column=0, padx=padX, pady=padY, sticky='ew')
        
                
        self.readImageCheckBox = Checkbutton(checkButtonFrame, text = 'Read', font=labelFont, anchor='w', variable = self.readImage)
        self.readImageCheckBox.grid(row = 0, column = 0, padx=10, pady=(padY, 1), sticky='ew')
        self.readImage.trace_add('write', lambda * args: self.toggleReadImageFrame(self.readImage.get()))
        self.readImageCheckBox.grid_forget()

        self.writeImageCheckBox = Checkbutton(checkButtonFrame, text = 'Write', font=labelFont, anchor='w', variable = self.writeImage)
        self.writeImageCheckBox.grid(row = 1, column = 0, padx=10, pady=(padY, 1), sticky='ew')
        self.writeImage.trace_add('write', lambda * args: self.toggleWriteImageFrame( self.writeImage.get(), args))
        self.writeImageCheckBox.grid_forget()

        self.utilizeCurResRangeCheckBoxButton = Checkbutton(checkButtonFrame, text = 'Range Verification', anchor='w', font=labelFont, variable = self.utilizeCurResRange)
        self.utilizeCurResRangeCheckBoxButton.grid(row = 1, column = 0, padx=10, pady=(padY, 1), sticky='ew')
        self.utilizeCurResRange.trace_add('write', 
                lambda * args:self.toggleRangeFrame(self.utilizeCurResRange.get(), args))


        self.gateRangeCheckBox = Checkbutton(checkButtonFrame, text = 'Gate Range', font=labelFont, anchor='w', variable = self.gateRangeTest)
        self.gateRangeCheckBox.grid(row = 2, column = 0, padx=10, pady=(padY, 1), sticky='ew')
        self.gateRangeTest.trace_add('write', lambda * args: self.toggleGateRangeFrame( self.gateRangeTest.get(), args))

        self.kernelProcessingTestCheckBox = Checkbutton(checkButtonFrame, text = 'Signal Processing', font=labelFont, anchor='w', variable = self.kernelProcessingTest)
        self.kernelProcessingTestCheckBox.grid(row = 2, column = 1, padx=10, pady=(padY, 1), sticky='ew')
        self.kernelProcessingTest.trace_add('write', lambda * args: self.toggleSignalProcessingFrame( self.kernelProcessingTest.get(), args))

        
        self.retentionCheckBox = Checkbutton(checkButtonFrame, text = 'Retention', font=labelFont, anchor='w', variable = self.retentionTest)
        self.retentionCheckBox.grid(row = 0, column = 1, padx=10, pady=(padY, 1), sticky='ew')
        self.retentionTest.trace_add('write', lambda * args: self.toggleRetentionFrame( self.retentionTest.get(), args))


        self.exportCheckBox = Checkbutton(checkButtonFrame, text='Export to CSV', 
                                          font=labelFont, anchor='w', variable=self.csvControlVariable)
        self.exportCheckBox.grid(row=1, column=1, padx=padX, pady=padY, sticky='ew')


        self.heatMapCheckBox = Checkbutton(checkButtonFrame, text='Make Heatmap', 
                                           font=labelFont, anchor='w', variable=self.createHeatMap)
        self.heatMapCheckBox.grid(row=0, column=2, padx=padX, pady=padY, sticky='ew')

        self.createPlots = Checkbutton(checkButtonFrame, text='Create Plots', 
                                       font=labelFont, anchor='w', variable = self.createSavePlots)
        self.createPlots.grid(row=1, column=2, padx=padX, pady=padY, sticky='ew')

        unitButtonFrame = Frame(checkButtonFrame)
        unitButtonFrame.grid(row=2, column=2, padx=(20, 1), pady=(padY, 2), sticky='ew')
        # unitButtonFrame.grid_columnconfigure(0, weight=1)

        #display of non-Voltage units
        self.unitButtonLabel = Label(unitButtonFrame, text = 'Unit:', font=labelFont, anchor='w')
        self.unitButtonLabel.grid(row = 0, column = 0, padx=2, pady=(padY, 1), sticky='e')

        #calls built-in "toggleOhmsLawUnit" function when pressed AND displays
        #the current/changed unit on the button
        self.unitButton = Button(unitButtonFrame, text=self.toggledOhmsLawUnit.get(), 
                            command = lambda:self.toggleUnitButton(self.toggledOhmsLawUnit,self.unitButton, self.unitList),
                            width = 5, padx = 2, pady = 1, 
                            bg = 'lightgreen')
        self.unitButton.grid(row = 0, column = 1, padx=1, pady=(padY, 1), sticky='e')


        
        pulseCanvasRow += 1
# --------------------------------------------------------------------------------------
        # spaceLabel = Label(self.pulseCanvas, text = ' ', font=labelFont, anchor='w')
        # spaceLabel.grid(row = pulseCanvasRow, column = 0, columnspan=5, padx = padX, pady = 1, sticky='nsew')
# --------------------------------------------------------------------------------------
        

        pulseCanvasRow += 1
        self.rangeFrameRow = pulseCanvasRow
        self.rangeFrame = LabelFrame(self.pulseCanvas, text = 'Read-Write Range', labelanchor = 'nw', font=labelFont)
        self.rangeFrame.grid(row=self.rangeFrameRow, column=2, padx=(10, 10), pady=(10, 2), sticky='ew')
        
        self.rangeFrame.grid_forget() # start hidden

        self.rangeFrame.grid_columnconfigure(1, weight=1)
        
        # Field definitions: (row, label1_text, var1, label2_text, var2)
        range_fields = [
            (0, 'HRS Min:', self.hrsRangeMin, 'Max:', self.hrsRangeMax, 'uA'),
            (1, 'LRS Min:', self.lrsRangeMin, 'Max:', self.lrsRangeMax, 'uA'),
            (2, 'Min VRst:', self.minResetVoltage, 'Min VG:', self.minGateVoltage, 'V')
        ]

        self.unitList = []
        self.rangeEntries = []
        for row, min_label_text, min_var, max_label_text, max_var, unit in range_fields:
            # Left (Min) Frame (now also includes range reset voltage)
            min_frame = Frame(self.rangeFrame)
            min_frame.grid(row=row, column=0, padx=(20, 1), pady=padY, sticky='ew')

            min_label = Label(min_frame, text=min_label_text, font=labelFont)
            min_label.grid(row=0, column=0, padx=padX, pady=padY, sticky='ew')

            min_entry = Entry(min_frame, width=7, textvariable=min_var, font=labelFont, bg='white')
            min_entry.grid(row=0, column=1, padx=(padX, 1), pady=padY, sticky='ew')

            min_unit_label = Label(min_frame, width=4, text=unit, font=labelFont)
            min_unit_label.grid(row=0, column=2, padx=1, pady=padY, sticky='ew')

            # Dash label between min and max (but not the reset and gate voltages)
            if (row != 2):
                range_dash_label = Label(self.rangeFrame, text='-', font=labelFont)
                range_dash_label.grid(row=row, column=1, padx=padX, pady=padY)

            # Right (Max) Frame (now also includes range gate voltage)
            max_frame = Frame(self.rangeFrame)
            max_frame.grid(row=row, column=2, padx=(1,20), pady=padY, sticky='ew')

            max_label = Label(max_frame, text=max_label_text, font=labelFont)
            max_label.grid(row=0, column=0, padx=padX, pady=padY, sticky='ew')

            max_entry = Entry(max_frame, width=7, textvariable=max_var, font=labelFont, bg='white')
            max_entry.grid(row=0, column=1, padx=(padX, 1), pady=padY, sticky='ew')

            max_unit_label = Label(max_frame, width=4,text=unit, font=labelFont)
            max_unit_label.grid(row=0, column=2, padx=1, pady=padY, sticky='ew')

            self.rangeEntries.append(min_entry)
            self.rangeEntries.append(max_entry)
            # Store unit labels for later use
            self.unitList.append(min_unit_label)
            self.unitList.append(max_unit_label)

        row += 1
        #maximum number of cycles to check the established range label and entry box
        frame = Frame(self.rangeFrame)
        frame.grid(row = row, column = 0, columnspan=3, padx = padX, pady = padY)

        self.rangeMaxCycleLabel = Label(frame, text = 'Max Cycle Limit: ', font=labelFont)
        self.rangeMaxCycleLabel.grid(row = 2, column = 1, padx = padX, pady = padY, sticky='w')
        self.rangeMaxCycleEntry = Entry(frame, width = 6, 
                                        textvariable = self.pulseTestRangeCycleCount, font=labelFont, bg = 'white')
        self.rangeMaxCycleEntry.grid(row = 2, column = 2, padx = padX, pady = padY, sticky='w')

        self.rangeEntries.append(self.rangeMaxCycleEntry)

        # --------------------------------------------------------------------------------------

        pulseCanvasRow += 1
        self.retentionFrameRow = pulseCanvasRow
        self.retentionFrame = LabelFrame(self.pulseCanvas, text = 'Retention', labelanchor = 'nw', font=labelFont)
        self.retentionFrame.grid(row=self.retentionFrameRow, column=2, padx=(10, 10), pady=(10, 2), sticky='ew')
        self.retentionFrame.grid_forget()

        self.retentionTimeLabel = Label(self.retentionFrame, text = 'Retention Time: ', font=labelFont)
        self.retentionTimeLabel.grid(row = 0, column = 0, padx = (20, padX), pady = padY, sticky='w')

        self.retentionTimeEntry = Entry(self.retentionFrame, width = 7, 
                                        textvariable = self.retentionTime, font=labelFont, bg = 'white')
        self.retentionTimeEntry.grid(row = 0, column = 1, padx = (padX, 1), pady = padY, sticky='w')
        self.retentionTimeUnit = Label(self.retentionFrame, text = 's', font=labelFont)
        self.retentionTimeUnit.grid(row = 0, column = 2, padx = (1, padX), pady = padY, sticky='w')

        self.retentionCycleLabel = Label(self.retentionFrame, text = 'Retention Cycles: ', font=labelFont)
        self.retentionCycleLabel.grid(row = 0, column = 3, padx = (20, padX), pady = padY, sticky='w')

        self.retentionCycleEntry = Entry(self.retentionFrame, width = 7, 
                                        textvariable = self.retentionCycles, font=labelFont, bg = 'white')
        self.retentionCycleEntry.grid(row = 0, column = 4, padx = (padX, 1), pady = padY, sticky='w')
        self.retentionCycleUnit = Label(self.retentionFrame, text = 'cycles', font=labelFont)
        self.retentionCycleUnit.grid(row = 0, column = 5, padx = (1, padX), pady = padY, sticky='w')

        pulseCanvasRow += 1
        self.gateRangeFrameRow = pulseCanvasRow
        self.gateRangeFrame = LabelFrame(self.pulseCanvas, text = 'Gate Range', labelanchor = 'nw', font=labelFont)
        self.gateRangeFrame.grid(row=self.gateRangeFrameRow, column=2, padx=(10, 10), pady=(10, 2), sticky='ew')
        self.gateRangeFrame.grid_forget()

        self.gateMinRangeLabel = Label(self.gateRangeFrame, text = 'Min : ', font=labelFont)
        self.gateMinRangeLabel.grid(row = 0, column = 0, padx = (20, padX), pady = padY, sticky='w')

        self.gateMinRangeEntry = Entry(self.gateRangeFrame, width = 7, 
                                        textvariable = self.gateRangeMin, font=labelFont, bg = 'white')
        self.gateMinRangeEntry.grid(row = 0, column = 1, padx = (padX, 1), pady = padY, sticky='w')
        self.gateMinRangeUnit = Label(self.gateRangeFrame, text = 'V', font=labelFont)

        label = Label(self.gateRangeFrame, text=' - ', font=labelFont)
        label.grid(row = 0, column = 2, padx = (1, padX), pady = padY, sticky='w')

        self.gateMaxRangeLabel = Label(self.gateRangeFrame, text = 'Max : ', font=labelFont)
        self.gateMaxRangeLabel.grid(row = 0, column = 3, padx = (1, padX), pady = padY, sticky='w')

        self.gateMaxRangeEntry = Entry(self.gateRangeFrame, width = 7, 
                                        textvariable = self.gateRangeMax, font=labelFont, bg = 'white')
        self.gateMaxRangeEntry.grid(row = 0, column = 4, padx = (padX, 1), pady = padY, sticky='w')
        
        self.gateMaxRangeUnit = Label(self.gateRangeFrame, text = 'V', font=labelFont)
        self.gateMaxRangeUnit.grid(row = 0, column = 5, padx = (1, padX), pady = padY, sticky='w')

        self.rowColLabel = Label(self.gateRangeFrame, text = 'Direction: ', font=labelFont)
        self.rowColLabel.grid(row = 0, column = 6, padx = (1, padX), pady = padY, sticky='w')

        self.rowColumnButton = Button(self.gateRangeFrame, text=self.rowColumnVariable.get(), 
                            command = lambda:self.toggleRowColButton(self.rowColumnVariable, self.rowColumnButton),
                            width = 5, padx = 2, pady = 1, 
                            bg = 'lightgreen')
        self.rowColumnButton.grid(row = 0, column = 7, padx=1, pady=(padY, 1), sticky='e')


        # --------------------------------------------------------------------------------------
        pulseCanvasRow += 1
        self.WriteImageFrameRow = pulseCanvasRow
        self.writeImageFrame = LabelFrame(self.pulseCanvas, text='Write Image Parameters', font=('calibre', 12))
        self.writeImageFrame.grid(row=self.WriteImageFrameRow, column=2, padx=(10, 10), pady=(10, 2), sticky='ew')
        self.writeImageFrame.grid_forget()
        self.writeImageFrame.grid_columnconfigure(2, weight=1)


        Label(self.writeImageFrame, text='Values: [0, ', font=('calibre', 12)).grid(row=1, column=1, padx=(20,0), pady=5, sticky='ew')
        Entry(self.writeImageFrame, textvariable=self.rangeValuesStr, font=('calibre', 12)).grid(row=1, column=2, padx=(0,10), pady=5, sticky='ew')
        Label(self.writeImageFrame, text=']', font=('calibre', 12)).grid(row=1, column=3, padx=(0,10), pady=5, sticky='w')
        Label(self.writeImageFrame, text='[0~1]', font=('calibre', 12)).grid(row=1, column=4, padx=(0,10), pady=5, sticky='w')

        self.resisterValuesLabel = Label(self.writeImageFrame, text='Levels: [', font=('calibre', 12))
        self.resisterValuesLabel.grid(row=2, column=1, padx=(20, 0), pady=5)
        Entry(self.writeImageFrame, textvariable=self.rangeLevelsStr, font=('calibre', 12)).grid(row=2, column=2, padx=(0, 10), pady=5, sticky='ew')
        Label(self.writeImageFrame, text=']', font=('calibre', 12)).grid(row=2, column=3, padx=(0, 10), pady=5, sticky='w')
        unitLabel = Label(self.writeImageFrame, text=self.getUnit(self.toggledOhmsLawUnit), font=('calibre', 12))
        unitLabel.grid(row=2, column=4, padx=(0, 10), pady=5, sticky='w')
        self.unitList.append(unitLabel)

        self.parametersFrame = Frame(self.writeImageFrame)
        self.parametersFrame.grid(row=3, column=1, columnspan=3, padx=0, pady=0, sticky='ew')
        self.parametersFrame.grid_columnconfigure(0, weight=1)
        self.parametersFrame.grid_columnconfigure(7, weight=1)

 
        Label(self.parametersFrame, text='Gate Range Threshold: ', font=('calibre', 12)).grid(row=0, column=1, padx=(20, 0), pady=5, sticky='ew')
        Entry(self.parametersFrame, textvariable=self.gateRangeThreshold, font=('calibre', 12), width=5).grid(row=0, column=2,  padx=(0, 10), pady=5, sticky='ew')
        unitLabel = Label(self.parametersFrame, text=self.getUnit(self.toggledOhmsLawUnit), font=('calibre', 12))
        unitLabel.grid(row=0, column=3, padx=(0, 10), pady=5, sticky='w')
        self.unitList.append(unitLabel)

        Label(self.parametersFrame, text='Gate Step Voltage: ', font=('calibre', 12)).grid(row=0, column=4, padx=(20, 0), pady=5, sticky='ew')
        Entry(self.parametersFrame, textvariable=self.gateStepVoltage, font=('calibre', 12), width=5).grid(row=0, column=5, padx=(0, 10), pady=5, sticky='ew')
        Label(self.parametersFrame, text='V', font=('calibre', 12)).grid(row=0, column=6, padx=(0, 10), pady=5, sticky='w')


        Label(self.parametersFrame, text='Level Tolerance: ±', font=('calibre', 12)).grid(row=1, column=1, padx=(20, 0), pady=5, sticky='ew')
        Entry(self.parametersFrame, textvariable=self.levelTolerance, font=('calibre', 12), width=5).grid(row=1, column=2, padx=(0, 0), pady=5, sticky='ew')
        Label(self.parametersFrame, text='%', font=('calibre', 12)).grid(row=1, column=3, padx=(0, 10), pady=5, sticky='w')
        

        Label(self.parametersFrame, text='Verify Cycles: ', font=('calibre', 12)).grid(row=1, column=4, padx=(20, 0), pady=5, sticky='ew')
        Entry(self.parametersFrame, textvariable=self.verifyCycles, font=('calibre', 12), width=5).grid(row=1, column=5, padx=(0, 0), pady=5, sticky='ew')
        #Label(self.parametersFrame, text='Cyc', font=('calibre', 12)).grid(row=1, column=6, padx=(1, 10), pady=5, sticky='w')

        Label(self.parametersFrame, text='Gate Voltage Min: ', font=('calibre', 12)).grid(row=2, column=1, padx=(20, 0), pady=5, sticky='ew')
        Entry(self.parametersFrame, textvariable=self.gateVoltageMin, font=('calibre', 12), width=5).grid(row=2, column=2, padx=(0, 0), pady=5, sticky='ew')
        Label(self.parametersFrame, text='V', font=('calibre', 12)).grid(row=2, column=3, padx=(0, 10), pady=5, sticky='w')
        

        Label(self.parametersFrame, text='Gate Voltage Max: ', font=('calibre', 12)).grid(row=2, column=4, padx=(20, 0), pady=5, sticky='ew')
        Entry(self.parametersFrame, textvariable=self.gateVoltageMax, font=('calibre', 12), width=5).grid(row=2, column=5, padx=(0, 0), pady=5, sticky='ew')
        Label(self.parametersFrame, text='V', font=('calibre', 12)).grid(row=2, column=6, padx=(0, 10), pady=5, sticky='w')


        Label(self.parametersFrame, text='Reset Voltage Min: ', font=('calibre', 12)).grid(row=3, column=1, padx=(20, 0), pady=5, sticky='ew')
        Entry(self.parametersFrame, textvariable=self.resetVoltageMin, font=('calibre', 12), width=5).grid(row=3, column=2, padx=(0, 0), pady=5, sticky='ew')
        Label(self.parametersFrame, text='V', font=('calibre', 12)).grid(row=3, column=3, padx=(0, 10), pady=5, sticky='w')
        

        Label(self.parametersFrame, text='Reset Voltage Max: ', font=('calibre', 12)).grid(row=3, column=4, padx=(20, 0), pady=5, sticky='ew')
        Entry(self.parametersFrame, textvariable=self.resetVoltageMax, font=('calibre', 12), width=5).grid(row=3, column=5, padx=(0, 0), pady=5, sticky='ew')
        Label(self.parametersFrame, text='V', font=('calibre', 12)).grid(row=3, column=6, padx=(0, 10), pady=5, sticky='w')
        # --------------------------------------------------------------------------------------

        # ----- Signal Processing Frame-----
        pulseCanvasRow += 1
        self.kernelProcessingFrameRow = pulseCanvasRow
        
        self.kernelProcessingFrame = LabelFrame(self.pulseCanvas, text='Signal Processing', font=labelFont, labelanchor='nw')
        self.kernelProcessingFrame.grid(row=self.kernelProcessingFrameRow , column=0, rowspan=3, columnspan=5, padx=(10, 10), pady=(2, 2), sticky='nsew')
        self.kernelProcessingFrame.grid_forget()
        self.kernelProcessingFrame.grid_columnconfigure(1, weight=1)

        row=1
        # Signal Processing label
        Label(self.kernelProcessingFrame, text='Kernel :', font=('calibre', 12), anchor='w').grid(row=row, column=0, padx=(10, 0), pady=(10, 10), sticky='ew')
        Entry(self.kernelProcessingFrame, textvariable=self.kernelMatStr, font=('calibre', 12), width=5).grid(row=row, column=1, padx=(5, 10), pady=(10, 10), sticky='ew')
        

        

        row += 1

        # ----- Pulse Control Frame -----
        pulseCanvasRow += 4
        self.pulseCanvas.grid_rowconfigure(pulseCanvasRow, weight=1)
        controlFrame = Frame(self.pulseCanvas)
        controlFrame.grid(row=pulseCanvasRow, column=0, rowspan=3, columnspan=5, padx=(10, 10), pady=(2, 2), sticky='nsew')

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

    def resetCycle(self, reset, args):
        if(reset):
            self.cycleNumber.set(1)
            self.cycleNumberEntry.config(state = 'disabled')
        else:
            self.cycleNumberEntry.config(state = 'normal')



            # (row + 1, 0, 'Gate Voltage:', self.gateVoltage, 'V'),
            # (row + 1, 2, 'Delay Period:', self.delayPeriodTime, 'us'),
            # # leave space for the buttons.
            # (row + 3, 0, 'Form Voltage:', self.formSetVoltage, 'V'),
            # (row + 2, 2, 'Read 1 Voltage:', self.formSetReadVoltage, 'V'),
            # (row + 4, 0, 'Form Time:', self.formSetTime, 'us'),
            # (row + 3, 2, 'Read 1 Time:', self.formSetReadTime, 'us'),
            # (row + 5, 0, 'Reset Voltage:', self.resetVoltage, 'V'),
            # (row + 4, 2, 'Read 2 Voltage:', self.resetReadVoltage, 'V'),
            # (row + 6, 0, 'Reset Time:', self.resetTime, 'us'),
            # (row + 5, 2, 'Read 2 Time:', self.resetReadTime, 'us'),
            # (row + 6, 2, 'Cycles:', self.cycleNumber, 'cyc'),
    def toggleBinaryMode(self, state, *args):
        self.binaryMode.set(state)
        if not state:
            self.utilizeCurResRange.set(False)
            self.applyToAllDevices.set(False)
            self.gateRangeTest.set(False)
            self.utilizeCurResRangeCheckBoxButton.grid_forget()
            self.allDevicesCheckBox.grid_forget()
            self.gateRangeCheckBox.grid_forget()

            self.changeFORMSETState('SET')
            self.FORMSelectButton.config(state='disabled')

            self.setResetVoltages(False)
            
            self.readImage.set(True)
            self.writeImageCheckBox.grid(row = 1, column = 0, padx=10, pady=(2, 1), sticky='ew')
            self.readImageCheckBox.grid(row = 0, column = 0, padx=10, pady=(2, 1), sticky='ew')

        else:
            self.allDevicesCheckBox.grid(row=0, column=0, padx=5, pady=2, sticky='ew')
            self.utilizeCurResRangeCheckBoxButton.grid(row = 1, column = 0, padx=10, pady=(2, 1), sticky='ew')
            self.gateRangeCheckBox.grid(row = 2, column = 0, padx=10, pady=(2, 1), sticky='ew')

            self.FORMSelectButton.config(state='normal')

            self.setResetVoltages(True)

            self.writeImageCheckBox.grid_forget()
            self.readImageCheckBox.grid_forget()
            
            self.writeImage.set(False)
            self.writeImageFrame.grid_forget()
            
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



    def toggleSignalProcessingFrame(self, state, *args):
        if state:
            self.kernelProcessingFrame.grid(row=self.kernelProcessingFrameRow , column=0, rowspan=3, columnspan=5, padx=(10, 10), pady=(2, 2), sticky='nsew')
        else:
            self.kernelProcessingFrame.grid_forget()



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



    def toggleRangeFrame(self, state, *args):
        self.resetCycle(state, args)
        if not state:
            self.rangeFrame.grid_forget()
            self.entryWidgets['Cycles']['Entry'].config(state = 'normal')
        else:
            self.retentionTest.set(False)
            self.entryWidgets['Cycles']['Entry'].config(state = 'disabled')
            self.rangeFrame.grid(row = self.rangeFrameRow, column=2, rowspan=4, padx=(10, 10), pady=(1, 10), sticky='ew')

    def toggleRetentionFrame(self, state, *args):
        self.resetCycle(state, args)
        if not state:
            self.utilizeCurResRangeCheckBoxButton.config(state = 'normal')
            self.allDevicesCheckBox.config(state = 'normal')
            # self.exportCheckBox.config(state = 'normal')
            self.cycleNumberEntry.config(state = 'normal')
            self.retentionFrame.grid_forget()
        else:
            self.utilizeCurResRange.set(False)
            self.utilizeCurResRangeCheckBoxButton.config(state = 'disabled')
            self.applyToAllDevices.set(False)
            self.allDevicesCheckBox.config(state = 'disabled')
            # self.csvControlVariable.set(True)
            # self.exportCheckBox.config(state = 'disabled')
            self.cycleNumberEntry.config(state = 'disabled') # cycles will be disabled since they are ignored in code anyway
            self.retentionFrame.grid(row = self.retentionFrameRow, column=2, rowspan=4, padx=(10, 10), pady=(1, 10), sticky='ew')

    #   (row + 1, 0, 'Gate Voltage:', self.gateVoltage, 'V'),
    #     (row + 1, 2, 'Delay Period:', self.delayPeriodTime, 'us'),
    #     # leave space for the buttons.
    #     (row + 3, 0, 'Form Voltage:', self.formSetVoltage, 'V'),
    #     (row + 2, 2, 'Read 1 Voltage:', self.formSetReadVoltage, 'V'),
    #     (row + 4, 0, 'Form Time:', self.formSetTime, 'us'),
    #     (row + 3, 2, 'Read 1 Time:', self.formSetReadTime, 'us'),
    #     (row + 5, 0, 'Reset Voltage:', self.resetVoltage, 'V'),
    #     (row + 4, 2, 'Read 2 Voltage:', self.resetReadVoltage, 'V'),
    #     (row + 6, 0, 'Reset Time:', self.resetTime, 'us'),
    #     (row + 5, 2, 'Read 2 Time:', self.resetReadTime, 'us'),
    #     (row + 6, 2, 'Cycles:', self.cycleNumber, 'cyc'),
    def toggleGateRangeFrame(self, state, *args):
        if not state:
            self.gateRangeFrame.grid_forget()
            self.changeFORMSETState('SET') # Stacia's note: I don't know why this is in here?
            self.toggleRetentionFrame(self.retentionTest.get(), args)
            self.resetVoltage.set(1.8)
            self.resetTime.set(100)
            self.formSetReadVoltage.set(0.2)
            self.formSetReadTime.set(500)
            self.cycleNumber.set(1)
            self.entryWidgets['Reset Voltage']['Entry'].config(state = 'normal')
            self.entryWidgets['Reset Time']['Entry'].config(state = 'normal')
            self.entryWidgets['Read 1 Voltage']['Entry'].config(state = 'normal')
            self.entryWidgets['Read 1 Time']['Entry'].config(state = 'normal')
            self.entryWidgets['Cycles']['Entry'].config(state = 'normal')
            self.allDevicesCheckBox.config(state = 'normal')
        else:
            self.toggleRetentionFrame(False, args)
            self.resetVoltage.set(0)
            self.resetTime.set(0)
            self.formSetReadVoltage.set(0)
            self.formSetReadTime.set(0)
            self.cycleNumber.set(1)
            self.entryWidgets['Reset Voltage']['Entry'].config(state = 'disabled')
            self.entryWidgets['Reset Time']['Entry'].config(state = 'disabled')
            self.entryWidgets['Read 1 Voltage']['Entry'].config(state = 'disabled')
            self.entryWidgets['Read 1 Time']['Entry'].config(state = 'disabled')
            self.applyToAllDevices.set(False)
            self.allDevicesCheckBox.config(state = 'disabled')
            self.cycleNumberEntry.config(state = 'disabled')

            self.gateRangeFrame.grid(row = self.gateRangeFrameRow, column=2, rowspan=4, padx=(10, 10), pady=(1, 10), sticky='ew')
   
    def toggleRowColButton(self, var: StringVar, button: Button):
        if(var.get() == 'Row'):
            var.set('Col')
        else:
            var.set('Row')

        button.config(text = var.get())


    def changeFORMSETState(self, stateString):
        self.formSetVoltageLabel.config(text = ''.join([stateString, ' Voltage:']))
        self.formSetTimeLabel.config(text = ''.join([stateString, ' Time:']))
        self.formSetStateString.set(stateString)

            
        if(stateString == 'FORM'): #if FORM state, configure GUI to prepare for FORM inputs
            #change associated button color to green to show it's selected
            self.FORMSelectButton.config(bg = 'lightgreen')
            self.SETSelectButton.config(bg = 'light gray') #set other button color to the default

            #change which voltage string is being displayed next to the corresponding entry
            #AND set the Entry value to the default value of THIS specific state
            self.formSetVoltage.set(3.3) #voltage, CHANGE IF NECESSARY

        else: #otherwise, SET state, configure GUI to prepare for SET inputs
            #change associated button color to green to show it's selected
            self.SETSelectButton.config(bg = 'lightgreen')
            self.FORMSelectButton.config(bg = 'light gray') #set other button color to the default

            #change which voltage string is being displayed next to the corresponding entry
            #AND set the Entry value to the default value of THIS specific state
            self.formSetVoltage.set(2) #voltage, CHANGE IF NECESSARY
