import pygame as p
from move import Move
from move import MoveLog
from board import Board  # Import Board class from board.py
from ai import ChessAI
from datetime import datetime 
import os


MENU = "menu"
GAME = "game"
HINTS = "hints"

difficulty = None  # easy/meduim/hard
mode = None           # two player or vs AI

game_state = MENU  # game starts in menu

highlighted_moves = []  # stores legal moves of currently selected piece

height = width = 512
square_size = height // 8
panel_width = 200
max_fps = 10

# side panel layout
panel_start_x = 512        # X coordinate where the side panel starts
panel_padding_x = 5        # horizontal padding inside the panel
panel_padding_y = 5        # vertical padding from the top of the panel
line_height = 20           # vertical spacing between moves


p.init()
clock = p.time.Clock()
screen = p.display.set_mode((height, width))
p.display.set_caption("Di-chess")

screen = p.display.set_mode((height + panel_width, width))

board = Board()      # create board object
board.loadImages()   # load all the chess piece images
board.setStartingPos()

moveLog = MoveLog()
turn = "w"
ai_player = None
game_over = False
game_result = ""

selected_square = None
running = True

position_counts = {}
halfmove_clock = 0 #icrements when no pawn move / capture ( for 50-move rule)


def makeNewGame():
    # Reset the board and move log
    # return (board, moveLog, turn, selected_square, highlighted_moves)
    board = Board()
    board.loadImages()
    board.setStartingPos()
    moveLog = MoveLog()
    turn = "w"
    selected_square = None
    highlighted_moves = []
    return board, moveLog, turn, selected_square, highlighted_moves


def drawMoveLog(surface, moveLog, panel_width, height):

    # Draw the panel background
    panel_rect = p.Rect(512, 0, panel_width, height)
    p.draw.rect(surface, (200, 200, 200), panel_rect)  # light grey panel

    # Set font
    font = p.font.SysFont("Arial", 18)

    # Loop through moves and render them
    for i, move_text in enumerate(moveLog.move_list, start=1):
        text_surface = font.render(
            f"{i}. {move_text}", True, (0, 0, 0))  # black text
        surface.blit(text_surface, (panel_start_x + panel_padding_x,
                     panel_padding_y + (i - 1) * line_height))  # margin + vertical spacing


def drawMenu(surface):
    surface.fill((230, 230, 230))
    title_font = p.font.SysFont("Arial", 36, True)
    button_font = p.font.SysFont("Arial", 24, True)
    title = title_font.render("Dichess - Main Menu", True, (30, 30, 30))
    surface.blit(title, (120, 40))

    # Buttons (x, y, w, h)
    buttons = {
        "two_player": p.Rect(150, 120, 260, 50),
        "easy":       p.Rect(150, 190, 260, 50),
        "medium":     p.Rect(150, 260, 260, 50),
        "hard":       p.Rect(150, 330, 260, 50),
        "hints":      p.Rect(150, 400, 260, 50),
    }

    # Draw buttons
    for key, rect in buttons.items():
        p.draw.rect(surface, (100, 180, 100), rect, border_radius=10)
        label = {
            "two_player": "Two Player (Local)",
            "easy": "Play vs AI (Easy)",
            "medium": "Play vs AI (Medium)",
            "hard": "Play vs AI (Hard)",
            "hints": "Hints / Tips",
        }[key]
        text = button_font.render(label, True, (255, 255, 255))
        surface.blit(text, (rect.x + 20, rect.y + 10))

    return buttons


def drawHints(surface):  # Renders a static list of tips
    surface.fill((245, 245, 245))
    title_font = p.font.SysFont("Arial", 32, True)
    text_font = p.font.SysFont("Arial", 20)

    title = title_font.render("Hints & Tips", True, (30, 30, 30))
    surface.blit(title, (160, 40))

    hints = [
        "1) Pawns move forward one square; capture diagonally.",
        "2) Knights move in an L-shape (2 then 1).",
        "3) Bishops move diagonally any distance.",
        "4) Rooks move straight (ranks/files) any distance.",
        "5) The Queen = rook + bishop movement.",
        "6) The King moves one square in any direction.",
        "7) Control the centre (e4, d4, e5, d5).",
        "8) Develop pieces before moving the same one twice.",
        "9) Castle early to protect your king.",
        "10) Don't leave pieces undefended (hanging).",
        "11) Press S to save the board!",
    ]

    y = 110
    for tip in hints:
        line = text_font.render(tip, True, (20, 20, 20))
        surface.blit(line, (40, y))
        y += 32
 # creates and draws a "back to Menu Button"
 # returns its rect for click detection
    back_rect = p.Rect(180, 430, 220, 48)
    p.draw.rect(surface, (180, 100, 100), back_rect, border_radius=10)
    back_text = p.font.SysFont("Arial", 22, True).render(
        "Back to Menu", True, (255, 255, 255))
    surface.blit(back_text, (back_rect.x + 40, back_rect.y + 10))
    return back_rect


