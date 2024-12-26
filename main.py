import tkinter as tk

# -----------------------
# Board Representation
# -----------------------
# We'll represent the board with an 8x8 list of lists.
#  0 = empty square
#  1 = red piece
#  2 = black piece
#  3 = red king
#  4 = black king
#
# Squares with a piece will only be on "valid" checkers squares
# (in a real game, typically black squares). 
# For simplicity, we'll mark all squares as if they can hold a piece,
# but in a real checkerboard, only half of the squares are used.

initial_board = [
    [3,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,3],
    [3,0,3,0,3,0,0,0],
    [0,0,0,0,0,0,0,4],
    [0,0,4,0,4,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0]
]
# Note: This is a "standard" initial layout just as an example.
# Replace `initial_board` with your actual position 
# if you want to evaluate a real game state.


# -----------------------
# Move Generation
# -----------------------
def get_all_moves(board, side):
    """
    Generate all possible legal (simplified) moves for the given side ('red' or 'black').
    Each move is returned as ( (start_row, start_col), (end_row, end_col) ).
    This function doesn't handle multi-jump sequences in detail; 
    you would expand it for fully correct checkers logic.
    """
    moves = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if side == 'red' and piece in (1, 3):  # Red piece or Red king
                moves.extend( possible_moves_for_piece(board, r, c) )
            elif side == 'black' and piece in (2, 4):  # Black piece or Black king
                moves.extend( possible_moves_for_piece(board, r, c) )
    return moves

def possible_moves_for_piece(board, r, c):
    """
    Return a list of all 'simple' moves (no multi-jumps) for the piece at board[r][c].
    """
    piece = board[r][c]
    direction = []
    if piece == 1:      # Red man
        direction = [(-1, -1), (-1, +1)]  # move up-left or up-right
    elif piece == 2:    # Black man
        direction = [(+1, -1), (+1, +1)]  # move down-left or down-right
    elif piece == 3:    # Red king
        direction = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]  # can move in all diagonals
    elif piece == 4:    # Black king
        direction = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]

    moves = []
    for dr, dc in direction:
        new_r = r + dr
        new_c = c + dc
        if 0 <= new_r < 8 and 0 <= new_c < 8 and board[new_r][new_c] == 0:
            moves.append(((r,c),(new_r,new_c)))
        # Check for capture (one jump)
        jump_r = r + 2*dr
        jump_c = c + 2*dc
        if (0 <= jump_r < 8 and 0 <= jump_c < 8 
            and board[new_r][new_c] != 0  # There's an opponent piece to jump
            and board[jump_r][jump_c] == 0 
            and not same_color(piece, board[new_r][new_c])):

            moves.append(((r,c),(jump_r,jump_c)))
    return moves

def same_color(piece_a, piece_b):
    """Return True if both pieces belong to the same side (man or king)."""
    # Red pieces are 1 or 3, black pieces are 2 or 4
    if piece_a in (1,3) and piece_b in (1,3):
        return True
    if piece_a in (2,4) and piece_b in (2,4):
        return True
    return False


# -----------------------
# Apply a Move
# -----------------------
def apply_move(board, move):
    """
    Return a NEW board state after applying the given move.
    A move is ((r1, c1), (r2, c2)).
    We'll also do a quick check to see if a capture occurred,
    and if so, remove the captured piece. 
    We won't handle multiple jumps here for brevity.
    """
    (r1, c1), (r2, c2) = move
    new_board = [row[:] for row in board]  # Make a copy

    piece = new_board[r1][c1]
    new_board[r1][c1] = 0
    new_board[r2][c2] = piece

    # Check if it's a jump
    if abs(r2 - r1) == 2:
        # The jumped piece is halfway between start and end
        jumped_r = (r1 + r2) // 2
        jumped_c = (c1 + c2) // 2
        new_board[jumped_r][jumped_c] = 0  # remove captured piece

    # Check if we should crown a piece
    if piece == 1 and r2 == 0:
        new_board[r2][c2] = 3  # Red king
    elif piece == 2 and r2 == 7:
        new_board[r2][c2] = 4  # Black king

    return new_board


