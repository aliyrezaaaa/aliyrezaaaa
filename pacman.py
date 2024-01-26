import random
import os
import time
from collections import deque


R, C = 9, 18
W = "#"
F = "."
E = " "
P = "P"
G = ["G", "g"]
V = [[False for x in range(C)] for x in range(R)]
V[0][0] = True


def init_grid():
    grid = [[F for _ in range(C)] for _ in range(R)]
    grid[0][0] = P  
    
    for j in range(6, 10):
        grid[3][j] = W
    for j in range(4, 9):
        grid[j][15] = W
        grid[j][3] = W
    r = 0
    for ghost in G:
        grid[2 + r][7] = ghost
        r += 2
    return grid


def print_g(g):
    for row in g:
        print(" ".join(row))
    print("\n")


def calc_dist_to_food(g, r, c):
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def is_valid(x, y):
        return 0 <= x < R and 0 <= y < C and g[x][y] != W

    q = deque([(r, c, 0)])

    v1 = set([(r, c)])

    while q:
        x, y, d = q.popleft()

        if g[x][y] == F:
            return d

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy

            if is_valid(nx, ny) and (nx, ny) not in v1:
                v1.add((nx, ny))
                q.append((nx, ny, d + 1))

    return float('inf')

# Calculate the distance to ghosts using Breadth-First Search
def calc_dist_to_ghosts(g, r, c, ghost):
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def is_valid(x, y):
        return 0 <= x < R and 0 <= y < C and g[x][y] != W

    q = deque([(r, c, 0)])

    v1 = set([(r, c)])

    while q:
        x, y, d = q.popleft()

        if g[x][y] == ghost:
            return d

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy

            if is_valid(nx, ny) and (nx, ny) not in v1:
                v1.add((nx, ny))
                q.append((nx, ny, d + 1))

    return float('inf')

# Evaluate the utility of Pac-Man's move
def u(g, r, c):
    ghost_p = 0
    score = 0
    if g[r][c] == F:
        score += 9
    elif g[r][c] == E:
        score -= 50
    elif g[r][c] in G:
        score -= 1000
    f_d = calc_dist_to_food(g, r, c)
    f_b = max(30 - f_d, 0)

    for ghost in G:
        d = calc_dist_to_ghosts(g, r, c, ghost)
        if 0 < d <= 4:
            ghost_p -= 800 / d

    return f_b + ghost_p + score

# Minimax algorithm for Pac-Man's move
def minimax_move(g, r, c, depth=0, turn=0):
    v2 = [row[:] for row in V]

    if depth == 1:
        return u(g, r, c)
    if turn == 0:  
        b_s = -float("inf")
        n_s = 0
        for n_r, n_c in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]:
            if 0 <= n_r < R and 0 <= n_c < C and g[n_r][n_c] != W:
                t_g = [row[:] for row in g]
                t_f = t_g[n_r][n_c]
                t_g[n_r][n_c] = P
                t_g[r][c] = E
                v2[n_r][n_c] = True
                if t_f == F:
                    n_s += 100

                s = minimax_move(t_g, n_r, n_c, depth, 1)
                s += n_s

                v2[n_r][n_c] = False
                t_g[n_r][n_c] = t_f
                t_g[r][c] = P

                if s > b_s:
                    b_s = s
                    b_m = (n_r, n_c)
        return b_m if depth == 0 else b_s
    elif turn == 1:  
        w_s = float("inf")
        try:
            g_r, g_c = [(i, row.index("G")) for i, row in enumerate(g) if "G" in row][0]
            for n_r, n_c in [(g_r + 1, g_c), (g_r - 1, g_c), (g_r, g_c + 1), (g_r, g_c - 1)]:
                if 0 <= n_r < R and 0 <= n_c < C and g[n_r][n_c] != W:
                    t_g = [row[:] for row in g]
                    t_f = t_g[n_r][n_c]
                    t_g[n_r][n_c] = "G"
                    if not v2[g_r][g_c]:
                        t_g[g_r][g_c] = F
                    else:
                        t_g[g_r][g_c] = E

                    s = minimax_move(t_g, r, c, depth, 2)
                    t_g[g_r][g_c] = "G"
                    t_g[n_r][n_c] = t_f
                    w_s = min(w_s, s)
        except:
            s = minimax_move(g, r, c, depth, 2)
            w_s = min(w_s, s)

        return w_s
    elif turn == 2:  
        w_s = float("inf")
        try:
            g_r, g_c = [(i, row.index("g")) for i, row in enumerate(g) if "g" in row][0]
            for n_r, n_c in [(g_r + 1, g_c), (g_r - 1, g_c), (g_r, g_c + 1), (g_r, g_c - 1)]:
                if 0 <= n_r < R and 0 <= n_c < C and g[n_r][n_c] != W:
                    t_g = [row[:] for row in g]
                    t_f = t_g[n_r][n_c]
                    t_g[n_r][n_c] = "g"
                    if not v2[g_r][g_c]:
                        t_g[g_r][g_c] = F
                    else:
                        t_g[g_r][g_c] = E

                    s = minimax_move(t_g, r, c, depth + 1, 0)
                    t_g[g_r][g_c] = "g"
                    t_g[n_r][n_c] = t_f
                    w_s = min(w_s, s)
        except:
            s = minimax_move(g, r, c, depth + 1, 0)
            w_s = min(w_s, s)

        return w_s

