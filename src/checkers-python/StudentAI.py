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
        self.depth = 4

    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        moves = self.board.get_all_possible_moves(self.color)
        best_score = float('-inf')
        best_moves = []
        alpha = float('-inf')
        beta = float('inf')
        for piece_moves in moves:
            for m in piece_moves:
                self.board.make_move(m,self.color)
                score = self.minmax(self.opponent[self.color], alpha, beta, self.depth - 1)
                self.board.undo()
                if score > best_score:
                    best_score = score
                    best_moves = [m]
                elif score == best_score:
                    best_moves.append(m)
        move = best_moves[randint(0, len(best_moves) - 1)]
        self.board.make_move(move,self.color)
        return move

    def minmax(self, player, alpha, beta, depth):
        if depth == 0:
            return self.evaluate(self.color)
        moves = self.board.get_all_possible_moves(player)
        if player == self.color:
            max_eval = float('-inf')
            for piece_moves in moves:
                for m in piece_moves:
                    self.board.make_move(m, player)
                    eval = self.minmax(self.opponent[player], alpha, beta, depth - 1)
                    self.board.undo()
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        return max_eval
            return max_eval
        else:
            min_eval = float('inf')
            for piece_moves in moves:
                for m in piece_moves:
                    self.board.make_move(m, player)
                    eval = self.minmax(self.opponent[player], alpha, beta, depth - 1)
                    self.board.undo()
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        return min_eval
            return min_eval

    def evaluate(self,me):
        my_color = "b" if me == 1 else "w"
        score = 0.0
        for r in range(self.board.row):
            for c in range(self.board.col):
                ch = self.board.board[r][c]
                if ch.color == ".":
                    continue
                value = 2.0 if ch.is_king else 1.0
                score += value if ch.color == my_color else -value
        return score
