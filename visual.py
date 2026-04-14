import numpy as np

WINNING_LINES = np.array([
    [0, 1, 2], [3, 4, 5], [6, 7, 8],    # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],    # columns
    [0, 4, 8], [2, 4, 6],               # diagonals
])

def print_board(board, indent=""):
    """Helper to draw the board nicely in the terminal."""
    symbols = {1: 'X', -1: 'O', 0: ' '}
    for i in range(0, 9, 3):
        row = [symbols[board[i+j]] for j in range(3)]
        print(f"{indent}[ {row[0]} | {row[1]} | {row[2]} ]")

def check_winner(board: np.ndarray) -> str | None:
    for line in WINNING_LINES:
        total = board[line].sum()
        if total == 3: return "X"
        elif total == -3: return "O"
    if np.all(board != 0): return "draw"
    return None

def minimax(board: np.ndarray, is_maximizing: bool, depth: int) -> int:
    indent = "    " * depth
    turn_name = "CPU (O)" if is_maximizing else "Player (X)"

    # 1. Check if this timeline hit a game over
    winner = check_winner(board)
    if winner == "O":
        print(f"{indent}🏁 GAME OVER: CPU wins here! (Score: 1)")
        return 1
    elif winner == "X":
        print(f"{indent}🏁 GAME OVER: Player wins here! (Score: -1)")
        return -1
    elif winner == "draw":
        print(f"{indent}🏁 GAME OVER: Draw here! (Score: 0)")
        return 0

    empty_cells = np.where(board == 0)[0]
    scores = []

    print(f"{indent}🧠 [Depth {depth}] {turn_name} is evaluating {len(empty_cells)} possible moves...")

    # 2. Try all possible moves
    for i in empty_cells:
        print(f"\n{indent}---> {turn_name} tries playing at index {i}:")
        board[i] = -1 if is_maximizing else 1
        print_board(board, indent + "  ")

        score = minimax(board, not is_maximizing, depth + 1)
        scores.append(score)

        board[i] = 0

    # NEW: Print the collected scores array before making a decision
    print(f"\n{indent}📊 [Depth {depth}] Evaluated moves {empty_cells.tolist()} resulted in scores: {scores}")

    # 3. Pick the best outcome
    best_score = max(scores) if is_maximizing else min(scores)

    # NEW: Make it clearer how the choice is being made
    action = "MAX" if is_maximizing else "MIN"
    print(f"{indent}✅ [Depth {depth}] {turn_name} chooses {action}{scores} = {best_score}")

    return best_score

def get_cpu_move(board: np.ndarray) -> int:
    print("===================================")
    print("     MINIMAX VISUALIZATION START     ")
    print("===================================")
    print("Current Board State:")
    print_board(board)
    print("===================================\n")

    best_score = -2
    best_index = -1
    root_scores = [] # NEW: Keep track of root scores
    root_moves = np.where(board == 0)[0]

    for i in root_moves:
        print(f"\n[ROOT] CPU evaluating its first option: Play at index {i}:")
        board[i] = -1
        print_board(board, "  ")

        score = minimax(board, False, depth=1)
        root_scores.append(score) # NEW: Save score
        board[i] = 0

        print(f"[ROOT] ---> Move {i} results in an ultimate score of {score}")
        if score > best_score:
            best_score = score
            best_index = i

    print(f"\n===================================")
    print(f"📊 [ROOT] Final evaluation for moves {root_moves.tolist()} = scores {root_scores}")
    print(f"CONCLUSION: CPU chooses MAX{root_scores} -> Score: {best_score} (Move: {best_index})")
    print(f"===================================")
    return int(best_index)

if __name__ == "__main__":
    test_board = np.array(
        [1, 0, 1,
        -1, -1, 0,
         0, 1, 0],
        dtype=np.int8)

    get_cpu_move(test_board)