# Move ghosts randomly
def move_ghost(g, ghost):
    r, c = [(i, row.index(ghost)) for i, row in enumerate(g) if ghost in row][0]
    m = [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]
    random.shuffle(m)
    for n_r, n_c in m:
        if 0 <= n_r < R and 0 <= n_c < C and g[n_r][n_c] != W:
            if g[n_r][n_c] not in ["g", "G"]:
                if V[r][c]:
                    g[r][c] = E
                else:
                    g[r][c] = F
                g[n_r][n_c] = ghost
                break
    return

# Main game loop
def play_game():
    g = init_grid()
    p_r, p_c = 0, 0
    s = 0
    t = 0
    while True:
        if t % 3 == 0:
            n_r, n_c = minimax_move(g, p_r, p_c, 0)
            # Update Pac-Man's position and score
            if (n_r, n_c) != (p_r, p_c):
                if g[n_r][n_c] in ["G", "g"]:
                    print(f"Game Over! You lost! Score: {s}")
                    break
                else:
                    if g[n_r][n_c] == F:
                        s += 9
                    else:
                        s -= 1
                    g[p_r][p_c] = E
                    p_r, p_c = n_r, n_c
                    g[n_r][n_c] = P
                    V[n_r][n_c] = True

            t += 1
            print(s)
            print_g(g)

        
        if t % 3 == 1:
            move_ghost(g, "G")
            t += 1

        if t % 3 == 2:
            move_ghost(g, "g")
            t += 1

        time.sleep(0.01)
        os.system("cls")

        # Check if Pac-Man encounters a ghost
        if g[p_r][p_c] in G:
            print(f"Game Over! You lost! Score: {s}")
            break

        # Check if all dots are eaten
        if not any(F in row for row in g):
            print(f"You win! Score: {s}")
            break

# Run the game
play_game()


