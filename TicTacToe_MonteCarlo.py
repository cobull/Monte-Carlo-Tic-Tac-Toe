from typing import Any
from random import randint
import copy
import math

class Node:
    """A node to be inserted into the tree during the Monte Carlo Tree Search.
    New nodes are created during the expand() function and the make_comp_move() 
    function.

    Attributes
        wins: number of wins acheived by traversing path with this node
        visits: number of times node has been traversed
        children: nodes that represent legal next moves
        parent: parent node
        game_state: nested lists that represent where players have moved 
        player: player who just moved in order to end up at this game state
        is_end_state: boolean indicating whether the game state is a win/draw

    Methods
        __init__
    """
    def __init__(self, game, player, parent = None):
        """Initializes attributes of new nodes

        Parameters
            game: nested lists that represent where players have moved
            player: player that moved to reach game state
            parent: parent node or None
        """
        self.wins = 0
        self.visits = 0
        self.children = []
        self.parent = parent
        self.game_state = game
        self.player = player
        self.is_end_state = False


def traverse(current_node):
    """Traverses down the tree starting from the root by either choosing 
    a child node that hasn't been visited, or choosing the node with the
    highest UCB1 value in the case that all child nodes have been visited
    at least once.

    Parameters
        current_node: Node
            The parent whose children will be interrogated.

    Returns
        node: Node
            The leaf node that the function traversed to.
    """
    current = current_node
    if current.children == []:
        return current
    elif any(x.visits == 0 for x in current.children):
        for child in current.children:
            if child.visits == 0:
                current = child
                return current
    else:
        current = current.children[max_UCB1_index(current)]
        current = traverse(current)
        return current  

def max_UCB1_index(current):
    """Iterates through children of parent node and returns the index
    of the child with the highest UCB1 score.

    Parameters
        current: Node
            The parent node whose children will be interrogated.

    Returns
        index: int
            The index of child node with highest UCB1 score.
    """
    index = 0
    max_UCB1 = calculate_UCB1(current.children[index])
    for i in range(len(current.children)):
        UCB1 = calculate_UCB1(current.children[i])
        if UCB1 > max_UCB1:
            max_UCB1 = UCB1
            index = i
    return index

def calculate_UCB1(child):
    """Calculates UCB1 score of a node in the tree and returns the.
    score

    Parameters
        child: Node
            The child node whose UCB1 score is to be calculated.

    Returns
        exploitation + exploration_constant * exploration: float
            UCB1 score
    """
    num_wins = child.wins
    num_visits = child.visits
    exploration_constant = 1.4
    num_parent_visits = child.parent.visits
    exploitation = float(num_wins / num_visits)
    exploration = math.sqrt(math.log2(num_parent_visits) / num_visits)
    return exploitation + exploration_constant * exploration

def expand(current):
    """Generates all legal game states from a given game state and
    creates new nodes from these game states. Appends these newly
    created nodes to the list of children of the parent node.

    Parameters
        current: Node
            Parent node whose children will be generated and added
            to child list.
    """
    current_game_state = copy.deepcopy(current.game_state)
    for x, row in enumerate(current_game_state):
        for y, place in enumerate(row):
            if current_game_state[x][y] == "X": 
                player_num = 1 if current.player == 2 else 2
                game = copy.deepcopy(current_game_state)
                game[x][y] = player_num
                child = Node(game, player_num, current)
                if check_for_draw(child.game_state):
                    child.is_end_state = True
                if check_for_win(child.game_state, player_num):
                    child.is_end_state = True
                current.children.append(child)

def check_for_win(game_board, player):
    """Checks to see if a win has been acheived by the player
    who just moved given a current game state. First checks
    for a win on the rows, then the columns, then the diagonals.

    Parameters
        game_board: nested lists
            The reprensentation of game state and where each player
            has moved.
        player: int
            The player that just moved to reach game_board game
            state.

    Returns
        is_win: boolean
            The truth value of whether a wins has been acheived.
    """
    is_win = False
    for i in range(3):
        if (game_board[i][0] == player and
            game_board[i][1] == player and
            game_board[i][2] == player):
            is_win = True
            return is_win
        
        if (game_board[0][i] == player and
            game_board[1][i] == player and
            game_board[2][i] == player):
            is_win = True
            return is_win
    
    if (game_board[0][0] == player and
        game_board[1][1] == player and
        game_board[2][2] == player):
        is_win = True
        return is_win
    
    if (game_board[0][2] == player and
        game_board[1][1] == player and
        game_board[2][0] == player):
        is_win = True
        return is_win
    
    return is_win

