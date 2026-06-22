import time
from tkinter import BooleanVar, Tk,Canvas,  Label, Button, Entry, LabelFrame, Frame, Checkbutton, CENTER, SUNKEN
import copy
from threading import Thread
#-------------------------------------------------------------------------

#interactive grid (tkinter widget) class that can vary in
#row/column dimension sizes (BUT IN THIS CODE'S CASE, THE DIMENSIONS ARE FIXED)
class GridWindow:

    def __init__ (self, master:Tk, binaryModeCallBack): #set input requirements
    
        #NOTE: "master" input is a "tkinter.Tk()" class object/main window

        #set class variables based on inputs
        self.master = master
        self.rows = 64 #FIXED TO MEET THE 64x64 REQUIREMENT
        self.columns = 64 #FIXED TO MEET THE 64x64 REQUIREMENT

        self.binaryModeCallBack:BooleanVar = binaryModeCallBack

        self.grid:list[list[Button]] = [] #grid to be made as a 2D list of buttons
        self.rowButtons:list[Button] = []
        self.colButtons:list[Button] = []

        self.current_btn_size = 4
        self.current_font = 10
        self.finishGrid = False

        self.currView = "Normal"

        #2D list to store all boolean logic associated with the
        #grid buttons, all set to "False" by default
        #meant to be the same dimensions as self.grid
        self.gridBooleans:list[list[bool]] = []  # initialize the gridBooleans in side the loop to save running time

        #2D list to store the imported csv or image.
        self.importedGrid:list[list[bool]] = None

        self.SelectedDevCount = 0
        self.totalDevCount = self.rows * self.columns

        self.master.bind_all("<MouseWheel>", self.resize_grid)


        def worker():
            self.create_grid()
            self.createRowEdgeButtons()
            self.createColumnEdgeButtons()
            self.createCornerButton()
        Thread(target=worker, daemon=True).start()
    

    def getGridData(self):
        return copy.deepcopy(self.gridBooleans) if self.binaryModeCallBack.get() else copy.deepcopy(self.importedGrid)
    
    # - - - - - - - - -

    #allow for class ojbect to be iterable when necessary
    def __iter__(self):
        return iter(self.grid)

    # - - - - - - - - -

    def create_grid(self):
        def worker():  
            for gridRow in range(self.rows):
                row_widgets = []
                row_booleans = []

                for gridColumn in range(self.columns):
                    row_booleans.append(False)

                    # Capture values needed for button creation
                    gr, gc = gridRow, gridColumn
                    text = f"({gr},{gc})"

                    def create_button(gr=gr, gc=gc, text=text, row=row_widgets):
                        button = Button(
                            self.master,
                            command=lambda gr=gr, gc=gc: self.clickedButton(gr, gc),
                            bg='white',
                            text=text,
                            font=('Arial', self.current_font)
                        )
                        button.grid(row=gr + 1, column=gc + 1, sticky='nsew')
                        row.append(button)
                    self.master.after(1, create_button)
                    time.sleep(0.001)

                self.gridBooleans.append(row_booleans)
                self.grid.append(row_widgets)
            self.finishGrid = True
            


        Thread(target=worker, daemon=True).start()

    def createRowEdgeButtons(self):
        """
        Safely creates row-edge toggle buttons in a separate thread and schedules
        widget creation in the Tkinter main thread.
        """
        self.rowButtons = []

        def worker():
            for rowIndex in range(self.rows):
                def create_button(rowVal=rowIndex):
                    rowButton = Button(self.master,
                                        text='>', 
                                        bg='light green', 
                                        height=2, width=2, 
                                        font=('Arial', self.current_font))
                    rowButton.grid(row=rowVal + 1, column=0)
                    rowButton.is_selected = False

                    def callback():
                        rowButton.is_selected = not rowButton.is_selected
                        rowButton.config(
                            bg='light blue' if rowButton.is_selected else 'light green',
                            text='<' if rowButton.is_selected else '>'
                        )
                        self.selectAllRowCol(rowVal, 'row', rowButton.is_selected)

                    rowButton.config(command=callback)
                    self.rowButtons.append(rowButton)

                # Schedule the button creation in the main GUI thread
                self.master.after(1, create_button)
                time.sleep(0.001)

        Thread(target=worker, daemon=True).start()

    

    def createColumnEdgeButtons(self):
        """
        Safely creates column-edge toggle buttons in a separate thread and schedules
        widget creation in the Tkinter main thread.
        """
        self.colButtons = []

        def worker():
            for colIndex in range(self.columns):
                def create_button(colVal=colIndex):
                    colButton = Button(self.master,
                                        text='V', 
                                        bg='light green',  
                                        width = 2,
                                        font=('Arial', self.current_font))
                    colButton.grid(row=0, column=colVal + 1 ,sticky='ew')
                    colButton.is_selected = False

                    def callback():
                        colButton.is_selected = not colButton.is_selected
                        colButton.config(
                            bg='light blue' if colButton.is_selected else 'light green',
                            text='/\\' if colButton.is_selected else 'V'
                        )
                        self.selectAllRowCol(colVal, 'column', colButton.is_selected)

                    colButton.config(command=callback)
                    self.colButtons.append(colButton)

                # Schedule the button creation in the main GUI thread
                self.master.after(1, create_button)
                time.sleep(0.001)

        Thread(target=worker, daemon=True).start()


    def createCornerButton(self):
        # Create the top-left corner button to select/deselect the entire grid
        self.selectAllButton = Button(self.master, 
                                      text='ALL', 
                                      bg='light green', 
                                      width=2,
                                      height=1,
                                      font=('Arial', self.current_font))
        self.selectAllButton.grid(row=0, column=0)
        self.selectAllButton.is_selected = False  # initial state: unselected

        self.selectAllButton.config(command=self.toggleCornerButton)

    def toggleCornerButton(self):
        self.selectAllButton.is_selected = not self.selectAllButton.is_selected
        
        if self.currView == "Pixel":
            self.currView = 'Normal'
            self.binaryModeCallBack.set(True)

            self.selectAllButton.is_selected = False
            self.setNormalView()
            
        selectState = self.selectAllButton.is_selected
        self.toggle_all(selectState)
        # reset to binary mode.
        
        

    def toggle_all(self, selectState):

        if selectState:
            if self.SelectedDevCount == self.totalDevCount:
                return
            self.SelectedDevCount = self.totalDevCount
        else:
            if self.SelectedDevCount == 0:
                return
            self.SelectedDevCount = 0
        print("DeviceCount: ", self.SelectedDevCount)

        # Update button appearance
        self.selectAllButton.config(
            bg='light blue' if selectState else 'light green',
            text='CLR' if selectState else 'ALL'
        )

        # Update all row buttons
        for rowButton in self.rowButtons:
            rowButton.is_selected = selectState
            rowButton.config(bg='light blue' if selectState else 'light green',
                            text='<' if selectState else '>')

        # Update all column buttons
        for colButton in self.colButtons:
            colButton.is_selected = selectState
            colButton.config(bg='light blue' if selectState else 'light green',
                            text='/\\' if selectState else '\\/')

        # Update entire grid
        for r in range(self.rows):
            for c in range(self.columns):
                self.gridBooleans[r][c] = selectState
                self.grid[r][c].config(
                    bg='black' if selectState else 'white',
                    fg='red' if selectState else 'black'
                )


    def resize_grid(self, event):
        if event.state & 0x0004:  # Ctrl is pressed (state bitmask)
            maxSize = 5 if self.currView == 'Normal' else 15
            minSize = 1 if self.currView == 'Normal' else 1
            if event.delta > 0:   # Scroll up
                self.current_btn_size = min(self.current_btn_size + 1, minSize)
                self.current_btn_text_size = min(self.current_font + 1, 6)
            else:  # Scroll down
                self.current_btn_size = max(self.current_btn_size - 1, maxSize)

            # for row in self.grid:
            #     for btn in row:
            #         self.master.after(1, lambda btn=btn:btn.config(width=self.current_btn_size, height=self.current_btn_size))
            #         time.sleep(0.001)
            
            for rowBtn in self.rowButtons:
                self.master.after(1, lambda btn=rowBtn:btn.config(height=self.current_btn_size))

            for colBtn in self.colButtons:
                self.master.after(1, lambda btn=colBtn:btn.config(width=self.current_btn_size))
           


    def setPixelView(self):
        """Switch grid to pixel-accurate view."""
        print("Switching to Pixel View")
        # TODO: resize buttons to pixel-based sizes
        self.currView = "Pixel"
        self.current_btn_size = 5
        for row in self.grid:
            for btn in row:
                btn.config(text='', font=("Arial", 1), padx=0, pady=0,
                       borderwidth=0, relief="flat")
                try:
                    btn.master.grid_propagate(False)
                except:
                    pass

        for rowBtn in self.rowButtons:
            rowBtn.config(text='', font=("Arial", 1), padx=0, pady=0, borderwidth=0, relief="flat")
            rowBtn.config(height=self.current_btn_size)
            try:
                rowBtn.master.grid_propagate(False)
            except:
                pass

        for colBtn in self.colButtons:
            colBtn.config(text='', font=("Arial", 1), padx=0, pady=0, borderwidth=0, relief="flat")
            # the - 2 below makes the buttons more square so that it looks more accurate to the image
            # ensure that self.current_btn_size is set to 3 or higher to allow for this, or remove if desired
            colBtn.config(width=self.current_btn_size - 2)
            try:
                colBtn.master.grid_propagate(False)
            except:
                pass

        self.selectAllButton.config(text='RST')
        self.selectAllButton.is_selected = False

        

    def setNormalView(self):
        """Switch grid to normal text-unit view."""
        print("Switching to Normal View")
        self.current_btn_size = 2  # text-unit size
        self.currView = "Normal"
        self.selectAllButton.config(text='ALL', width=2, height=1,)
        # Restore main grid buttons

        # Restore row buttons
        for r, rowBtn in enumerate(self.rowButtons):
            rowBtn.config(
                text='>', 
                bg='light green', 
                height=2, width=2, 
                font=('Arial', self.current_font),
                borderwidth=2, relief="raised",
            )
            try:
                rowBtn.master.grid_propagate(True)
            except:
                pass

        # Restore column buttons
        for c, colBtn in enumerate(self.colButtons):
            colBtn.config(
                text='V', 
                bg='light green',  
                width = 5,
                font=('Arial', self.current_font),
                borderwidth=2, relief="raised",
            )
            try:
                colBtn.master.grid_propagate(True)
            except:
                pass   

        for r, row in enumerate(self.grid):
            for c, btn in enumerate(row):
                btn.config(
                    text=f"({r},{c})",
                    font=('Arial', self.current_font),
                    width=5,
                    bg='white',
                    fg = 'black',
                    borderwidth=2, relief="raised"
                )
                try:
                    btn.master.grid_propagate(False)  # Let the grid resize naturally
                except:
                    pass
                btn.config(width=self.current_btn_size, height=self.current_btn_size)        


    def reset_button_size(self, event):
        if event.state & 0x0004:  # Ctrl
            self.current_btn_size = 4
            for row in self.grid:
                for btn in row:
                    btn.config(width=4, height=2)
            for rowBtn in self.rowButtons:
                rowBtn.config(width=2, height=2)
            for colBtn in self.colButtons:
                colBtn.config(width=4)

    #function to address changes in button/boolean state for a cell at any
    #set row/column combination when the self.grid button for this cell is clicked
    def clickedButton(self, row, column):
        if not self.binaryModeCallBack.get():
            return
        
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
            self.SelectedDevCount += 1
            
        else: #otherwise (i.e. if black, reset to default text and background colors)
            singleCellButton.config(bg = 'white', fg = 'black')
            self.SelectedDevCount -= 1

        #change Boolean logic at the determined row/column cell position
        self.gridBooleans[row][column] = not singleCellBoolean
        print("DeviceCount: ", self.SelectedDevCount)
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

    # #function that will set all cells/devices to FALSE when prompted
    # def allFalse(self):

    #     #set boolean logic to all FALSE in self.gridBooleans
    #     self.gridBooleans = [[False for GridY in \
    #                           range(self.columns)] for GridX in range(self.rows)]

    #     #set the color for all buttons to their "FALSE" defaults
    #     #of a WHITE background with BLACK text
    #     for gridRow in range(self.rows):            
    #         for gridColumn in range(self.columns):
    #             singleCellButton = self.grid[gridRow][gridColumn]
    #             singleCellButton.config(bg = 'white', fg = 'black')                

    # - - - - - - - - -

    # #function that will set all cells/devices to TRUE when prompted
    # def allTrue(self):

    #     #set boolean logic to all TRUE in self.gridBooleans
    #     self.gridBooleans = [[True for GridY in \
    #                           range(self.columns)] for GridX in range(self.rows)]

    #     #set the color for all buttons to their "TRUE" defaults
    #     #of a BLACK background with RED text
    #     for gridRow in range(self.rows):            
    #         for gridColumn in range(self.columns):
    #             singleCellButton = self.grid[gridRow][gridColumn]
    #             singleCellButton.config(bg = 'black', fg = 'red')

    # - - - - - - - - -

    #function that will be called if any of the buttons around the grid
    #that represent all of one row or column is selected and will set all
    #of the grid buttons within that said row/column to True when pressed
    def selectAllRowCol(self, selectedIndex, directionString, selectState):
        """
            When a button representing an entire row or column is selected and 
            either the row or column index is provided, this function will set all 
            of the cells in that row or column to the given selectState.

            Parameters
            ----------
            selectedIndex : int
                The row or column index to modify
            directionString : str
                Either 'row' or 'column', indicating which direction to modify
            selectState : bool
                The state to set the cells to
        """

        if not self.binaryModeCallBack.get():
            return
        
        selectedCount = 0
        if directionString == 'row':
            for gridColumn in range(self.columns):
                if self.gridBooleans[selectedIndex][gridColumn]:
                    selectedCount += 1

                self.gridBooleans[selectedIndex][gridColumn] = selectState
                self.grid[selectedIndex][gridColumn].config(
                    bg='black' if selectState else 'white',
                    fg='red' if selectState else 'black'
                )
            #singleCellButton.config(bg = 'black', fg = 'red')
   
            #singleCellButton.config(bg = 'white', fg = 'black')
            if selectState:
                self.SelectedDevCount += self.columns - selectedCount # add 64 and subtract the a
            else:
                self.SelectedDevCount -=  selectedCount

        else:  # directionString == 'column'
            for gridRow in range(self.rows):
                if self.gridBooleans[gridRow][selectedIndex]:
                    selectedCount += 1
                self.gridBooleans[gridRow][selectedIndex] = selectState
                self.grid[gridRow][selectedIndex].config(
                    bg='black' if selectState else 'white',
                    fg='red' if selectState else 'black'
                )
            if selectState:
                self.SelectedDevCount += self.rows - selectedCount
            else:
                self.SelectedDevCount -= selectedCount
        print("DeviceCount: ", self.SelectedDevCount)
        
        

    # - - - - - - - - -

    # #function that will disable/return the buttons' states to normal in regards
    # #to user interactivity
    # #this is done to prevent users from changing buttons at unwanted times
    # def changeGridButtonStates(self, chosenStateCommand):

    #     #go through the entire list (grid) of buttons and set them
    #     #all to the chosenStateCommand state
    #     for gridRow in range(self.rows):            
    #         for gridColumn in range(self.columns):
    #             singleCellButton = self.grid[gridRow][gridColumn]
    #             singleCellButton['state'] = chosenStateCommand

#-------------------------------------------------------------------------
