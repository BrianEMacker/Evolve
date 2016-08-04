# Copyright 2015 Brian Macker
import turtle
import math
from creature import *

class CreaturePanel:
    """ Class to control a single creature display panel.

        Note: Subclassed from printableAttributes for use when doing hardcoded debugging.

        A panel contains a single creature, has a rectangular border, and can
        be communicated with using a right or left mouse click.
    """
    
    def __init__(self, creatureDisplay, creatureIndex, exteriorLeftX, exteriorBottomY):
        """ Constructor for a CreaturePanel

            Args:
                creatureDisplay (CreatureDisplay): The creature display singleton object
                creatureIndex (int): Index of the creature belonging to this panel.
                   This index is used to access the creature from the creatureArray.
                exteriorLeftX (int): The x position of the left edge of the panel border
                exteriorBottomY (int): y position of the bottom edge of the panel border.
        """

        #**********************************************
        # Save the passed in parameters as attributes
        #**********************************************

        #: CreatureDisplay: The display this panel belongs to
        self.creatureDisplay = creatureDisplay
        #: int: Index of the creature belonging to this panel.
        self.creatureIndex = creatureIndex
        #: int: The x position of the left edge of the panel border
        self.exteriorLeftX = exteriorLeftX
        #: int: y position of the bottom edge of the panel border.
        self.exteriorBottomY = exteriorBottomY

        #*****************************************************
        # Define the area the creature has to fit into
        # This is the area that is blanked out during redraw
        #*****************************************************
        
        #: int: The x position of the left interior edge of the blank area
        self.interiorLeftX = exteriorLeftX + creatureDisplay.PANEL_BORDER_WIDTH
        #: int: The y position of the bottom interior edge of the blank area
        self.interiorBottomY = exteriorBottomY + creatureDisplay.PANEL_BORDER_WIDTH
        #: int: The x position of the right interior edge of the blank area
        self.interiorRightX = exteriorLeftX + creatureDisplay.panelWidth - creatureDisplay.PANEL_BORDER_WIDTH
        #: int: The y position of the top interior edge of the blank area
        self.interiorTopY = exteriorBottomY + creatureDisplay.panelHeight - creatureDisplay.PANEL_BORDER_WIDTH

    def drawPanelBorder(self):
        """ Draw a border around this panel using the panel border attributes.
        """
        creatureDisplay = self.creatureDisplay
        creatureDisplay.drawRectangle(self.exteriorLeftX, self.exteriorBottomY,
                                      creatureDisplay.panelWidth, creatureDisplay.panelHeight,
                                      creatureDisplay.PANEL_BORDER_WIDTH,
                                      creatureDisplay.PANEL_BORDER_COLOR)
    def erasePanel(self):
        """ Erase the interior of the panel.
        """
        creatureDisplay = self.creatureDisplay
        creatureDisplay.drawRectangle(self.exteriorLeftX + creatureDisplay.PANEL_BORDER_WIDTH,
                                      self.exteriorBottomY + creatureDisplay.PANEL_BORDER_WIDTH,
                                      creatureDisplay.panelInteriorWidth, creatureDisplay.panelInteriorHeight,
                                      1,
                                      creatureDisplay.PANEL_BACKGROUND_COLOR, creatureDisplay.PANEL_BACKGROUND_COLOR)
    def leftClick(self):
        """ Handle a left click event inside the panel to make this a parent.
        
            The left click event will make the current creature in the panel the parent creature
            for mutant children populated to all other panels.  It then labels the parent as such.
        """
        
        # Make the creature on this panel the parent creature
        self.creatureDisplay.makeParent(self.creatureIndex)

        # Redrawn Parent to erase any text in panel
        self.erasePanel()
        self.displayCreature()

        # Indicate this is the Parent
        self.writePanelWord("Parent", "red")

    def rightClick(self):
        """ Handle a right click event inside the panel to replace with a new creature.
        
            The right click event will replace the current creature with a brand new mutant.
            It then labels the panel as having been replaced.
        """
        
        # Kill that creature
        self.creatureDisplay.replaceCreature(self.creatureIndex)

        # Indicate it has been replaced
        # self.writePanelWord("Replaced", "blue")

    def writePanelWord(self, word, color):
        """ Write a word in the lower left corner of the panel in the color specified.

            Args:
                word (str): The word to write
                color (str): The color to use.  Allowed color names are specified by turtle graphics.
        """

        self.creatureDisplay.write(self.interiorLeftX + self.creatureDisplay.PANEL_TEXT_MARGIN,
                                   self.interiorBottomY,
                                   word, color)

    def startingPenPosition(self):
        """ Return the starting pen position for the panels creature.
        
            The pen position is the center of the panel pointing up.
            
         Returns:
            PenPosition object set to the center of the panel pointing up.
       """

        # Determine the center of the panel
        xCenterPos = self.exteriorLeftX + (self.creatureDisplay.panelWidth / 2)
        yCenterPos = self.exteriorBottomY + (self.creatureDisplay.panelHeight / 2)
        
        # Get the pen and move it to the initial pen position for drawing a creature.
        pen = self.creatureDisplay.pen
        pen.penup()                             # Don't accidentally draw as we move the pen
        pen.setposition(xCenterPos, yCenterPos) # Center the pen
        pen.setheading(90)                      # Point the pen up

        # Return a newly constructed pen position set to where the pen is currently positioned.
        return PenPosition(pen)

    def displayCreature(self):
        """ Display the creature in its panel.  

            Displays the creature belonging to the panel and returns if it is successful.
            If it fails to display because it is too big for the panel then it keep trying
            with new creatures until it succeeds.  The successfully drawn new creature will
            replace the original.  If a parent exists then the new creatures will
            be mutated children of the parent, otherwise just new random creatures. 
        """
        # Get the current creature for this panel
        creature = self.creatureDisplay.creatureArray[self.creatureIndex]

        # If we can display it then return
        if creature != None:
            if creature.display(self):
                # Return because we are done
                return None
        
        # Get the parent creature
        parentCreature = self.creatureDisplay.parentCreature
        
        # Loop forever until we can properly show a creature without it failing
        # because it runs outside the borders, has too many segements, etc.
        while True:
            # Generate another creature
            # If there is no parent then
            if parentCreature == None:
                # Generate a random creature
                creature = Creature()
            # Otherwise there is a parent so
            else:
                # Generate a mutated child of the parent
                creature = parentCreature.mutatedChild()

            # If the creature can be displayed then 
            if creature.display(self):
                # Save the good creature
                self.creatureDisplay.creatureArray[self.creatureIndex] = creature

                # Return because we are done
                return None


        # Return
        return None
        
    
