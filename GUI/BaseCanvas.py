
from tkinter import ttk, Frame, Label, StringVar, IntVar, DoubleVar, BooleanVar, Listbox, END #ttk = themed Tkinter for "improved aesthetics and additional widgets"
import matplotlib.pyplot as plt #installed matplotlib (python -m pip install -U matplotlib (https://matplotlib.org/stable/install/index.html))


class BaseCanvas:
    def __init__(self, parent: Frame):
        self.modeState = StringVar(parent)
        
        self.console:Listbox = None

        self.HRSMinValue = IntVar(parent)
        self.LRSMaxValue = IntVar(parent)
        self.HRSMinValue.set(10e3)
        self.LRSMaxValue.set(10e3)

        self.applyToAllDevices = BooleanVar(parent)
        self.invertIVStates = BooleanVar(parent)
        self.showRunTime = BooleanVar(parent)
        self.createSavePlots = BooleanVar(parent)
        self.toggledOhmsLawUnit = StringVar(parent)
        self.csvControlVariable = BooleanVar(parent)

        self.gateVoltage = DoubleVar(parent)
        self.gateCycleVoltage = DoubleVar(parent)
        self.formSetVoltage = DoubleVar(parent)
        self.formSetTime = IntVar(parent)
        self.delayPeriodTime = IntVar(parent)
        self.formSetReadVoltage = DoubleVar(parent)
        self.formSetReadTime = IntVar(parent)
        self.resetVoltage = DoubleVar(parent)
        self.resetTime = IntVar(parent)
        self.resetReadVoltage = DoubleVar(parent)
        self.resetReadTime = IntVar(parent)
        self.cycleNumber = IntVar(parent)
        self.stepNumber = IntVar(parent)

        self.formSetStateString = StringVar(parent)

        self.IvTestState = StringVar(parent)

        # UNIQUE TO STEP PULSE TEST
        self.maxFormSetVoltage = DoubleVar(parent)
        self.maxResetVoltage = DoubleVar(parent)
        self.chosenStepVoltage = StringVar(parent)
        self.stepVoltageDirection = StringVar(parent)
        self.incrementVoltage = BooleanVar(parent)

        # UNIQUE TO IV TEST AND PULSE TEST SET/RESET SWITCH MODES
        self.setGateVoltage = DoubleVar(parent)
        self.resetGateVoltage = DoubleVar(parent)

        # Other variables

        self.utilizeCurResRange = BooleanVar(parent)
        self.createHeatMap = BooleanVar(parent)
        self.pulseTestRangeMin = DoubleVar(parent)
        self.pulseTestRangeMax = DoubleVar(parent)
        self.hrsRangeMin = DoubleVar(parent)
        self.hrsRangeMax = DoubleVar(parent)
        self.lrsRangeMin = DoubleVar(parent)
        self.lrsRangeMax = DoubleVar(parent)
        self.pulseTestRangeCycleCount = IntVar(parent)
        self.minGateVoltage = DoubleVar(parent)
        self.minResetVoltage = DoubleVar(parent)

        self.saveFileName = StringVar(parent)
        self.saveDirectory = StringVar(parent)
        
        self.retentionTest = BooleanVar(parent)
        self.retentionTime = IntVar(parent)
        self.retentionCycles = IntVar(parent)

        self.gateRangeTest = BooleanVar(parent)
        self.gateRangeMin = DoubleVar(parent)
        self.gateRangeMax = DoubleVar(parent)

        self.writeImage = BooleanVar(parent)
        self.readImage = BooleanVar(parent)

        self.rowColumnVariable = StringVar(parent)

        self.submitButton:ttk.Button = None
        self.stopButton:ttk.Button = None

        self.binaryMode = BooleanVar(parent)

        self.rangeValuesStr = StringVar(parent)
        self.rangeLevelsStr = StringVar(parent)

        self.gateRangeThreshold = IntVar(parent)
        self.gateVoltageMin = DoubleVar(parent)
        self.gateVoltageMax = DoubleVar(parent)

        self.resetVoltageMin = DoubleVar(parent)
        self.resetVoltageMax = DoubleVar(parent)

        self.gateStepVoltage = DoubleVar(parent)

        self.levelTolerance = DoubleVar(parent)
        
        self.verifyCycles = IntVar(parent)

        self.kernelProcessingTest = BooleanVar(parent)
        self.kernelMatStr = StringVar(parent)


    def pressedClearOutput(self, messageListBox:Listbox):
        #list box display resets
        messageListBox.delete(0, END)

    
    def toggleOhmsLawUnit(self, OhmsLawUnit, OhmsLawUnitButton, rangeVerificationTitleLabel=None):

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
        unit = self.getUnit(OhmsLawUnit)
        OhmsLawUnitButton.config(text = unit)
        if rangeVerificationTitleLabel != None:
            rangeVerificationTitleLabel.config(text=''.join(['Read-Write Range (', unit, ')']))
        #populate the canvas frame with the information specific to the pulse testing


    def toggleBinaryMode(self, state, *args):
        None
    

    def toggleUnitButton(self, OhmsLawUnit, OhmsLawUnitButton, unitList:list[Label]):

        #change the inputted unit and thus the corresponding labels to whichever
        #unit type is NOT the inputted one (between current and resistance)

        #if inputted unit is current, change to resistance
        if(OhmsLawUnit.get() == 'uA'):
            OhmsLawUnit.set('kOhm')
            OhmsLawUnitButton.config(bg = 'lightgreen')

        #otherwise (only toggled between two units), change from resistance
        #to current
        else:
            OhmsLawUnit.set('uA')
            OhmsLawUnitButton.config(bg = 'lightgreen')

        newUnit = self.getUnit(OhmsLawUnit)
        #set the text of the OhmsLawUnitButton to the new OhmsLawUnit text
        OhmsLawUnitButton.config(text = newUnit)
        for unit in unitList:
            unit.config(text = newUnit)
        #populate the canvas frame with the information specific to the pulse testing


    def getUnit(self, OhmsLawUnit):
        return 'k\u03A9' if OhmsLawUnit.get() == 'kOhm' else 'uA'

    def getByteList(self):
      
        gateVoltageBytes         = BaseCanvas.twoByteComboSplit(self.gateVoltage.get() * 1000)
        formSetVoltageBytes      = BaseCanvas.twoByteComboSplit(self.formSetVoltage.get() * 1000)
        formSetTimeBytes         = BaseCanvas.twoByteComboSplit(self.formSetTime.get())
        read1VoltageBytes  = BaseCanvas.twoByteComboSplit(self.formSetReadVoltage.get() * 1000)
        read1TimeBytes     = BaseCanvas.twoByteComboSplit(self.formSetReadTime.get())
        resetVoltageBytes        = BaseCanvas.twoByteComboSplit(self.resetVoltage.get() * 1000)
        resetTimeBytes           = BaseCanvas.twoByteComboSplit(self.resetTime.get())
        read2VoltageBytes    = BaseCanvas.twoByteComboSplit(self.resetReadVoltage.get() * 1000)
        read2TimeBytes       = BaseCanvas.twoByteComboSplit(self.resetReadTime.get())
        sharedDelayPeriodBytes   = BaseCanvas.twoByteComboSplit(self.delayPeriodTime.get())
        cyclesNumberBytes        = BaseCanvas.twoByteComboSplit(self.cycleNumber.get())
        stepNumberBytes          = BaseCanvas.twoByteComboSplit(self.stepNumber.get())
        modeStateNum             = 1 if self.modeState.get() == 'iv_test' else 0

        inputByteList = [85, 170,   gateVoltageBytes[0], gateVoltageBytes[1], \
                                    formSetVoltageBytes[0], formSetVoltageBytes[1], \
                                    formSetTimeBytes[0], formSetTimeBytes[1], \
                                    sharedDelayPeriodBytes[0], sharedDelayPeriodBytes[1], \
                                    read1VoltageBytes[0], read1VoltageBytes[1], \
                                    read1TimeBytes [0], read1TimeBytes[1], \
                                    resetVoltageBytes[0], resetVoltageBytes[1], \
                                    resetTimeBytes[0], resetTimeBytes[1], \
                                    read2VoltageBytes[0], read2VoltageBytes[1], \
                                    read2TimeBytes[0], read2TimeBytes[1], \
                                    0, 0, \
                                    cyclesNumberBytes[0], cyclesNumberBytes[1], \
                                    stepNumberBytes[0], stepNumberBytes[1], \
                                    modeStateNum, 170, 85]
        
        return inputByteList
    
    def getRead2ByteList(self):
        gateVoltageBytes         = BaseCanvas.twoByteComboSplit(self.gateVoltage.get() * 1000)
        formSetVoltageBytes      = BaseCanvas.twoByteComboSplit(0)
        formSetTimeBytes         = BaseCanvas.twoByteComboSplit(0)
        read1VoltageBytes        = BaseCanvas.twoByteComboSplit(0)
        read1TimeBytes           = BaseCanvas.twoByteComboSplit(0)
        resetVoltageBytes        = BaseCanvas.twoByteComboSplit(0)
        resetTimeBytes           = BaseCanvas.twoByteComboSplit(0)
        read2VoltageBytes        = BaseCanvas.twoByteComboSplit(self.resetReadVoltage.get() * 1000)
        read2TimeBytes           = BaseCanvas.twoByteComboSplit(self.resetReadTime.get())
        sharedDelayPeriodBytes   = BaseCanvas.twoByteComboSplit(self.delayPeriodTime.get())
        cyclesNumberBytes        = BaseCanvas.twoByteComboSplit(self.cycleNumber.get())
        stepNumberBytes          = BaseCanvas.twoByteComboSplit(self.stepNumber.get())
        modeStateNum             = 1 if self.modeState.get() == 'iv_test' else 0

        inputByteList = [85, 170,   gateVoltageBytes[0], gateVoltageBytes[1], \
                                    formSetVoltageBytes[0], formSetVoltageBytes[1], \
                                    formSetTimeBytes[0], formSetTimeBytes[1], \
                                    sharedDelayPeriodBytes[0], sharedDelayPeriodBytes[1], \
                                    read1VoltageBytes[0], read1VoltageBytes[1], \
                                    read1TimeBytes [0], read1TimeBytes[1], \
                                    resetVoltageBytes[0], resetVoltageBytes[1], \
                                    resetTimeBytes[0], resetTimeBytes[1], \
                                    read2VoltageBytes[0], read2VoltageBytes[1], \
                                    read2TimeBytes[0], read2TimeBytes[1], \
                                    0, 0, \
                                    cyclesNumberBytes[0], cyclesNumberBytes[1], \
                                    stepNumberBytes[0], stepNumberBytes[1], \
                                    modeStateNum, 170, 85]
        
        return inputByteList
    

    def getRead1ByteList(self):
        gateVoltageBytes         = BaseCanvas.twoByteComboSplit(self.gateVoltage.get() * 1000)
        formSetVoltageBytes      = BaseCanvas.twoByteComboSplit(0)
        formSetTimeBytes         = BaseCanvas.twoByteComboSplit(0)
        read1VoltageBytes        = BaseCanvas.twoByteComboSplit(self.formSetReadVoltage.get() * 1000)
        read1TimeBytes           = BaseCanvas.twoByteComboSplit(self.formSetReadTime.get())
        resetVoltageBytes        = BaseCanvas.twoByteComboSplit(0)
        resetTimeBytes           = BaseCanvas.twoByteComboSplit(0)
        read2VoltageBytes        = BaseCanvas.twoByteComboSplit(0)
        read2TimeBytes           = BaseCanvas.twoByteComboSplit(0)
        sharedDelayPeriodBytes   = BaseCanvas.twoByteComboSplit(self.delayPeriodTime.get())
        cyclesNumberBytes        = BaseCanvas.twoByteComboSplit(self.cycleNumber.get())
        stepNumberBytes          = BaseCanvas.twoByteComboSplit(self.stepNumber.get())
        modeStateNum             = 1 if self.modeState.get() == 'iv_test' else 0

        inputByteList = [85, 170,   gateVoltageBytes[0], gateVoltageBytes[1], \
                                    formSetVoltageBytes[0], formSetVoltageBytes[1], \
                                    formSetTimeBytes[0], formSetTimeBytes[1], \
                                    sharedDelayPeriodBytes[0], sharedDelayPeriodBytes[1], \
                                    read1VoltageBytes[0], read1VoltageBytes[1], \
                                    read1TimeBytes [0], read1TimeBytes[1], \
                                    resetVoltageBytes[0], resetVoltageBytes[1], \
                                    resetTimeBytes[0], resetTimeBytes[1], \
                                    read2VoltageBytes[0], read2VoltageBytes[1], \
                                    read2TimeBytes[0], read2TimeBytes[1], \
                                    0, 0, \
                                    cyclesNumberBytes[0], cyclesNumberBytes[1], \
                                    stepNumberBytes[0], stepNumberBytes[1], \
                                    modeStateNum, 170, 85]
        
        return inputByteList

    
    def getSetRead2ByteList(self):
        gateVoltageBytes         = BaseCanvas.twoByteComboSplit(self.gateVoltage.get() * 1000)
        formSetVoltageBytes      = BaseCanvas.twoByteComboSplit(self.formSetVoltage.get() * 1000)
        formSetTimeBytes         = BaseCanvas.twoByteComboSplit(self.formSetTime.get())
        read1VoltageBytes        = BaseCanvas.twoByteComboSplit(0)
        read1TimeBytes           = BaseCanvas.twoByteComboSplit(0)
        resetVoltageBytes        = BaseCanvas.twoByteComboSplit(0)
        resetTimeBytes           = BaseCanvas.twoByteComboSplit(0)
        read2VoltageBytes        = BaseCanvas.twoByteComboSplit(self.resetReadVoltage.get() * 1000)
        read2TimeBytes           = BaseCanvas.twoByteComboSplit(self.resetReadTime.get())
        sharedDelayPeriodBytes   = BaseCanvas.twoByteComboSplit(self.delayPeriodTime.get())
        cyclesNumberBytes        = BaseCanvas.twoByteComboSplit(self.cycleNumber.get())
        stepNumberBytes          = BaseCanvas.twoByteComboSplit(self.stepNumber.get())
        modeStateNum             = 1 if self.modeState.get() == 'iv_test' else 0

        inputByteList = [85, 170,   gateVoltageBytes[0], gateVoltageBytes[1], \
                                    formSetVoltageBytes[0], formSetVoltageBytes[1], \
                                    formSetTimeBytes[0], formSetTimeBytes[1], \
                                    sharedDelayPeriodBytes[0], sharedDelayPeriodBytes[1], \
                                    read1VoltageBytes[0], read1VoltageBytes[1], \
                                    read1TimeBytes [0], read1TimeBytes[1], \
                                    resetVoltageBytes[0], resetVoltageBytes[1], \
                                    resetTimeBytes[0], resetTimeBytes[1], \
                                    read2VoltageBytes[0], read2VoltageBytes[1], \
                                    read2TimeBytes[0], read2TimeBytes[1], \
                                    0, 0, \
                                    cyclesNumberBytes[0], cyclesNumberBytes[1], \
                                    stepNumberBytes[0], stepNumberBytes[1], \
                                    modeStateNum, 170, 85]
        
        return inputByteList
    
    
    def getResetByteList(self):
        gateVoltageBytes         = BaseCanvas.twoByteComboSplit(self.gateVoltage.get() * 1000)
        formSetVoltageBytes      = BaseCanvas.twoByteComboSplit(0)
        formSetTimeBytes         = BaseCanvas.twoByteComboSplit(0)
        read1VoltageBytes        = BaseCanvas.twoByteComboSplit(0)
        read1TimeBytes           = BaseCanvas.twoByteComboSplit(0)
        resetVoltageBytes        = BaseCanvas.twoByteComboSplit(self.resetVoltage.get() * 1000)
        resetTimeBytes           = BaseCanvas.twoByteComboSplit(self.resetTime.get())
        read2VoltageBytes        = BaseCanvas.twoByteComboSplit(0)
        read2TimeBytes           = BaseCanvas.twoByteComboSplit(0)
        sharedDelayPeriodBytes   = BaseCanvas.twoByteComboSplit(self.delayPeriodTime.get())
        cyclesNumberBytes        = BaseCanvas.twoByteComboSplit(self.cycleNumber.get())
        stepNumberBytes          = BaseCanvas.twoByteComboSplit(self.stepNumber.get())
        modeStateNum             = 1 if self.modeState.get() == 'iv_test' else 0

        inputByteList = [85, 170,   gateVoltageBytes[0], gateVoltageBytes[1], \
                                    formSetVoltageBytes[0], formSetVoltageBytes[1], \
                                    formSetTimeBytes[0], formSetTimeBytes[1], \
                                    sharedDelayPeriodBytes[0], sharedDelayPeriodBytes[1], \
                                    read1VoltageBytes[0], read1VoltageBytes[1], \
                                    read1TimeBytes [0], read1TimeBytes[1], \
                                    resetVoltageBytes[0], resetVoltageBytes[1], \
                                    resetTimeBytes[0], resetTimeBytes[1], \
                                    read2VoltageBytes[0], read2VoltageBytes[1], \
                                    read2TimeBytes[0], read2TimeBytes[1], \
                                    0, 0, \
                                    cyclesNumberBytes[0], cyclesNumberBytes[1], \
                                    stepNumberBytes[0], stepNumberBytes[1], \
                                    modeStateNum, 170, 85]
        
        return inputByteList
    

    def getSetResetRead2ByteList(self):
        gateVoltageBytes         = BaseCanvas.twoByteComboSplit(self.gateVoltage.get() * 1000)
        formSetVoltageBytes      = BaseCanvas.twoByteComboSplit(self.formSetVoltage.get() * 1000)
        formSetTimeBytes         = BaseCanvas.twoByteComboSplit(self.formSetTime.get())
        read1VoltageBytes        = BaseCanvas.twoByteComboSplit(0)
        read1TimeBytes           = BaseCanvas.twoByteComboSplit(0)
        resetVoltageBytes        = BaseCanvas.twoByteComboSplit(self.resetVoltage.get() * 1000)
        resetTimeBytes           = BaseCanvas.twoByteComboSplit(self.resetTime.get())
        read2VoltageBytes        = BaseCanvas.twoByteComboSplit(self.resetReadVoltage.get() * 1000)
        read2TimeBytes           = BaseCanvas.twoByteComboSplit(self.resetReadTime.get())
        sharedDelayPeriodBytes   = BaseCanvas.twoByteComboSplit(self.delayPeriodTime.get())
        cyclesNumberBytes        = BaseCanvas.twoByteComboSplit(self.cycleNumber.get())
        stepNumberBytes          = BaseCanvas.twoByteComboSplit(self.stepNumber.get())
        modeStateNum             = 1 if self.modeState.get() == 'iv_test' else 0

        inputByteList = [85, 170,   gateVoltageBytes[0], gateVoltageBytes[1], \
                                    formSetVoltageBytes[0], formSetVoltageBytes[1], \
                                    formSetTimeBytes[0], formSetTimeBytes[1], \
                                    sharedDelayPeriodBytes[0], sharedDelayPeriodBytes[1], \
                                    read1VoltageBytes[0], read1VoltageBytes[1], \
                                    read1TimeBytes [0], read1TimeBytes[1], \
                                    resetVoltageBytes[0], resetVoltageBytes[1], \
                                    resetTimeBytes[0], resetTimeBytes[1], \
                                    read2VoltageBytes[0], read2VoltageBytes[1], \
                                    read2TimeBytes[0], read2TimeBytes[1], \
                                    0, 0, \
                                    cyclesNumberBytes[0], cyclesNumberBytes[1], \
                                    stepNumberBytes[0], stepNumberBytes[1], \
                                    modeStateNum, 170, 85]
        return inputByteList


    @staticmethod
    def twoByteComboSplit(hexCombo):
        return divmod(int(hexCombo), 0x100)
