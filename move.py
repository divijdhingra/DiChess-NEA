# contains the move contrsuctor


class Move:

    # dictionaries which map keys to value
    # key : value

    ranks_to_rows = {"1": 7, "2": 6, "3": 5,"4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    # reverses the dictionary
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_row, start_col, end_sq, board,  captured_piece = None):

        self.startRow = start_row
        self.startCol = start_col
        self.endRow = end_sq[0]
        self.endCol = end_sq[1]

        self.moved_piece = None 
        self.captured_piece = captured_piece
        

    def getRankFile(self, row, col):  # converts (row,col) to standard chess notation
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

class MoveLog :

    def __init__(self):
        self.move_list = []

    def logMove(self, move):
        notation = move.getChessNotation()
        log_entry = move.moved_piece.symbol + " " + notation
        if move.captured_piece is not None: 
            log_entry += " (captured " + move.captured_piece.symbol + ")"

        self.move_list.append(log_entry)
        i = 1
        for move in self.move_list:
                print("Move made:"+ str(i) + "." + log_entry)
                i += 1
        
    def showMoves(self):
        print("Move History : ")
        count = 1  # starts move numbering from 1
        for move in self.move_list:
            print(str(count) + ". " + str(move))
            count += 1

    def save_to_file(self):

        with open("move_log.txt", "w") as file:
            for i, move in enumerate(self.move_list, start=1):
                file.write(f"{i}. {move}\n")

            
    def getMoveList(self):
        return self.move_list