class CreatureDisplay():
    """ Class to control the entire display of all creatures

        Note: Subclassed from printableAttributes for use when doing hardcoded debugging.
        
        Attributes:
            PANEL_BORDER_WIDTH (int) = Width of a panel border line
            PANEL_BORDER_COLOR (str) = Color of a panel border line
            PANEL_BACKGROUND_COLOR (str) = Color of the panel background
    """
    
    PANEL_BORDER_WIDTH = 3
    PANEL_BORDER_COLOR = "green"
    PANEL_BACKGROUND_COLOR = "black"
    PANEL_TEXT_MARGIN = 6     # Margin required between text and border

    #********************
    # Private attributes
    #********************
    _HEADER_TEXT_LINE_HEIGHT = 20    # Height in pixels of standard text line
    _HEADER_TEXT_MARGIN = 6     # Margin required between text and border
    _HEADER_TEXT_COLOR = "white"
    _HEADER_BORDER_WIDTH = 3
    _HEADER_BORDER_COLOR = "light green"
    _HEADER_BACKGROUND_COLOR = "black"
    _HEADER_TEXT = ["Left click a parent creature to breed child mutants to other boxes.",
                   "Right click on any creature to replace with a new random creature.",
                   "Right click to this header to replace all.  Press ESC to quit."]
    
    def __init__(self, rows=2, columns=2):
        """ Constructor for a CreaturePanel

            Args:
                rows (int): How many rows of creature panels to display.
                columns (int): How many columns of creature panels to display.
        """

        # Initialize the turtle graphics window
        self.window = turtle.Screen()
        self.window.bgcolor("black")
        self.window.tracer(0,0)     # This turns off screen refresh which dramatically increases the speed
        screensize = self.window.screensize()
        self._screenwidth = screensize[0] * 2
        self._screenheight = screensize[1] * 2
        turtle.setworldcoordinates(0, 0, self._screenwidth, self._screenheight)

        # Initialize the turtle
        self.pen = turtle.Turtle()
        self.pen.speed(0)           # Set the turtle to maximum speed
        self.pen.color("green")
        self.pen.hideturtle()
        self.rows = rows
        self.columns = columns
        self.creatureCount = rows * columns

        # The parent creature to use in generating children in empty panels during drawing process
        # Panels will empty on each generation caused by a mouse click, or if a creature dies for any reason
        # Initially set the parent creature to none 
        # None indicates that a random creature should be generated to fill an empty panel during drawing
        self.parentCreature = None

        self._initializeHeaderSize()
        self._drawHeaderBox()
        self._initializePanelSize()
        self._initializeScreenDivisions()
        self._initializeCreatures()
        self.eraseAllCreaturePanels()
        self.drawAllCreaturePanels()
        
        #***********************
        # Initialize the mouse
        #***********************

        # First get the window object
        window = turtle.Screen()
        
        # Initialize left mouse click
        window.onscreenclick(leftClick, 1)   
        # Initialize right mouse click
        window.onscreenclick(rightClick, 2)  # Some systems this is right button
        window.onscreenclick(rightClick, 3)  # Some systems this is right button

        # Initalize various keys to terminate
        window.onkey(quitDisplay, "Escape")
        window.onkey(quitDisplay, "space")
        window.listen()   # Listen for key events
        

    def clickedPanel(self, xCoordinate, yCoordinate):
        """ Return the creature panel that is at location (x,y), or None if not on panel.
            Args:
                xCoordinate (int): The x coordinate that was mouse clicked
                yCoordinate (int): The y coordinate that was mouse clicked

            Returns:
                CreaturePanel which was clicked, or None
        """
        # Calculate the panel column and row which the mouse click is on.
        panelColumn = int(math.floor(xCoordinate/self.panelWidth))
        panelRow = int(math.floor(yCoordinate/self.panelHeight))

        # If the panel column and row numbers fall within the defined panel array then
        if ((panelColumn >=0) and (panelRow>=0) and (panelColumn < self.columns) and (panelRow < self.rows)):
            # Return the CreaturePanel at that position
            return self.creaturePanelArray[(panelRow * self.columns) + panelColumn]

        # Otherwise return None because click was outside the table of creature panels
        return None
            
    def leftClick(self, xCoordinate, yCoordinate):
        """ Process a left click on the display.   This will cause creature replacement.
            Args:
                xCoordinate (int): The x coordinate that was mouse clicked
                yCoordinate (int): The y coordinate that was mouse clicked
        """
        creaturePanel = self.clickedPanel(xCoordinate, yCoordinate) 
        if creaturePanel != None:
            creaturePanel.leftClick()
        

    def rightClick(self, xCoordinate, yCoordinate):
        """ Process a right click on the display.   This will cause parenthood if done on a creature panel.
            Args:
                xCoordinate (int): The x coordinate that was mouse clicked
                yCoordinate (int): The y coordinate that was mouse clicked
        """
        creaturePanel = self.clickedPanel(xCoordinate, yCoordinate) 
        if creaturePanel != None:
            creaturePanel.rightClick()
        # Otherwise a right click outside any panel will cause all creatures to be replaced
        else:
            self._replaceAllCreatures()

    def _initializeHeaderSize(self):
        """ Initialize private attributes defining the size of display header. """

        # The height of the header with the border included
        self._headerHeight = (self._HEADER_TEXT_LINE_HEIGHT * len(self._HEADER_TEXT)) + ((self._HEADER_BORDER_WIDTH + self._HEADER_TEXT_MARGIN)* 2);
        # The x position of the left edge of the header border
        self._headerLeftX = 0;
        # The y position of the bottom edge of the header border
        self._headerBottomY = self._screenheight - self._headerHeight + self.PANEL_BORDER_WIDTH;
        
    def _initializePanelSize(self):
        """ Initialize public attributes defining the size of one creature panel. """
        
        #: int: The width of one creature panel
        self.panelWidth = (self._screenwidth-self.PANEL_BORDER_WIDTH)/self.columns
        #: int: The height of one creature panel
        self.panelHeight = (self._screenheight - self._headerHeight)/self.rows        
        #: int: The interior width of one creature panel not including the border
        self.panelInteriorWidth = self.panelWidth - (2 * self.PANEL_BORDER_WIDTH)
        #: int: The interior height of one creature panel  not including the border
        self.panelInteriorHeight = self.panelHeight - (2 * self.PANEL_BORDER_WIDTH)     
        
    def write(self, x, y, text, color):
        """ Write text at (x,y) location with the specified color.
            Args:
                x (int): The x coordinate for the text
                y (int): The y coordinate for the text
                text (str): The text string to write
                color (str): The text color
        """
        self.pen.penup()            # Raise the pen to prevent unwanted drawing
        self.pen.setposition(x, y)  # Place the pen at the position to write the text
        self.pen.color(color)       # Set pen to text color
        self.pen.write(text, align="left", font=("Courier", 14, "bold")) # Write the text

    def drawLine(self, startx, starty, endx, endy, lineWidth, color):
        """ Draw a line as specified.
            Args:
                startx (int): The x coordinate of the start of the line
                starty (int): The y coordinate of the start of the line
                endx (int): The x coordinate of the end of the line
                endy (int): The y coordinate of the end of the line
                lineWidth (int): The width of the line in pixels
                color (str): The text color
        """
        self.pen.penup()                        # Raise the pen to prevent unwanted drawing
        self.pen.width(lineWidth)               # Set the pen to draw the width of the line
        self.pen.setposition(startx, starty)    # Place the pen at the position to write the text
        self.pen.color(color)                   # Set pen to the line color
        self.pen.pendown()                      # Put pen down so can start drawing
        self.pen.setposition(endx, endy)        # Draw to the end of the line

    def drawRectangle(self, leftX, bottomY, width, height, borderWidth, color, fillcolor=""):
        """ Draw a rectangle as specified
            Args:
                leftX (int): The x coordinate of left edge
                bottomY (int): The y coordinate of the bottom edge
                width (int): The width of the rectangle on the x axis
                height (int): The height of the rectangle on the y axis
                borderWidth (int): The width of the rectangles border line in pixels
                color (str): The color of the border
                fillcolor (str=""): An optional color used to fill the rectangle.  Default is no fill.
        """
        
        # Calculate what half the border width is so can center the rectangles border
        # so the outside edge is exactly inside the defined boundaries
        halfBorderWidth = (borderWidth/2)

        # Calculate the other two border edge positions
        rightX = leftX + width;
        topY = bottomY + height;

        # Start the drawing process by positioning to first corner    
        self.pen.penup()                        # Raise the pen to prevent unwanted drawing
        self.pen.setposition(leftX, bottomY)    # Position to start at bottom left corner of the rectangle

        #********************
        # Set pen attributes
        #********************
        self.pen.color(color)                   # Set the pen to the color of the line
        self.pen.width(borderWidth)             # Set the pen to the border width
        
        # If a fill color was provided
        if (fillcolor != ""):
            # Set the fill color and begin the fill
            self.pen.fillcolor(fillcolor)
            self.pen.begin_fill();
        self.pen.pendown()                      # Put pen down to start drawing

        #****************************************************************
        # Draw all around all four corners back to the starting position
        #****************************************************************
        self.pen.setposition(rightX, bottomY)   
        self.pen.setposition(rightX, topY)
        self.pen.setposition(leftX, topY)
        self.pen.setposition(leftX, bottomY)
        
        # If a fill color was provided
        if (fillcolor != ""):
            # End the filling which will fill in the rectangle
            self.pen.end_fill();

    def _drawHeaderBox(self):
        """ Draw the display header box with text
                fillcolor (str=""): An optional color used to fill the rectangle.  Default is no fill.
        """
        self.drawRectangle(self._headerLeftX, self._headerBottomY,
                           self._screenwidth - self.PANEL_BORDER_WIDTH,
                           self._headerHeight - self._HEADER_BORDER_WIDTH,
                           self._HEADER_BORDER_WIDTH, self._HEADER_BORDER_COLOR,
                           self._HEADER_BACKGROUND_COLOR)
        headerTextLeftMargin = self._headerLeftX + self._HEADER_BORDER_WIDTH + self._HEADER_TEXT_MARGIN
        headerTextBottomMargin =  self._headerBottomY + self._HEADER_BORDER_WIDTH + self._HEADER_TEXT_MARGIN
        headerTextLines = len(self._HEADER_TEXT)
        for headerIndex in range(headerTextLines):
            headerText = self._HEADER_TEXT[headerIndex]
            self.write(headerTextLeftMargin,
                       headerTextBottomMargin  + (self._HEADER_TEXT_LINE_HEIGHT * (headerTextLines - 1 - headerIndex)),
                       headerText, self._HEADER_TEXT_COLOR)

    def _initializeCreaturePanel(self, creatureIndex):
        """ Initialize the creature panel corresponding to the creature at the index.
            
            Args:
                creatureIndex (int): The index of the creature in the creatureArray

            Returns:
                CreaturePanel: The creature panel belonging to the creature at that index.
        """

        # Figure out the zero based row and column of the panel in the table
        row = creatureIndex // self.columns 
        column = creatureIndex % self.columns

        # Calculate where the left bottom corner of the panel is
        leftX = column * self.panelWidth
        bottomY = row * self.panelHeight

        # Create the creature panel for that position and draw it's border to initialize the panel display
        creaturePanel = CreaturePanel(self, creatureIndex, leftX, bottomY)
        creaturePanel.drawPanelBorder()

        # Return that creature panel
        return creaturePanel
    
    def _initializeScreenDivisions(self):
        """ Initialize the creature panel divisions and place them in the creature panel array.
        """
        self.creaturePanelArray = [self._initializeCreaturePanel(creatureIndex) for creatureIndex in range(self.creatureCount)]
        
    def _initializeCreatures(self):
        """ Initialize the creatures and place them in the creature array.
        """
        self.creatureArray=[Creature() for creatureIndex in range(self.creatureCount)]
        
    def drawAllCreaturePanels(self):
        """ Display all the creatures in their panels.
        """
        for creaturePanel in self.creaturePanelArray:
            creaturePanel.displayCreature()
                
    def eraseAllCreaturePanels(self):
        """ Erase all creatures from their creature panels.
        """
        for creaturePanel in self.creaturePanelArray:
            creaturePanel.erasePanel()

    def makeParent(self, parentIndex):
        """ Make the creature at the parent index into the parent of all other creatures.
            
            Args:
                parentIndex (int): The index of the creature iwhich becomes the parent.
        """
        
        # Make the creature on this panel the parent creature
        if parentIndex in range(self.creatureCount):
            self.parentCreature = self.creatureArray[parentIndex]
        else:
            self.parentCreature = None

        # Kill every other creature and replace with a mutated child
        for creatureIndex in range(self.creatureCount):
            # If this is not the parent creature
            if creatureIndex != parentIndex:
                # If there is a parent then replace with the parents mutated child
                if self.parentCreature != None:
                    self.creatureArray[creatureIndex] = self.parentCreature.mutatedChild()
                # Otherwise create a brand new random creature
                else:
                    self.creatureArray[creatureIndex] = Creature()
                    
                # Erase the panel
                self.creaturePanelArray[creatureIndex].erasePanel()
                # Draw the new child
                self.creaturePanelArray[creatureIndex].displayCreature()

    def _replaceAllCreatures(self):
        """ Replace all creatures with new randomly generated ones.
        """
        # Save the old parent
        oldParent = self.parentCreature
        
        # Replace every creature with a new random one except a prior parent
        for creatureIndex in range(self.creatureCount):
            # If this is not the parent creature then
            if oldParent != self.creatureArray[creatureIndex]:
                # Replace with a random creature
                self.replaceCreature(creatureIndex)

    def replaceCreature(self, creatureIndex):
        """ Replace the creature at the index with new randomly generated one.
            
            Args:
                creatureIndex (int): The index of the creature in the creatureArray
        """

        # There is no parent for this creature
        # This will cause display algorithm to use random creature to fill empty panel
        self.parentCreature = None

        # Kill the creature in this panel
        self.creatureArray[creatureIndex] = None
        
        # Erase the panel
        self.creaturePanelArray[creatureIndex].erasePanel()
        
        # Draw (which will replace with new random creature
        self.creaturePanelArray[creatureIndex].displayCreature()
        
        # Indicate it has been replaced
        #self.creaturePanelArray[creatureIndex].writePanelWord("Replaced", "blue")


