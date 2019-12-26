solve sudoku puzzles in python

this is a project to solve sudoku puzzles at the moment is is totally command line based.

is is made up of only 2 classes: cell represents one cell of the sudoku. It is basically a set.
If the cell is unsolved it contains all values from 1 .. 9. Through elimination and other steps
values can be erased from it.
If the cell contains only 1 value, it is considered solved.

board represents a whole sudoku board with 9x9 cells. These cells are arrange in a 9x9 grid.
Use the function self.at(i,j) to retrieve a single cell. There are other functions to solve the board.

sudoku_data.csv contains a few sudoku puzzles for testing purposes. The sudokus are in csv format.
Each line is one row in a sudoku puzzle. A value of 0 means that the cell is not solved,
i.e. it contains all possible values 1,2,3,...,9.

at the moment use main in board.py to read in puzzles from sudoku_data.csv. Then solve them with
methods from the class board. At this stage we can only solve simple puzzles. I will implement
a branching algorithms next. With this algortithm we can try different values from an unsolved
cell with only a few (ideally 2) values. We try each value and see if the resulting boards can
be solved or if contradictions arise.