# -----------------------
# Evaluation Function
# -----------------------
def evaluate(board):
    """
    Give a quick numeric evaluation of the board:
      + Positive if it's good for Red
      + Negative if it's good for Black
    """
    score = 0
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == 1:
                score += 5
            elif p == 3:  # Red king
                score += 8
            elif p == 2:
                score -= 5
            elif p == 4:  # Black king
                score -= 8
    return score


# -----------------------
# Alpha-Beta Search
# -----------------------
def alpha_beta(board, depth, alpha, beta, maximizing_player):
    """
    Standard alpha-beta search. 'maximizing_player' = True means it's Red's turn.
    """
    if depth == 0:
        return evaluate(board), None

    side = 'red' if maximizing_player else 'black'
    moves = get_all_moves(board, side)

    if not moves:  
        # No moves available => this side loses => big negative if Red to move, positive if Black to move
        return (float('-inf') if maximizing_player else float('inf')), None

    best_move = None

    if maximizing_player:
        value = float('-inf')
        for mv in moves:
            new_b = apply_move(board, mv)
            child_val, _ = alpha_beta(new_b, depth-1, alpha, beta, False)
            if child_val > value:
                value = child_val
                best_move = mv
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value, best_move
    else:
        value = float('inf')
        for mv in moves:
            new_b = apply_move(board, mv)
            child_val, _ = alpha_beta(new_b, depth-1, alpha, beta, True)
            if child_val < value:
                value = child_val
                best_move = mv
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value, best_move

def find_best_move(board, side, depth):
    """
    Top-level function to get the best move from alpha-beta.
    'side' = 'red' or 'black'.
    'depth' = search depth (increase for stronger, but slower).
    """
    maximizing = True if side == 'red' else False
    _, move = alpha_beta(board, depth, float('-inf'), float('inf'), maximizing)
    return move


# -----------------------
# GUI via tkinter
# -----------------------
class CheckersGUI:
    def __init__(self, root, board):
        self.root = root
        self.board = board
        self.cell_size = 60
        self.canvas = tk.Canvas(root, width=8*self.cell_size, height=8*self.cell_size)
        self.canvas.pack()
        self.draw_board()

        # Example usage: find best move for Red, then highlight it
        best_move = find_best_move(self.board, 'red', depth=8)
        if best_move:
            self.highlight_move(best_move)

    def draw_board(self):
        """
        Draw the checkers board and pieces.
        """
        for r in range(8):
            for c in range(8):
                # Draw the square (checkerboard pattern)
                color = "black" if (r + c) % 2 == 0 else "#B22222"
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                # Draw the piece if present
                piece = self.board[r][c]
                if piece != 0:
                    px = x1 + self.cell_size//2
                    py = y1 + self.cell_size//2
                    radius = self.cell_size//2 - 5

                    if piece in (1, 3):  # Red
                        fill_col = "red"
                    else:               # Black
                        fill_col = "gray"

                    self.canvas.create_oval(px-radius, py-radius,
                                             px+radius, py+radius,
                                             fill=fill_col)

                    # If it's a king, draw a small crown or mark
                    if piece in (3,4):
                        self.canvas.create_text(px, py, text="K", fill="white", font=("Arial", 14, "bold"))

    def highlight_move(self, move):
        """
        Visually highlight the best move found by alpha-beta.
        move is ((r1,c1),(r2,c2))
        """
        (r1,c1),(r2,c2) = move
        # Draw a yellow rectangle around start and end squares
        for (rr, cc) in [(r1,c1), (r2,c2)]:
            x1 = cc * self.cell_size
            y1 = rr * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)

def main():
    root = tk.Tk()
    root.title("Checkers Next-Move Demo")
    gui = CheckersGUI(root, initial_board)
    root.mainloop()

if __name__ == "__main__":
    main()
