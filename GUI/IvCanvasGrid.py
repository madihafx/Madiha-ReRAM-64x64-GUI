from tkinter import BooleanVar, Canvas,  Label, Button, Entry, Listbox,LabelFrame, Frame, Checkbutton, Scrollbar, CENTER, SUNKEN, StringVar
import tkinter as tk

from .BaseCanvas import BaseCanvas

class IVCanvasGrid(BaseCanvas):

    def __init__(self, canvasFrame:Frame):
        BaseCanvas.__init__(self, canvasFrame)
        
        canvasFrame.grid_rowconfigure(0, weight=1)
        canvasFrame.grid_columnconfigure(0, weight=1)
        canvasFrame.grid_rowconfigure(1, weight=1)
        canvasFrame.grid_columnconfigure(1, weight=1)
        canvasFrame.grid_rowconfigure(2, weight=1)
        canvasFrame.grid_columnconfigure(2, weight=1)

        self.IVCanvas = Canvas(canvasFrame)
        
        self.IVCanvas.grid(row=0, column=0, sticky='nsew')
        self.startRun:bool = True
        self.modeState.set('iv_test')

        self.setDefaultValues()
        self.createIVCanvas()

        #CALL FUNCTION TO SET THE FORM STATE AS THE FIRST SELECTED
        #IV MODE STATE WHILE DISABLING INTERACTIONS WITH ALL OTHER
        #FRAMES UNTIL THEIR BUTTONS ARE PRESSED
        self.changeIVState('FORM')
        
        self.startRun = False
    
    def setDefaultValues(self):
        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE IV
        #CANVAS TO THEIR PULSE TEST DEFAULTS
        self.IvTestState.set('FORM')

        #SET ALL DEFAULT VALUES THAT GET CHANGED IN THE BASE
        #CANVAS TO THEIR PULSE STEP TEST DEFAULTS
        #NOTE: These ones are automatically changed between
        #IV test modes and, should the user go back to the Pulse
        #Test window, NOT RESETTING THESE will have these set
        #to 0 and this is done to avoid tedium
        self.gateVoltage.set(1.5)
        self.gateCycleVoltage.set(0)
        self.formSetStateString.set('')
        self.formSetVoltage.set(0)
        self.formSetTime.set(0)
        self.formSetReadVoltage.set(3.3) 
        self.formSetReadTime.set(500)
        self.resetVoltage.set(0)
        self.resetTime.set(0)
        self.resetReadVoltage.set(0) 
        self.resetReadTime.set(0) 
        self.stepNumber.set(25)
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

    def createIVCanvas(self):
        
        self.IVCanvas.grid_columnconfigure(0, weight=4) #first column
        self.IVCanvas.grid_columnconfigure(1, weight=2)
        self.IVCanvas.grid_columnconfigure(2, weight=0)
        self.IVCanvas.grid_columnconfigure(3, weight=2)
        self.IVCanvas.grid_columnconfigure(4, weight=4) #last column

        
        IVCanvasRow = 0
        # Title
        self.titleIVLabel = Label(self.IVCanvas, text='IV Test Mode', font=('calibre', 20, 'bold'))
        self.titleIVLabel.grid(row = IVCanvasRow, column=0, columnspan=5, pady=(10, 5), sticky='nsew')

        IVCanvasRow += 1
        TestNameFrame = Frame(self.IVCanvas)
        TestNameFrame.grid(row = IVCanvasRow, column=0, columnspan=5, padx=10, pady=(10, 5), sticky='nsew')

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

        labelFont = ('calibre', 8, 'normal')
        labelWidth = 13
        padX = 5
        padY = 2

        rightFramePadX = 5
        
        IVCanvasRow += 1
        row = 0

        #-------------------------------------------------------------------------------------------

        #create the FORM, SET, RESET and (unique) IV Mode Frames in the same row

        #FORM
        self.FORMFrame = LabelFrame(self.IVCanvas, text = 'FORM Mode', font=labelFont, labelanchor = 'nw')
        self.FORMFrame.grid(row = IVCanvasRow, column = 1, sticky='nsew')

        # Store widgets in case you want to reference them later
        self.entryFORMWidgets = {}

        # Only the mid column should expand
        # entryFrame.grid_columnconfigure(1, weight=1)

        fieldsFORM = [
            (row + 2, 0, 'Gate Voltage:', self.gateVoltage, 'V'),
            (row + 3, 0, 'Delay Period:', self.delayPeriodTime, 'us'),            
            (row + 4, 0, 'Read 1 Voltage:', self.formSetReadVoltage, 'V'),
            (row + 5, 0, 'Read 1 Time:', self.formSetReadTime, 'us'),
            (row + 6, 0, 'Cycles:', self.cycleNumber, ''),
            (row + 7, 0, 'Step Number:', self.stepNumber, '')
        ]

        for row, col, label_text, var, unit in fieldsFORM:
            frameFORM = Frame(self.FORMFrame)
            frameFORM.grid(row=row, column=col, padx=5, pady=padY, sticky='ew')

            # frame.grid_columnconfigure(0, weight=1)
            # frame.grid_columnconfigure(1, weight=2)
            # frame.grid_columnconfigure(2, weight=1)

            labelFORM = Label(frameFORM, text=label_text, width=labelWidth, font=labelFont, anchor='w')
            labelFORM.grid(row=0, column=0, padx=(padX, 1), pady=padY, sticky='ew')

            entryFORMUnitFrame = Frame(frameFORM)
            entryFORMUnitFrame.grid(row=0, column=1, padx=(1,padX), pady=padY, sticky='ew')

            entryFORM = Entry(entryFORMUnitFrame, textvariable=var, width=7, font=labelFont, bg='white')
            entryFORM.grid(row=0, column=0, padx=padX, pady=padY, sticky='ew')

            unit_labelFORM = Label(entryFORMUnitFrame, text=unit, width=3, font=labelFont, anchor='w')
            unit_labelFORM.grid(row=0, column=1, padx=(1,padX),  pady=padY, sticky='ew')

            self.entryFORMWidgets[label_text.strip(':')] = {'Label':labelFORM, 'Entry':entryFORM}

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #SET (has same logic as FORM besides the IvTestState)
        self.SETFrame = LabelFrame(self.IVCanvas, text = 'SET Mode', font=labelFont, labelanchor = 'nw')
        self.SETFrame.grid(row = IVCanvasRow, column = 2, sticky='nsew', padx = rightFramePadX)

        # Store widgets in case you want to reference them later
        self.entrySETWidgets = {}

        # Only the mid column should expand
        # entryFrame.grid_columnconfigure(1, weight=1)

        fieldsSET = [
            (row + 2, 0, 'Gate Voltage:', self.gateVoltage, 'V'),
            (row + 3, 0, 'Delay Period:', self.delayPeriodTime, 'us'),            
            (row + 4, 0, 'Read 1 Voltage:', self.formSetReadVoltage, 'V'),
            (row + 5, 0, 'Read 1 Time:', self.formSetReadTime, 'us'),
            (row + 6, 0, 'Cycles:', self.cycleNumber, ''),
            (row + 7, 0, 'Step Number:', self.stepNumber, '')
        ]

        for row, col, label_text, var, unit in fieldsSET:
            frameSET = Frame(self.SETFrame)
            frameSET.grid(row=row, column=col, padx=5, pady=padY, sticky='ew')

            # frame.grid_columnconfigure(0, weight=1)
            # frame.grid_columnconfigure(1, weight=2)
            # frame.grid_columnconfigure(2, weight=1)

            labelSET = Label(frameSET, text=label_text, width=labelWidth, font=labelFont, anchor='w')
            labelSET.grid(row=0, column=0, padx=(padX, 1), pady=padY, sticky='ew')

            entrySETUnitFrame = Frame(frameSET)
            entrySETUnitFrame.grid(row=0, column=1, padx=(1,padX), pady=padY, sticky='ew')

            entrySET = Entry(entrySETUnitFrame, textvariable=var, width=7, font=labelFont, bg='white')
            entrySET.grid(row=0, column=0, padx=padX, pady=padY, sticky='ew')

            unit_labelSET = Label(entrySETUnitFrame, text=unit, width=3, font=labelFont, anchor='w')
            unit_labelSET.grid(row=0, column=1, padx=(1,padX),  pady=padY, sticky='ew')

            self.entrySETWidgets[label_text.strip(':')] = {'Label':labelSET, 'Entry':entrySET}

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #RESET
        self.RESETFrame = LabelFrame(self.IVCanvas, text = 'RESET Mode', font=labelFont, labelanchor = 'nw')
        self.RESETFrame.grid(row = IVCanvasRow, column = 3, sticky='nsew', padx = rightFramePadX)

        # Store widgets in case you want to reference them later
        self.entryRESETWidgets = {}

        # Only the mid column should expand
        # entryFrame.grid_columnconfigure(1, weight=1)

        fieldsRESET = [
            (row + 2, 0, 'Gate Voltage:', self.gateVoltage, 'V'),
            (row + 3, 0, 'Delay Period:', self.delayPeriodTime, 'us'),            
            (row + 4, 0, 'Read 2 Voltage:', self.resetReadVoltage, 'V'),
            (row + 5, 0, 'Read 2 Time:', self.resetReadTime, 'us'),
            (row + 6, 0, 'Cycles:', self.cycleNumber, ''),
            (row + 7, 0, 'Step Number:', self.stepNumber, '')
        ]

        for row, col, label_text, var, unit in fieldsRESET:
            frameRESET = Frame(self.RESETFrame)
            frameRESET.grid(row=row, column=col, padx=5, pady=padY, sticky='ew')

            # frame.grid_columnconfigure(0, weight=1)
            # frame.grid_columnconfigure(1, weight=2)
            # frame.grid_columnconfigure(2, weight=1)

            labelRESET = Label(frameRESET, text=label_text, width=labelWidth, font=labelFont, anchor='w')
            labelRESET.grid(row=0, column=0, padx=(padX, 1), pady=padY, sticky='ew')

            entryRESETUnitFrame = Frame(frameRESET)
            entryRESETUnitFrame.grid(row=0, column=1, padx=(1,padX), pady=padY, sticky='ew')

            entryRESET = Entry(entryRESETUnitFrame, textvariable=var, width=7, font=labelFont, bg='white')
            entryRESET.grid(row=0, column=0, padx=padX, pady=padY, sticky='ew')

            unit_labelRESET = Label(entryRESETUnitFrame, text=unit, width=3, font=labelFont, anchor='w')
            unit_labelRESET.grid(row=0, column=1, padx=(1,padX),  pady=padY, sticky='ew')

            self.entryRESETWidgets[label_text.strip(':')] = {'Label':labelRESET, 'Entry':entryRESET}

        # - - - - - - - - - - - - - - - - - - - - - - - -

        #(unique) IV State Mode
        self.IVModeFrame = LabelFrame(self.IVCanvas, text = 'IV Mode', font=labelFont, labelanchor = 'nw')
        self.IVModeFrame.grid(row = IVCanvasRow, column = 4, sticky='nsew', padx = rightFramePadX)

        # Store widgets in case you want to reference them later
        self.entryIVModeWidgets = {}

        # Only the mid column should expand
        # entryFrame.grid_columnconfigure(1, weight=1)

        fieldsIVMode = [
            (row + 2, 0, 'SET Gate Volt:', self.gateVoltage, 'V'),
            (row + 3, 0, 'RESET Gate V:', self.gateCycleVoltage, 'V'),
            (row + 4, 0, 'Delay Period:', self.delayPeriodTime, 'us'),            
            (row + 5, 0, 'Read 1 Voltage:', self.formSetReadVoltage, 'V'),
            (row + 6, 0, 'Read 1 Time:', self.formSetReadTime, 'us'),
            (row + 7, 0, 'Read 2 Voltage:', self.resetReadVoltage, 'V'),
            (row + 8, 0, 'Read 2 Time:', self.resetReadTime, 'us'),
            (row + 9, 0, 'Cycles:', self.cycleNumber, ''),
            (row + 10, 0, 'Step Number:', self.stepNumber, '')
        ]

        for row, col, label_text, var, unit in fieldsIVMode:
            frameIVMode = Frame(self.IVModeFrame)
            frameIVMode.grid(row=row, column=col, padx=5, pady=padY, sticky='ew')

            # frame.grid_columnconfigure(0, weight=1)
            # frame.grid_columnconfigure(1, weight=2)
            # frame.grid_columnconfigure(2, weight=1)

            labelIVMode = Label(frameIVMode, text=label_text, width=labelWidth, font=labelFont, anchor='w')
            labelIVMode.grid(row=0, column=0, padx=(padX, 1), pady=padY, sticky='ew')

            entryIVModeUnitFrame = Frame(frameIVMode)
            entryIVModeUnitFrame.grid(row=0, column=1, padx=(1,padX), pady=padY, sticky='ew')

            entryIVMode = Entry(entryIVModeUnitFrame, textvariable=var, width=7, font=labelFont, bg='white')
            entryIVMode.grid(row=0, column=0, padx=padX, pady=padY, sticky='ew')

            unit_labelIVMode = Label(entryIVModeUnitFrame, text=unit, width=3, font=labelFont, anchor='w')
            unit_labelIVMode.grid(row=0, column=1, padx=(1,padX),  pady=padY, sticky='ew')

            self.entryIVModeWidgets[label_text.strip(':')] = {'Label':labelIVMode, 'Entry':entryIVMode}

        #-------------------------------------------------------------------------------------------

        #create the buttons to select which of the IV mode states will be
        #tested when pressing the "Send" button
        self.FORMIVModeButton = Button(self.FORMFrame, text = 'Select FORM')
        self.FORMIVModeButton.config(command = lambda: self.changeIVState('FORM'), padx=1, pady=2, bg='light gray')
        self.FORMIVModeButton.grid(row = 1, column = 0, padx = padX, pady = padY, sticky='w')

        self.SETIVModeButton = Button(self.SETFrame, text = 'Select SET')
        self.SETIVModeButton.config(command = lambda: self.changeIVState('SET'), padx=1, pady=2, bg='light gray')
        self.SETIVModeButton.grid(row = 1, column = 0, padx = padX, pady = padY, sticky='w')

        self.RESETIVModeButton = Button(self.RESETFrame, text = 'Select RESET')
        self.RESETIVModeButton.config(command = lambda: self.changeIVState('RESET'), padx=1, pady=2, bg='light gray')
        self.RESETIVModeButton.grid(row = 1, column = 0, padx = padX, pady = padY, sticky='w')

        self.IVModeButton = Button(self.IVModeFrame, text = 'Select IV')
        self.IVModeButton.config(command = lambda: self.changeIVState('IV'), padx=1, pady=2, bg='light gray')
        self.IVModeButton.grid(row = 1, column = 0, padx = padX, pady = padY, sticky='w')


        #-------------------------------------------------------------------------------------------

        IVCanvasRow += 1

        # column 1, 2, 3
        optionsFrame = LabelFrame(self.IVCanvas, text='Options', font=labelFont, labelanchor = 'nw')
        optionsFrame.grid(row = IVCanvasRow, column = 1, columnspan=3, padx = padX, pady=(20, 10), sticky='ew')
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

        IVCanvasRow += 1
