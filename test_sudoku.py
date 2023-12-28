from sudoku import Sudoku, SudokuNode, is_unique

def test_is_unique_returns_true_if_unique():
    values = '003020600'
    assert is_unique(values)

def test_is_unique_returns_false_if_not_unique():
    values = '303020600'
    assert not is_unique(values)

def test_is_valid_returns_true_if_valid():
    node = SudokuNode(lines=[
        '003020600',
        '900305001',
        '001806400',
        '008102900',
        '700000008',
        '006708200',
        '002609500',
        '800203009',
        '005010300',
    ])
    assert node.is_valid()

def test_is_valid_returns_false_if_non_unique_row():
    node = SudokuNode(lines=[
        '303020600',
        '900305001',
        '001806400',
        '008102900',
        '700000008',
        '006708200',
        '002609500',
        '800203009',
        '005010300',
    ])
    assert not node.is_valid()

def test_is_valid_returns_false_if_non_unique_column():
    node = SudokuNode(lines=[
        '803020600',
        '900305001',
        '001806400',
        '008102900',
        '700000008',
        '006708200',
        '002609500',
        '800203009',
        '005010300',
    ])
    assert not node.is_valid()

def test_is_valid_returns_false_if_non_unique_block():
    node = SudokuNode(lines=[
        '903020600',
        '900305001',
        '001806400',
        '008102900',
        '700000008',
        '006708200',
        '002609500',
        '800203009',
        '005010300',
    ])
    assert not node.is_valid()

def test_find_adjacent_nodes():
    game = Sudoku(SudokuNode(lines=[
        '003020600',
        '900305001',
        '001806400',
        '008102900',
        '700000008',
        '006708200',
        '002609500',
        '800203009',
        '005010300',
    ]))

    nodes = game.find_adjacent_nodes()
    assert len(nodes) == 3

    first_values_of_adjacent_nodes = [node.lines[0][0] for node in nodes]
    assert '1' in first_values_of_adjacent_nodes
    assert '4' in first_values_of_adjacent_nodes
    assert '5' in first_values_of_adjacent_nodes
