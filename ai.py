# ai.py
# ==========================================
# Chess AI module using Minimax and Alpha-Beta pruning
# The AI difficulty (Easy / Medium / Hard) is controlled
# by adjusting the search depth and adding a blunder probability.
# ==========================================

import random


# Import Move class to execute AI-selected moves
from move import Move


class ChessAI:
    def __init__(self, colour, difficulty="medium"):
     # Initialises the AI with a specific colour (usually black) and difficulty setting which controls search depth and blunder probability.

        self.colour = colour
        self.difficulty = difficulty

        # Adjust AI intelligence parameters based on difficulty
        if difficulty == "easy":
            self.depth = 1
            self.blunder_rate = 0.3  # 30% chance to play a random move
        elif difficulty == "medium":
            self.depth = 2
            self.blunder_rate = 0.1
        else:  # hard
            self.depth = 3
            self.blunder_rate = 0.0

        # Piece evaluation scores (used in heuristic evaluation)
        self.piece_values = {
            "P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 20000
        }

    def evaluateBoard(self, board):  # Evaluation Function

        # Assigns a numerical score to the board state
        # Positive = Advantage for white
        # Negative = Advantage for black

        score = 0
        for row in board.tiles:
            for piece in row:
                if piece is not None:
                    value = self.piece_values.get(piece.name, 0)
                    score += value if piece.colour == "w" else -value
        return score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        # Minimax Algorithm with Alpha-Beta Pruning
        # Recursively evaluates future board states by exploring possible legal moves and using alpha-beta pruning to eliminate inefficient branches

        if depth == 0:
            return self.evaluateBoard(board), None

        legal_moves = []
        for r in range(8):
            for c in range(8):
                piece = board.tiles[r][c]
                if piece is not None and ((piece.colour == "w" and maximizing_player) or (piece.colour == "b" and not maximizing_player)):
                    moves = board.getLegalMoves(r, c)

                    for move in moves:
                        legal_moves.append(((r, c), move))

        if not legal_moves:
            return self.evaluateBoard(board), None

        best_move = None

        if maximizing_player:
            max_eval = float('-inf')
            for start, end in legal_moves:
                new_board = board.copy()
                piece = new_board.tiles[start[0]][start[1]]
                captured = new_board.tiles[end[0]][end[1]]
                new_board.tiles[end[0]][end[1]] = piece
                new_board.tiles[start[0]][start[1]] = None

                eval, _ = self.minimax(
                    new_board, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (start, end)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move

        else:
            min_eval = float('inf')
            for start, end in legal_moves:
                new_board = board.copy()
                piece = new_board.tiles[start[0]][start[1]]
                captured = new_board.tiles[end[0]][end[1]]
                new_board.tiles[end[0]][end[1]] = piece
                new_board.tiles[start[0]][start[1]] = None

                eval, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (start, end)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def getBestMove(self, board):     # Main AI move selection

        # Determines the AI’s next move using minimax search,with added blunder chance based on difficulty.
        # Generate all legal moves for the AI

        all_moves = []
        for r in range(8):
            for c in range(8):
                piece = board.tiles[r][c]
                if piece is not None and piece.colour == self.colour:
                    legal_moves = board.getLegalMoves(r, c)
                    for move in legal_moves:
                        all_moves.append(((r, c), move))
        if not all_moves:
            return None

        # Blunder logic (randomness)
        if random.random() < self.blunder_rate:
            return random.choice(all_moves)

        # Otherwise use minimax to calculate best move
        # _ acts as a placeholder vairable , we only need the move , and the self.minmax(...) returns two things
        _, best_move = self.minimax(board, self.depth, float(
            '-inf'), float('inf'), maximizing_player=(self.colour == "w"))
        return best_move