# --------------------------------------------------------------------------------------
        # spaceLabel = Label(self.pulseStepCanvas, text = ' ', font=labelFont, anchor='w')
        # spaceLabel.grid(row = pulseStepCanvasRow, column = 0, columnspan=5, padx = padX, pady = 1, sticky='nsew')
# --------------------------------------------------------------------------------------
        
        IVCanvasRow += 1
        
        # --------------------------------------------------------------------------------------


        # ----- IV Control Frame -----
        IVCanvasRow += 4
        self.IVCanvas.grid_rowconfigure(IVCanvasRow, weight=1)
        controlFrame = Frame(self.IVCanvas)
        controlFrame.grid(row=IVCanvasRow, column=0, rowspan=3, columnspan=5, padx=(10, 10), pady=(2, 2), sticky='nsew')

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

    # - - - - - - - - - - - - - - - - - - - - - - - - -

    #function to enable/disable which of the IV states is selected
    #upon pressing the "Send" button while resetting the state's default
    #values
    def changeIVState(self, inputtedState):

        for canvasWidget in self.IVCanvas.winfo_children(): #for all IV Canvas widgets

            #focus strictly on the labelFrame information
            if(isinstance(canvasWidget, tk.LabelFrame)):

                if('Mode' in canvasWidget.cget('text')): #ONLY FOCUS ON THE FOUR MODE CANVASES
                
                    #look at the name of the labelFrame and, if it does NOT have an exact
                    #match as newIVTestState, DISABLE ALL ENTRY WIDGETS, also
                    #reset the color of the buttons to their defaults if one of the
                    #state buttons was previously selected
                    #NOTE: In the unique case of "SET" being within "RESET", this specific
                    #condition will also be checked in the following IF statement by checking
                    #if the newIVTestState string is an EXACT match for the FIRST FULL
                    #WORD of the labelFrame title
                    if(inputtedState != canvasWidget.cget('text').split()[0]):

                        #get all widget descendants from all widget children
                        totalWrongWidgets = []
                        for differentIVStateWidget in canvasWidget.winfo_children():
                            
                            totalWrongWidgets.append(self.getAllWidgetDescendants(differentIVStateWidget))

                            if(isinstance(differentIVStateWidget, tk.Button)): #if the selection button
                                differentIVStateWidget.config(bg = 'light gray')

                        #flatten the list, because totalWrongWidgets is currently a list of lists
                        totalWrongWidgetsFlat = [item for sublist in totalWrongWidgets for item in sublist]

                        #now, disable all Entry widgets within totalWrongWidgets
                        for wrongWidget in totalWrongWidgetsFlat:
                            if(isinstance(wrongWidget, tk.Entry)):
                                wrongWidget.config(state = 'disabled') #disable Entry widget

                    #also, if the labelFrame is the one selected, ENABLE all Entry
                    #widgets AND set its corresponding button color to showcase that
                    #it's selected
                    else:

                        #get all widget descendants from all widget children
                        totalCorrectWidgets = []
                        for correctIVStateWidget in canvasWidget.winfo_children():
                            
                            totalCorrectWidgets.append(self.getAllWidgetDescendants(correctIVStateWidget))

                            if(isinstance(correctIVStateWidget, tk.Button)): #if the selection button
                                correctIVStateWidget.config(bg = 'light green')

                        #flatten the list, because totalWrongWidgets is currently a list of lists
                        totalCorrectWidgetsFlat = [item for sublist in totalCorrectWidgets for item in sublist]

                        #now, disable all Entry widgets within totalWrongWidgets
                        for wrongWidget in totalCorrectWidgetsFlat:
                            if(isinstance(wrongWidget, tk.Entry)):
                                wrongWidget.config(state = 'normal') #reenable Entry widget

        match inputtedState:

            case 'FORM': #if the FORMIVModeButton button is pressed

                #set all FORM IV state defaults
                self.IvTestState.set('FORM')
                self.gateVoltage.set(1.5)
                self.gateCycleVoltage.set(0)
                self.formSetReadVoltage.set(3.3) 
                self.formSetReadTime.set(500)
                self.resetReadVoltage.set(0) 
                self.resetReadTime.set(0)
                
            case 'SET': #if the SETIVModeButton button is pressed

                #set all SET IV state defaults
                self.IvTestState.set('SET')
                self.gateVoltage.set(1.5)
                self.gateCycleVoltage.set(0)
                self.formSetReadVoltage.set(2) 
                self.formSetReadTime.set(500)
                self.resetReadVoltage.set(0) 
                self.resetReadTime.set(0)
            
            case 'RESET': #if the RESETIVModeButton button is pressed

                #set all RESET IV state defaults
                self.IvTestState.set('RESET')
                self.gateVoltage.set(1.5)
                self.gateCycleVoltage.set(0)
                self.formSetReadVoltage.set(0) 
                self.formSetReadTime.set(0)
                self.resetReadVoltage.set(1) 
                self.resetReadTime.set(500)
            
            case 'IV': #if the IVModeButton button is pressed

                #set all (unique) IV MODE state defaults
                self.IvTestState.set('IV')
                self.gateVoltage.set(1.5)
                self.gateCycleVoltage.set(3.3)
                self.formSetReadVoltage.set(2) 
                self.formSetReadTime.set(500)
                self.resetReadVoltage.set(1) 
                self.resetReadTime.set(500)

    # - - - - - - - - - - - - - - - -

    #function to recursively collect all widgets from an inputted parent widget
    #(since this version of the code Quotayba built keeps making excess frames within
    #frames)
    def getAllWidgetDescendants(self, widget):
        descendants = []
        for child in widget.winfo_children():
            descendants.append(child)
            descendants.extend(self.getAllWidgetDescendants(child)) # Recursively get children of children
        return descendants