def check_for_draw(game):
    """Checks to see if a draw has been acheived given a game
    state.

    Parameters
        game: nested lists
            The representation of the game board and where each
            player has moved.
        
    Returns
        True or False
            The truth value of whether a draw has been acheived.
    """
    l = [x for y in game for x in y]
    if any(x == "X" for x in l):
        return False
    else:
        return True
   
def rollout(game_state, player):
    """Creates a copy of the game state and makes random, alternating
    moves until a win or draw is acheived.

    Parameters
        game_state: nested lists
            The representation of the game board and where each
            player has moved.
        player: int
            The player that just moved to reach the game state.

    Returns
        player_num: int
            The player who acheived the win.
        -20: int
            An arbitrary number that will be returned if a draw is 
            acheived.
    """
    current_game_state = copy.deepcopy(game_state)
    player_num = copy.deepcopy(player)
    while (not check_for_win(current_game_state, player_num) 
           and not check_for_draw(current_game_state)):
        rand_row = randint(0, 2)
        rand_col = randint(0, 2)
        while current_game_state[rand_row][rand_col] != "X":
            rand_row = randint(0, 2)
            rand_col = randint(0, 2)
        player_num = 2 if player_num == 1 else 1
        current_game_state[rand_row][rand_col] = player_num
    if check_for_win(current_game_state, player_num):   
        return player_num
    elif check_for_draw(current_game_state):
        return -20

def back_propagate(current_node, rollout_result):
    """Traverses from leaf node, back up to the root node and updates
    each traversed node's wins and visits attributes based on the
    result of the rollout

    Parameters
        current_node: Node
            The leaf node from where the rollout was initiated.
        rollout_result: int
            The player who achieved the win during the rollout,
            or an arbitrary number to indicate a draw.
    """
    current = current_node
    while current != None:
        if rollout_result == -20:
            current.wins += 0.5
            current.visits += 1
            current = current.parent
        else:
            if current.player == rollout_result:
                current.wins += 1
                current.visits += 1
            else:
                current.visits += 1
            current = current.parent

def calc_highest_visits(node):
    """Iterates through a nodes children to find the child that
    was visited the most.

    Parameters
        node: Node
            The parent node whose children will be interrogated.
    
    Returns
        node.children[index].game_state: nested lists
            The representation of the game board and where each
            player has moved.
    """
    index = 0
    highest_visits = node.children[index].visits
    for i in range(len(node.children)):
        if node.children[i].visits > highest_visits:
            index = i
            highest_visits = node.children[i].visits
    return node.children[index].game_state

def find_comp_move(game_state, comp_move_state):
    """Determines the row and column where the computer should
    move based on the difference in the current game state and
    the game state of the child node that was visited the most.

    Parameters
        game_state: nested lists
            The representation of the current game board and
            where each player has moved.
        comp_move_state: nested lists
            The representation of the game board and where
            the computer should move
        
    Returns
        x, y: ints
            The row and column of where the computer should 
            move on the game board
        -1, -1: ints
            The arbitrary numbers returned if there isn't a 
            difference between current game board and game
            board of child where the computer should move.
            This should not be reachable.
    """
    for x, row in enumerate(game_state):
        for y, col in enumerate(row):
            if game_state[x][y] != comp_move_state[x][y]:
                return x, y
            
    return -1, -1

def make_comp_move(state, num):
    """The procedure for making a computer move. Follows the classic
    Monte Carlo Tree Search process of Selection, Expansion, Simulation,
    and Back-propagation. The number of iterations to execute before
    making a computer move is set to 1000. 

    Parameters
        state: nested lists
            The representation of the game board and where each player
            has moved.
        num: int
            The player number of the human competitor.

    Returns
        comp_row, comp_col: ints
            The row and column of where the computer should move
            on the game board.
    """
    root = Node(state, num)
    
    for num_iter in range(1000):
        current = traverse(root)
        if current.visits == 0 or current.is_end_state is True:
            rollout_result = rollout(current.game_state, current.player)
            back_propagate(current, rollout_result)
        else:
            expand(current)
            child = current.children[0]
            rollout_result = rollout(child.game_state, child.player)
            back_propagate(child, rollout_result)

    comp_move_state = calc_highest_visits(root)
    comp_row, comp_col = find_comp_move(root.game_state, comp_move_state)
    del root
    return comp_row, comp_col

