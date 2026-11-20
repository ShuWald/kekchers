#include "StudentAI.h"
#include <algorithm>
#include <cstdlib>
#include <limits>

GameState::GameState(int col, int row, int p) : board(col, row, p) {
    board.initializeGame();
}

vector<vector<Move>> GameState::get_possible_moves(int player) {
    return board.getAllPossibleMoves(player);
}

void GameState::make_move(const Move& move, int player) {
    board.makeMove(move, player);
}

void GameState::undo_move() {
    board.Undo();
}

Board& GameState::get_board() {
    return board;
}

//PositionCache::PositionCache() {}

Evaluator::Evaluator(GameState& game_state, int color)
    : game_state(game_state), color(color) {}

double Evaluator::evaluate() {
    // Need to update logic
    const string my_color = color == 1 ? "B" : "W";
    double score = 0.0;
    Board& current_board = game_state.get_board();
    for (const auto& row : current_board.board) {
        for (const Checker& checker : row) {
            if (checker.color == ".") {
                continue;
            }
            const double value = checker.isKing ? 2.0 : 1.0;
            score += checker.color == my_color ? value : -value;
        }
    }
    return score;
}

double Evaluator::cheap_evaluate() {
    // Quick evaluation for non-leaf nodes
    // Used to sort nodes to make pruning more likely
    return 0.0;
}

double Evaluator::deep_evaluate(double cheap_score) {
    // Deeper evaluation at leaf nodes to fully evaluate position
    // Future optimization: reuse cheap_score
    (void)cheap_score;
    return evaluate();
}

double Evaluator::evaluate_material() {
    // What evaluate() currently does
    return 0.0;
}

double Evaluator::evaluate_win() {
    // Desperately needed
    return 0.0;
}

// A bunch of other possible evaluation functions we could use in the future
double Evaluator::evaluate_advancement() { return 0.0; }
double Evaluator::evaluate_center_control() { return 0.0; }
double Evaluator::evaluate_mobility() { return 0.0; }
double Evaluator::evaluate_piece_safety() { return 0.0; }
double Evaluator::evaluate_king_potential() { return 0.0; }

SearchEngine::SearchEngine(GameState& game_state, Evaluator& evaluator,
                           PositionCache& position_cache, int color)
    : game_state(game_state), evaluator(evaluator),
      position_cache(position_cache), color(color), node_count(0) {
    opponent[1] = 2;
    opponent[2] = 1;
}

double SearchEngine::alpha_beta(int player, int depth, double alpha, double beta) {
    // alpha beta
    ++node_count;
    if (depth <= 0) {
        return evaluator.deep_evaluate();
    }
    if (player == color) {
        return maximize(player, depth, alpha, beta);
    }
    return minimize(player, depth, alpha, beta);
}

double SearchEngine::maximize(int player, int depth, double alpha, double beta) {
    // Searches for the highest score from the AI's perspective.
    vector<Move> moves = order_moves(game_state.get_possible_moves(player));
    if (moves.empty()) {
        return evaluator.deep_evaluate();
    }
    double max_eval = -numeric_limits<double>::infinity();
    for (const Move& move : moves) {
        game_state.make_move(move, player);
        double score = minmax(opponent[player], alpha, beta, depth - 1);
        game_state.undo_move();
        max_eval = max(max_eval, score);
        alpha = max(alpha, score);
        if (beta <= alpha) {
            break;
        }
    }
    return max_eval;
}

double SearchEngine::minimize(int player, int depth, double alpha, double beta) {
    // Searches for the lowest score from the AI's perspective.
    vector<Move> moves = order_moves(game_state.get_possible_moves(player));
    if (moves.empty()) {
        return evaluator.deep_evaluate();
    }
    double min_eval = numeric_limits<double>::infinity();
    for (const Move& move : moves) {
        game_state.make_move(move, player);
        double score = minmax(opponent[player], alpha, beta, depth - 1);
        game_state.undo_move();
        min_eval = min(min_eval, score);
        beta = min(beta, score);
        if (beta <= alpha) {
            break;
        }
    }
    return min_eval;
}

