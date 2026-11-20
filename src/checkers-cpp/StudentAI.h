#ifndef STUDENTAI_H
#define STUDENTAI_H
#include "AI.h"
#include "Board.h"
#include <utility>

#pragma once

//The following part should be completed by students.
//Students can modify anything except the class name and exisiting functions and varibles.
class GameState {
    Board board;
public:
    // Currently, just a wrapper for the Board class
    // Will utilize BoardOptimized in the future to improve performance
    // Will use PositionCache in the future to store position metadata
    //   \- Possible similarity evaluation using Zobrist hashing
    GameState(int col, int row, int p);
    vector<vector<Move>> get_possible_moves(int player);
    void make_move(const Move& move, int player);
    void undo_move();
    Board& get_board();
};

class PositionCache {
    // Future storage for position metadata
    // Uses provided keys, does not own complete board states.\
public:
    PositionCache();
};

class Evaluator {
public:
    GameState& game_state;
    int color; // 1 for black, 2 for white
    Evaluator(GameState& game_state, int color);
    double evaluate();
    double cheap_evaluate();
    double deep_evaluate(double cheap_score = 0.0);
    double evaluate_material();
    double evaluate_win();
    // A bunch of other possible evaluation functions we could use in the future
    double evaluate_advancement();
    double evaluate_center_control();
    double evaluate_mobility();
    double evaluate_piece_safety();
    double evaluate_king_potential();
};

class SearchEngine {
public:
    GameState& game_state;
    Evaluator& evaluator;
    PositionCache& position_cache;
    int color;
    int opponent[3];
    int node_count;
    SearchEngine(GameState& game_state, Evaluator& evaluator,
                 PositionCache& position_cache, int color);
    double alpha_beta(int player, int depth, double alpha, double beta);
    double maximize(int player, int depth, double alpha, double beta);
    double minimize(int player, int depth, double alpha, double beta);
    pair<Move, double> search_root(int depth, bool& found_move);
    // Improve pruning possiblity by ordering moves based on cheap evaluation/heuristics
    vector<Move> order_moves(const vector<vector<Move>>& moves);
    // Convert moves to a list for easier sorting (order_moves)
    vector<Move> flatten_moves(const vector<vector<Move>>& moves);
    double minmax(int player, double alpha, double beta, int depth);
};

class IterativeDeepening {
public:
    SearchEngine& search_engine;
    int max_depth;
    int current_depth;
    Move best_move;
    bool has_best_move;
    double best_score;
    vector<pair<int, pair<Move, double>>> search_history;
    IterativeDeepening(SearchEngine& search_engine, int max_depth);
    // For now literally just a pass through function
    pair<Move, double> search(int max_depth, bool& found_move);
};

class BetterBoard {
    // Stores the board as integers
    // Can be further optimized by only storing checker tiles
    // According to BoardClasses.py, during generation top left tile is always a checker
    int col, row;
    vector<vector<int>> board;
public:
    BetterBoard(int col, int row, Board* board = nullptr);
    void to_board(Board& board);
    // Later optimization (would require appropriate move-inference)
    // self.board = [[0 for _ in range((col + 1) // 2)] for _ in range(row)]
};

class BoardOptimized {
    // Simulates the board more optimally instead of relying on Board
    // Optimized board operations utilizing:
    // - Zobrist hashing to store board states and optimize calculations
    // - Faster calculations overall
    int col, row, p;
public:
    BoardOptimized(int col, int row, int p);
    // - Bitboards???
    // Must reproduce Board functionality to avoid errors
};

class StudentAI : public AI {
public:
    Board board;
    GameState game_state;
    int color;
    int opponent[3];
    int depth;
    Evaluator evaluator;
    PositionCache position_cache;
    SearchEngine search_engine;
    IterativeDeepening iterative_deepening;
    StudentAI(int col, int row, int p);
    virtual Move GetMove(Move board);
};

#endif //STUDENTAI_H
