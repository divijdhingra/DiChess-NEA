
# class system for generating all legal moves for each piece
class Piece:
    def __init__(self, colour, name):
        self.colour = colour
        self.name = name
        self.symbol = colour + name 

    # this is a base mothod for getthing legel moves , which gets ovveridden in the subclasses
    def getLegalMoves(self, board, row, col):
        return []


class SlidingPiece(Piece):
    def __init__(self, colour, name, directions):
        super().__init__(colour, name)
        self.directions = directions  # list of (row_step, col_step) directions

    def get_legal_moves(self, board, row, col):
        legal_moves = []
        for dx, dy in self.directions:
            r = row + dx
            c = col + dy
            while 0 <= r < 8 and 0 <= c < 8:
                target = board.tiles[r][c]
                if target is None:
                    legal_moves.append((r, c))
                else:
                    if target.colour != self.colour:
                        legal_moves.append((r, c))  # capture
                    break
                r += dx
                c += dy
        return legal_moves


class Rook(SlidingPiece):  # creates new class that inherits from slidingPiece
    def __init__(self, colour):
        super().__init__(colour, "R", [(1, 0), (-1, 0), (0, 1), (0, -1)])


class Bishop(SlidingPiece):
    def __init__(self, colour):
        super().__init__(colour, "B", [(1, 1), (1, -1), (-1, 1), (-1, -1)])


class Queen(SlidingPiece):
    def __init__(self, colour):
        super().__init__(colour, "Q", [
            (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)])


class Knight(Piece):
    def __init__(self, colour):
        super().__init__(colour, "N")

    def get_legal_moves(self, board, row, col):
        moves = []
        offsets = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                   (-2, -1), (-1, -2), (1, -2), (2, -1)]
        for dx, dy in offsets:
            r = row + dx
            c = col + dy
            if 0 <= r < 8 and 0 <= c < 8:
                target = board.tiles[r][c]
                if target is None or target.colour != self.colour:
                    moves.append((r, c))
        return moves


class King(Piece):
    def __init__(self, colour):
        super().__init__(colour, "K")

    def get_legal_moves(self, board, row, col):
        moves = []
        offsets = [(1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in offsets:
            r = row + dx
            c = col + dy
            if 0 <= r < 8 and 0 <= c < 8:
                target = board.tiles[r][c]
                if target is None or target.colour != self.colour:
                    moves.append((r, c))
        return moves


class Pawn(Piece):
    def __init__(self, colour):
        super().__init__(colour, "P")

    def get_legal_moves(self, board, row, col):
        moves = []
        if self.colour == "w":
            direction = -1
            start_row = 6
        else:
            direction = 1
            start_row = 1

        # Forward move (with bounds check)
        if 0 <= row + direction < 8 and board.tiles[row + direction][col] is None:
            moves.append((row + direction, col))
            # Double move from start position
            if row == start_row and 0 <= row + 2*direction < 8 and board.tiles[row + 2*direction][col] is None:
                moves.append((row + 2*direction, col))

        # Captures
        for dy in [-1, 1]:
            r = row + direction
            c = col + dy
            if 0 <= r < 8 and 0 <= c < 8:
                target = board.tiles[r][c]
                if target is not None and target.colour != self.colour:
                    moves.append((r, c))

        return moves





