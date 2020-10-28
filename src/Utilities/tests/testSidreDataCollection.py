from math import *
import unittest
from Spheral1d import *
from SpheralTestUtilities import *

import sys

import random
g = random.Random()

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
n = 1000
eos = GammaLawGasCGS(5.0/3.0, 2.0)
WT = TableKernel(BSplineKernel(), 1000)

#-------------------------------------------------------------------------------
#  Helper method to convert a list to vector_of_int
#-------------------------------------------------------------------------------
def vector_from_list(l):
    n = len(l)
    try:
        result = vector_of_int(n)    # pybindgen
        for i in xrange(n):
            result[i] = l[i]
    except:
        result = vector_of_int(l)    # pybind11
    return result

#-------------------------------------------------------------------------------
# Define our unit test class.
#-------------------------------------------------------------------------------
class testSidreDataCollection(unittest.TestCase):

    #---------------------------------------------------------------------------
    # Constructor
    #---------------------------------------------------------------------------
    def setUp(self):
        self.nodes = makeFluidNodeList("test bed",
                                       eos,
                                       n)
        self.field = IntField("test field", self.nodes)
        self.SidreDataCollection = SidreDataCollection()
        for i in xrange(n):
            self.field[i] = i
        return

    #---------------------------------------------------------------------------
    # Destructor
    #---------------------------------------------------------------------------
    def tearDown(self):
        del self.field
        del self.nodes
        return

    #---------------------------------------------------------------------------
    # alloc_view (Field of int)
    #---------------------------------------------------------------------------
    def testAlloc_viewInt(self):
        answer = self.SidreDataCollection.alloc_view("IntSidreTest", self.field).getDataA(n)
        # for i in self.field:
        #     print(self.field[i]),
        # print(id(self.field))
        # print '[%s]' % ', '.join(map(str, answer))
        # print(answer[0])
        # for i in xrange(n):
        #     print(answer[i]),
        # self.SidreDataCollection.printDataStore()
        assert sys.getsizeof(self.field[0]) == sys.getsizeof(answer[0])
        assert len(self.field) == len(answer)
        for i in xrange(n):
            assert self.field[i] == answer[i]
        return



#-------------------------------------------------------------------------------
# Run the test
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()