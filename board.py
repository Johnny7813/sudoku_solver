# -*- coding: utf-8 -*-

from cell import *
from collections import deque
from itertools import product
from termcolor import colored
import copy
import distutils.text_file



# llval is a list of rows (list). Every unspecified element in the
# sudoku is -1
# indeces are from 1..9 not rom 0..8

class board(object):
    def __init__(self, ival, ival2=None):
        self.parts = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        self.board_list = []  # a list of lists with cells as elements,
        # every list represents a row on the board starting from top

        # list of pairs (i,j) that describe solved cells, that
        # have not been used to delete elements from other cells
        self.unexploited_cells = deque([])
        # these cells represented by indices (i,j) have been processed already
        self.exploited_cells = deque([])
        self.saved_states = deque([])
        self.unsolved_num = 81  # number of unsolved cells

        if isinstance(ival, str):
            rows = self.initFromCSVFile(ival, ival2)
            self.initFrom2DList(rows)
        elif isinstance(ival, list):
            self.initFrom2DList(ival)

    def initFrom2DList(self, rows):
        for i, iRow in enumerate(rows):
            row = [cell(e) for e in iRow]
            for j, entry in enumerate(iRow):
                c = cell(entry)
                row.append(c)
                if c.value() > 0:
                    self.unexploited_cells.append((i + 1, j + 1))
                    self.unsolved_num -= 1

            self.board_list.append(row)

    # read data that defines a sudoku from
    # a csv file. Unsolved cells are 0
    # each data block is preceded by a line that starts with *
    # this line defines the name of the sudoku
    # lines with # prefix are ignored
    def initFromCSVFile(self, FilePath, name=None):
        textfile = distutils.text_file.TextFile(FilePath, lstrip_ws=True)
        file_lines = textfile.readlines()
        read   = False
        sudoku = []

        for line in file_lines:
            #print(line)
            if line[0] == '*':
                tmp = line[1:]
                sudoku_name = tmp.strip()
                if name == None:
                    if read: # we must have read already a previous sudoku data set
                        return sudoku
                    else:    # we start reading now
                        read = True
                        continue

                elif sudoku_name == name:
                    read = True
                    continue
                elif (sudoku_name != name) and (read): # we have read, time to return it
                    return sudoku


            if read:
                row = [int(v) for v in line.split(',')]
                sudoku.append(row)
                #print(row)

        return sudoku

    # return cell at position i,j in range from 1..9, 1..9
    # i is row and j is column
    def at(self, i, j):
        assert i>=1 or i<=9
        row = self.board_list[i-1]
        return row[j-1]


    # set cell at index (i,j) as solved cell
    # with value val
    def set(self, i, j, val):
        #print("set: Index=",(i,j), "## Value=",val)
        if (1 <= val) and (val <= 9):
            row        = self.board_list[i - 1]
            row[j - 1] = cell(val)
            return True
        else:
            return False


    # export board into a list of lists
    def export(self):
        eboard = []

        for i in range(9):
            nrow = []  # represents a row on the board
            orow = self.board_list[i]

            for j in range(9):
                ce = orow[j]
                nrow.append(ce.value())

            eboard.append(nrow)

        return eboard

    # make a copy of the board and save it
    # these states are saved in a heap. First in, last out
    def saveState(self):
        board_list_copy = copy.deepcopy(self.board_list)
        unexploited_cells_copy = copy.deepcopy(self.unexploited_cells)

        self.saved_states.append((board_list_copy, unexploited_cells_copy, self.unsolved_num))
        return True

    # restore the last saved state. This is a heap. The last state that was saved is returned
    def restoreState(self):
        if len(self.saved_states) == 0:
            return False

        tupel = self.saved_states.pop()
        self.board_list = tupel[0]
        self.unexploited_cells = tupel[1]
        self.unsolved_num = tupel[2]

        return True


