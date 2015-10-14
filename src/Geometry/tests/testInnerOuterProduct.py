#ATS:test(SELF, label="Geometry inner/outer product unit tests")
# Unit tests for the inner & outer products.

import unittest
from math import *
from SpheralTestUtilities import fuzzyEqual

# What dimensions are we testing?
from spheralDimensions import spheralDimensions
dims = spheralDimensions()

from Spheral import *

# Create a global random number generator.
import random
rangen = random.Random()
ranrange = (-1.0, 1.0)

#===============================================================================
# Generate a random geometric type.
#===============================================================================
def fillRandom(Constructor):
    result = Constructor()
    ndim = Constructor.nDimensions
    nelem = Constructor.numElements
    for i in xrange(Constructor.numElements):
        result[i] = rangen.uniform(*ranrange)
    return result

#===============================================================================
# Test class for inner product.
#===============================================================================
class TestInnerProduct(unittest.TestCase):

    #---------------------------------------------------------------------------
    # scalar . value
    #---------------------------------------------------------------------------
    def testScalarDotThing(self):
        for typestring in ("Vector%id", "Tensor%id", "SymTensor%id", "ThirdRankTensor%id"):
            for dim in dims:
                type = eval(typestring % dim)
                x = rangen.uniform(*ranrange)
                y = fillRandom(type)
                result = innerProduct(x, y)
                answer = type()
                for i in xrange(type.numElements):
                    answer[i] = x*y[i]
                self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # value . scalar
    #---------------------------------------------------------------------------
    def testThingDotScalar(self):
        for typestring in ("Vector%id", "Tensor%id", "SymTensor%id", "ThirdRankTensor%id"):
            for dim in dims:
                type = eval(typestring % dim)
                x = rangen.uniform(*ranrange)
                y = fillRandom(type)
                result = innerProduct(y, x)
                answer = type()
                for i in xrange(type.numElements):
                    answer[i] = x*y[i]
                self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # vector . vector
    #---------------------------------------------------------------------------
    def testVectorDotVector(self):
        for dim in dims:
            type = eval("Vector%id" % dim)
            x = fillRandom(type)
            y = fillRandom(type)
            result = innerProduct(x, y)
            answer = 0.0
            for i in xrange(type.numElements):
                answer += x[i]*y[i]
            self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # tensor . vector
    #---------------------------------------------------------------------------
    def testTensorDotVector(self):
        for typestring in ("Tensor%id", "SymTensor%id"):
            for dim in dims:
                vtype = eval("Vector%id" % dim)
                ttype = eval(typestring % dim)
                x = fillRandom(ttype)
                y = fillRandom(vtype)
                result = innerProduct(x, y)
                answer = vtype()
                for i in xrange(vtype.nDimensions):
                    for j in xrange(vtype.nDimensions):
                        answer[i] += x(i,j)*y(j)
                self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    #  vector . tensor
    #---------------------------------------------------------------------------
    def testVectorDotTensor(self):
        for typestring in ("Tensor%id", "SymTensor%id"):
            for dim in dims:
                vtype = eval("Vector%id" % dim)
                ttype = eval(typestring % dim)
                x = fillRandom(vtype)
                y = fillRandom(ttype)
                result = innerProduct(x, y)
                answer = vtype()
                for i in xrange(vtype.nDimensions):
                    for j in xrange(vtype.nDimensions):
                        answer[i] += x(j)*y(j,i)
                self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # vector . tensor
    #---------------------------------------------------------------------------
    def testVectorDotTensor(self):
        for typestring in ("Tensor%id", "SymTensor%id"):
            for dim in dims:
                vtype = eval("Vector%id" % dim)
                ttype = eval(typestring % dim)
                x = fillRandom(vtype)
                y = fillRandom(ttype)
                result = innerProduct(x, y)
                answer = vtype()
                for i in xrange(vtype.nDimensions):
                    for j in xrange(vtype.nDimensions):
                        answer[j] += x(i)*y(i,j)
                self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # thirdranktensor . vector
    #---------------------------------------------------------------------------
    def testThirdRankTensorDotVector(self):
        for dim in dims:
            vtype = eval("Vector%id" % dim)
            trttype = eval("ThirdRankTensor%id" % dim)
            ttype = eval("Tensor%id" % dim)
            x = fillRandom(trttype)
            y = fillRandom(vtype)
            result = innerProduct(x, y)
            answer = ttype()
            for i in xrange(vtype.nDimensions):
                for j in xrange(vtype.nDimensions):
                    for k in xrange(vtype.nDimensions):
                        answer[dim*i + j] += x(i,j,k)*y(k)
            self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # vector . thirdranktensor
    #---------------------------------------------------------------------------
    def testVectorDotThirdRankTensor(self):
        for dim in dims:
            vtype = eval("Vector%id" % dim)
            trttype = eval("ThirdRankTensor%id" % dim)
            ttype = eval("Tensor%id" % dim)
            x = fillRandom(vtype)
            y = fillRandom(trttype)
            result = innerProduct(x, y)
            answer = ttype()
            for i in xrange(vtype.nDimensions):
                for j in xrange(vtype.nDimensions):
                    for k in xrange(vtype.nDimensions):
                        answer[dim*j + k] += x(i)*y(i,j,k)
            self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # tensor . tensor
    #---------------------------------------------------------------------------
    def testTensorDotTensor(self):
        for t1typestring in ("Tensor%id", "SymTensor%id"):
            for t2typestring in ("Tensor%id", "SymTensor%id"):
                for dim in dims:
                    atype = eval("Tensor%id" % dim)
                    t1type = eval(t1typestring % dim)
                    t2type = eval(t2typestring % dim)
                    x = fillRandom(t1type)
                    y = fillRandom(t2type)
                    result = innerProduct(x, y)
                    answer = atype()
                    for i in xrange(atype.nDimensions):
                        for j in xrange(atype.nDimensions):
                            for k in xrange(atype.nDimensions):
                                answer[dim*i + j] += x(i,k)*y(k,j)
                    self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # tensor . thirdranktensor
    #---------------------------------------------------------------------------
    def testTensorDotThirdRankTensor(self):
        for ttypestring in ("Tensor%id", "SymTensor%id"):
            for dim in dims:
                trttype = eval("ThirdRankTensor%id" % dim)
                ttype = eval(ttypestring % dim)
                x = fillRandom(trttype)
                y = fillRandom(ttype)
                result = innerProduct(x, y)
                answer = trttype()
                for i in xrange(ttype.nDimensions):
                    for j in xrange(ttype.nDimensions):
                        for k in xrange(ttype.nDimensions):
                            for m in xrange(ttype.nDimensions):
                                z = answer(i, j, k) + x(i, j, m)*y(m, k)
                                answer(i, j, k, z)
                self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # thirdranktensor . tensor
    #---------------------------------------------------------------------------
    def testThirdRankTensorDotTensor(self):
        for ttypestring in ("Tensor%id", "SymTensor%id"):
            for dim in dims:
                trttype = eval("ThirdRankTensor%id" % dim)
                ttype = eval(ttypestring % dim)
                x = fillRandom(ttype)
                y = fillRandom(trttype)
                result = innerProduct(x, y)
                answer = trttype()
                for i in xrange(ttype.nDimensions):
                    for j in xrange(ttype.nDimensions):
                        for k in xrange(ttype.nDimensions):
                            for m in xrange(ttype.nDimensions):
                                z = answer(i, j, k) + x(i, m)*y(m, j, k)
                                answer(i, j, k, z)
                self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # scalar x value
    #---------------------------------------------------------------------------
    def testScalarOuterThing(self):
        for typestring in ("Vector%id", "Tensor%id", "SymTensor%id", "ThirdRankTensor%id"):
            for dim in dims:
                type = eval(typestring % dim)
                x = rangen.uniform(*ranrange)
                y = fillRandom(type)
                result = outerProduct(x, y)
                answer = type()
                for i in xrange(type.numElements):
                    answer[i] = x*y[i]
                self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # value x scalar
    #---------------------------------------------------------------------------
    def testThingOuterScalar(self):
        for typestring in ("Vector%id", "Tensor%id", "SymTensor%id", "ThirdRankTensor%id"):
            for dim in dims:
                type = eval(typestring % dim)
                x = rangen.uniform(*ranrange)
                y = fillRandom(type)
                result = outerProduct(y, x)
                answer = type()
                for i in xrange(type.numElements):
                    answer[i] = x*y[i]
                self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # vector x vector
    #---------------------------------------------------------------------------
    def testVectorOuterVector(self):
        for dim in dims:
            type = eval("Vector%id" % dim)
            ttype = eval("Tensor%id" % dim)
            x = fillRandom(type)
            y = fillRandom(type)
            result = outerProduct(x, y)
            answer = ttype()
            for i in xrange(type.numElements):
                for j in xrange(type.numElements):
                    answer(i, j, x[i]*y[j])
            self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    # tensor x vector
    #---------------------------------------------------------------------------
    def testTensorOuterVector(self):
        for typestring in ("Tensor%id", "SymTensor%id"):
            for dim in dims:
                vtype = eval("Vector%id" % dim)
                ttype = eval(typestring % dim)
                trttype = eval("ThirdRankTensor%id" % dim)
                x = fillRandom(ttype)
                y = fillRandom(vtype)
                result = outerProduct(x, y)
                answer = trttype()
                for i in xrange(vtype.nDimensions):
                    for j in xrange(vtype.nDimensions):
                        for k in xrange(vtype.nDimensions):
                            answer(i, j, k, x(i,j)*y(k))
                self.failUnless(result == answer)
        return

    #---------------------------------------------------------------------------
    #  vector x tensor
    #---------------------------------------------------------------------------
    def testVectorOuterTensor(self):
        for typestring in ("Tensor%id", "SymTensor%id"):
            for dim in dims:
                vtype = eval("Vector%id" % dim)
                ttype = eval(typestring % dim)
                trttype = eval("ThirdRankTensor%id" % dim)
                x = fillRandom(vtype)
                y = fillRandom(ttype)
                result = outerProduct(x, y)
                answer = trttype()
                for i in xrange(vtype.nDimensions):
                    for j in xrange(vtype.nDimensions):
                        for k in xrange(vtype.nDimensions):
                            answer(i, j, k, x(i)*y(j,k))
                self.failUnless(result == answer)
        return

if __name__ == "__main__":
    unittest.main()
