import pygame as p  # Import Pygame
from pieces import Rook, Bishop, Queen, Knight, King, Pawn

height = width = 512
square_size = height // 8


class Board:
    def __init__(self):
        # Initialise an 8x8 empty chessboard
        # Create a 2D list (8x8)
        self.tiles = [[None for _ in range(8)] for _ in range(8)]  # Initialises an empty list
        self.colours = [(240, 217, 181), (181, 136, 99)]  # light, dark
        self.piece_images = {} #dictionary to store loaded images 

        for row in range(8):    # outer loop for rows
            row_list = []          # create a new row
            for col in range(8):      # inner loop for columns
                row_list.append(None)   # add an empty square to the row
            self.tiles.append(row_list)  # adds new row to the board

    def loadImages(self):  # load and scale all of the images
        pieces = ["wP", "wR", "wN", "wB", "wK",
                  "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
        for piece in pieces:
            self.piece_images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (square_size, square_size))

    def setStartingPos(self):
        # black pieces
        self.tiles[0] = [Rook("b"), Knight("b"), Bishop("b"), Queen("b"),King("b"), Bishop("b"), Knight("b"), Rook("b")]
        self.tiles[1] = [Pawn("b") for _ in range(8)]

        # Empty rows
        for row in range(2, 6):
            self.tiles[row] = [None]*8

        # white pieces
        self.tiles[7] = [Rook("w"), Knight("w"), Bishop("w"), Queen("w"),
            King("w"), Bishop("w"), Knight("w"), Rook("w")]
        self.tiles[6] = [Pawn("w") for _ in range(8)]


    def getLegalMoves(self, row, col):  #Returns all valid moves for the selected piece at (row, col)
        
        piece = self.tiles[row][col]
        if piece is None:
            return []  # no piece selected

        colour = piece.colour
        # call the piece’s own move generation logic
        legal_moves=  []
        possible_moves = piece.get_legal_moves(self, row, col)
        for (new_row, new_col) in possible_moves:
            #Simulate the move on a copied board
            temp_board = self.copy()
            moving_piece = temp_board.tiles[row][col]
            temp_board.tiles[new_row][new_col] = moving_piece
            temp_board.tiles[row][col] = None

            #If after this move, my king is not in check, keep the move
            if not temp_board.isInCheck(colour):
                legal_moves.append((new_row, new_col)) 
        return legal_moves

    def findKing(self, colour):
        #Finds the position of the king of the given colour
        #Returns (row, col) or None if not found
        for r in range(8):
            for c in range(8):
                piece = self.tiles[r][c]
                if piece is not None and piece.colour == colour and piece.name == "K":
                    return (r, c)
        return None

    def isSquareAttacked(self, row, col, by_colour):
        # returns True if the square (row, col) is attacked by any piece of 'by_colour'. 
        from pieces import Pawn  # to special-case pawn attacks

        for r in range(8):
            for c in range(8):
                piece = self.tiles[r][c]
                if piece is None or piece.colour != by_colour:
                    continue

                # Special case for pawns as they don't attack forward squares
                if isinstance(piece, Pawn):
                    direction = -1 if by_colour == "w" else 1
                    for dc in [-1, 1]:
                        pr = r + direction
                        pc = c + dc
                        if 0 <= pr < 8 and 0 <= pc < 8:
                            if pr == row and pc == col:
                                return True
                else:
                    # Use normal move generation for other pieces
                    moves = piece.get_legal_moves(self, r, c)
                    if (row, col) in moves:
                        return True

        return False

    def isInCheck(self, colour):
         #Returns True if the king of 'colour' is currently in check
        king_pos = self.findKing(colour)
        if king_pos is None:
            return False  # should not happen in a normal game
        enemy_colour = "b" if colour == "w" else "w"
        return self.isSquareAttacked(king_pos[0], king_pos[1], enemy_colour)

    def hasAnyLegalMoves(self, colour):
           
            # returns True if the player with 'colour' has at least one legal move
            # used to detect checkmate and stalemate
           
            for r in range(8):
                for c in range(8):
                    piece = self.tiles[r][c]
                    if piece is not None and piece.colour == colour:
                        moves = self.getLegalMoves(r, c)
                        if moves:
                            return True
            return False









    def copy(self):
       
        #Creates a copy of the board state for AI simulations
        #Only the tiles (piece layout) are copied and the images are shared
        
        new_board = Board()
        # copy the tile layout (8x8 grid)
        new_board.tiles = [row[:] for row in self.tiles]
        # reuse the same images dictionary (no need to copy surfaces)
        new_board.piece_images = self.piece_images
        return new_board


    def draw(self, surface):
        
        # Calculates the size of each tile by dividing the surface width by 8 (number of columns)
        # loops over all rows and columns of the board

        for row in range(8):
            for col in range(8):

                # Alternate colors between light and dark tiles using (row + col) mod 2
                colour = self.colours[(row + col) % 2]

                # Draws a rectangle (tile) at the correct position on the surface (the pygame window)
                # Size is tile_size by tile_size pixels.
                # a tuple defining the position and size of the rectangle

                p.draw.rect(surface, colour, (col * square_size,
                            row * square_size, square_size, square_size))
                piece = self.tiles[row][col]

                if piece is None:
                    continue
                # blit() copies the pixels from one image(surface) to another
                surface.blit(
                    self.piece_images[piece.symbol], (col * square_size, row * square_size))
                
    def drawHighlights(self, surface, highlighted_moves): #Highlights all valid moves for the selected piece.
        highlight_colour = (186, 202, 68)  # light green
        for (r, c) in highlighted_moves:
            rect = p.Rect(c * square_size, r * square_size, square_size, square_size)
            p.draw.rect(surface, highlight_colour, rect, 4)  # outline only

    def highlightSelected(self, surface, selected_square):
        if selected_square is not None:
            r, c = selected_square
            rect = p.Rect(c * square_size, r * square_size, square_size, square_size)
            p.draw.rect(surface, (0, 255, 0), rect, 4) #green border

        
                
    