"""### alpha beta
import secrets

def minimax_move(hidden_grid, x, y, depth=0, turn=0, alpha=float('-inf'), beta=float('inf')):
    secret_visited = [row[:] for row in hidden_grid]

    # If the maximum depth is reached or it's a leaf node, return the utility value
    if depth == 2:
      return secret_utility(hidden_grid, x, y)

    if turn == 0: 
        best_score = -float("inf")
        new_score = 0

        # Evaluate all possible moves for Secret-Man
        for new_x, new_y in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
            # Check if the move is valid
            if 0 <= new_x < SECRET_ROWS and 0 <= new_y < SECRET_COLS and hidden_grid[new_x][new_y] != SECRET_WALL:
                temp_hidden_grid = [row[:] for row in hidden_grid]
                temp_food = temp_hidden_grid[new_x][new_y]
                temp_hidden_grid[x][y] = SECRET_EMPTY
                temp_hidden_grid[new_x][new_y] = SECRET_MAN
                secret_visited[new_x][new_y] = True

                # Assign a higher score for collecting secret food
                if temp_food == SECRET_FOOD:
                    new_score += 60

                # Recursive call for the next move
                score = minimax_move(temp_hidden_grid, new_x, new_y, depth, 1, alpha, beta)
                score += new_score

                secret_visited[new_x][new_y] = False
                temp_hidden_grid[new_x][new_y] = temp_food
                temp_hidden_grid[x][y] = SECRET_MAN

                # Update the best move and score
                if score > best_score:
                    best_score = score
                    best_move = (new_x, new_y)

                # Perform alpha-beta pruning
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break

        return best_move if depth == 0 else best_score

    elif turn == 1:  
        worst_score = float("inf")

        try:
            
            secret_x, secret_y = [(i, row.index(SECRET_GHOST)) for i, row in enumerate(hidden_grid) if SECRET_GHOST in row][0]

            
            for new_x, new_y in [(secret_x + 1, secret_y), (secret_x - 1, secret_y), (secret_x, secret_y + 1), (secret_x, secret_y - 1)]:
                if 0 <= new_x < SECRET_ROWS and 0 <= new_y < SECRET_COLS and hidden_grid[new_x][new_y] != SECRET_WALL:
                    temp_hidden_grid = [row[:] for row in hidden_grid]
                    temp_food = temp_hidden_grid[new_x][new_y]
                    temp_hidden_grid[new_x][new_y] = SECRET_GHOST

                   
                    if not secret_visited[secret_x][secret_y]:
                        temp_hidden_grid[secret_x][secret_y] = SECRET_FOOD
                    else:
                        temp_hidden_grid[secret_x][secret_y] = SECRET_EMPTY

                   
                    score = minimax_move(temp_hidden_grid, x, y, depth, 2, alpha, beta)

                    temp_hidden_grid[secret_x][secret_y] = SECRET_GHOST
                    temp_hidden_grid[new_x][new_y] = temp_food
                    worst_score = min(worst_score, score)

                    
                    beta = min(beta, worst_score)
                    if beta <= alpha:
                        break

        except:
            
            score = minimax_move(hidden_grid, x, y, depth, 2, alpha, beta)
            worst_score = min(worst_score, score)

        return worst_score

    elif turn == 2:  
        worst_score = float("inf")

        try:
            
            secret_x, secret_y = [(i, row.index(SECRET_GHOST_SMALL)) for i, row in enumerate(hidden_grid) if SECRET_GHOST_SMALL in row][0]

            
            for new_x, new_y in [(secret_x + 1, secret_y), (secret_x - 1, secret_y), (secret_x, secret_y + 1), (secret_x, secret_y - 1)]:
                if 0 <= new_x < SECRET_ROWS and 0 <= new_y < SECRET_COLS and hidden_grid[new_x][new_y] != SECRET_WALL:
                    temp_hidden_grid = [row[:] for row in hidden_grid]
                    temp_food = temp_hidden_grid[new_x][new_y]
                    temp_hidden_grid[new_x][new_y] = SECRET_GHOST_SMALL

                    
                    if not secret_visited[secret_x][secret_y]:
                        temp_hidden_grid[secret_x][secret_y] = SECRET_FOOD
                    else:
                        temp_hidden_grid[secret_x][secret_y] = SECRET_EMPTY

                    
                    score = minimax_move(temp_hidden_grid, x, y, depth + 1, 0, alpha, beta)

                    temp_hidden_grid[secret_x][secret_y] = SECRET_GHOST_SMALL
                    temp_hidden_grid[new_x][new_y] = temp_food
                    worst_score = min(worst_score, score)

                    
                    beta = min(beta, worst_score)
                    if beta <= alpha:
                        break

        except:
            
            score = minimax_move(hidden_grid, x, y, depth + 1, 0, alpha, beta)
            worst_score = min(worst_score, score)

        return worst_score"""

