from GUI.MasterWindow import MasterWindowClass
from GUI.BaseCanvas import BaseCanvas
from Util import SerialPort, InOutManger

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.ticker import MaxNLocator

import re

import time, os
from threading import Thread

from mpl_toolkits.axes_grid1 import make_axes_locatable


class MainApp:
    def __init__(self):
        super().__init__()
        self.timeElapsed_ms = 0
        self.sudoTest = False
        self.cmd = None
        

        # main window setup, call the GUI, pass in the send button callback
        self.ui = MasterWindowClass(self.sendButtonCallback, self.closeThreads)
        self.ui.protocol("WM_DELETE_WINDOW", self.closeMaster)

        # self.inOutManger = InOutManger(self.cmd)
        self.inOutManger = InOutManger(self.cmd, debug=False, sudoTest=self.sudoTest)
        #self.inOutManger = InOutManger(self.cmd, debug=True, sudoTest=self.sudoTest)




    def initCMD(self, baudRate = 115200, startup = False):
        try:
            self.ui.print('Initializing Serial Port ...', isCommand=startup)
            time.sleep(1)
            cmd = SerialPort('/dev/ttyUSB0', baudRate = baudRate) # time out will be updated dynamically, see "init" function on the InOutManger
            if not cmd.isOpen():
                time.sleep(1)
                self.ui.print('Serial Port not found ...')
                time.sleep(0.5)
                self.ui.print('Done ...', isDone=startup) if startup else None
                self.cmd = None
            else:
                time.sleep(1)
                self.ui.print('Serial Port is Open: ' + cmd.portName)
                time.sleep(0.5)
                self.ui.print('Done ...', isDone=startup) if startup else None
                self.inOutManger.cmd = cmd
                self.cmd = cmd
            
        except Exception as e:
            self.ui.print(f'Error: {e}')
            self.cmd = None


    def sendButtonCallback(self):
        self.canvas = None
        self.canvas:BaseCanvas = self.ui.getCanvas()

        self.canvas.submitButton.config(bg='white')

        if self.inOutManger.inUse():
            self.ui.print('Threads are running ...')
            self.canvas.submitButton.config(bg='lightgreen')
            return
        
        # initialize the serial port if it has not been initialized
        if not self.cmd and not self.inOutManger.sudoTest:
            self.initCMD()
            if self.cmd is None:
                time.sleep(0.5)
                self.ui.print('aborting ...', isDone=True) 
            
        if not self.inOutManger.sudoTest and self.cmd is not None and not self.cmd.isOpen():
            if not self.cmd.reConnect():
                time.sleep(1)
                self.ui.print('Failed to reconnect to Serial Port ...')
                self.ui.print('aborting ...', isDone=True)
                self.canvas.submitButton.config(bg='lightgreen')
                return
    
        # get the canvas and devices from the GUI
        if not self.canvas.binaryMode.get() and self.canvas.readImage.get():
            devices = [[1 for _ in range(64)] for _ in range(64)]
        else:
            devices = self.ui.cellGrid.getGridData()

        self.ui.print('validating settings ...')
        time.sleep(0.5)
        if not self.isValidSetting(self.canvas):
            time.sleep(0.5)
            self.ui.print('aborting ...', isDone=True)
            self.canvas.submitButton.config(bg='lightgreen')
            return
        time.sleep(0.5)
        self.ui.print('Done ...')
        
        time.sleep(0.5)
        self.ui.print('Starting the Threads ...')
        time.sleep(0.5)
        if not self.inOutManger.sudoTest:
            while self.cmd.inWaiting():
                self.ui.print(self.cmd.readline())
            
        self.inOutManger.init(self.canvas)
        self.inOutManger.start()
        time.sleep(1)
        self.ui.print('Done ...')
        time.sleep(1)

        self.startTime = time.time()
        self.checkDone_completed = False
        
        match self.canvas.modeState.get():
            case 'pulse_test': 
                if self.canvas.createHeatMap or self.canvas.createSavePlots:
                    self.init_scatterPlots()
                    self.init_heatMap()

                self.ui.print('Starting Pulse Test ...')
                self.successfulRun = False
                self.totalDevCount = 0

                def run_pulse_test():
                    if self.canvas.retentionTest.get():
                        inputByteList = self.canvas.getByteList()
                        self.totalDevCount = self.ui.cellGrid.SelectedDevCount*self.canvas.retentionCycles.get()
                        self.updateProgress(self.canvas)
                        self.successfulRun = self.ProcessRetentionTest(inputByteList, self.canvas, devices)

                    elif self.canvas.writeImage.get() and not self.canvas.binaryMode.get():
                        inputByteList = self.canvas.getByteList()
                        self.totalDevCount = self.ui.cellGrid.totalDevCount*self.canvas.cycleNumber.get()
                        self.updateProgress(self.canvas)
                        self.successfulRun = self.ProcessWriteImage(inputByteList, self.canvas, devices)
                    
                    elif self.canvas.kernelProcessingTest.get():
                        inputByteList = self.canvas.getRead2ByteList()
                        self.totalDevCount = self.ui.cellGrid.totalDevCount*self.canvas.cycleNumber.get()
                        self.updateProgress(self.canvas)
                        self.successfulRun = self.ProcessKernelProcessingTest(inputByteList, self.canvas, devices)

                    elif self.canvas.gateRangeTest.get():
                        self.totalDevCount = self.ui.cellGrid.totalDevCount*self.canvas.cycleNumber.get() if self.canvas.applyToAllDevices.get() else self.ui.cellGrid.SelectedDevCount*self.canvas.cycleNumber.get()
                        self.updateProgress(self.canvas)
                        inputByteList = self.canvas.getSetRead2ByteList()
                        self.successfulRun = self.ProcessGateRangeTest(inputByteList, self.canvas, devices)
                    
                    elif self.canvas.utilizeCurResRange.get():
                        self.totalDevCount = self.ui.cellGrid.totalDevCount*self.canvas.cycleNumber.get() if self.canvas.applyToAllDevices.get() else self.ui.cellGrid.SelectedDevCount*self.canvas.cycleNumber.get()
                        self.updateProgress(self.canvas)
                        inputByteList = self.canvas.getByteList()
                        self.successfulRun = self.ProcessPulseTest(inputByteList, self.canvas, devices)

                    else:
                        inputByteList = self.canvas.getByteList() if self.canvas.binaryMode.get() else self.canvas.getRead2ByteList()
                        if self.canvas.binaryMode.get():
                            self.totalDevCount = self.ui.cellGrid.SelectedDevCount*self.canvas.cycleNumber.get()
                        else:
                            self.totalDevCount = self.ui.cellGrid.totalDevCount
                        self.updateProgress(self.canvas)
                        self.successfulRun = self.ProcessPulseTest(inputByteList, self.canvas, devices)
                    
                    
                    if self.successfulRun:
                        print("input done")
                        
                        self.ui.after(100, self.inOutManger.inputDone)
                    else:
                        self.ui.print('Pulse Test Failed ...')
                        self.ui.print('aborting ...', isDone=True)
                        self.ui.after(0, self.inOutManger.hardStop)
                Thread(target=run_pulse_test, daemon=True).start()
                    
            case 'pulse_step_test':

                if self.canvas.createSavePlots:
                    self.init_scatterPlots()

                self.ui.print('Starting Pulse Step Test ...')
                self.successfulRun = False
                self.totalDevCount = 0

                def runPulseStepTest(): #function to be called as a target for threading

                    #build on Quotayba's established logic above for basic Pulse Testing
                    inputByteList = self.canvas.getByteList() if self.canvas.binaryMode.get() else self.canvas.getRead2ByteList()
                    if self.canvas.binaryMode.get():
                        self.totalDevCount = self.ui.cellGrid.SelectedDevCount*self.canvas.cycleNumber.get()
                    else:
                        self.totalDevCount = self.ui.cellGrid.totalDevCount
                    self.updateProgress(self.canvas)
                    self.successfulRun = self.ProcessPulseTest(inputByteList, self.canvas, devices)

                    if self.successfulRun:
                        print("input done")
                        
                        self.ui.after(100, self.inOutManger.inputDone)
                    else:
                        self.ui.print('Pulse Step Test Failed ...')
                        self.ui.print('aborting ...', isDone=True)
                        self.ui.after(0, self.inOutManger.hardStop)
                    
                Thread(target = runPulseStepTest, daemon=True).start() #peforming threading on the created function above
                    
            case 'pulse_cycle_test': 

                if self.canvas.createSavePlots:
                    self.init_scatterPlots()

                self.ui.print('Starting Pulse SET/RESET Switch Test ...')
                self.successfulRun = False
                self.totalDevCount = 0

                def runPulseCycleTest(): #function to be called as a target for threading

                    #build on Quotayba's established logic above for basic Pulse Testing
                    inputByteList = self.canvas.getByteList() if self.canvas.binaryMode.get() else self.canvas.getRead2ByteList()
                    if self.canvas.binaryMode.get():
                        self.totalDevCount = self.ui.cellGrid.SelectedDevCount*self.canvas.cycleNumber.get()
                    else:
                        self.totalDevCount = self.ui.cellGrid.totalDevCount
                    self.updateProgress(self.canvas)
                    self.successfulRun = self.ProcessPulseTest(inputByteList, self.canvas, devices)

                    if self.successfulRun:
                        print("input done")
                        
                        self.ui.after(100, self.inOutManger.inputDone)
                    else:
                        self.ui.print('Pulse SET/RESET Switch Test Failed ...')
                        self.ui.print('aborting ...', isDone=True)
                        self.ui.after(0, self.inOutManger.hardStop)
                    
                Thread(target = runPulseCycleTest, daemon=True).start() #peforming threading on the created function above

            case 'iv_test':

                if self.canvas.createSavePlots:
                    self.init_scatterPlots()

                self.ui.print('Starting IV Test ...')
                self.successfulRun = False
                self.totalDevCount = 0

                def runIVTest(): #function to be called as a target for threading

                    #build on Quotayba's established logic above for basic Pulse Testing
                    inputByteList = self.canvas.getByteList() if self.canvas.binaryMode.get() else self.canvas.getRead2ByteList()
                    if self.canvas.binaryMode.get():
                        self.totalDevCount = self.ui.cellGrid.SelectedDevCount*self.canvas.cycleNumber.get()
                    else:
                        self.totalDevCount = self.ui.cellGrid.totalDevCount
                    self.updateProgress(self.canvas)
                    self.successfulRun = self.ProcessPulseTest(inputByteList, self.canvas, devices)

                    if self.successfulRun:
                        print("input done")
                        
                        self.ui.after(100, self.inOutManger.inputDone)
                    else:
                        self.ui.print('IV Test Failed ...')
                        self.ui.print('aborting ...', isDone=True)
                        self.ui.after(0, self.inOutManger.hardStop)
                    
                Thread(target = runIVTest, daemon=True).start() #peforming threading on the created function above
                
            case _: 
                self.inOutManger.stop()

        
    def ProcessPulseTest(self, ByteList:list, canvas: BaseCanvas, devices):
        try:
            if canvas.applyToAllDevices.get():
                setResetRead2ByteList = canvas.getSetResetRead2ByteList()
                setRead2ByteList = canvas.getSetRead2ByteList()

                row = 0
                while row < len(devices): 
                    col = 0
                    while col < len(devices[row]):
                        if not self.inOutManger.isRunning():
                            return False
                        deviceStat = devices[row][col]
                        
                        if deviceStat:
                            inputByteList = setResetRead2ByteList.copy() 
                        else:
                            inputByteList = setRead2ByteList.copy() 

                        inputByteList[22] = col  #column
                        inputByteList[23] = row #row 

                        if self.inOutManger.debug:
                            print(inputByteList) 
                            print(f"[ {' | '.join([f'{x:02X}' for x in inputByteList])} ]")  

                        self.inOutManger.addDeviceStatInput(row, col, inputByteList, deviceStat)

                        col+=1
                    row+=1
                else:
                    return True
            else:
                addInput = None 
                if canvas.utilizeCurResRange.get():
                    if canvas.hrsRangeMax.get() > 0:
                        inputByteList = canvas.getSetResetRead2ByteList() 
                    else:
                        inputByteList = canvas.getSetRead2ByteList()
                    addInput = self.inOutManger.addDeviceStatInput
                else:
                    inputByteList = ByteList
                    addInput = self.inOutManger.addInput
                row = 0
                while row < len(devices): 
                    col = 0
                    while col < len(devices[row]):
                        if not self.inOutManger.isRunning():
                            return False
                        
                        if not devices[row][col]:
                            col+=1
                            continue
                        
                        inputByteList[22] = col  #column
                        inputByteList[23] = row #row 
                        if self.inOutManger.debug:
                            print(ByteList) 
                            print(f"[ {' | '.join([f'{x:02X}' for x in inputByteList])} ]")  

                        addInput(row, col, inputByteList.copy())
                        col+=1
                    row+=1
                else:
                    return True
        except Exception as e:
            print(e)
            return False
            
    # [ 0  |  1 | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 ]
    # [ 85 | 170|  gate-V |  set-V  |  set-T  |  delay  |  R1-V   |  R1-T   | reset-V | reset-T |  R2-V   |  R2 T   | r  | c  |  cyl    |  stp    | M  | 170| 85 ]
    def ProcessRetentionTest(self, ByteList:list, canvas: BaseCanvas, devices):
        try:
            ByteList[4],  ByteList[5]  = 0, 0   # Set Voltage
            ByteList[10], ByteList[11] = 0, 0   # Read1 Voltage
            ByteList[14], ByteList[15] = 0, 0   # Reset Voltage
            ByteList[24], ByteList[25] = 0, 1   # Cycles

            # will save the csv files in this function
            # canvas.csvControlVariable.set(False)
            # canvas.createHeatMap.set(False)
            # canvas.createSavePlots.set(False)

            for cycle in range(1, canvas.retentionCycles.get() + 1):
                startTime = time.time()
                for row in range(len(devices)): 
                    for col in range(len(devices[row])):
                        if not self.inOutManger.isRunning():
                            return False
                        
                        deviceStat = devices[row][col]
                        if not deviceStat:
                            continue

                        inputByteList = ByteList.copy()
                        inputByteList[22] = col  #column
                        inputByteList[23] = row  #row

                        if self.inOutManger.debug:
                            print(ByteList) 
                            print(f"[ {' | '.join([f'{x:02X}' for x in ByteList])} ]") 

                        self.inOutManger.addInput(row, col, inputByteList, cycle)


                while not (self.inOutManger.inputQueue.empty() and \
                    self.inOutManger.outputQueue.empty()) and self.inOutManger.isRunning():
                    print('waiting for Queues ...')
                    time.sleep(1)

                if cycle in [1, canvas.retentionCycles.get()]:
                    data = self.inOutManger.getData(canvas.toggledOhmsLawUnit.get())
                    data['Cycle'] = cycle
                    # self.ui.after(0, lambda data=data:self.inOutManger.createdRetentionPulseTestPLots(data))
                    # self.ui.after(100, lambda canvas=canvas: self.UpdatePlots(canvas, repeat=False))
                
                if canvas.csvControlVariable.get(): # this will export to the "Retention" CSV file
                    self.inOutManger.exportRetentionData(cycle, self.inOutManger.getData(canvas.toggledOhmsLawUnit.get()))
                # self.inOutManger.resetResults()
                
                while (time.time() - startTime < canvas.retentionTime.get()) and self.inOutManger.isRunning():
                    print("waiting for Retention Time ...")
                    time.sleep(1)
                
            else:
                return True
        except Exception as e:
            print(e)
            return False

    def ProcessGateRangeTest(self, ByteList:list, canvas: BaseCanvas, devices):

        try:  
            if canvas.rowColumnVariable.get() == 'Row':
                numOfRows = sum(any(bool(devices[row][col]) for col in range(64)) for row in range(64)) 
                voltageStep = (canvas.gateRangeMax.get() - canvas.gateRangeMin.get()) * 1000 / (numOfRows-1) if (numOfRows-1) != 0 else 0
                currGateVoltage = canvas.gateRangeMin.get() * 1000
                for row in range(len(devices)): 
                    ByteList[2], ByteList[3] = BaseCanvas.twoByteComboSplit(currGateVoltage)
                    selectedDev = sum(bool(dev) for dev in devices[row])
                    if not selectedDev:
                        continue
                    for col in range(len(devices[row])):
                        if not self.inOutManger.isRunning():
                            return False
                        
                        if not devices[row][col]:
                            continue
                        
                        inputByteList = ByteList.copy()
                        inputByteList[22] = col  #column
                        inputByteList[23] = row #row 

                        if self.inOutManger.debug:
                            print(ByteList) 
                            print(f"[ {' | '.join([f'{x:02X}' for x in ByteList])} ]") 

                        self.inOutManger.addGateRangeInput(row, col, inputByteList, currGateVoltage)
                    if selectedDev > 0:
                        currGateVoltage += voltageStep
            else:
                numOfCol = sum(any(bool(devices[row][col]) for row in range(64)) for col in range(64)) 

                voltageStep = (canvas.gateRangeMax.get() - canvas.gateRangeMin.get()) * 1000 / (numOfCol-1) if numOfCol-1 != 0 else 0
                currGateVoltage = canvas.gateRangeMin.get() * 1000
                for col in range(len(devices[0])):
                    ByteList[2], ByteList[3] = BaseCanvas.twoByteComboSplit(currGateVoltage)
                    selectedDev = sum(bool(devices[row][col]) for row in range(64)) 
                    if not selectedDev > 0:
                        continue
                    for row in range(len(devices)):
                        if not self.inOutManger.isRunning():
                            return False
                        
                        if not devices[row][col]:
                            continue

                        inputByteList = ByteList.copy()
                        inputByteList[22] = col  #column
                        inputByteList[23] = row #row 

                        if self.inOutManger.debug:
                            print(ByteList) 
                            print(f"[ {' | '.join([f'{x:02X}' for x in ByteList])} ]") 

                        self.inOutManger.addGateRangeInput(row, col, inputByteList, currGateVoltage)
                    if selectedDev > 0:
                        currGateVoltage += voltageStep

            return True
        except Exception as e:
            print(e)
            return False


    def ProcessWriteImage(self, ByteList, canvas: BaseCanvas, devices):
        setResetRead2ByteList = canvas.getSetResetRead2ByteList()
        setRead2ByteList = canvas.getSetRead2ByteList()

        rangeValues = [float(item.strip()) for item in canvas.rangeValuesStr.get().strip().strip('[]').split(',')]  
        rangeLevels = [float(item.strip()) for item in canvas.rangeLevelsStr.get().strip().strip('[]').split(',')]
                         

        if canvas.toggledOhmsLawUnit.get() != 'uA':
            rangeLevels = [canvas.resetReadVoltage.get()*1000 / level for level in rangeLevels]
        if len(rangeValues) != len(rangeLevels):
            self.ui.print("Range Values and Range Levels must have the same number of items ...")
            return False
        
        import bisect
        def get_level(value):
            # Find insertion point to keep rangeValues sorted
            idx = bisect.bisect_left(rangeValues, value)
            if idx >= len(rangeValues):
                return rangeLevels[-1]
            return rangeLevels[idx]
        
        row = 0
        try:
            while row < len(devices): 
                col = 0
                while col < len(devices[row]):
                    if not self.inOutManger.isRunning():
                        return False
                    deviceStat = devices[row][col]
                    deviceLevel = get_level(deviceStat)

                    if deviceLevel < self.inOutManger.rangeThreshold:
                        inputByteList = setResetRead2ByteList.copy()
                    else:
                        inputByteList = setRead2ByteList.copy()

                    inputByteList[22] = col  #column
                    inputByteList[23] = row #row 

                    if self.inOutManger.debug:
                        print(inputByteList) 
                        print(f"[ {' | '.join([f'{x:02X}' for x in inputByteList])} ]")  

                    self.inOutManger.addDeviceLevelInput(row, col, inputByteList, deviceLevel, canvas.gateVoltage.get()*1000)

                    col+=1
                row+=1
            else:
                return True
        

        except Exception as e:
            print(e)
            return False
        
    def ProcessKernelProcessingTest(self, ByteList:list, canvas: BaseCanvas, devices):
        try:
            row = 0
            while row < len(devices): 
                col = 0
                while col < len(devices[row]):
                    if not self.inOutManger.isRunning():
                        return False

                    ByteList[22] = col  #column
                    ByteList[23] = row #row 
                    if self.inOutManger.debug:
                        print(ByteList) 
                        print(f"[ {' | '.join([f'{x:02X}' for x in ByteList])} ]")  

                    self.inOutManger.addInput(row, col, ByteList.copy())
                    col+=1
                row+=1
            else:
                return True

        except Exception as e:
            print(e)
            return False

    def init_scatterPlots(self):
        self.deviceScatterPlots = {}
        self.UpdatePlots(self.canvas)

    def init_heatMap(self):
        # Adjust this to show on the color bar.
        self.boundaries = self.ui.currentBounders if self.canvas.toggledOhmsLawUnit.get() == 'uA' else \
                            self.ui.resistanceBounders
        self.plotCMap, self.plotNorm = MasterWindowClass.getNormCMap(self.boundaries, colorMap=self.ui.cmapColors)
        self.heatMapPlots = {}
        self.UpdatePlots(self.canvas)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    '''
    NOTE: For reasons Nicholas Van Nostrand could not figure out in regards to threading (as threading was not
    something he was familiar with before Quotayba provided this code on short notice close to the end of his
    employment), this function would not be called once newPlotDataEvent was set after all the data was sifted through,
    leading to all scatter plots not being generated UNLESS the heatmap plots were ALSO generated.

    For this reason, the scatter plot logic by itself won't work, which is a problem for the step voltage
    plots that do not have the same X-axis as the cycle X-axis Pulse Test plots (with these options not having
    heatmap options).  But for the sake of not breaking something that could not be tested under the given
    circumstances, ONLY the Pulse Test scatter plot logic is included within. Other scatter plots related
    to step voltage will have to be included.

    NOTE: Stacia Oktyabrsky has resolved the issue. The thread in InputOutputManager that sets newPlotDataEvent
    (CreatePulseTestPlots) is run AFTER UpdatePlots runs for the first time, so newPlotDataEvent would not be set
    until after UpdatePlots had already run. The reason it worked with heatmaps activated is because the heatmap
    secion calls UpdatePlots continuously, allowing UpdatePlots to still be running once newPlotDataEvent is set.
    This has been fixed so that UpdatePlots repeats if scatter plots are requested but newPlotDataEvent isn't set yet.
    '''

    def UpdatePlots(self, canvas: BaseCanvas, repeat=True):

        '''
        print('Plots bool: ' + str(self.inOutManger.newPlotDataEvent.is_set()))
        print('HeatMap bool: ' + str(self.inOutManger.newPlotDataEventHeatMap.is_set()))
        '''

        if self.canvas.createSavePlots.get():

            '''
            print('here 2!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('Plots bool check 2 : ' + str(self.inOutManger.newPlotDataEvent.is_set()))
            print('-----------')
            '''

            if self.inOutManger.newPlotDataEvent.is_set():
                self.inOutManger.newPlotDataEvent.clear()

                '''
                print('here 3!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                '''
                
                i = 0
                for cycle, gridData in self.inOutManger.getPlotData().items():
                    fig, ax1, ax2 = None, None, None

                    # ((read1_title, read1_grid), (read2_title, read2_grid))
                    # @see Util.InputOutputManager.createdPulseTestPLots
                    read1_data, read2_data = gridData.values()

                    #BY DEVICE, HAVE "DEVICE" AS ONE OF THE FOR LOOP INSTANCES ABOVE

                    match self.canvas.modeState.get():

                        case 'pulse_test' | 'pulse_cycle_test':

                            # can only do plot for pulse test if > 1 cycles
                            if (self.canvas.cycleNumber.get() > 1 or \
                                self.canvas.pulseTestRangeCycleCount.get() > 1):

                                #read1_data[0] is the device row/column string ({row}-{col})
                                if read1_data[0] not in self.deviceScatterPlots:
                                    fig, ax = plt.subplots(figsize=(10, 6))
                                    self.deviceScatterPlots[read1_data[0]] = (ax, fig)
                                    newFig = True
                                else:
                                    ax, fig = self.deviceScatterPlots[read1_data[0]]
                                    newFig = False
                                    #ax.clear()  # Clear previous points to redraw

                                # Plot Read1
                                if read1_data:
                                    title, df_read1 = read1_data
                                    if not df_read1.empty:
                                        ax.scatter(df_read1.index, df_read1.values, label = \
                                                   f'LRS ({self.canvas.toggledOhmsLawUnit.get()})', \
                                                   color = 'red', marker = 'p')

                                # Plot Read2
                                if read2_data:
                                    title, df_read2 = read2_data
                                    if not df_read2.empty:
                                        ax.scatter(df_read2.index, df_read2.values, label = \
                                                   f'HRS ({self.canvas.toggledOhmsLawUnit.get()})', \
                                                   color = 'blue', marker = '^')

                                if newFig:
                                    #for aesthetic reasons, get the row and column numbers from read1_data[0]
                                    #to use to give a different format to the plot title
                                    rowVal, colVal = re.findall(r'\d+', read1_data[0])

                                    ax.set_xlabel("Cycle")
                                    if self.canvas.toggledOhmsLawUnit.get() == 'kOhm':
                                        ax.set_ylabel("Resistance (kOhm)")
                                        ax.set_title(f"Device ({rowVal}/{colVal}) - Resistance vs. Cycle")
                                    else:
                                        ax.set_ylabel("Current (uA)")
                                        ax.set_title(f"Device ({rowVal}/{colVal}) - Current vs. Cycle")
                                    ax.legend(loc='lower right', bbox_to_anchor=(1, 1))

                                    ax.xaxis.set_major_locator(MaxNLocator(integer=True)) #only show whole numbers/cycles for x-axis
                                    ax.set_yscale('log') #have y-axis show values in "log" format
                                    plt.show(block=False)

                                fig.canvas.draw_idle()
                                fig.canvas.flush_events()

                                # Repeat loop
                                if repeat and (self.inOutManger.isRunning() or self.inOutManger.newPlotDataEvent.is_set()):
                                    self.ui.after(100, lambda: self.UpdatePlots(canvas))
                                else:
                                    # Save scatter plots
                                    if not self.inOutManger.csvMgr.folderDirectory:
                                        self.inOutManger.csvMgr.setDataDirectory(self.canvas.saveDirectory.get(), self.canvas.saveFileName.get())
                                    plotFolder = os.path.join(self.inOutManger.csvMgr.folderDirectory, 'Plots')
                                    if not os.path.exists(plotFolder):
                                        os.makedirs(plotFolder)

                                    for dev, (ax, fig) in self.deviceScatterPlots.items():
                                        fig.savefig(os.path.join(plotFolder, f'Scatter_Device_{dev}.png'))
                            
                            else:
                                self.canvas.console.insert('end', 'WARNING!: Cannot create plots with 1 cycle for X axis')

                        case 'pulse_step_test':

                            # need to calculate the steps first so they can be the x-axis
                            if (self.canvas.incrementVoltage.get()):
                                if self.canvas.stepVoltageDirection.get() != 'Rise then Fall':
                                    StepsData = list(range(0, (self.canvas.stepNumber.get() + 1) * \
                                                        self.canvas.cycleNumber.get()))
                                else:
                                    StepsData = list(range(0, (self.canvas.stepNumber.get() + 1) * \
                                                        2 * self.canvas.cycleNumber.get())) # amount of steps for one rise operatoin
                            else:
                                if self.canvas.stepVoltageDirection.get() != 'Rise then Fall':
                                    StepsData = list(range(1, (self.canvas.stepNumber.get() + 1) * \
                                                            self.canvas.cycleNumber.get()))
                                else:
                                    StepsData = list(range(1, (self.canvas.stepNumber.get() + 1) * \
                                                        2 * self.canvas.cycleNumber.get())) # amount of steps for one rise operatoin

                            if (self.canvas.chosenStepVoltage.get() == 'SET'): # if it's SET, there is one pretest operation
                                StepsData.insert(0, -1)
                            else: # if it's RESET, there are 2 pretest operations
                                StepsData.insert(0, -1)
                                StepsData.insert(0, -1)

                            #read1_data[0] is the device row/column string ({row}-{col})
                            if read1_data[0] not in self.deviceScatterPlots:
                                fig, ax = plt.subplots(figsize=(10, 6))
                                self.deviceScatterPlots[read1_data[0]] = (ax, fig)
                                newFig = True
                            else:
                                ax, fig = self.deviceScatterPlots[read1_data[0]]
                                newFig = False
                                #ax.clear()  # Clear previous points to redraw

                            # Plot Read1
                            if read1_data:
                                title, df_read1 = read1_data
                                if not df_read1.empty:
                                    ax.scatter(StepsData[:len(df_read1)], df_read1.values, label = \
                                               f'LRS ({self.canvas.toggledOhmsLawUnit.get()})', \
                                               color = 'red', marker = 'p')

                            # Plot Read2
                            if read2_data:
                                title, df_read2 = read2_data
                                if not df_read2.empty:
                                    ax.scatter(StepsData[:len(df_read2)], df_read2.values, label = \
                                               f'HRS ({self.canvas.toggledOhmsLawUnit.get()})', \
                                               color = 'blue', marker = '^')

                            if newFig:
                                #for aesthetic reasons, get the row and column numbers from read1_data[0]
                                #to use to give a different format to the plot title
                                rowVal, colVal = re.findall(r'\d+', read1_data[0])

                                ax.set_xlabel("Step")
                                if self.canvas.toggledOhmsLawUnit.get() == 'kOhm':
                                    ax.set_ylabel("Resistance (kOhm)")
                                    ax.set_title(f"Device ({rowVal}/{colVal}) - Resistance vs. Step")
                                else:
                                    ax.set_ylabel("Current (uA)")
                                    ax.set_title(f"Device ({rowVal}/{colVal}) - Current vs. Step")
                                ax.legend(loc='lower right', bbox_to_anchor=(1, 1))

                                ax.xaxis.set_major_locator(MaxNLocator(integer=True)) #only show whole numbers/cycles for x-axis
                                ax.set_yscale('log') #have y-axis show values in "log" format
                                plt.show(block=False)

                            fig.canvas.draw_idle()
                            fig.canvas.flush_events()

                            # Repeat loop
                            if repeat and (self.inOutManger.isRunning() or self.inOutManger.newPlotDataEvent.is_set()):
                                self.ui.after(100, lambda: self.UpdatePlots(canvas))
                            else:
                                # Save scatter plots
                                if not self.inOutManger.csvMgr.folderDirectory:
                                    self.inOutManger.csvMgr.setDataDirectory(self.canvas.saveDirectory.get(), self.canvas.saveFileName.get())
                                plotFolder = os.path.join(self.inOutManger.csvMgr.folderDirectory, 'Plots')
                                if not os.path.exists(plotFolder):
                                    os.makedirs(plotFolder)

                                for dev, (ax, fig) in self.deviceScatterPlots.items():
                                    fig.savefig(os.path.join(plotFolder, f'Scatter_Device_{dev}.png'))

                        case 'iv_test':

                            #read1_data[0] is the device row/column string ({row}-{col})
                            if read1_data[0] not in self.deviceScatterPlots:
                                fig, ax = plt.subplots(figsize=(10, 6))
                                ax.plot([],[], color = 'black', marker = 'o', \
                                    linestyle="-", linewidth=1, markersize=2)
                                self.deviceScatterPlots[read1_data[0]] = (ax, fig)
                                newFig = True
                                plt.show(block=False)
                            else:
                                ax, fig = self.deviceScatterPlots[read1_data[0]]
                                newFig = False
                                #ax.clear()  # Clear previous points to redraw
                            
                            xData = list(ax.get_lines()[0].get_xdata())
                            yData = list(ax.get_lines()[0].get_ydata())

                            # Plot Read1
                            if read1_data:
                                title, df_read1, df_read1Volts = read1_data
                                if not df_read1.empty:
                                    xData += list(df_read1Volts['Read1 Output Voltage'])
                                    yData += list(df_read1.values)

                            # Plot Read2
                            if read2_data:
                                title, df_read2, df_read2Volts = read2_data
                                if not df_read2.empty:
                                    xData += list(df_read2Volts['Read2 Output Voltage'])
                                    yData += list(df_read2.values)
                            
                            ax.get_lines()[0].set_data(xData, yData)
                            ax.relim()
                            ax.autoscale_view()

                            if newFig:
                                #for aesthetic reasons, get the row and column numbers from read1_data[0]
                                #to use to give a different format to the plot title
                                rowVal, colVal = re.findall(r'\d+', read1_data[0])

                                if self.canvas.IvTestState.get() == 'FORM':
                                    ax.set_title(f"Device ({rowVal}/{colVal}) - FORM IV Testing")
                                elif self.canvas.IvTestState.get() == 'SET':
                                    ax.set_title(f"Device ({rowVal}/{colVal}) - SET IV Testing")
                                elif self.canvas.IvTestState.get() == 'RESET':
                                    ax.set_title(f"Device ({rowVal}/{colVal}) - RESET IV Testing")
                                else:
                                    ax.set_title(f"Device ({rowVal}/{colVal}) - IV Testing")
                                ax.set_xlabel("Voltage (mV)")
                                ax.set_ylabel(f"Current (uA)")
                                ax.grid(True, which='major', axis='both', color='gray', \
                                        linestyle='-', linewidth=0.5, alpha=0.5)

                                ax.xaxis.set_major_locator(MaxNLocator(integer=True)) #only show whole numbers/cycles for x-axis
                                ax.set_yscale('linear') #have y-axis show values in "linear" format
                                plt.show(block=False)

                            fig.canvas.draw_idle()
                            fig.canvas.flush_events()

                            # Repeat loop
                            if repeat and (self.inOutManger.isRunning() or self.inOutManger.newPlotDataEvent.is_set()):
                                self.ui.after(100, lambda: self.UpdatePlots(canvas))
                            else:
                                # Save scatter plots
                                if not self.inOutManger.csvMgr.folderDirectory:
                                    self.inOutManger.csvMgr.setDataDirectory(self.canvas.saveDirectory.get(), self.canvas.saveFileName.get())
                                plotFolder = os.path.join(self.inOutManger.csvMgr.folderDirectory, 'Plots')
                                if not os.path.exists(plotFolder):
                                    os.makedirs(plotFolder)

                                for dev, (ax, fig) in self.deviceScatterPlots.items():
                                    fig.savefig(os.path.join(plotFolder, f'Scatter_Device_{dev}.png'))

                    i += 1

            elif self.deviceScatterPlots and not self.inOutManger.isRunning():
                # save scatter plots if we've made them but newPlotDataEvent is clear
                # this was a problem in retention testing
                if not self.inOutManger.csvMgr.folderDirectory:
                    self.inOutManger.csvMgr.setDataDirectory(self.canvas.saveDirectory.get(), self.canvas.saveFileName.get())
                plotFolder = os.path.join(self.inOutManger.csvMgr.folderDirectory, 'Plots')
                if not os.path.exists(plotFolder):
                    os.makedirs(plotFolder)

                for dev, (ax, fig) in self.deviceScatterPlots.items():
                    fig.savefig(os.path.join(plotFolder, f'Scatter_Device_{dev}.png'))
                
            else: # if newPlotDataEvent has not been set yet, keep repeating until it is
                self.ui.after(100, lambda: self.UpdatePlots(canvas))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - -

        if self.canvas.createHeatMap.get():
            
            if self.inOutManger.newPlotDataEventHeatMap.is_set():
                self.inOutManger.newPlotDataEventHeatMap.clear()
                for cycle, gridData in self.inOutManger.getPlotDataHeatMap().items():
                    fig, ax1, ax2 = None, None, None

                    # ((read1_title, read1_grid), (read2_title, read2_grid))
                    # @see Util.InputOutputManager.createdPulseTestPLots
                    read1_data, read2_data = gridData.values()

                    # Selecting the axes and whether to plot to axes or one axis
                    if cycle not in self.heatMapPlots:
                        if read1_data and read2_data:
                            fig, ax = plt.subplots(1, 2, figsize=(15, 7))
                            ax1 = ax[0]
                            ax2 = ax[1]
                        elif read1_data:
                            fig, ax = plt.subplots(1, 1, figsize=(15, 7))
                            ax1 = ax
                            ax2 = None
                        elif read2_data:    
                            fig, ax = plt.subplots(1, 1, figsize=(15, 7))
                            ax1 = None
                            ax2 = ax
                        self.heatMapPlots[cycle] = {
                            "ax1": ax1, "ax2": ax2, "fig": fig, "img1": None, "img2": None
                        }
                        newFig = True  
                    else:
                        ax1, ax2, fig = self.heatMapPlots[cycle]["ax1"], self.heatMapPlots[cycle]["ax2"], self.heatMapPlots[cycle]["fig"]
                        newFig = False

                        
                    if newFig:
                        if read2_data:
                            read2_title, read2_grid = read2_data
                            self.heatMapPlots[cycle][4] = ax2.imshow(read2_grid, norm=self.plotNorm, cmap=self.plotCMap) #SET plot (with selected device/cell format)
                            ax2.set_title(read2_title)
                            divider = make_axes_locatable(ax2)
                            cax = divider.append_axes("right", size="5%", pad=0.05)
                            cbar = fig.colorbar(self.heatMapPlots[cycle][4], cax=cax, boundaries=self.boundaries, ticks=self.boundaries)
                            cbar.ax.set_yticklabels([f"{int(val)}" for val in self.boundaries], fontsize=14)
                            cbar.set_label(f"Read - {canvas.toggledOhmsLawUnit.get()}", labelpad=10, fontsize=20)
                            cbar.ax.yaxis.set_label_position('right')

                        if read1_data:
                            read1_title, read1_grid = read1_data
                            self.heatMapPlots[cycle][3] = ax1.imshow(read1_grid, norm=self.plotNorm, cmap=self.plotCMap) #RESET plot (with selected device/cell format)
                            ax1.set_title(read1_title)
                            divider = make_axes_locatable(ax1)
                            cax = divider.append_axes("right", size="5%", pad=0.05)
                            cbar = fig.colorbar(self.heatMapPlots[cycle][3], cax=cax, boundaries=self.boundaries, ticks=self.boundaries)
                            cbar.ax.set_yticklabels([f"{int(val)}" for val in self.boundaries], fontsize=14)
                            cbar.set_label(f"Read - {canvas.toggledOhmsLawUnit.get()}", labelpad=10, fontsize=20)
                            cbar.ax.yaxis.set_label_position('right')

                        plt.show(block=False)
                        plt.tight_layout()
                    
                    else:
                        if read2_data and self.heatMapPlots[cycle][4] is not None:
                            _, grid = read2_data
                            self.heatMapPlots[cycle][4].set_data(grid)
                        if read1_data and self.heatMapPlots[cycle][3] is not None:
                            _, grid = read1_data
                            self.heatMapPlots[cycle][3].set_data(grid)
                    
                    if fig:
                        fig.canvas.draw_idle()
                        #fig.canvas.flush_events()
                        if ax1 and ax2:
                            ax1
                    

            if repeat and (self.inOutManger.isRunning() or self.inOutManger.newPlotDataEventHeatMap.is_set()):
                self.ui.after(100, lambda: self.UpdatePlots(canvas))
            else:
                if not self.inOutManger.csvMgr.folderDirectory:
                    self.inOutManger.csvMgr.setDataDirectory(self.canvas.saveDirectory.get(), self.canvas.saveFileName.get())
                plotFolder = os.path.join(self.inOutManger.csvMgr.folderDirectory, 'Plots')
                if not os.path.exists(plotFolder):
                    os.makedirs(plotFolder)
                for cycle, plots in self.heatMapPlots.items():
                    plots["fig"].savefig(os.path.join(plotFolder, f'HeatMap_Cycle({cycle}).png'))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
              
    def updateProgress(self, canvas:BaseCanvas): 
    
        if self.inOutManger.isRunning():
            self.ui.after(100, lambda:self.updateProgress(canvas))
        else:
            self.canvas.submitButton.config(bg='lightgreen')
            self.ui.print('Finished ...')
        
        elapsed_seconds = int(time.time() - self.startTime)
        # Convert elapsed milliseconds to total seconds
        hours = elapsed_seconds// 3600
        minutes = (elapsed_seconds % 3600) // 60
        seconds = elapsed_seconds % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        self.ui.clearProgress(canvas)
        self.ui.print(f'Time Elapsed: {time_str}')

        #NOTE: "totalDevCount" incoporates cycle number within this value alongside the number of devices for Binary mode
        match canvas.modeState.get():

            case 'pulse_test':

                if self.canvas.applyToAllDevices.get():
                    self.ui.print(f'Progress: ({int((self.inOutManger.progress/4096) * 100)}%)') # 4096 FIXED TO MEET 64x64 REQUIREMENT
                else:
                    self.ui.print(f'Progress: ({int((self.inOutManger.progress/self.totalDevCount) * 100)}%)')

            case 'pulse_step_test':

                #dividing by the number of steps given how many more times each step will add to this percentage,
                #while also dividing by 2 for the "Rise then Fall" direction when it does both directions per cycle
                if self.canvas.incrementVoltage.get(): # if the voltage increments, there will be an extra step since min and max inclusive
                    extraStep = 1
                else:
                    extraStep = 0
                if(canvas.stepVoltageDirection.get() == 'Rise then Fall'):
                    self.ui.print(f'Progress: ({int((self.inOutManger.progress/(self.totalDevCount * ((canvas.stepNumber.get() + extraStep) * 2))) * 100)}%)')
                else:
                    self.ui.print(f'Progress: ({int((self.inOutManger.progress/(self.totalDevCount * (canvas.stepNumber.get() + extraStep))) * 100)}%)')

            case 'pulse_cycle_test':

                #dividing by 2 given how this will be doing two separate pulse tests (SET and RESET) per cycle
                self.ui.print(f'Progress: ({int((self.inOutManger.progress/(self.totalDevCount * 2)) * 100)}%)')

            case 'iv_test':
                #dividing by the number of steps given how many more times each step will add to this percentage,
                #while also dividing by 2 for the IV state when it does both SET and RESET per cycle
                if(canvas.IvTestState.get() == 'IV'):
                    self.ui.print(f'Progress: ({int((self.inOutManger.progress/(self.totalDevCount * canvas.stepNumber.get() * 2)) * 100)}%)')
                else:
                    self.ui.print(f'Progress: ({int((self.inOutManger.progress/(self.totalDevCount * canvas.stepNumber.get())) * 100)}%)')

    def isValidSetting(self, canvas:BaseCanvas):

        if(canvas.modeState.get() == 'iv_test'): #IV test specific error checks

            if (canvas.stepNumber.get() <= 0): #if the step number is <= 0, thrown an error
                self.ui.print('Invalid settings: Step Number ...')
                self.ui.print('Must be greater than 0 ...')
                return False

        # - - - - - - - - - - - - - - - - - - - - - -
        
        if canvas.modeState.get() == 'pulse_step_test':
            # Stacia's note: it doesn't care if the max is zero if it's not stepping
            if(canvas.maxFormSetVoltage.get() <= 0):
                if (not (canvas.maxFormSetVoltage.get() == 0 and \
                    canvas.chosenStepVoltage.get() == 'RESET' and \
                    canvas.stepVoltageDirection.get() != 'Rise then Fall')):
                    self.ui.print('Invalid settings: Max Form/Set Voltage ...')
                    self.ui.print('Must be greater than 0 ...')
                    return False
            if(canvas.maxResetVoltage.get() <= 0):
                if (not (canvas.maxResetVoltage.get() == 0 and \
                    canvas.chosenStepVoltage.get() == 'SET' and \
                    canvas.stepVoltageDirection.get() != 'Rise then Fall')):
                    self.ui.print('Invalid settings: Max Reset Voltage ...')
                    self.ui.print('Must be greater than 0 ...')
                    return False
            
            # Stacia's note: used to be just >, caused infinite looping when = (looping could be fixed if necessary)
            # also added condition that it only cares if they're greater than 0 and stepping
            # extra note: if min step voltage is 0 when it will be used,
            # this will likely cause a recursion error from readlines (delay must be updated)
            if (((canvas.resetVoltage.get() >= canvas.maxResetVoltage.get()) \
                and canvas.maxResetVoltage.get() != 0 and (canvas.chosenStepVoltage.get() == 'RESET' \
                or canvas.stepVoltageDirection.get() == 'Rise then Fall')) or \
               ((canvas.formSetVoltage.get() >= canvas.maxFormSetVoltage.get() \
                 and canvas.maxFormSetVoltage.get() != 0) and (canvas.chosenStepVoltage.get() == 'SET' \
                or canvas.stepVoltageDirection.get() == 'Rise then Fall'))):
                self.ui.print('Invalid settings: Min Step Voltage ...')
                self.ui.print(f' must be less than max step voltage ...')
                return False
            
            if (canvas.stepNumber.get() <= 0):
                self.ui.print('Invalid settings: Step Number ...')
                self.ui.print('Must be greater than 0 ...')
                return False    
        
        if canvas.modeState.get() == 'pulse_test':

            # if the selected mode is FORM but no reads are used, invalid
            # must have either read 1 or read 2 so that the devices can be read prior to applying form voltage
            if self.canvas.formSetStateString.get() == 'FORM':
                if (self.canvas.formSetReadVoltage.get() == 0 or self.canvas.formSetReadTime.get() == 0) \
                    and (self.canvas.resetReadVoltage.get() == 0 or self.canvas.resetReadTime.get() == 0):
                    self.ui.print('Invalid settings: When FORM voltage applied ...')
                    self.ui.print('At least one Read voltage and time must be > 0 ...')
                    return False
        
            if self.canvas.utilizeCurResRange.get():

                if canvas.pulseTestRangeCycleCount.get() < 1:
                    self.ui.print('Invalid settings: Pulse Test Range Cycle Count ...')
                    self.ui.print('Must be greater than 0 ...')
                    return False
                
                if (canvas.hrsRangeMax.get() < canvas.hrsRangeMin.get()) or \
                    (self.canvas.lrsRangeMax.get() < self.canvas.lrsRangeMin.get())    :
                    self.ui.print('Invalid settings: Pulse Test Range ...')
                    self.ui.print('Max must be greater than Min ...')
                    return False
                
                if (canvas.formSetVoltage.get() <= 0) or (canvas.resetVoltage.get() <= 0):
                    self.ui.print('Invalid settings: Set Voltage and Reset Voltage ...')
                    self.ui.print('Cannot perform range test if reset and set voltage are not set ...')
                    return False
                
                if (canvas.resetReadVoltage.get() <= 0):
                    self.ui.print('Invalid settings: Read2 Voltage ...')
                    self.ui.print('resetReadVoltage cannot be 0 for range test ...')
                    return False
                
                if (canvas.formSetReadVoltage.get() > 0):
                    self.ui.print('Invalid settings: Read1 Voltage ...')
                    self.ui.print('Only Read2 is allowed for range test ...')
                    return False

                if (canvas.minResetVoltage.get() < 0) or (canvas.minGateVoltage.get() < 0):
                    self.ui.print('Invalid settings: Min Reset Voltage and Min Gate Voltage ...')
                    self.ui.print('Must be greater than 0 ...')
                    return False
                
                # note: if rangeGateVoltage or rangeResetVoltage is 0 when it will be used,
                # this will likely cause a recursion error from readlines (delay must be updated)
                if (canvas.minGateVoltage.get() < 0):
                    self.ui.print('Invalid settings: Range Gate Voltage ...')
                    self.ui.print('Must be greater than or equal to 0 ...')
                    return False
                
                if (canvas.minResetVoltage.get() < 0):
                    self.ui.print('Invalid settings: Range Reset Voltage ...')
                    self.ui.print('Must be greater than or equal to 0 ...')
                    return False

                if not canvas.applyToAllDevices.get():

                    if (canvas.hrsRangeMax.get() > 0) and (canvas.lrsRangeMax.get() > 0):
                        self.ui.print('Invalid settings: HRS and LRS range ...')
                        self.ui.print('Must only use HRS or LRS for range test in single device mode ...')
                        return False
                
               
            if canvas.applyToAllDevices.get():
                if (canvas.formSetStateString.get() == 'FORM'):
                    self.ui.print('Invalid settings: Form Set State ...')
                    self.ui.print('Cannot select FORM if applyToAllDevices is selected ...')
                    return False
                
                if canvas.utilizeCurResRange.get() and \
                    ((canvas.hrsRangeMax.get() <= 0) or (canvas.lrsRangeMax.get() <= 0)):
                    self.ui.print('Invalid settings: HRS and LRS range ...')
                    self.ui.print('Must use HRS and LRS for range test in multi device mode ...')
                    return False
                
                if (canvas.resetReadVoltage.get() <= 0):
                    self.ui.print('Invalid settings: Read2 Voltage ...')
                    self.ui.print('resetReadVoltage cannot be 0 for range test ...')
                    return False


        if self.ui.binaryMode.get() and self.ui.cellGrid.SelectedDevCount == 0:
            self.ui.print('No devices selected ...')
            return False   
        
        if (canvas.gateVoltage == 0) or \
            not ((canvas.formSetVoltage != 0) or (canvas.resetVoltage != 0) \
            or (canvas.resetReadVoltage != 0) or (canvas.formSetReadVoltage != 0)):

            self.ui.print('Invalid settings ...')
            return False
        
        # range verification makes its own plots that do not require read1
        # RESET IV testing cannot have read1 either so that is circumvented
        #if canvas.createSavePlots.get() and canvas.formSetReadVoltage.get() <= 0 and \
        #    not canvas.utilizeCurResRange.get() and canvas.IvTestState.get() != 'RESET':
        #    self.ui.print('Invalid settings ...')
        #    self.ui.print('Read 1 voltage must be greater than 0 to make plots ...')
        #    return False

        return True 


    def getDevicesCount(self, canvas:BaseCanvas):
        if canvas.applyToAllDevices.get() or self.ui.colorMode.get():
            self.ui.cellGrid.totalDevCount*canvas.cycleNumber.get()
        else:
            self.ui.cellGrid.SelectedDevCount*canvas.cycleNumber.get()
    
    
    def closeThreads(self):
        try:
            self.ui.print('Stop Button Pressed ...')
            self.ui.print('Closing threads ...')
            self.inOutManger.hardStop()
            self.ui.print('aborting ...', isDone=True)
            self.ui.after(500, lambda canvas=self.canvas: self.ui.clearProgress(canvas))
            self.canvas.submitButton.config(bg='lightgreen')

        #if the GUI "Stop" button is pressed BEFORE any "Send" button presses,
        #no processing canvas/threads will exist to close
        except:
            print('No processed canvas/threads have been created to Stop yet') 
    
    def closeMaster(self):
        self.inOutManger.hardStop()
        self.ui.destroy()
