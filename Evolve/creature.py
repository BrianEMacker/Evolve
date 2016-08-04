# Copyright 2015 Brian Macker
import random

class PenPosition:
    """ Class used to remember the pen position, and chirality.

        Instances of this class can save a pen position and associate a chirality
        (either right or left handed) to that position.   This is useful during the
        creature grown proces in remembering where a segment starts and whether it
        is has turned right or left from a prior position.

        Attribute:
            pen (turtle): The pen being used 
            chiralityRight (bool): The chirality (handedness) of the position.  True=right handed, False= left handed  
            xPosition (int): The saved pen x position
            yPosition (int): The saved pen y position 
            heading (int): The saved pen heading.  0-360 with 90 being straight up. 
    """
    def __init__(self, pen, chiralityRight = True):
        """ Constructor for a CreaturePanel

            Args:
                pen (turtle): The pen being used 
                chiralityRight (bool): The chirality (handedness) of the position.  True=right handed, False= left handed  
        """
        self.pen = pen
        self.chiralityRight = chiralityRight
        self.savePosition()
        
    def savePosition(self):
        """  Save the pen's position into this object.
        """
        self.xPosition = self.pen.xcor()
        self.yPosition = self.pen.ycor()
        self.heading = self.pen.heading()
        
    def restore(self):
        """  Restore the pen's position using this object.
        """
        self.pen.penup()
        self.pen.setposition(self.xPosition, self.yPosition)
        self.pen.setheading(self.heading)
        
    def flipChirality(self):
        """  Change the chirality from right to left, or left to right.
        """
        self.chiralityRight = not self.chiralityRight
        
    def clone(self):
        """ Return a clone of this instance.
    
            Returns:
                PenPostion: A clone of this instance.
        """

        # Duplicate the object
        clonedPenPosition = PenPosition(self.pen, self.chiralityRight)
        clonedPenPosition.xPosition = self.xPosition
        clonedPenPosition.yPosition = self.yPosition
        clonedPenPosition.heading = self.heading

        # Return the duplicate
        return clonedPenPosition


