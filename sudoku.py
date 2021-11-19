import math
import sys
import os


class Node:
    def __init__(self):
        self.adj = set()
        self.chars = set()


class StatsTracker:
    def __init__(self):
        self.cells_examined = 0
        self.guesses = 0
        self.max_depth = 0
        self.depth = 0


def board_from_string(string):
    """ Turns an input string into a 2D list. This is really just to make printing easier """

    arr = string.replace("\n", " ").split(" ")
    n = math.floor(math.sqrt(len(arr)))

    board = []
    for y in range(n):
        row = []
        for x in range(n):
            cell = Node()
            index = y * n + x
            if arr[index] != "0":
                cell.chars.add((arr[index]))
            else:
                for i in range(n):
                    cell.chars.add(str(i + 1))
            row.append(cell)
        board.append(row)

    return (board, n)


def print_board(board, n):
    """ Prints out a 2D list representing a board """
    m = math.floor(math.sqrt(n))
    for y, row in enumerate(board):
        for x, node in enumerate(row):
            char = node.chars
            # only print if there's one option for the character
            if len(char) == 1:
                c = next(iter(char))
                print(c, end=" ")
                for i in range(0, len(str(n)) - len(c)):
                    print("", end=" ")
            else:
                for i in range(0, len(str(n)) + 1):
                    print("", end=" ")
            if (x + 1) % m == 0 and x > 0:
                print(" ", end=" ")
        print("")
        if (y + 1) % m == 0 and y > 0:
            print("")


def create_graph(board, n):
    """ Converts a 2D list into an adjacency list representing the board """

    m = math.floor(math.sqrt(n))
    vertices = []
    for y in range(n):
        for x in range(n):
            cell = board[y][x]
            # don't both creating adjacencies for solved cells
            if len(cell.chars) > 1:
                # columns
                for dy in range(n):
                    if dy != y:
                        cell.adj.add(board[dy][x])
                # rows
                for dx in range(n):
                    if dx != x:
                        cell.adj.add(board[y][dx])
                # subgrids
                for dy in range(m * (y // m), m * ((y // m) + 1)):
                    for dx in range(m * (x // m), m * ((x // m) + 1)):
                        if dy != y or dx != x:
                            cell.adj.add(board[dy][dx])

                vertices.append(cell)

    return vertices


def num_adjacent_possibilities(v):
    # this could be made faster by not computing each time
    count = 0
    for u in v.adj:
        count += len(u.chars)
    return count


def guess_confidence(v):
    # this is also doing some redundant calculation but it's not upper-bounding our function
    return len(v.chars) + num_adjacent_possibilities(v)


def solve(V, stats):
    """ Solves an n x n sudoku in the form of an adjacency list """

    # update the states
    stats.depth += 1
    if stats.depth > stats.max_depth:
        stats.max_depth = stats.depth

    # deduction
    while len(V) > 0:
        changed = False
        # look at the vertices with the fewest options first
        V.sort(key=num_adjacent_possibilities)
        for v in V:
            stats.cells_examined += 1

            # update possibilities based on neighbors
            for u in v.adj:
                if len(u.chars) == 1:
                    c = next(iter(u.chars))
                    if c in v.chars:
                        v.chars.remove(c)
                        changed = True

            if len(v.chars) == 1:
                # there is only one option for this cell so it's solved
                V.remove(v)
            elif len(v.chars) == 0:
                # there are no options for this cell so this branch is invalid
                return False

        # only continue to loop if we are still updating things
        if not changed:
            break

    # see if we've solved it
    if len(V) == 0:
        return True

    # the board couldn't be solved through deduction so make guesses

    # sort roughly by how confident we can be that a guess will be correct
    # there is some randomness in this
    V.sort(key=guess_confidence)

    # save current state of the board for backtracking
    save_chars = dict()
    for v in V:
        save_chars[v] = set(v.chars)
    save_vertices = list(V)
    save_depth = stats.depth

    # go through and make all necessary guesses
    for v in V:
        stats.cells_examined += 1
        for c in save_chars[v]:
            # pick an option
            v.chars = set([c])
            V.remove(v)
            stats.guesses += 1

            # recursively solve with this guess
            if solve(V, stats):
                return True

            # the guess didn't work so undo changes
            for u in V:
                u.chars = set(save_chars[u])
            V = list(save_vertices)
            stats.depth = save_depth

    # all guesses couldn't result in a successful solve
    return False


if len(sys.argv) < 2:
    print("Expected argument for input filename")
else:
    if sys.argv[1].endswith(".txt"):
        input_path = os.path.join(sys.argv[1])
        with open(input_path, "r") as f:
            board, n = board_from_string(f.read())
            print_board(board, n)
            print("Attempting to solve...\n")
            graph = create_graph(board, n)
            stats = StatsTracker()
            if solve(graph, stats):
                print_board(board, n)
            else:
                print("The board is unsolvable")
            print(f"Cells examined: {stats.cells_examined}")
            print(f"Max guess depth: {stats.max_depth}")
            print(f"Number of guesses: {stats.guesses}")
    else:
        print("The file must be a .txt")