############# index functions ####################################
## produce all indices in row, col, square that (r,c) is in

    def _row_indices(self,r,c, remove=False):
        # produce row indices for row r
        tmp = list(range(1, 10))
        indices = list(product([r], tmp))
        if remove: # remove (r,c) element from list
            indices.remove((r,c))
        #print("Main index ", (r,c), " ### Row indices ", indices)
        return indices

    def _col_indices(self,r,c, remove=False):
        # produce col indices for row r
        tmp = list(range(1, 10))
        indices = list(product(tmp, [c]))
        if remove: # remove (r,c) element from list
            indices.remove((r,c))
        #print("Main index ", (r, c), " ### Column indices ", indices)
        return indices

    def _square_indices(self,r,c, remove=False):
        # produce square index list without (r,c)
        row_part = (r - 1) // 3  # floored division to find part row
        col_part = (c - 1) // 3  # floored division to find part col
        # produce list without (r,c)
        indices = list(product(self.parts[row_part], self.parts[col_part]))
        if remove: # remove (r,c) element from list
            indices.remove((r, c))
        #print("Main index ", (r, c), " ### Square indices ", indices)
        return indices

    # every square is labelled uniquely from 1...9
    # this will go through the square by rom from left to right
    # return the corresponding indices
    def _square_indices_unique(self,n):
        row_part = (n - 1) // 3   # floored division to find part row
        col_part = (n - 1) % 3    # floored division to find part col

        # produce index list for square (row_part, col_part)
        indices = list(product(self.parts[row_part], self.parts[col_part]))
        return indices


