from abc import ABC, abstractmethod
from typing import Union, Literal, List, TypeVar, Generic, Set, Tuple
import time

SEARCH_TYPE = Union[Literal['dfs'], Literal['bfs']]

T = TypeVar("T")
ROW = Tuple[int, ...]
ROWS = Tuple[ROW, ...]

class Game(ABC, Generic[T]):
    @abstractmethod
    def is_complete(self) -> bool:
        pass

    @abstractmethod
    def find_adjacent_nodes(self, node: Union[T, None]) -> List[T]:
        pass

REGISTER_VALUES = {
    1: 0b1,
    2: 0b10,
    3: 0b100,
    4: 0b1000,
    5: 0b10000,
    6: 0b100000,
    7: 0b1000000,
    8: 0b10000000,
    9: 0b100000000,
}

def is_unique(values: ROW) -> bool:
    registers = 0

    for value in values:
        if value == 0:
            continue

        rv = REGISTER_VALUES[value]

        if rv & registers:
            return False
        
        registers |= rv

    return True

def generate_group_coords():
    result = []

    # rows and columns
    for y in range(9):
        row = []
        column = []

        for x in range(9):
            row.append((x, y))
            column.append((y, x))

        result.append(row)
        result.append(column)

    # blocks
    for x_block in range(3):
        for y_block in range(3):
            block = []

            for x in range(3):
                for y in range(3):
                    block.append((y_block * 3 + y, x_block * 3 + x))

            result.append(block)

    return result

SUDOKU_GROUP_COORDS = generate_group_coords()

class Sudoku(Game):
    def __init__(self, lines: ROWS):
        self.lines = lines

    def is_complete(self) -> bool:
        incomplete_lines = [line for line in self.lines if 0 in line]
        return len(incomplete_lines) == 0
    
    def find_next_zero(self):
        "Find the group with the least zeros and pick the next zero in that group"
        group_with_least_zeros = None
        values_with_least_zeros = None

        max_non_zero_count = 0

        for coords in SUDOKU_GROUP_COORDS:
            values = [self.lines[y][x] for x, y in coords]
            count_of_values_with_non_zero = len([x for x in values if x != 0])
            zero_count = len([x for x in values if x == 0])

            if zero_count and count_of_values_with_non_zero > max_non_zero_count:
                group_with_least_zeros = coords
                values_with_least_zeros = values
                max_non_zero_count = count_of_values_with_non_zero

        if not group_with_least_zeros or not values_with_least_zeros:
            raise Exception('couldn\'t find the group')

        next_zero_value_index = values_with_least_zeros.index(0)
        coord_with_next_zero = group_with_least_zeros[next_zero_value_index]
        return coord_with_next_zero

    def find_adjacent_nodes(self, node: Union["Sudoku", None] = None) -> List["Sudoku"]:
        next_zero = self.find_next_zero()

        if not next_zero:
            return []
        
        x, y = next_zero

        possible_adjacent_nodes: List["Sudoku"] = []

        for possible_digit in range(1, 10):
            possible_adjacent_node = self.clone()
            possible_adjacent_node.set(x, y, possible_digit)

            if possible_adjacent_node.is_valid():
                possible_adjacent_nodes.append(possible_adjacent_node)

        return possible_adjacent_nodes


    def clone(self):
        return Sudoku(lines=self.lines)
    
    def set(self, x: int, y: int, value: int):
        line = self.lines[y]
        new_line = tuple(line[:x] + tuple([value]) + line[x + 1:]) # type: ignore
        self.lines = tuple(self.lines[:y] + tuple([new_line]) + self.lines[y + 1:]) # type: ignore

    def is_valid(self):
        for coords in SUDOKU_GROUP_COORDS:
            values = [self.lines[y][x] for x, y in coords]
            if not is_unique(values):
                return False

        return True

    def __eq__(self, other): 
        if not isinstance(other, Sudoku):
            return NotImplemented

        return self.lines == other.lines
    
    def __hash__(self):
        return hash(self.lines)

class Walk:
    def __init__(self, current_node: T, search_type: SEARCH_TYPE='dfs'):
        self.current_node = current_node
        self.frontier: List[T] = []
        self.visited: Set[T] = set()
        self.search_type = search_type

    def advance(self):
        changes = []

        unvisited_adjacent_nodes = [node for node in self.current_node.find_adjacent_nodes(self.current_node) if node not in self.visited]
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

def lines_to_internal(lines: List[str]) -> ROWS:
    data: List[ROW] = []
    for line in lines:
        d = tuple([int(x) for x in line])
        data.append(d) # type: ignore
    return tuple(data) # type: ignore

def read_puzzles():
    buffer = []
    puzzle_name = None
    puzzles = {}

    def on_puzzle_complete():
        puzzles[puzzle_name] = lines_to_internal(buffer)

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

def format_lines(data):
    result = []

    for d in data:
        result.append(''.join([str(x) for x in d]))

    return result

def solve(game: Sudoku):
    walk = Walk(game, search_type='dfs')

    while walk.current_node is None or not walk.current_node.is_complete():
        # print(f'visited {len(walk.visited)} nodes')
        print('\n-----------\n')
        print('\n'.join(format_lines(walk.current_node.lines)))
        # else:
        #     print('gug')
        walk.advance()

    print('solved')
    return walk.current_node

if __name__ == '__main__':
    puzzles = read_puzzles()

    with open('solutions.txt', 'w') as fh:
        def debug(message):
            print(message)
            fh.write(f'{message}\n')
            fh.flush()

        for key, lines in puzzles.items():
            start_time = time.time()
            debug(f'\nPuzzle {key}\n')
            debug('\n'.join(format_lines(lines)) + '\n\n')
            game = Sudoku(lines)
            solution = solve(game)
            end_time = time.time()
            elapsed_seconds = int(end_time - start_time)
            debug(f'Solution in {elapsed_seconds} seconds:\n')
            debug('\n'.join(format_lines(solution.lines)) + '\n')
            # break
