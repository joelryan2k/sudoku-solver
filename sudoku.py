from abc import ABC, abstractmethod
from typing import Union, Literal, List, TypeVar, Generic, Set

SEARCH_TYPE = Union[Literal['dfs'], Literal['bfs']]

T = TypeVar("T")

class Game(ABC, Generic[T]):
    @abstractmethod
    def is_complete(self) -> bool:
        pass

    @abstractmethod
    def find_adjacent_nodes(self, node: Union[T, None]) -> List[T]:
        pass

def is_unique(values: str) -> bool:
    non_zero_values = [x for x in values if x != '0']
    unique_non_zero_values = set(non_zero_values)
    return len(non_zero_values) == len(unique_non_zero_values)

class SudokuNode:
    def __init__(self, lines: List[str]):
        self.lines = lines

    def clone(self):
        return SudokuNode(lines=[line for line in self.lines])
    
    def set(self, x, y, value):
        line = self.lines[y]
        self.lines[y] = line[:y] + str(value) + line[y + 1:]

    def is_valid(self):
        # test rows
        for values in self.lines:
            if not is_unique(values):
                return False

        # test columns
        for x in range(9):
            values = ''.join([line[x] for line in self.lines])
            if not is_unique(values):
                return False

        # test blocks
        for x_block in range(2):
            for y_block in range(2):
                values_list = []
                for x in range(2):
                    for y in range(2):
                        values_list.append(self.lines[y_block * 3 + y][x_block * 3 + x])
                        values = ''.join(values_list)
                        if not is_unique(values):
                            return False
                        
        return True

class Sudoku(Game[SudokuNode]):
    def __init__(self, initial_state: SudokuNode):
        self.state = initial_state

    def is_complete(self) -> bool:
        incomplete_lines = [line for line in self.state.lines if '0' in line]
        return len(incomplete_lines) == 0
    
    def find_next_zero(self):
        for y, line in enumerate(self.state.lines):
            if '0' in line:
                return line.index('0'), y

    def find_adjacent_nodes(self, node: Union[SudokuNode, None] = None) -> List[SudokuNode]:
        next_zero = self.find_next_zero()

        if not next_zero:
            return []
        
        x, y = next_zero

        possible_adjacent_nodes: List[SudokuNode] = []

        for possible_digit in range(1, 10):
            possible_adjacent_node = self.state.clone()
            possible_adjacent_node.set(x, y, possible_digit)

            if possible_adjacent_node.is_valid():
                possible_adjacent_nodes.append(possible_adjacent_node)

        return possible_adjacent_nodes

class Walk(Generic[T]):
    def __init__(self, game: Game, current_node: Union[T, None] = None, search_type: SEARCH_TYPE='dfs'):
        self.game = game
        self.current_node = current_node
        self.frontier: List[T] = []
        self.visited: Set[T] = set()
        self.search_type = search_type

    def advance(self):
        changes = []

        unvisited_adjacent_nodes = [node for node in self.game.find_adjacent_nodes(self.current_node) if node not in self.visited]
        self.frontier.extend(unvisited_adjacent_nodes)

        if self.current_node:
            self.visited.add(self.current_node)
            changes.append(self.current_node)

        if self.search_type == 'bfs':
            self.current_node = self.frontier.pop(0)
        elif self.search_type == 'dfs':
            self.current_node = self.frontier.pop()
        else:
            raise Exception('unknown search type')

        if self.current_node is None:
            raise Exception('out of nodes :(')
        
        changes.append(self.current_node)

        return changes

def read_puzzles():
    buffer = []
    puzzle_name = None
    puzzles = {}

    def on_puzzle_complete():
        puzzles[puzzle_name] = buffer

    with open('sudoku.txt', 'r') as fh:
        for line in fh.readlines():
            if line.startswith('Grid'):
                if len(buffer):
                    on_puzzle_complete()

                buffer = []
                puzzle_name = line.split(' ')[1].rstrip('\n')
            else:
                buffer.append(line.rstrip('\n'))

    on_puzzle_complete()

    return puzzles

def solve(game: Sudoku):
    walk = Walk(game, search_type='dfs')

    while not game.is_complete():
        print('\n-----------\n')
        print('\n'.join(game.state.lines))
        walk.advance()

    print('solved')

if __name__ == '__main__':
    puzzles = read_puzzles()
    game = Sudoku(SudokuNode(puzzles['01']))
    solve(game)