#################### eliminate functions ###############################
### reduce cells by eliminating values of solved cells from other
### cells on the same row, column or square

    # base function for all eliminate functions
    # remove int val from all cells in indices
    # indices: list of index tupels (i,j)
    # val: int that is supposed to be removed from cells
    # repeat == 0: stop after first value erased
    # repeat == 1: stop after first cell solved
    # repeat == 2: continue until throughout whole row
    # return -1: error, tried to remove value from a solved cell
    # return  0: nothing could be erased
    # return  1: value(s) could be erased
    # return  2: cell(s) could be solved
    def eliminateFromUnit(self, val, indices, repeat=0):
        solved_cells  = [] #indices of cells that were solved
        reduced_cells = [] # indices of cells that could be reduced

        # loop over all cells for given indices
        for i,j in indices:
            ret = self.at(i, j).remove(val)
            if ret == 3:  # element was removed and cell solved

                # add index to list of unexploited cells
                # this can happen only once for a cell
                if not (i, j) in self.unexploited_cells:
                    # save index of new solved cell
                    self.unexploited_cells.append((i, j))
                    self.unsolved_num -= 1

                solved_cells.append((i, j))
                reduced_cells.append((i, j))

                if repeat <=1:
                    return (2, reduced_cells, solved_cells)

            elif ret == 2:  # element was but cell not solved
                reduced_cells.append((i, j))
                if repeat == 0:
                    return (1, reduced_cells, solved_cells)
            elif ret == -1:  # error was encountered
                error_cell = (i,j)
                return (-1, reduced_cells, solved_cells, error_cell)

        retVal = 0
        if reduced_cells: retVal += 1
        if solved_cells:  retVal += 1

        #print("return: ", retVal, "## reduced calls: ", reduced_cells, "## solved_cells: ", solved_cells)
        # return 2: cells solved, 1: elements could be removed
        # 0: nothing could be removed, -1: error encountered
        return (retVal, reduced_cells, solved_cells)


    # like eliminateFromUnit, but here Unit is going to
    # be a column. A value is obtained form reference cell (r,c)
    # indices are all other indices in row r
    # repeat value, like before, return value like before
    def eliminateFromCol(self, r, c, repeat=0):

        refVal = self.at(r, c).value()
        if refVal == 0:
            raise ValueError # cell not solved

        # produce column index list without (r,c)
        indices = self._col_indices(r,c, True)

        return self.eliminateFromUnit(refVal, indices, repeat)


        # like eliminateFromUnit, but here Unit is going to
        # be a row. A value is obtained form reference cell (r,c)
        # indices are all other indices i   n column c
        # repeat value, like before, return value like before
    def eliminateFromRow(self, r, c, repeat=0):

        refVal = self.at(r, c).value()
        if refVal == 0:
            raise ValueError  # cell not solved

        # produce row index list without (r,c)
        indices = self._row_indices(r, c, True)

        return self.eliminateFromUnit(refVal, indices, repeat)


        # like eliminateFromUnit, but here Unit is going to
        # be a sub square. A value is obtained form reference cell (r,c)
        # indices are all other indices in row r
        # repeat value, like before, return value like before
    def eliminateFromSquare(self, r, c, repeat=0):
        refVal = self.at(r, c).value()
        if refVal == 0:
            raise ValueError  # cell not solved

        # produce square index list without (r,c)
        indices = self._square_indices(r, c, True)

        return self.eliminateFromUnit(refVal, indices, repeat)

    # eliminate value from solved cell for index (r,c) from
    # all other cells in the same row, cell and square
    # repeat == 0: stop after first value erased
    # repeat == 1: stop after first cell solved
    # repeat == 2: continue until throughout whole row
    # return -1: error, tried to remove value from a solved cell
    # return  0: nothing could be erased
    # return  1: value(s) could be erased
    # return  2: cell(s) could be solved
    def eliminateVal(self, r, c, repeat=0):
        solved_cells  = []
        reduced_cells = []

        # this variable is used in the following if statements
        # the higher comp, the harder it is to return prematurely
        # notice if repeat==2, then comp==3 and all if condition
        # are False
        comp = 1+repeat


        ret1 = self.eliminateFromCol(r, c, repeat)
        reduced_cells.extend(ret1[1])
        solved_cells.extend(ret1[2])

        if ret1[0] == -1  or  ret1[0] >= comp:
            self.unexploited_cells.extend(solved_cells)
            return (ret1[0], reduced_cells, solved_cells)


        ret2 = self.eliminateFromRow(r, c, repeat)
        reduced_cells.extend(ret2[1])
        solved_cells.extend(ret2[2])

        if ret2[0] == -1  or  ret2[0] >= comp:
            self.unexploited_cells.extend(solved_cells)
            return (ret2[0], reduced_cells, solved_cells)


        ret3 = self.eliminateFromSquare(r, c, repeat)
        reduced_cells.extend(ret2[1])
        solved_cells.extend(ret2[2])

        if ret3[0] == -1 or ret3[0] >= comp:
            self.unexploited_cells.extend(solved_cells)
            return (ret3[0], reduced_cells, solved_cells)

        self.unexploited_cells.extend(solved_cells)

        retmax = max(ret1[0], ret2[0], ret3[0])
        return (retmax, reduced_cells, solved_cells)


    # erase all possible values, i.e. solve as far as possible
    # by elimination only
    def eliminateAll(self):
        while self.unexploited_cells:
            i, j = sudoku.unexploited_cells.popleft()
            ret  = sudoku.eliminateVal(i, j, 2)
            if ret == -1: return -1  # error encountered

        if self.unsolved_num == 0:
            return 2  # the board is completely solved
        else:
            return 1  # the board is partially solved

    def solve(self):
        pass
        ret = eraseAll()
        self.dump2()

        if ret == 2:
            return True
        elif ret == 1:
            pass
        pass


    #################### hidden singles functions ##########################
    ### reduce cells by eliminating values of solved cells from other
    ### cells on the same row, column or square

    # repeat==1: continue if a cell was solved
    # repeat==0: stop if a cell was solved
    # return n:  number of solved cells
    def findHiddenSinglesInUnit(self, indices, repeat=True):
        unsolved_values  = cell()  # candidates that are not fixed to a cell, this creates a full cell
        unsolved_indices = []      # indices of cells in the Unit that are not solved
        solved_indices   = []      # here we write the indices of all cells we could solve

        for i,j in indices:
            mcell = self.at(i,j)
            if mcell.isSolved():
                unsolved_values.discard(mcell.value())
            else:
                unsolved_indices.append((i,j))

        for val in unsolved_values:
            contained = []
            for i,j in unsolved_indices:
                mcell = self.at(i, j)
                if val in mcell:
                    contained.append((i, j))

            if len(contained) == 1:
                i,j = contained[0]
                self.set(i, j, val)
                self.unexploited_cells.append((i,j))
                self.unsolved_num -= 1
                solved_indices.append((i,j))

                if not repeat: # return findings of one solved cell
                    return (1,solved_indices)

                unsolved_indices.remove((i,j))
                #print("value: ", val, "## contained: ", contained)

        num = len(solved_indices)

        return (num, solved_indices)



    # find all hidden singles in Row r
    def findHiddenSinglesInRow(self, r, repeat=True):
        indices = self._row_indices(r,1,False)
        return self.findHiddenSinglesInUnit(indices, repeat)

    # find all hidden singles in Column c
    def findHiddenSinglesInCol(self, c, repeat=True):
        indices = self._col_indices(1,c,False)
        return self.findHiddenSinglesInUnit(indices, repeat)

    # find all hidden singles in square n
    # see _square_indices_unique()  function
    def findHiddenSinglesInSquare(self, n, repeat=True):
        indices = self._square_indices_unique(n)
        return self.findHiddenSinglesInUnit(indices, repeat)


    # find all hidden singles
    def findAllHiddenSingles(self, repeat=True):
        for n in range(1,10):
            self.findHiddenSinglesInRow(n, True)
            self.findHiddenSinglesInCol(n, True)
            self.findHiddenSinglesInSquare(n, True)