pair<Move, double> SearchEngine::search_root(int depth, bool& found_move) {
    // Retained core recursive minimax logic from StudentAI.get_move()
    node_count = 0;
    vector<vector<Move>> moves = game_state.get_possible_moves(color);
    double best_score = -numeric_limits<double>::infinity();
    vector<Move> best_moves;
    double alpha = -numeric_limits<double>::infinity();
    double beta = numeric_limits<double>::infinity();
    for (const vector<Move>& piece_moves : moves) {
        for (const Move& move : piece_moves) {
            game_state.make_move(move, color);
            double score = minmax(opponent[color], alpha, beta, depth - 1);
            game_state.undo_move();
            if (score > best_score) {
                best_score = score;
                best_moves = {move};
            } else if (score == best_score) {
                best_moves.push_back(move);
            }
        }
    }
    if (best_moves.empty()) {
        found_move = false;
        return {Move(), best_score};
    }
    found_move = true;
    return {best_moves[rand() % best_moves.size()], best_score};
}

// Improve pruning possiblity by ordering moves based on cheap evaluation/heuristics
vector<Move> SearchEngine::order_moves(const vector<vector<Move>>& moves) {
    return flatten_moves(moves);
}

// Convert moves to a list for easier sorting (order_moves)
vector<Move> SearchEngine::flatten_moves(const vector<vector<Move>>& moves) {
    vector<Move> flattened;
    for (const vector<Move>& piece_moves : moves) {
        flattened.insert(flattened.end(), piece_moves.begin(), piece_moves.end());
    }
    return flattened;
}

double SearchEngine::minmax(int player, double alpha, double beta, int depth) {
    // max or min
    ++node_count;
    if (depth <= 0) {
        return evaluator.evaluate();
    }
    if (player == color) {
        return maximize(player, depth, alpha, beta);
    }
    return minimize(player, depth, alpha, beta);
}

IterativeDeepening::IterativeDeepening(SearchEngine& search_engine, int max_depth)
    : search_engine(search_engine), max_depth(max_depth), current_depth(0),
      has_best_move(false), best_score(-numeric_limits<double>::infinity()) {}

// For now literally just a pass through function
pair<Move, double> IterativeDeepening::search(int max_depth, bool& found_move) {
    this->max_depth = max_depth;
    current_depth = max_depth;

    // Pass through to search root, which is the same logic as previous get_move() core loop
    auto result = search_engine.search_root(max_depth, found_move);
    best_move = result.first;
    best_score = result.second;
    has_best_move = found_move;

    // Stores the best move and scores for depths (pass through for now)
    // Useful for ordering nodes in future searches to improve pruning efficiency.
    search_history.push_back({current_depth, {best_move, best_score}});
    return result;
}

BetterBoard::BetterBoard(int col, int row, Board* source) : col(col), row(row) {
    if (source == nullptr) {
        board.assign(row, vector<int>(col, 0));
    } else {
        to_board(*source);
    }
    // Later optimization (would require appropriate move-inference)
    // self.board = [[0 for _ in range((col + 1) // 2)] for _ in range(row)]
}

void BetterBoard::to_board(Board& source) {
    // Convert Board to BetterBoard
}

BoardOptimized::BoardOptimized(int col, int row, int p) : col(col), row(row), p(p) {}

StudentAI::StudentAI(int col, int row, int p)
    : AI(col, row, p), board(col, row, p), game_state(col, row, p), color(2),
      opponent{0, 2, 1}, depth(4), evaluator(game_state, color),
      search_engine(game_state, evaluator, position_cache, color),
      iterative_deepening(search_engine, depth) {
    board.initializeGame();
    player = color;
}

Move StudentAI::GetMove(Move move) {
    if (!move.seq.empty()) {
        game_state.make_move(move, opponent[color]);
    } else {
        color = 1;
        evaluator.color = color;
        search_engine.color = color;
    }
    search_engine.color = color;
    iterative_deepening.max_depth = depth;
    bool found_move = false;
    auto result = iterative_deepening.search(depth, found_move);
    if (!found_move) {
        throw runtime_error("No legal move is available");
    }
    game_state.make_move(result.first, color);
    return result.first;
}