# Function to handle left click on creature display         
def leftClick(x, y):
    """ Handle left click on creature display.

        This must be a module function to be compatible with the screen callback.

        Args:
            x (int): The x position of the click
            y (int): The y position of the click
    """

    # Process the click with the creature display singleton
    autoCreatureDisplay.leftClick(x, y)
    return 0

# Function to handle right click on creature display         
def rightClick(x, y):
    """ Handle right click on creature display.

        This must be a module function to be compatible with the screen callback.

        Args:
            x (int): The x position of the click
            y (int): The y position of the click
    """

    # Process the click with the creature display singleton
    autoCreatureDisplay.rightClick(x, y)
    return 0

# Method to quit the turtle main loop on key press
def quitDisplay():
    """ Handle quiting the creature display.

        This must be a module function to be compatible with the key press callback.
    """

    # End the display which will terminate the main loop and leave.
    turtle.Screen().bye()

# How many rows and columns of creatures to display
CreatureRows = 3
CreatureColumns = 4
    
# Variable to contain the only create display needed
# Use this as simple singleton generating method because nothing more complex
# is needed.
# This causes the creature display to appear just by instantiating the class instance
autoCreatureDisplay = CreatureDisplay(CreatureRows,CreatureColumns)

# Start turtle main loop to handle the key and mouse input and interpretation  
turtle.Screen().mainloop()