class Chromosome:
    """
    Class defining a single chromosome and how it creates the next segment(s).

    Note: Subclassed from printableAttributes for use when doing hardcoded debugging.
    
    @type chromosomeValue: int
    @param chromosomeValue: An integer value for the chromosome.  If not provided it will be randomly.  
    """

    # Definition of genes in the chromosome and what they do
    _BRANCH_ANGLE_GENE_BITS          = 0x0000003F # Bits for angle from current direction to branch (max 128 degrees)
    _BRANCH_ANGLE_SHIFT_NUMBER       = 0          # Branch angle bits start at bit 0
    _LENGTH_GENE_BITS                = 0x000007C0 # Bits for length of Segment (up to 265 pixels) [Line length, Dot or Circle diameter}
    _LENGTH_SHIFT_NUMBER             = 6          # Length bits start at bit 6
    _SYMMETRY_GENE_BITS              = 0x00003000 # Bits used for symmetry
    _SYMMETRY_SHIFT_NUMBER           = 12         # Symmetry bits start at bit 12
    _SYMMETRY_STRAIGHT_VALUE         = 0x0        # Symmetry: Segment goes straight with serial segment branching
    _SYMMETRY_SAME_HANDED_VALUE      = 0x1        # Symmetry: Branch in same direction as prior chromosome
    _SYMMETRY_OPPOSITE_HANDED_VALUE  = 0x2        # Symmetry: Branch in opposite direction of prior chromosome
    _SYMMETRY_BILATERAL_VALUE        = 0x3        # Symmetry: Branch in both directions
    _BRANCH_COUNT_GENE_BITS          = 0x00030000 # Branch count per direction (range is 1-3, zero means terminate growth)
    _BRANCH_COUNT_SHIFT_NUMBER       = 16         # Branch count bits start at bit 16
    _SEGMENT_TERMINATION_GENE_BITS   = 0x00030000 # Branch count bits are overloaded as termination flag when zero
    _SEGMENT_TERMINATED              = 0x00000000 # Value of zero means terminate growth of creature at this chromosome
    _SEGMENT_TERMINATION_PREVENT     = 0x00010000 # To prevent termination set this to indicate one branch.  
    _SHAPE_GENE_BITS                 = 0x000C0000 # Bits that indicate shape   
    _SHAPE_SHIFT_NUMBER              = 18         # Shape bits start at bit 24
    _SHAPE__LINE_VALUE               = 0          # Shape: Line
    _SHAPE_DOT_VALUE                 = 1          # Shape: Dot
    _SHAPE_CIRCLE_VALUE              = 2          # Shape: Empty Circle  
    _SHAPE_FILLED_CIRCLE_VALUE       = 3          # Shape: Filled Circle
    _LINE_WIDTH_GENE_BITS            = 0x00300000 # Bits for how much to widen line beyond one wide
    _LINE_WIDTH_SHIFT_NUMBER         = 20         # Line width bits start at bit 20
    _LINE_COLOR_GENE_BITS            = 0x07000000 # Three bits for line color giving 8 colors
    _LINE_COLOR_SHIFT_NUMBER         = 24         # Line color bits start at bit 24
    _FILL_COLOR_GENE_BITS            = 0x70000000 # Three bits for fill color giving 8 colors
    _FILL_COLOR_SHIFT_NUMBER         = 28         # Fill color bits start at bit 28

    # Provide eight segment colors 
    _SEGMENT_COLORS = ["brown", "red", "orange", "yellow", "green", "blue", "purple", "white"]
    _MAX_COLORS = 8

    # Create a chromosome randomly if the integer value is not provided
    def __init__(self, index, chromosomeValue = None):
        """ Constructor for a Chromosome.

            Args:
                index (int): The zero based chromosome number in the genome (list of all the creatures chromosomes)s.
                chromosomeValue (int): The value of the chromosome.  Default = None will cause a randomly generated chromosome value.  
        """

        # Store the chromosomes index into the genome
        self._index = index

        # Store the chromosomes integer value
        if (chromosomeValue == None):
            chromosomeValue = random.randint(0,0xFFFFFFFF)
            # If this is the first chromosome then force it to be bilateral
            # for the sake of making things interesting at first
            chromosomeValue |= self._SEGMENT_TERMINATION_PREVENT

        self.chromosomeValue = chromosomeValue

        # Now interpret the chromosome value
        self._interpretChromosomeValue()
        
    def _interpretChromosomeValue(self):
        """
        Interpret the chromosome value generating the decoded instance attributes.

        This should only be run from the constructor.
        """
    
        # Extract branch angle.
        # The angle at which the next segment should diverge from the path of the prior segment.
        self.branchAngle = (self.chromosomeValue & self._BRANCH_ANGLE_GENE_BITS) >> self._BRANCH_ANGLE_SHIFT_NUMBER
        # Extract segment length
        self.length = (self.chromosomeValue & self._LENGTH_GENE_BITS) >> self._LENGTH_SHIFT_NUMBER
        # Extract symmetry information
        self.symmetryBits = (self.chromosomeValue & self._SYMMETRY_GENE_BITS) >> self._SYMMETRY_SHIFT_NUMBER
        # Extract branch count information
        self.branchCount = (self.chromosomeValue & self._BRANCH_COUNT_GENE_BITS) >> self._BRANCH_COUNT_SHIFT_NUMBER
        if ((self.chromosomeValue & self._SEGMENT_TERMINATION_GENE_BITS) == self._SEGMENT_TERMINATED):
            self.terminated = True
        else:
            self.terminated = False
        # Extract line width.  Number indicates how much to widen past on bit wide.
        self.lineWidth  = 1 + (self.chromosomeValue & self._LINE_WIDTH_GENE_BITS) >> self._LINE_WIDTH_SHIFT_NUMBER
        # Extract line color
        lineColorOffset  = (self.chromosomeValue & self._LINE_COLOR_GENE_BITS) >> self._LINE_COLOR_SHIFT_NUMBER
        lineColorOffset %= self._MAX_COLORS
        self.lineColor = self._SEGMENT_COLORS[lineColorOffset]
        # Extract fill color
        fillColorOffset  = (self.chromosomeValue & self._FILL_COLOR_GENE_BITS) >> self._FILL_COLOR_SHIFT_NUMBER
        fillColorOffset %= self._MAX_COLORS
        self.fillColor = self._SEGMENT_COLORS[fillColorOffset]
        
        # Extract the shape
        self.shape  = (self.chromosomeValue & self._SHAPE_GENE_BITS) >> self._SHAPE_SHIFT_NUMBER

    # Given a starting postion generate a list of starting positions for the segments
    def childSegmentPositions(self, priorSegmentEndingPenPosition):
        """ Return a list of segments this chromosome will cause to bud off the end of the prior segment.

            Args:
                priorSegmentEndingPenPosition (PenPosition): The ending pen position of the parent segment we are budding from.

            Returns:
                PenPosition[]: An array of pen positions for all the child segments grown from the chromosome.
        """

        # Initially there are no child segments.
        childSegmentStartingPenPositions = []

        # Get a direct reference to the pen
        pen = priorSegmentEndingPenPosition.pen

        # Get the starting chirality as defined from the end of the prior segment.
        startingchiralityRight = priorSegmentEndingPenPosition.chiralityRight

        # Restore the pen to the position specified for the end of the parent segment.
        priorSegmentEndingPenPosition.restore()

        # If the chromosome is not defined as terminated then
        if (not self.terminated):
            # If the symmetry is straight forward then
            if (self.symmetryBits == self._SYMMETRY_STRAIGHT_VALUE):
                priorSegmentEndingPenPosition.restore()
                # Create pen positions for the branches serially connected moving straight forward
                for branchIndex in range(self.branchCount):
                    childSegmentStartingPenPositions.append(PenPosition(pen, startingchiralityRight))
                    pen.forward(self.length)
                    
            # Otherwise the symmetry is angled same, angled opposite, or both  indicating bilateral symmetry.
            else:
                # If the chromosome codes for creating branches with the same chriality
                # as the parent segment then do that same side first.
                if (self.symmetryBits & self._SYMMETRY_SAME_HANDED_VALUE):

                    # Position the pen at the end of the parent segment pointing in the direction it does.
                    priorSegmentEndingPenPosition.restore()

                    # Create the number of branches specified in the branch count.
                    # The first must diverge by the branch angle from the start position
                    # defined by the end of the prior segement. 
                    # Each additional segment should diverge from the prior by the branch angle.
                    for branchIndex in range(self.branchCount):
                        if (startingchiralityRight):
                            pen.right(self.branchAngle)
                        else:
                            pen.left(self.branchAngle)

                        # Save a new pen starting position for this new segement
                        # in the list of starting pen positions for this chromosome.
                        childSegmentStartingPenPositions.append(PenPosition(pen, startingchiralityRight))                    

                # If the chromosome codes for an opposite chirality then flip and do branches on the opposite side.
                #   Note: If the _SYMMETRY_SAME_HANDED_VALUE was also set and processed above, then this
                #   will cause a bilaterally symmetrical branching.   The prior section doing one side and this
                #   section doing the other side.
                if (self.symmetryBits & self._SYMMETRY_OPPOSITE_HANDED_VALUE):
                    # Flip chirality to do the opposite side
                    startingchiralityRight = not startingchiralityRight

                    # Position the pen at the end of the parent segment pointing in the direction it does.
                    priorSegmentEndingPenPosition.restore()

                    # Create the number of branches specified in the branch count.
                    # The first must diverge by the branch angle from the start position
                    # defined by the end of the prior segement. 
                    # Each additional segment should diverge from the prior by the branch angle.
                    for branchIndex in range(self.branchCount):
                        if (startingchiralityRight):
                            pen.right(self.branchAngle)
                        else:
                            pen.left(self.branchAngle)

                        # Save a new pen starting position for this new segement
                        # in the list of starting pen positions for this chromosome.
                        childSegmentStartingPenPositions.append(PenPosition(pen, startingchiralityRight))                    

        # Return the list of starting pen positions for the child segements           
        return childSegmentStartingPenPositions
            


    # Test a single segment constructed from this chromosome to see if it runs past the panel boundaries
    def segmentOutOfBounds(self, creaturePanel, penPosition):
        """ Returns if a single segment constructed from this chromosome at the start position will run out of bounds.

            Args:
                creaturePanel (CreaturePanel): The creature panel which the creature must remain inside of.
                penPostion (PenPosition): The initial pen position for the segment.

            Returns:
                (boolean): True if the chromosmes segment runs out of the bounds of the panel.  False if it remains within bounds.
        """
        # if no creaturePanel or penPosition is provided then fail
        if ((creaturePanel == None) or (penPosition == None)):
            # Assume out of bounds on bad arguments
            return True
        
        # Get panel boundaries
        leftX = creaturePanel.interiorLeftX
        bottomY = creaturePanel.interiorBottomY
        rightX = creaturePanel.interiorRightX
        topY = creaturePanel.interiorTopY
        
        # Restore pen position and raise the pen up
        penPosition.restore()
    
        # Get the pen
        pen = penPosition.pen
        
        # Use appropriate testing method depending on shape
        if (self.shape == self._SHAPE__LINE_VALUE):
            pen.forward(self.length)
        else:
            # Radius is have the length (diameter) of circle or dot
            radius = self.length >> 1
            
            # Move to center of circle or dot 
            pen.forward(radius)

            # Trim panel boundaries inward by radius
            # This effectively reduces test to whether center of circle falls outside boundary
            leftX += radius
            bottomY += radius
            rightX -= radius
            topY -= radius

        # Get pen position
        penX = pen.xcor()
        penY = pen.ycor()
        
        # If pen is outside of the reduced panel boundary then
        if ((penX <= leftX) or (penX >= rightX) or (penY <= bottomY) or (penY >= topY)):
            # Return that the segment went out of bounds
            # No need to fix final circle position because it has failed
            return True

        # Finish moving across circle or dot
        if (self.shape != self._SHAPE__LINE_VALUE):
            pen.forward(radius)

        # Return that the segment remains in bounds
        return False
        
        

    # Draw a single segment onto the panel at turtle position using this chromosome    
    def drawSingleSegment(self, creaturePanel, penPosition):
        """ Draw a single segment constructed from this chromosome at the start position will run out of bounds.

            Note:
                This function assumes that out of bounds detection was already run.

            Args:
                creaturePanel (CreaturePanel): The creature panel which the creature must remain inside of.
                penPostion (PenPosition): The initial pen position for the segment.
        """
        # if no creaturePanel or penPosition is provided then do nothing
        if ((creaturePanel == None) or (penPosition == None)):
            # Return the pen position
            return None

        # Restore pen position and raise the pen up
        penPosition.restore()
    
        # Get the pen
        pen = penPosition.pen

        # Prepare the pen
        pen.pencolor(self.lineColor)
        pen.fillcolor(self.fillColor)
        pen.width(self.lineWidth)

        # Radius is have the length (diameter) of circle or dot
        radius = self.length >> 1

        # Use appropriate drawing method depending on shape

        # If drawing a line put the pen down
        if (self.shape == self._SHAPE__LINE_VALUE):
            pen.pendown()
        else:
            if (self.shape == self._SHAPE_DOT_VALUE):
                pen.forward(radius)
                pen.pendown()
                pen.dot(self.length, self.lineColor)
                pen.up()
                pen.forward(radius)
            elif (self.shape == self._SHAPE_CIRCLE_VALUE):
                pen.right(90)
                pen.pendown()
                pen.circle(radius)
                pen.left(90)
                pen.penup()
            elif (self.shape == self._SHAPE_FILLED_CIRCLE_VALUE):
                pen.right(90)
                pen.pendown()
                pen.begin_fill()
                pen.circle(radius)
                pen.end_fill()
                pen.left(90)
                pen.penup()
                
            # Restore pen position and raise the pen up
            # So that we can simulate moving forward like a line segment
            penPosition.restore()

        # Now move pen forward to final position if dot or circle, or draw line
        pen.forward(self.length)

        # Finally lift the pen back up to avoid inadvertant drawing.
        pen.penup()