class TicTacToe:
    """A new TicTacToe game. This will be created once human competitor
    chooses which player they want to be.

    Attributes
        game_board: representation of the game board and where each
        player has moved
        user_num: the player number of the human competitor
        comp_piece: the player number of the computer competitor

    Methods
        __init__
        print_game_board
        check_for_legality
        make_player_move
    """
    def __init__(self, user_piece, comp_piece):
        """Initialize the attributes of a new TicTacToe game.

        Parameters
            user_piece: int
                The player number of the human competitor.
            comp_piece: int
                The player number of the computer competitor.
        """
        self.game_board = [["X", "X", "X"], ["X", "X", "X"], ["X", "X", "X"]]
        self.user_num = user_piece
        self.comp_piece = comp_piece

    def print_game_board(self):
        """Prints a representation of the game board and where
        each player has moved.
        """
        i = 1
        print("\t1\t2\t3\n")
        for row in self.game_board:
            print(f"{i}\t", end = "")
            for item in row:
                print(f"{item}\t", end = "")
            print("\n")
            i += 1

    def check_for_legality(self, row, col):
        """Checks to see if a player move is legal according to 
        the rules of TicTacToe.

        Parameters
            row: int
                The row where the human player would like to move.
            col: int
                The column where the human player would like to move.

        Returns
            is_legal: boolean
                The truth value of whether a human move is legal or not.
        """
        is_legal = True
        if row not in [1, 2, 3]:
            is_legal = False
        if col not in [1, 2, 3]:
            is_legal = False
        if self.game_board[row - 1][col - 1] != "X":
            is_legal = False
        return is_legal

    def make_player_move(self, row, col):
        """Updates the game board to represent where the human
        player moved.

        Parameters
            row: int
                The row where the human player would like to move.
            col: int
                The column where the human player would like to move.
        """
        self.game_board[row - 1][col - 1] = self.user_num

# Begin script        
first_to_move = input("Enter 0 if you would like to go first, otherwise enter any other number: ")

if first_to_move == "0":
    print("You are Player 1. Your moves will be denoted by \"1\"")
    print("The computer is Player 2. Computer moves will be denoted by \"2\"")
    print("X's denote an empty cell")
    game = TicTacToe(1, 2)
else:
    print("You are Player 2. Your moves will be denoted by \"2\"")
    print("The computer is Player 1. Computer moves will be denoted by \"1\"")
    print("X's denote an empty cell")
    game = TicTacToe(2, 1)
    game_state = copy.deepcopy(game.game_board)
    comp_row, comp_col = make_comp_move(game_state, game.user_num)
    game.game_board[comp_row][comp_col] = game.comp_piece

game.print_game_board()

# Main game loop
while True:

    while True:
        user_row = int(input("Enter row number you would like to move to: "))
        user_col = int(input("Enter column number you would like to move to: "))
        
        if game.check_for_legality(user_row, user_col):
            game.make_player_move(user_row, user_col)
            break
        else:
            print("That is not a valid move")

    if check_for_win(game.game_board, game.user_num):
        game.print_game_board()
        print("Congrats, you have won!")
        break
    if check_for_draw(game.game_board):
        game.print_game_board()
        print("It's a draw! Try again.")
        break
    game_state = copy.deepcopy(game.game_board)
    player_num = copy.deepcopy(game.user_num)
    comp_row, comp_col = make_comp_move(game_state, player_num)
    game.game_board[comp_row][comp_col] = game.comp_piece

    game.print_game_board()

    if check_for_win(game.game_board, game.comp_piece):
        print("You lost to a computer! Sad day.")
        break
    if check_for_draw(game.game_board):
        print("It's a draw! Try again.")
        break

print("End of program")