def save_screen(screen): # saves screen as a PNG
    os.makedirs("savedPositions",exist_ok=True) # creates new file os.makedisr(name,order,boolcheck)
    filename= datetime.now().strftime("position_%Y-%m-%d_%H-%M-%S.png") # creates a unique filename
    path = os.path.join("savedPositions",filename) #builds a full path 
    p.image.save(screen,path) #saves image 
    print(os.getcwd())
    return path 


def getPositionKey(board, turn):
    #creates a simple position key for repetition detection
    #includes piece placement + side to move
    
    rows = []
    for r in range(8):
        row_str = []
        for c in range(8):
            piece = board.tiles[r][c]
            row_str.append(piece.symbol if piece is not None else "--")
        rows.append(",".join(row_str))
    return "|".join(rows) + f"|turn={turn}"


def updateRepetitionTable(board, turn):
    key = getPositionKey(board, turn)
    position_counts[key] = position_counts.get(key, 0) + 1
    return position_counts[key]


def updateHalfmoveClock(moved_piece, captured_piece):
    global halfmove_clock
    if moved_piece is None:
        return
    pawn_moved = (moved_piece.name == "P")
    capture_happened = (captured_piece is not None)

    if pawn_moved or capture_happened:
        halfmove_clock = 0
    else:
        halfmove_clock += 1


   
def isInsufficientMaterial(board):
        non_king_pieces = []

        for r in range(8):
            for c in range(8):
                peace = board.tiles[r][c]
                if peace is None:
                    continue
                if peace.name != "K":
                    non_king_pieces.append(peace.name)

        if len(non_king_pieces) == 0:
            return True

        if len(non_king_pieces) == 1 and non_king_pieces[0] in ("B", "N"):
            return True

        return False



def checkGameOver(board, turn):

    # checks if the current player to move (turn) is checkmated or stalemated.
    # returns whteher or not this is true (game over BOOLEAN) + result as a string

    in_check = board.isInCheck(turn)
    has_moves = board.hasAnyLegalMoves(turn)

    if in_check and not has_moves:
        # current player is checkmated, so the other player wins
        winner = "White" if turn == "b" else "Black"
        return True, f"Checkmate - {winner} wins!"

    if not in_check and not has_moves:
        return True, "Draw - stalemate"
    #Three fold repitition
    current_key = getPositionKey(board, turn)
    if position_counts.get(current_key, 0) >= 3:
        return True, "Draw - threefold repetition"
    
    # 50-move rule (100 half-moves)
    if halfmove_clock >= 100:
        return True, "Draw - 50-move rule"
    
    if isInsufficientMaterial(board):
        return True, "Draw - insufficient material"

    return False, ""


board, moveLog, turn, selected_square, highlighted_moves = makeNewGame()