class Genotype:
    """ Class defining a creatures genotype, which is a list of chromosomes.

        Note: Subclassed from printableAttributes for use when doing hardcoded debugging.

        Attributes: 
            chromosomes (Chromosome[]): A array of CHROMOSOME_COUNT initial chromosomes for the genotype.
                If not provided it will be randomly generated. 
    """
    
    CHROMOSOME_COUNT = 4      # Creatures have a fixed number of chromosomes.  The depth of segment drawing is limited by this.
    MUTATION_RATE_MAXIMUM = 2 # The maximum number of mutations that occur during reproduction

    # Constructor for the genotype
    def __init__(self, chromosomes = None):
        """ Constructor for a Genotype.  A genotype being a list of chromosomes.

            Args:
                chromosomes (Chromosome[]): The creatures genotype as an list of chromosomes.  If not provided it will be randomly generated.
        """

        # If the chromosomes were not provided, or had an improper count then
        if ((chromosomes == None) or (len(chromosomes) != self.CHROMOSOME_COUNT)):
            # Generate random chromosomes
            self.chromosomes = [Chromosome(chromosomeIndex) for chromosomeIndex in range(self.CHROMOSOME_COUNT)]
        # Otherwise use the provided chromosomes
        else:
            self.chromosomes = chromosomes

    def mutatedCopy(self):
        """ Generate a mutated copy of this genotype.

            Returns:
                A child decendant genotype with up to MUTATION_RATE_MAXIMUM point mutations.
        """
        # Copy chromosome values into an array
        mutatedChromosomeValues = [self.chromosomes[chromosomeIndex].chromosomeValue for chromosomeIndex in range(self.CHROMOSOME_COUNT)]

        # Determine the number of mutations to occur
        mutationNumber = random.randint(1, self.MUTATION_RATE_MAXIMUM)

        # Generate that number of mutations randomly throughout the genotypes chromosomes
        for mutationCount in range(mutationNumber):
            # Randomly select chromosome to mutate
            chromosomeIndex = random.randint(0, self.CHROMOSOME_COUNT - 1)

            # Modify random bit of the 32 bits to modify
            # Do this by randomly generating a number from 0 to 31
            # Then shift a 1 bit to that bit location
            # Finally to an exclusive or to flip that bit to the opposite value
            mutatedChromosomeValues[chromosomeIndex] ^= (1 << random.randint(0, 31))

        # Generate new copy of old chromosomes
        newChromosomes = [self.chromosomes[chromosomeIndex] for chromosomeIndex in range(self.CHROMOSOME_COUNT)]

        # Where the chromosome has mutated from the old chromosome replace with mutated copy
        for chromosomeIndex in range(self.CHROMOSOME_COUNT):
            if (newChromosomes[chromosomeIndex].chromosomeValue != mutatedChromosomeValues[chromosomeIndex]):
               newChromosomes[chromosomeIndex] = Chromosome(chromosomeIndex, mutatedChromosomeValues[chromosomeIndex])

        # Return a new genotype with the mutated chromosomes
        return Genotype(newChromosomes)
        
        
           
