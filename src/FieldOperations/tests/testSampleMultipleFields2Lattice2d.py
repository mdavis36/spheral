#ATS:test(SELF,       label="sampleMultipleFields2Lattice 2D unit tests (serial)")
#ATS:test(SELF, np=4, label="sampleMultipleFields2Lattice 2D unit tests (4 proc)")

import unittest

from Spheral import *
from SpheralTestUtilities import fuzzyEqual
import mpi

from testSampleMultipleFields2Lattice import TestSampleMultipleFields2Lattice

#===============================================================================
# 2-D tests.
#===============================================================================
class TestSampleMultipleFields2Lattice2d(TestSampleMultipleFields2Lattice,
                                         unittest.TestCase):

    #---------------------------------------------------------------------------
    # Initialize the problem.
    #---------------------------------------------------------------------------
    def setUp(self):

        self.ndim = 2
        self.genxmin = (0.0, 0.0)
        self.genxmax = (1.0, 1.0)
        self.xmin = Vector2d(0.2, 0.2)
        self.xmax = Vector2d(0.8, 0.8)
        self.nsample = vector_of_int()
        [self.nsample.append(x) for x in (100, 100)]

        # Tolerances for the test
        self.scalarTol = 1.0e-2
        self.vectorTol = 1.0e-2
        self.tensorTol = 1.0e-2

        nx, ny = 50, 50
        self.rho0 = 10.0
        self.v0 = Vector2d(1.0, -1.0)
        self.eps0 = -1.0
        self.gradv0 = Tensor2d(8.5, -4.0,
                               2.2, 1.3)

        # Create the nodes and such.
        self.eos = GammaLawGasMKS2d(5.0/3.0, 1.0)
        self.WT = TableKernel2d(BSplineKernel2d())
        self.nodes = makeFluidNodeList2d("nodes", self.eos)

        # Distribute the nodes.
        from GenerateNodeDistribution2d import GenerateNodeDistribution2d
        from PeanoHilbertDistributeNodes import distributeNodes2d
        generator = GenerateNodeDistribution2d(nx, ny,
                                               self.rho0,
                                               "lattice",
                                               xmin = self.genxmin,
                                               xmax = self.genxmax,
                                               nNodePerh = 2.01)
        distributeNodes2d((self.nodes, generator))

        # Set the velocities and energies.
        self.nodes.velocity(VectorField2d("tmp", self.nodes, self.v0))
        self.nodes.specificThermalEnergy(ScalarField2d("tmp", self.nodes, self.eps0))

        self.db = DataBase2d()
        self.db.appendNodeList(self.nodes)

        # Create the boundary conditions.
        px0 = Plane2d(Vector2d(0.0, 0.0), Vector2d(1.0, 0.0))
        px1 = Plane2d(Vector2d(1.0, 0.0), Vector2d(-1.0, 0.0))
        py0 = Plane2d(Vector2d(0.0, 0.0), Vector2d(0.0, 1.0))
        py1 = Plane2d(Vector2d(0.0, 1.0), Vector2d(0.0, -1.0))
        xbc = PeriodicBoundary2d(px0, px1)
        ybc = PeriodicBoundary2d(py0, py1)
        self.bcs = [xbc, ybc]
        try:
            self.bcs.append(TreeDistributedBoundary2d.instance())
        except:
            if mpi.procs > 1:
                raise RuntimeError, "Unable to get parallel boundary condition"
            else:
                pass

        # Enforce boundaries.
        db = DataBase2d()
        db.appendNodeList(self.nodes)
        for bc in self.bcs:
            bc.setAllGhostNodes(db)
            bc.finalizeGhostBoundary()
            self.nodes.neighbor().updateNodes()
        for bc in self.bcs:
            bc.applyGhostBoundary(self.nodes.mass())
            bc.applyGhostBoundary(self.nodes.massDensity())
            bc.applyGhostBoundary(self.nodes.specificThermalEnergy())
            bc.applyGhostBoundary(self.nodes.velocity())
        for bc in self.bcs:
            bc.finalizeGhostBoundary()

        self.H0 = self.nodes.Hfield()[0]
        return

    def tearDown(self):
        del self.nodes

#===============================================================================
# Run the tests
#===============================================================================
if __name__ == "__main__":
    unittest.main()
