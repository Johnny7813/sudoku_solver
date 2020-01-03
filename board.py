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

class modelBoard(object):
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



    # make a copy of the board and save it
    # these states are saved in a heap. First in, last out
    def saveState(self):
        board_list_copy = copy.deepcopy(self.board_list)
        unexploited_cells_copy = copy.deepcopy(self.unexploited_cells)

        self.saved_states.append((board_list_copy, unexploited_cells_copy, self.unsolved_num))
        return True

    # restore the last saved state. This is a heap. Object is put into this last state
    # but this state is not removed from the heap
    def restoreState(self):
        if len(self.saved_states) == 0:
            return False

        tupel = self.saved_states[-1]
        self.board_list = tupel[0]
        self.unexploited_cells = tupel[1]
        self.unsolved_num = tupel[2]

        return True


    # removed last saved state if there is one
    # the state of the object does not change
    def removeState(self):
        if len(self.saved_states) == 0:
            return False

        self.saved_states.pop()
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
    # repeat == -1: stop if erasing is possible but don't do it
    # repeat == 0: stop after first value erased
    # repeat == 1: stop after first cell solved
    # repeat == 2: continue until throughout whole row
    # return -1: error, tried to remove value from a solved cell
    # return  0: nothing could be erased
    # return  1: erasing is possible, but has not been done
    # return  2: value(s) could be erased
    # return  3: cell(s) could be solved
    def eliminateFromUnit(self, val, indices, repeat=0):
        solved_cells  = [] #indices of cells that were solved
        reduced_cells = [] # indices of cells that could be reduced

        # loop over all cells for given indices
        for i,j in indices:
            mcell = self.at(i, j)
            if repeat == -1 and val in mcell:
                return (1, [], [])
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
                    return (3, reduced_cells, solved_cells)

            elif ret == 2:  # element was but cell not solved
                reduced_cells.append((i, j))
                if repeat == 0:
                    return (2, reduced_cells, solved_cells)
            elif ret == -1:  # error was encountered
                error_cell = (i,j)
                return (-1, reduced_cells, solved_cells, error_cell)

        retVal = 1
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
    # repeat == -1: stop if erasing is possible but don't do it
    # repeat == 0: stop after first value erased
    # repeat == 1: stop after first cell solved
    # repeat == 2: continue until throughout whole row
    # return -1: error, tried to remove value from a solved cell
    # return  0: nothing could be erased
    # return  1: it is possible to erase but it has not been done
    # return  2: value(s) have been erased
    # return  3: cell(s)  have been solved (and values erased
    def eliminateVal(self, r, c, repeat=0):
        solved_cells  = []
        reduced_cells = []

        # this variable is used in the following if statements
        # the higher comp, the harder it is to return prematurely
        # notice if repeat==2, then comp==3 and all if condition
        # are False
        comp = 2+repeat


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
    # return -1: error encountered, board not consistent
    # return 0: nothing could be erased and nothing solved
    # return 1: numbers could be erased but no cell solved
    # return 2: cells could be solved
    def eliminateAll(self):
        fret = 0  # return value of this function
        solved_cells  = []
        reduced_cells = []

        while self.unexploited_cells:
            i, j = sudoku.unexploited_cells.popleft()
            ret  = sudoku.eliminateVal(i, j, 2)

            if ret[0] == -1:
                return (-1, reduced_cells, solved_cells)  # error encountered

            reduced_cells.extend(ret[1])
            solved_cells.extend(ret[2])
            fret = max(ret[0], fret)  # fret set to max value of all returns

        return (fret, reduced_cells, solved_cells)


    #################### hidden singles functions ##########################
    ### reduce cells by eliminating values of solved cells from other
    ### cells on the same row, column or square

    # repeat==-1: is it possible to solve a cell, stop after first cell could be solved but don't change it
    # repeat==0: stop if a cell was solved
    # repeat==1: continue if a cell was solved
    # return (num, solved_indices) : num=number of solved cells, solved_indices= list of indices of solved cells
    def findHiddenSinglesInUnit(self, indices, repeat=1):
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
                solved_indices.append((i, j))

                # yes a cell can be solved, but don't change it
                if repeat == -1:
                    return (1, solved_indices)

                mcell = self.at(i, j)
                mcell.removeAllBut(val)
                self.unexploited_cells.append((i,j))
                self.unsolved_num -= 1


                if repeat == 0: # return findings of first solved cell
                    return (1,solved_indices)

                unsolved_indices.remove((i,j))
                #print("value: ", val, "## contained: ", contained)

        num = len(solved_indices)

        return (num, solved_indices)



    # find all hidden singles in Row r
    def findHiddenSinglesInRow(self, r, repeat=2):
        indices = self._row_indices(r,1,False)
        return self.findHiddenSinglesInUnit(indices, repeat)

    # find all hidden singles in Column c
    def findHiddenSinglesInCol(self, c, repeat=2):
        indices = self._col_indices(1,c,False)
        return self.findHiddenSinglesInUnit(indices, repeat)

    # find all hidden singles in square n
    # see _square_indices_unique()  function
    def findHiddenSinglesInSquare(self, n, repeat=2):
        indices = self._square_indices_unique(n)
        return self.findHiddenSinglesInUnit(indices, repeat)


    # find all hidden singles
    def findAllHiddenSingles(self, repeat=2):
        num = 0
        solved_indices = []
        for n in range(1,10):
            tmp, ind = self.findHiddenSinglesInRow(n, repeat)
            num += tmp
            solved_indices.extend(ind)
            if (not repeat) and num > 0:
                return (num, solved_indices)

            tmp, ind = self.findHiddenSinglesInCol(n, repeat)
            num += tmp
            solved_indices.extend(ind)
            if (not repeat) and num > 0:
                return (num, solved_indices)

            tmp, ind = self.findHiddenSinglesInSquare(n, repeat)
            num += tmp
            solved_indices.extend(ind)
            if (not repeat) and num > 0:
                return (num, solved_indices)

        # num = number of solved cells
        # solved_indices = all indices of solved cells
        return (num, solved_indices)