##################################################################


    # find first cell with the least entries
    # return number of elements and index
    def findLowestCell(self):
        val = 100
        ind = (10, 10)
        indices = product(range(1, 10), range(1, 10))

        for i, j in indices:
            c = self.at(i, j)
            l = c.size()

            if l == 1: continue

            if l < val:
                val = l
                ind = (i, j)

            if l == 2: break

        return (val, ind)

####################################################################################
######### test if the sukoku is consistent?

    # check if there are 2 solved cells
    # with the same number in unit defined
    # by the input indices
    def is_unit_consistent(self, indices):
        all_values = cell()  # initiated as full row

        # find all set of values which are not yet assigned in row
        for (i, j) in indices:
            v = self.at(i, j).value()
            if v > 0:
                # v is not in all values, it must have been taken out before
                # in the loop, which means that we have double values
                if all_values.remove(v) == 1:
                    return False  # value has been take out already

        return True

    # row goes from 1 to 9
    # test if the row is consistent (no double values)
    # returns False if unconsistent and True if ok
    def is_row_consistent(self, r):
        assert r >= 1 and r <= 9
        indices = self._row_indices(r, 1)
        return self.is_unit_consistent(indices)



    # col goes from 1 to 9
    # test if the col is consistent (no double values)
    # returns False if unconsistent and True if ok
    def is_col_consistent(self, c):
        assert c >= 1 and c <= 9
        indices = self._col_indices(1, c)
        return self.is_unit_consistent(indices)


    # n goes from 1 to 9, cycling through all squares
    # test if the col is consistent (no double values)
    # returns False if unconsistent and True if ok
    def is_square_consistent(self, n):
        assert n >= 1 and n <= 9
        indices = self._square_indices_unique(n)
        return self.is_unit_consistent(indices)


    # check the whole board, all rows, all columns and all squares
    def is_all_consistent(self):
        for i in range(1,10):
            if not self.is_row_consistent(i):
                return (False, "row", i)
            if not self.is_col_consistent(i):
                return (False, "column", i)
            if not self.is_square_consistent(i):
                return (False, "square", i)
        return (True, 0)

###################################################################

    def solve_branch(self,num, index):
        pass















    # print the whole board
    def dump(self, caption=None):
        if caption: print(caption)

        print("\n\n" + "-" * 33)
        for i in range(9):
            s = "|"
            row = self.board_list[i]
            for j in range(9):
                u = row[j]
                if u.value() > 0:
                    s += " {0:d} ".format(u.value())
                else:
                    s += " - "
                if (j + 1) % 3 == 0:    s += "| "
            print(s)
            if (i + 1) % 3 == 0:    print("-" * 33)
        print("\n\n")

    # print the whole board
    def dump2(self, index=(-1, -1)):
        print("-" * 33)
        for i in range(9):
            s = "|"
            row = self.board_list[i]
            for j in range(9):
                u = row[j]
                if (i + 1, j + 1) == index:
                    color = 'red'
                else:
                    color = 'white'
                if u.value() > 0:
                    s += colored(" {0} ".format(u.value()), color)
                else:
                    s += colored(" {0} ".format(u.size()), 'blue', attrs=['reverse'])
                if (j + 1) % 3 == 0:    s += "| "
            print(s)
            if (i + 1) % 3 == 0:    print("-" * 33)
        print("\n\n")


    # another dump function
    def dump3(self, caption=None):
        if caption: print(caption)
        print("Number of unsolved cells: ", self.unsolved_num)
        print("Unexploited cells: ", self.unexploited_cells)
        self.dump2()



if __name__ == '__main__':

    sudoku = board("sudoku_data.csv", "hard1")

    sudoku.dump3()
    sudoku.eliminateAll()

    sudoku.dump3()
    sudoku.findAllHiddenSingles()

    sudoku.dump3()
    sudoku.eliminateAll()

    sudoku.dump3()

    if sudoku.is_all_consistent():
        print("board is consistent")

    (val, ind) = sudoku.findLowestCell()
    #print("Value, Index: ", val, ind)

    mcell = sudoku.at(ind[0], ind[1])
    mcell.dump()
    mcell.remove(5)
    mcell.dump()
    sudoku.unsolved_num -= 1
    sudoku.unexploited_cells.append(ind)

    ret = sudoku.eliminateAll()
    sudoku.dump3()

    ret = sudoku.is_all_consistent()
    if ret[0]:
        print("board is consistent")
    else:
        print("board is NOT consistent, ", ret[1], ret[2])
