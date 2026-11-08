from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2

    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        moves = self.board.get_all_possible_moves(self.color)
        best_score = float('-inf')
        best_moves = []
        for piece_moves in moves:
            for m in piece_moves:
                self.board.make_move(m,self.color)
                score = self.evaluate(self.color)
                self.board.undo()
                if score > best_score:
                    best_score = score
                    best_moves = [m]
                elif score == best_score:
                    best_moves.append(m)
        move = best_moves[randint(0, len(best_moves) - 1)]
        self.board.make_move(move,self.color)
        return move

    def evaluate(self,me):
        my_color = "B" if me == 1 else "W"
        score = 0.0
        for r in range(self.board.row):
            for c in range(self.board.col):
                ch = self.board.board[r][c]
                if ch.color == ".":
                    continue
                value = 1.5 if ch.is_king else 1.0
                score += value if ch.color == my_color else -value
        return score