class Creature:
    """ Class defining a creature based on a genotype.
    """
    
    _MAX_CHROMOSOME_SEGMENTS = 32 # Maximum number of segments a chromosome can generate for the phenotype of the creature.
                                  # A chromosome that generates more than this number of segments will cause creature death.
                                  # This is provided to restrict the duration of creature construction to enhance performance.
    
    def __init__(self, genotype=None):
        """ Constructor for a creature.  A genotype being a list of chromosomes.

            Args:
                genotype (Genotype): The creatures genotype.  If not provided it will be randomly generated.
        """

        # If not genotype is provided then
        if (genotype == None):
            # Assign a randomly generated genotypes
            genotype = genotype=Genotype()

        # Use the genotype
        self.genotype = genotype
        
    def mutatedChild(self):
        """ Generate a mutated child from the current creature

            Returns:
                Creature: A slightly mutated child of this creature
        """
        return Creature(self.genotype.mutatedCopy())

    # Display creature in panel and return true if successful
    def display(self, creaturePanel):
        """ Draw the creature into its own panel.  Return True if successful and False on failure.

            Note: If a creature fails to draw then the calling function should eliminate it as uninteresting. 

            Args:
                creaturePanel (CreaturePanel): The creature panel which the creature must remain inside of.
                
            Returns:
                boolean: True if the creature was properly drawn.  False if the creature failed to draw.
        """
        
        
        # Allocate an array with and equal number of empty subarrays as there are chromosomes
        # The subarrays will be filled with pen positions for every segment drawn for a chromosome
        # Later the array will allow the drawing of the creature by order of chromosome (instead of tree path order)
        segmentPenPositions = [[] for chromosomeNumber in range(Genotype.CHROMOSOME_COUNT)]
        chromosomes = self.genotype.chromosomes
        startingPenPosition = creaturePanel.startingPenPosition()
        segmentPenPositions[0].extend(chromosomes[0].childSegmentPositions(startingPenPosition))

        # Get all initial pen positions for all segments for each chromosome
        for chromosomeNumber in range(Genotype.CHROMOSOME_COUNT):
            chromosomePenPositions = segmentPenPositions[chromosomeNumber]
            # If too many segments then creature must die from using up resources before fully formed
            if (len(chromosomePenPositions) > self._MAX_CHROMOSOME_SEGMENTS):
                return False

            # If no pen position were created for this chromosome then
            if (len(chromosomePenPositions) == 0):
                # If this is the first chromosome then terminate the creature
                if chromosomeNumber == 0:
                    return False
                # Otherwise break out of the loop because there are no more segments to draw
                else:
                    break

            # For each segments pen position being drawn for this chromosome
            for segmentPenPosition in chromosomePenPositions:
                # Get the chromosome
                chromosome = chromosomes[chromosomeNumber]

                # Pseudo-draw the segment at that position seeing if it runs out of bounds
                # Actual pen postion after this call will be at end of segment
                if chromosome.segmentOutOfBounds(creaturePanel, segmentPenPosition):
                    # Creature failed to draw
                    return False
                
                # Get the penPosition for the end of the current segment
                segmentEndPenPosition = PenPosition(segmentPenPosition.pen, segmentPenPosition.chiralityRight)

                # If this is not the last chromosome then
                # Generate the positions for the segments sprouting from the end of this segment
                # using the next chromosome.
                if (chromosomeNumber < Genotype.CHROMOSOME_COUNT - 1):
                    # Get the next chromosome
                    nextChromosome = chromosomes[chromosomeNumber + 1]
                    # Get the array of existing pen positions of the next chromosome that sprouted from other segments 
                    nextChromosomePenPositions = segmentPenPositions[chromosomeNumber + 1]
                    # Generate pen positions for the new chromosome off the end of this segment
                    # then extend that next chromosomes list of positions with all of them
                    nextChromosomePenPositions.extend(nextChromosome.childSegmentPositions(segmentEndPenPosition))
        

        # Draw all segments for each chromosome
        for chromosomeNumber in range(Genotype.CHROMOSOME_COUNT):
            for segmentPenPosition in segmentPenPositions[chromosomeNumber]:
                chromosome = chromosomes[chromosomeNumber]
                chromosome.drawSingleSegment(creaturePanel, segmentPenPosition)

        # Creature successfully drawn
        return True        

        
        
        
        

