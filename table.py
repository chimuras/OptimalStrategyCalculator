#!/usr/bin/python3
#
# table.py
#
# Implements a two-dimension table where all cells must be of same type
#

from collections.abc import Sized

class Table:
    #
    # Initializes an instance of Table class
    #
    # celltype: type of each cell in table
    # xlabels: labels of x-axis
    # ylables: labels of y-axis
    # unit: unit of each cell (printed as suffix)
    #
    def __init__(self, celltype, xlabels, ylabels, unit=""):
        if not isinstance(celltype, type):
            raise TypeError("celltype must be a type (e.g. str, float)")
        self.celltype = celltype
        self.xlabels = tuple(xlabels)
        self.ylabels = tuple(ylabels)
        self.unit = unit

        # TODO: finish me
        #set a dictionary with tuples for keys with default values of None
        self.tabledict = {}
        for i in self.ylabels:
            self.tabledict[i]={}
            for j in self.xlabels:
                # row, col = self._validate_key((i,j))
                # self.tabledict[row, col]=Non
                self.tabledict[i][j] = None
        return
    
    #
    # "private" member function to validate key
    #
    def _validate_key(self, key):
        if not isinstance(key, Sized):
            raise TypeError("key must be a sized container")
        if len(key) != 2:
            raise KeyError("key must have exactly two elements")
        # unpack key to row and column
        row, col = key    
        if row not in self.ylabels:
            raise KeyError("%s is not a valid y-label"%str(row))
        if col not in self.xlabels:
            raise KeyError("%s is not a valid x-label"%str(col))
        return row, col
        
    #
    # Overloads index operator for assigning to a cell
    #
    # key: key of the cell
    # value: value of the cell (must be of type 'celltype')
    #    
    def __setitem__(self, key, value):
        if not isinstance(value, self.celltype):
            raise TypeError("value must be of type %s"%(self.celltype.__name__))
        row, col = self._validate_key(key)
        
        # TODO: implement me
        self.tabledict[row][col] = value

    #
    # Overloads index operator for retrieving a value from a cell
    #
    # key: key of the cell
    #    
    def __getitem__(self, key):
        row, col = self._validate_key(key) 
        
        # TODO: implement me
        return self.tabledict[row][col]

    #
    # Overloads index operator for deleting a cell's value. You should
    # set the cell's value back to None
    #
    # key: key of the cell
    #  
    def __delitem__(self, key):
        row, col = self._validate_key(key) 
        
        # TODO: implement me
        self.tabledict[row][col] = None
    
            

