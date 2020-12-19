# -*- coding: utf-8 -*-

from random import getrandbits
import wx

class Game(wx.Frame):
    """ Frame handling the grid and game parameters. """
    def __init__(self, amount: int, width: int, origin: int, left: int):
        # Non-resizable frame with predefined title and size
        wx.Frame.__init__(self, None, title = 'Elskeda', style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetClientSize((width + origin + left,) * 2)

        # Panel meant to contain the grid
        panel = wx.Panel(self, size = (width + origin + left,) * 2, pos = (0, 0))

        # Deduced width of any given cell
        self.cellWidth = int(width / amount)

        # TODO
        print(f'Width of a cell is {width}/{amount} = {self.cellWidth}')
        print(f'Origin of the grid is at ({origin, origin})')

        # Coordinates of the top left corner of the grid
        self.origin = origin

        # Amount of pixels left for spacing on the right side
        self.left = left

        # Amount of cells on a line
        self.amount = amount

        # Current cell type to draw
        # 2 types : normal (True) and crossed (False)
        self.normalCell = True

        # Cells of the grid
        self.cells = list()

        # Hints (left, top) for completing the grid
        self.hints = {key: [list()] * self.amount for key in ('left', 'top')}

        # Amount of lives left
        self.lives = 3

        # Setting up the panel
        self.SetBackgroundColour('#414345')

        # Event handlers
        panel.Bind(wx.EVT_LEFT_UP, self.onClick)
        self.Bind(wx.EVT_PAINT, self.onPaint)

        # Display frame
        self.Show()

    def switchCellType(self):
        """ Switch type of cell to reveal. """
        self.normalCell = not self.normalCell

    def onPaint(self, event: wx.Event):
        """ Display all cells. """
        # Return if cells or hints haven't been generated
        if not self.cells or not self.hints.values():
            return

        def drawHints(self, index: int):
            """ Draw hints of a specific line either on the left or on top. """
            # Device context for drawing
            dc = wx.PaintDC(self)
            dc.SetTextForeground('#efefef')

            # Get text for hints
            character = lambda key: ' ' if key == 'left' else '\n'
            hText, vText = (character(key).join(str(hint) for hint in self.hints[key][index]) for key in self.hints)

            # Calculate font sizes (horizontal and vertical)
            # and set limits based on origin and cell width
            hSize, vSize = (int(self.origin / (len(text) + 1)) * 1.3 for text in (hText, vText))
            hSize, vSize = (self.origin / 6 if size < self.origin / 6 else self.origin / 4.3 if size > self.origin / 4.3 else size for size in (hSize, vSize))
            hSize, vSize = (self.cellWidth if size >= self.cellWidth / 2 else size for size in (hSize, vSize))

            # Set font for drawing hints
            hFont, vFont = (wx.Font(size, wx.ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) for size in (hSize, vSize))
            dc.SetFont(hFont)
            dc.SetFont(vFont)

            # Draw texts
            hX, hY = int((self.origin - hFont.GetPixelSize()[0] * len(hText)) / 2), self.origin + int(self.cellWidth / 2) + index * self.cellWidth
            vX, vY = self.origin + int(self.cellWidth / 2) + index * self.cellWidth, int((self.origin - vFont.GetPixelSize()[0] * len(vText)) / 2)
            dc.DrawTextList((hText, vText), ((hX, hY), (vX, vY)))

        def drawLives(self):
            """ Draw remaining lives in a heart. """
            # Device context for drawing
            dc = wx.PaintDC(self)
            dc.SetTextForeground('#f4fffd')

            # Set up device context for life info
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.Brush('#eb003f'))

            # Draw heart with life information
            xLeft, yLeft = (0.1 * self.origin,) * 2

            x, y = xLeft, yLeft
            width, height = int(self.origin / 2) - xLeft, int(self.origin / 2)
            start, end = 0, 180
            dc.DrawEllipticArc(x, y, width, height, start, end)

            x, y = int(self.origin / 2), yLeft
            start, end = 0, 180
            dc.DrawEllipticArc(x, y, width, height, start, end)

            x, y = xLeft, - 2 * yLeft
            width, height = self.origin -  2 * xLeft, self.origin
            start, end = 180, 270
            dc.DrawEllipticArc(x, y, width, height, start, end)

            x, y = int((self.origin - width) / 2), - 2 * yLeft
            start, end = - 90, 0
            dc.DrawEllipticArc(x, y, width, height, start, end)

            # Add amount of lives inside the heart
            size = 0.4 * self.origin
            font = wx.Font(size, wx.ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            dc.SetFont(font)

            x, y = xLeft + int(self.origin / 2) - int(size / 2), 0.3 * self.origin + int(yLeft / 2)
            dc.DrawText(str(self.lives), (x, y))

        def drawEndScreen(self):
            """ Draw screen asking for playing again. """
            def onSpace(event: wx.Event):
                """ Restart the current or generate a new game. """
                # Check if the key is the spacebar
                if not event.GetKeyCode() == wx.WXK_SPACE:
                    return

                # Reset cells to restart
                if self.lives == 0:
                    self.cells = [[[value, False] for value, _ in line] for line in self.cells]
                # Generate new cells
                else:
                    self.generate()

                # Reset lives
                self.lives = 3

                # Unbind spacebar event
                self.Unbind(wx.EVT_CHAR_HOOK)

                # Refresh panel
                self.Refresh()

            # Device context for drawing
            dc = wx.PaintDC(self)
            dc.SetBrush(wx.Brush('#efefef'))

            # Draw rectangle covering whole interface
            width, height = (self.origin + self.left + self.amount * self.cellWidth,) * 2
            dc.DrawRectangle(0, 0, width, height)

            # Fill background with gradient
            dc.GradientFillLinear((0, 0, width, height), '#051937', '#ec6f66', nDirection = wx.BOTTOM)

            # Display information message
            font = wx.Font(40, wx.ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            dc.SetFont(font)
            dc.SetTextForeground('#c0bfdc')

            message = 'Game Over\nPress [Space] to try again!'
            if self.lives > 0:
                message = 'Congratulations!\nYou did it!\nPress [Space] for next one!'
            dc.DrawLabel(message, (0, 0, width, height), alignment = wx.ALIGN_CENTER)

            # Handle eventual spacebar event
            self.Bind(wx.EVT_CHAR_HOOK, onSpace)

        def drawCell(dc, i: int, j: int):
            """ Draw either a normal or crossed cell. """
            # Set pen and brush for cell background
            dc.SetPen(wx.Pen(wx.BLACK, 0))
            dc.SetBrush(wx.Brush('#efefef'))
            
            # Draw cell background
            x, y = (self.origin + k * self.cellWidth for k in (j, i))
            dc.DrawRectangle(x, y, self.cellWidth, self.cellWidth)

            # Check if the cell is revealed
            value, revealed = self.cells[i][j]
            if not revealed:
                return

            # Draw cell depending on its value
            if not bool(value):
                # Set pen and brush for crossed lines
                dc.SetPen(wx.Pen('#4a4a57', 5))
                dc.SetBrush(wx.Brush(wx.BLACK))

                # Draw crossed lines
                xStart, yStart = (0.2 * self.cellWidth + self.origin + k * self.cellWidth for k in (j, i))
                xEnd, yEnd = (0.8 * self.cellWidth + self.origin + k * self.cellWidth for k in (j, i))
                dc.DrawLine(xStart, yStart, xEnd, yEnd)

                xStart, yStart = (c * self.cellWidth + self.origin + k * self.cellWidth for c, k in ((0.8, j), (0.2, i)))
                xEnd, yEnd = (c * self.cellWidth + self.origin + k * self.cellWidth for c, k in ((0.2, j), (0.8, i)))
                dc.DrawLine(xStart, yStart, xEnd, yEnd)
            else:
                # Deduce and set brush to use
                brush = wx.Brush('#efefef') if not self.cells[i][j][1] or not bool(self.cells[i][j][0]) else wx.Brush('#ec6f66')
                dc.SetBrush(brush)

                # Draw cell
                x, y = self.origin + j * self.cellWidth, self.origin + i * self.cellWidth
                dc.DrawRectangle(x, y, self.cellWidth, self.cellWidth)

        # Draw end screen if the game is over
        if self.lives == 0 or self.isComplete():
            drawEndScreen(self)
            return

        # Device context for drawing cells
        dc = wx.PaintDC(self)

        # Clear the panel
        dc.Clear()

        for i in range(self.amount):
            for j in range(self.amount):
                # Draw cell
                drawCell(dc, i, j)

            # Draw hints on vertical and horizontal
            # line of index i (from top-left corner)
            drawHints(self, i)

        # Draw life information
        drawLives(self)

        # Refresh panel
        self.Refresh()

    def generate(self):
        """ Generate a random grid and figure out hints. """
        def analyze(line: list) -> list:
            """ Deduce the series of consecutive 1 of a line. """
            series, previous = list(), False
            for i, (value, _) in enumerate(line):
                if value:
                    if not previous: series.append(1)
                    else: series[-1] += 1
                previous = value
            return series
        
        # Generate cells with one of two possible values
        self.cells = list()
        for i in range(self.amount):
            # Line of cells
            line = list()
            for j in range(self.amount):
                # Add cell to list
                value = [getrandbits(1), False]
                line.append(value)
            self.cells.append(line)

            # Deduce horizontal hints on this line
            self.hints['left'][i] = analyze(self.cells[i])
        
        # Deduce vertical hints
        self.hints['top'] = [analyze([self.cells[j][i] for j in range(self.amount)]) for i in range(self.amount)]

        # TODO
        from pprint import pprint
        pprint([[value for value, _ in line] for line in self.cells])
        pprint(self.hints)

    def onClick(self, event: wx.MouseEvent):
        """ Deduce the cell if it's clicked, and reveal it or not. """
        # Check whether there are remaining lives
        if self.lives == 0:
            return

        # Get the position of the click on the frame
        dc = wx.PaintDC(self)
        x, y = event.GetLogicalPosition(dc).Get()

        # Deduce the cell that has been clicked
        for i, line in enumerate(self.cells):
            for j, _ in enumerate(line):
                if self.origin + j * self.cellWidth < x < self.origin + (j+1) * self.cellWidth and self.origin + i * self.cellWidth < y < self.origin + (i+1) * self.cellWidth:
                    # TODO
                    print(f'Cell [{j},{i}] located at ({self.origin + j * self.cellWidth}, {self.origin + i * self.cellWidth}) with value "{self.cells[i][j][0]}"')

                    # Reveal the cell or deduct a life
                    self._reveal(i, j)

    def _reveal(self, i: int, j: int):
        """ Reveal the cell of given indexes. """
        # Check that the cell hasn't been revealed yet
        value, revealed = self.cells[i][j]
        if revealed:
            return

        # Change the revealing value
        self.cells[i][j][1] = True

        # Check that the cell has the value 1
        if bool(value):
            # Check whether the grid is complete
            if self.isComplete():
                # TODO: Game win animation
                print('You WON! Congrats!')

            # Refresh panel
            self.Refresh()
        else:
            # Life loss animation
            # TODO

            # Lose a life
            if self.lives - 1 > 0:
                self.lives -= 1
            else:
                self.lives = 0

                # TODO: Game loss animation
                print('GAME OVER! You lost!')

            # Refresh panel
            self.Refresh()

    def isComplete(self):
        """ Check whether or not the grid is complete. """
        for i in range(self.amount):
            # A cell hasn't been revealed, it's not complete
            revealed = (reveal for value, reveal in self.cells[i] if bool(value))
            if False in revealed:
                return False
        return True
