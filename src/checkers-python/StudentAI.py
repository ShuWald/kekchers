from __future__ import annotations

from random import randint
from typing import Optional

from BoardClasses import Board, Move


class StudentAI:
    # The following part should be completed by students.
    # Students can modify anything except the class name and existing functions and variables.
    def __init__(self, col: int, row: int, p: int) -> None:
        self.col: int = col
        self.row: int = row
        self.p: int = p
        self.game_state: GameState = GameState(col, row, p)
        self.board: Board = self.game_state.get_board()
        self.color: int = 2
        self.opponent: dict[int, int] = {1: 2, 2: 1}
        self.depth: int = 4
        self.evaluator: Evaluator = Evaluator(self.game_state, self.color)
        self.position_cache: PositionCache = PositionCache()
        self.search_engine: SearchEngine = SearchEngine(
            self.game_state,
            self.evaluator,
            self.position_cache,
            self.color,
            self.opponent,
        )
        self.iterative_deepening: IterativeDeepening = IterativeDeepening(
            self.search_engine,
            self.depth,
        )

    def get_move(self, move: Move) -> Move:
        if len(move) != 0:
            self.game_state.make_move(move, self.opponent[self.color])
        else:
            self.color = 1
            self.evaluator.color = self.color
            self.search_engine.color = self.color
        self.search_engine.color = self.color
        self.iterative_deepening.max_depth = self.depth
        selected_move, _ = self.iterative_deepening.search(self.depth)
        if selected_move is None:
            raise RuntimeError("No legal move is available")
        self.game_state.make_move(selected_move, self.color)
        return selected_move


###
###     Search-related classes
###