##################################################################


    # find first cell with the least entries
    # return number of elements in the cell and it's index
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

###################################################################################
###############
    # mode==0: find pair, if possible
    # mode==1: remove values
    # return 0 no pair found
    # return 1 pair found
    # return 2 pair found, values removed
    def findNakedPairInUnit(self, indices, mode=1):
        chosen = []
        for i,j in indices:
            mcell = self.at(i,j)
            if mcell.size() == 2:
                chosen.append((i,j))

        if len(chosen) <= 1:
            return (0, [])

        found = []
        while len(chosen) >= 2:
            (i,j) = chosen.pop()
            mcell = self.at(i,j)
            for k,l in chosen:
                if mcell == self.at(k,l):
                    print("Found a naked pair")
                    found = [(i,j), (k,l)]

        if len(found) == 0:
            return (0, [])
        elif mode == 0:
            return (1, found)

        values = set(self.at(*found[0]))

        for i,j in indices:
            if (i,j) in found:
                continue
            mcell  = self.at(i,j)
            mcell -= values

        return (2, found)


    # mode==0: find pair, if possible
    # mode==1: remove values
    # return 0 no pair found
    # return 1 pair found
    # return 2 pair found, values removed
    def findNakedPairInRow(self, row, mode=1):
        indices = self._row_indices(row, 1, False)
        return  self.findNakedPairInUnit(indices, mode)

    # mode==0: find pair, if possible
    # mode==1: remove values
    # return 0 no pair found
    # return 1 pair found
    # return 2 pair found, values removed
    def findNakedPairInCol(self, col, mode=1):
        indices = self._col_indices(1, col, False)
        return  self.findNakedPairInUnit(indices, mode)

    # mode==0: find pair, if possible
    # mode==1: remove values
    # return 0 no pair found
    # return 1 pair found
    # return 2 pair found, values removed
    def findNakedPairInSquare(self, num, mode=1):
        indices = self._square_indices_unique(num)
        return  self.findNakedPairInUnit(indices, mode)









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
    # solve as much as possible using only elimination and
    # and hiddenSingles
    # return:  number of iterations till nothing more can be solved
    # return: -1  board not consistent
    def solve_logic(self):
        fret = 0
        ret  = self.eliminateAll()
        if ret[0] == -1: # error, board not consistent
            return -1
        else:
            fret = ret[0]

        for i in range(1, 10):
            #print("iteration =", i)
            (num, solved_indices) = self.findAllHiddenSingles(repeat=True)

            if not self.is_all_consistent():  # board not consistent
                return -1

            #if num > 0:  # more has been solved, we can leave
             #   fret = 3

            ret = self.eliminateAll()
            if ret[0] == -1:  # error, board not consistent
                return -1

            if num == 0 and ret[0] == 0: # no cell has been solved, or eliminated
                return i

        #iterations maxed out, but stuff still changes
        return 1000




    # branch puzzle in the cell with cell_index
    def solve_branch(self, root_cell_index=None):
        if not root_cell_index:
            (num, ind)      = self.findLowestCell()
            root_cell_index = ind

        # make common changes and save
        # this save state is only used in this function
        self.unexploited_cells.append(root_cell_index)
        self.unsolved_num -= 1
        self.saveState()

        # root_cell: this is where we branch. We just try both values
        # and see which leads to a consistent puzzle
        # candidates: the values of root_cell. In turn we remove each
        # value from root_cell.
        root_cell     = self.at(*root_cell_index)  # * unpacks roo_cell_index into 2 arguments
        candidates    = list(root_cell)
        first         = True
        #candidates.sort(reverse=True)
        print("\nsolve_branch with values =", candidates, " , at index =", root_cell_index)


        for v in candidates:
            print("try branch with value v =", v)
            print("recurstion depth =", len(self.saved_states))

            if not first:
                self.restoreState()
                root_cell = self.at(*root_cell_index)
            first = False

            root_cell.remove(v)

            # do an elimination step
            ret = self.solve_logic()

            if   ret == -1: # not consistent
                continue
            else:
                if self.unsolved_num == 0:  # puzzle completely solved
                    self.removeState()
                    return True
                else: # puzzle consistent, but not fully solved, we do another branch
                    self.dump3()
                    if self.solve_branch():
                        self.removeState()
                        return True

            #print("Do I ever get here?") # yes


        self.removeState()
        return False






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

    sudoku = modelBoard("sudoku_data.csv", "hard1")
    sudoku.findHiddenSinglesInCol(4, 0)
    sudoku.dump3()

    ret = sudoku.solve_logic()
    sudoku.dump3()
    print("sove_logic returns=", ret)
    if sudoku.unsolved_num > 0:
        ret = sudoku.solve_branch()


    sudoku.dump3()