while running:
    for event in p.event.get():
        if event.type == p.QUIT:
            running = False  # when window is closed , close the game

        if game_state == MENU:
            if event.type == p.MOUSEBUTTONDOWN:
                x, y = p.mouse.get_pos()
                buttons = drawMenu(screen)
                if buttons["two_player"].collidepoint(x, y):
                    mode = "two_player"
                    difficulty = None
                    board, moveLog, turn, selected_square, highlighted_moves = makeNewGame()
                    ai_player = None
                    game_state = GAME

                elif buttons["easy"].collidepoint(x, y):
                    mode = "vs_AI"
                    difficulty = "easy"
                    board, moveLog, turn, selected_square, highlighted_moves = makeNewGame()
                    ai_player = ChessAI("b", difficulty)   # AI plays as black
                    game_state = GAME

                elif buttons["medium"].collidepoint(x, y):
                    mode = "vs_AI"
                    difficulty = "medium"
                    board, moveLog, turn, selected_square, highlighted_moves = makeNewGame()
                    ai_player = ChessAI("b", difficulty)   # AI plays as black
                    game_state = GAME
                elif buttons["hard"].collidepoint(x, y):
                    mode = "vs_AI"
                    difficulty = "hard"
                    board, moveLog, turn, selected_square, highlighted_moves = makeNewGame()
                    ai_player = ChessAI("b", difficulty)   # AI plays as black
                    game_state = GAME
                elif buttons["hints"].collidepoint(x, y):
                    game_state = HINTS

        elif game_state == HINTS:
            if event.type == p.MOUSEBUTTONDOWN:
                x, y = p.mouse.get_pos()
                back_rect = drawHints(screen)
                if back_rect.collidepoint(x, y):
                    game_state = MENU

        elif game_state == GAME:
            if game_over:
                continue
            # Allow ESC to return to menu from a game
            if event.type == p.KEYDOWN and event.key == p.K_ESCAPE:
                game_state = MENU
                mode = None
                difficulty = None
                ai_player = None
                board, moveLog, turn, selected_square, highlighted_moves = makeNewGame()
                game_over = False
                game_result = ""
                continue

        
            if event.type == p.KEYDOWN and event.key == p.K_s:
                p.display.flip()  # ensures it is the latest frame is on the display , not an older frame 
                path = save_screen(screen)
                print("Saved:", path)    

            
            if event.type == p.MOUSEBUTTONDOWN:  # converting mouse coords to board coords
                location = p.mouse.get_pos()
                col = location[0] // square_size
                row = location[1] // square_size

                # checks if user selects same square on second click

                if col >= 8 or row >= 8:
                    continue

                clicked_piece = board.tiles[row][col]

            # deseclt piece
                if selected_square == (row, col):
                    selected_square = None
                    highlighted_moves = []

                elif selected_square is None:  # checks if player has selcted a piece yet
                    # checks if clicked tile actually has a piece
                    if clicked_piece is not None and clicked_piece.colour == turn:
                        selected_square = (row, col)
                        # Highlight legal moves for that piece
                        highlighted_moves = board.getLegalMoves(row, col)
                        highlighted_moves = [tuple(move)
                                             for move in highlighted_moves]
                        print("Legal moves for", clicked_piece.symbol,
                              ":", highlighted_moves)
                        print(
                            f"Selected {clicked_piece.symbol} at {(row, col)}")
                        print("Legal moves:", highlighted_moves)
                    else:
                        selected_square = None
                        highlighted_moves = []

                        # places the selected peice in the location clicked by the user.If another piece is there , that piece is deleted
                else:

                    if (row, col) in highlighted_moves:
                        moved_piece = board.tiles[selected_square[0]
                                                  ][selected_square[1]]
                        captured_piece = board.tiles[row][col]

                        move = Move(selected_square[0], selected_square[1],  # start square , end square

                                    (row, col),
                                    board.tiles,     # current board state
                                    captured_piece   # piece captured, if any are captured
                                    )

                        move.moved_piece = moved_piece
                        # execute move
                        piece = board.tiles[selected_square[0]
                                            ][selected_square[1]]
                        board.tiles[row][col] = piece
                        board.tiles[selected_square[0]
                                    ][selected_square[1]] = None

                        moveLog.logMove(move)
                        turn = "b" if turn == "w" else "w"

                        # deseclect regardless if the move was valid or not
                        selected_square = None
                        highlighted_moves = []
                        # check if game over after human move
                        game_over, game_result = checkGameOver(board, turn)
                        if game_over:
                            selected_square = None
                            highlighted_moves = []
                            continue

                    # AI MOVEMMENT LOGIC

                        if mode == "vs_AI" and ai_player is not None and turn == ai_player.colour:
                            ai_move = ai_player.getBestMove(board)
                            if ai_move is None:
                                game_over, game_result = checkGameOver(board, turn)
                            else:
                                (start_row, start_col), (end_row, end_col) = ai_move

                                ai_moved_piece = board.tiles[start_row][start_col]
                                ai_captured_piece = board.tiles[end_row][end_col]

                                ai_move_obj = Move(start_row, start_col,
                                                   (end_row, end_col),
                                                   board.tiles,
                                                   ai_captured_piece)
                                ai_move_obj.moved_piece = ai_moved_piece

                                # execute AI move
                                board.tiles[end_row][end_col] = ai_moved_piece
                                board.tiles[start_row][start_col] = None

                                moveLog.logMove(ai_move_obj)

                            # switch back to human turn
                            turn = "w"
                            # check if game is over after the AI's turn
                            game_over, game_result = checkGameOver(board, turn)

    if game_state == MENU:
        drawMenu(screen)
    elif game_state == HINTS:
        drawHints(screen)
    elif game_state == GAME:
        board.draw(screen)
        board.highlightSelected(screen, selected_square)
        board.drawHighlights(screen, highlighted_moves)
        drawMoveLog(screen, moveLog, panel_width, height)

        if board.isInCheck(turn) and not game_over:
            check_font = p.font.SysFont("Arial", 24, True)
            check_text = check_font.render("CHECK!", True, (200, 0, 0))
            check_rect = check_text.get_rect(center=(height // 2, height // 2))
            screen.blit(check_text, check_rect)

        if game_over:
            font = p.font.SysFont("Arial", 32, True)
            text_surface = font.render(game_result, True, (200, 0, 0))
            text_rect = text_surface.get_rect(center=(height // 2, height // 2))
            screen.blit(text_surface, text_rect)

    clock.tick(max_fps)

    p.display.flip()  # update the display

p.quit()
moveLog.save_to_file()
