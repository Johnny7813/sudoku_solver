# -*- coding: utf-8 -*-

import copy


# cell represents one element in a sudoku
# this element has 9 possible values represented
# by this cell
class cell(set):
    default_cell = set(range(1,10))

    def __init__(self, val=0):
        # init set with one value only
        # or a complete default_cell
        if isinstance(val, int):
            if val <= 0:
                super().__init__(cell.default_cell)
            elif val <= 9:
                super().__init__()
                super().add(val)
        elif isinstance(val, list):
            super().__init__(val)
        elif isinstance(val, set):
            super().__init__(val)

    # return value if a single value is in the cell
    # or 0 otherwise
    def value(self):
        if len(self) == 1:
            return max(self)
        else:
            return 0

    # number of elements in the set
    def size(self):
        return len(self)

    # True if cell has only one element
    # otherwise false
    def isSolved(self):
        return len(self)==1

    # remove element from set, if the cell has
    # more then one element. Save removed element
    # return -1: error last element can't be removed
    # return  1: element not in cell
    # return  2: element successfully removed but cell not solved
    # return  3: element successfully removed and cell solved
    def remove(self, v):
        if v in self:
            if len(self) == 1:
                return -1  # error: last element can't be removed
            else:
                super().discard(v)
                if len(self)>1:
                    return 2  # element removed and cell NOT solved
                else:
                    return 3  # element removed and cell solved
        else:
            return 1  # element not in cell

    # remove element v from set
    # return True: element successfully removed
    # return False: element was not in set
    def discard(self, v):
        if v in self:
            super().discard(v)
            return True
        else:
            return False


    # return a deep copy of the cell useful for branching
    def copy(self):
        c = copy.deepcopy(self)
        return c

    # print cell to terminal
    def dump(self):
        print()
        text = f"Cell {self} +++ Cell Length = {len(self)}"
        if self.isSolved():
            text += f" +++  Cell Value = {self.value()}"

        print(text)


if __name__ == '__main__':
    A = cell()
    A.dump()
    A.remove(2)
    A.remove(2)
    A.remove(4)
    A.dump()