class SearchEngine:
    def __init__(
        self,
        game_state: GameState,
        evaluator: Evaluator,
        position_cache: PositionCache,
        color: int,
        opponent: dict[int, int],
    ) -> None:
        self.game_state: GameState = game_state
        self.evaluator: Evaluator = evaluator
        self.position_cache: PositionCache = position_cache
        self.color: int = color
        self.opponent: dict[int, int] = opponent
        self.node_count: int = 0

    def alpha_beta(
        self,
        player: int,
        depth: int,
        alpha: float,
        beta: float,
    ) -> float:
        # alpha beta 
        self.node_count += 1
        if depth <= 0:
            return self.evaluator.deep_evaluate()

        if player == self.color:
            return self.maximize(player, depth, alpha, beta)
        return self.minimize(player, depth, alpha, beta)

    def maximize(
        self,
        player: int,
        depth: int,
        alpha: float,
        beta: float,
    ) -> float:
        # Searches for the highest score from the AI's perspective.
        moves = self.order_moves(self.game_state.get_possible_moves(player))
        if not moves:
            return self.evaluator.deep_evaluate()
        max_eval = float("-inf")
        for move in moves:
            self.game_state.make_move(move, player)
            score = self.minmax(self.opponent[player], alpha, beta, depth - 1)
            self.game_state.undo_move()
            max_eval = max(max_eval, score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return max_eval

    def minimize(
        self,
        player: int,
        depth: int,
        alpha: float,
        beta: float,
    ) -> float:
        # Searches for the lowest score from the AI's perspective.
        moves = self.order_moves(self.game_state.get_possible_moves(player))
        if not moves:
            return self.evaluator.deep_evaluate()
        min_eval = float("inf")
        for move in moves:
            self.game_state.make_move(move, player)
            score = self.minmax(self.opponent[player], alpha, beta, depth - 1)
            self.game_state.undo_move()
            min_eval = min(min_eval, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return min_eval

    def search_root(self, depth: int) -> tuple[Optional[Move], float]:
        # Retained core recursive minimax logic from StudentAI.get_move()
        self.node_count = 0
        moves = self.game_state.get_possible_moves(self.color)
        best_score = float("-inf")
        best_moves: list[Move] = []
        alpha = float("-inf")
        beta = float("inf")
        for piece_moves in moves:
            for move in piece_moves:
                self.game_state.make_move(move, self.color)
                score = self.minmax(
                    self.opponent[self.color], alpha, beta, depth - 1
                )
                self.game_state.undo_move()
                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

        if not best_moves:
            return None, best_score
        return best_moves[randint(0, len(best_moves) - 1)], best_score

    # Improve pruning possiblity by ordering moves based on cheap evaluation/heuristics
    def order_moves(self, moves: list[list[Move]]) -> list[Move]:
        return self.flatten_moves(moves)

    # Convert moves to a list for easier sorting (order_moves)
    def flatten_moves(self, moves: list[list[Move]]) -> list[Move]:
        return [move for piece_moves in moves for move in piece_moves]

    def minmax(
        self,
        player: int,
        alpha: float,
        beta: float,
        depth: int,
    ) -> float:
        # max or min
        self.node_count += 1
        if depth <= 0:
            return self.evaluator.evaluate()
        if player == self.color:
            return self.maximize(player, depth, alpha, beta)
        return self.minimize(player, depth, alpha, beta)


class IterativeDeepening:
    def __init__(self, search_engine: SearchEngine, max_depth: int) -> None:
        self.search_engine: SearchEngine = search_engine
        self.max_depth: int = max_depth
        self.current_depth: int = 0
        self.best_move: Optional[Move] = None
        self.best_score: float = float("-inf")
        self.search_history: list[tuple[int, Optional[Move], float]] = []

    # For now literally just a pass through function
    def search(self, max_depth: int) -> tuple[Optional[Move], float]:
        self.max_depth = max_depth
        self.current_depth = max_depth

        # Pass through to search root, which is the same logic as previous get_move() core loop
        self.best_move, self.best_score = self.search_engine.search_root(max_depth)

        # Stores the best move and scores for depths (pass through for now)
        # Useful for ordering nodes in future searches to improve pruning efficiency.
        self.search_history.append(
            (self.current_depth, self.best_move, self.best_score)
        )
        return self.best_move, self.best_score


###
###     Evaluation-related classes
###

class Evaluator:
    def __init__(self, game_state: GameState, color: int) -> None:
        self.game_state: GameState = game_state
        self.color: int = color # 1 for black, 2 for white

    def evaluate(self) -> float:
        # Need to update logic
        my_color = "B" if self.color == 1 else "W"
        score = 0.0
        board = self.game_state.get_board()
        for row in board.board:
            for checker in row:
                if checker.color == ".":
                    continue
                value = 2.0 if checker.is_king else 1.0
                score += value if checker.color == my_color else -value
        return score

    def cheap_evaluate(self):
        # Quick evaluation for non-leaf nodes
        # Used to sort nodes to make pruning more likely
        pass

    def deep_evaluate(self, cheap_score=None):
        # Deeper evaluation at leaf nodes to fully evaluate position
        # Future optimization: reuse cheap_score
        return self.evaluate()

    def evaluate_material(self) -> float:
        # What evaluate() currently does
        return 0.0
    def evaluate_win(self) -> float:
        # Desperately needed
        return 0.0

    # A bunch of other possible evaluation functions we could use in the future
    def evaluate_advancement(self) -> float:
        return 0.0
    def evaluate_center_control(self) -> float:
        return 0.0
    def evaluate_mobility(self) -> float:
        return 0.0
    def evaluate_piece_safety(self) -> float:
        return 0.0
    def evaluate_king_potential(self) -> float:
        return 0.0


###
###     Game State-related classes
###

class GameState:
    # Currently, just a wrapper for the Board class
    # Will utilize BoardOptimized in the future to improve performance
    # Will use PositionCache in the future to store position metadata
    #   \- Possible similarity evaluation using Zobrist hashing

    def __init__(self, col, row, p):
        self.board = Board(col, row, p)
        self.board.initialize_game()

    def get_possible_moves(self, player):
        return self.board.get_all_possible_moves(player)

    def make_move(self, move, player):
        self.board.make_move(move, player)

    def undo_move(self):
        self.board.undo()

    def get_board(self):
        return self.board


class BetterBoard:
    # Stores the board as integers
    # Can be further optimized by only storing checker tiles
    # According to BoardClasses.py, during generation top left tile is always a checker
    def __init__(self, col: int, row: int, board: Board = None) -> None:
        self.col: int = col
        self.row: int = row
        if board is None:
            self.board: list[list[int]] = [[0 for _ in range(col)] for _ in range(row)]
        else:
            self.to_board(board)
        # Later optimization (would require appropriate move-inference)
        # self.board = [[0 for _ in range((col + 1) // 2)] for _ in range(row)]

    def to_board(self, board: Board) -> None:
        # Convert Board to BetterBoard
        pass


class BoardOptimized:
    # Simulates the board more optimally instead of relying on Board
    # Optimized board operations utilizing:
    # - Zobrist hashing to store board states and optimize calculations
    # - Faster calculations overall

    def __init__(self, col: int, row: int, p: int) -> None:
        self.col: int = col
        self.row: int = row
        self.p: int = p

    # - Bitboards???
    # Must reproduce Board functionality to avoid errors

class PositionCache:
    # Future storage for position metadata
    # Uses provided keys, does not own complete board states.\
    def __init__(self) -> None:
        pass