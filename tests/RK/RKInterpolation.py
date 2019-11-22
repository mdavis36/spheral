#-------------------------------------------------------------------------------
# Manufactured diffusion test
#-------------------------------------------------------------------------------
from Spheral import *
from SpheralTestUtilities import *
import os, shutil
import numpy as np
from matplotlib import pyplot as plt
title("Reproducing kernel test")

#-------------------------------------------------------------------------------
# Generic problem parameters
#-------------------------------------------------------------------------------
commandLine(
    # Spatial parameters
    dimension = 1,
    nx = 32,
    ny = 32,
    nz = 32,
    x0 = -2.0,
    x1 = 2.0,
    y0 = -2.0,
    y1 = 2.0,
    z0 = -2.0,
    z1 = 2.0,
    correctionOrder = LinearOrder,
    
    # Manufactured parameters
    funcType = "linear",
    
    # Interpolation kernel choice
    nPerh = 4.01,
    hminfrac = 1.e-3,
    hmaxfrac = 1.e3,
    
    # Material parameters
    rho0 = 2.5e-7,
    gamma = 5.0/3.0,
    mu = 1.0,

    # Data dir
    dataDirBase = "dumps-RKInterpolation"
)

if dimension == 1:
    from Spheral1d import *
elif dimension == 2:
    from Spheral2d import *
else:
    from Spheral3d import *

#-------------------------------------------------------------------------------
# Set up data
#-------------------------------------------------------------------------------

# Set limits
lims = [[x0, x1], [y0, y1], [z0, z1]]

# Get point spacing
units = MKS()
delta = [(x1-x0)/nx]
if dimension > 1:
    delta.append((y1 -y0)/ny)
if dimension > 2:
    delta.append((z1 - z0)/nz)
deltaMin = min(delta)
deltaMax = max(delta)
hmin = deltaMin * nPerh * hminfrac
hmax = deltaMax * nPerh * hmaxfrac

#-------------------------------------------------------------------------------
# Check if the necessary output directories exist.  If not, create them.
#-------------------------------------------------------------------------------
dataDir = os.path.join(dataDirBase,
                       "dim={}".format(dimension),
                       "nx={}".format(nx))
restartDir = os.path.join(dataDir, "restarts")
vizDir = os.path.join(dataDir, "viz")
restartBaseName = os.path.join(restartDir, "RKInterpolation")

import os, sys
if mpi.rank == 0:
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)
    if not os.path.exists(vizDir):
        os.makedirs(vizDir)
    if not os.path.exists(restartDir):
        os.makedirs(restartDir)
mpi.barrier()

#-------------------------------------------------------------------------------
# Material properties.
#-------------------------------------------------------------------------------
eos = GammaLawGas(gamma, mu, units)

#-------------------------------------------------------------------------------
# Interpolation kernels.
#-------------------------------------------------------------------------------
WT = TableKernel(WendlandC4Kernel(), 1000)
kernelExtent = WT.kernelExtent
output("WT")

#-------------------------------------------------------------------------------
# Make the NodeList.
#-------------------------------------------------------------------------------
nodes = makeFluidNodeList("nodes", eos, 
                          hmin = hmin,
                          hmax = hmax,
                          nPerh = nPerh,
                          kernelExtent = kernelExtent)
output("nodes")
output("nodes.hmin")
output("nodes.hmax")
output("nodes.nodesPerSmoothingScale")

#-------------------------------------------------------------------------------
# Construct a DataBase to hold our node list
#-------------------------------------------------------------------------------
dataBase = DataBase()
output("dataBase")
output("dataBase.appendNodeList(nodes)")
output("dataBase.numNodeLists")
output("dataBase.numFluidNodeLists")

#-------------------------------------------------------------------------------
# Seed the nodes
#-------------------------------------------------------------------------------
if dimension == 1:
    from DistributeNodes import distributeNodesInRange1d
    distributeNodesInRange1d([(nodes, nx, rho0, (x0, x1))],
                             nPerh = nPerh)
elif dimension == 2:
    from GenerateNodeDistribution2d import *
    generator = GenerateNodeDistribution2d(distributionType="lattice",
                                           nRadial = nx,
                                           nTheta = ny,
                                           xmin = (x0, y0),
                                           xmax = (x1, y1),
                                           rho = rho0,
                                           nNodePerh = nPerh)
    if mpi.procs > 1:
        from VoronoiDistributeNodes import distributeNodes2d
    else:
        from DistributeNodes import distributeNodes2d
    distributeNodes2d((nodes, generator))
else:
    from GenerateNodeDistribution3d import *
    generator = GenerateNodeDistribution3d(distributionType="lattice",
                                           n1 = nx,
                                           n2 = ny,
                                           n3 = nz,
                                           xmin = (x0, y0, z0),
                                           xmax = (x1, y1, z1),
                                           rho=rho0,
                                           nNodePerh = nPerh)
    if mpi.procs > 1:
        from VoronoiDistributeNodes import distributeNodes3d
    else:
        from DistributeNodes import distributeNodes3d
    distributeNodes3d((nodes, generator))
    
output("nodes.numNodes")
numLocal = nodes.numInternalNodes
output("numLocal")

dataBase.updateConnectivityMap(True)
connectivity = dataBase.connectivityMap()

#-------------------------------------------------------------------------------
# Build the RK object
#-------------------------------------------------------------------------------
rk = RKCorrections(dataBase = dataBase,
                   W = WT,
                   correctionOrder = correctionOrder,
                   volumeType = CRKMassOverDensity)
packages = [rk]

#-------------------------------------------------------------------------------
# Run the startup stuff 
#-------------------------------------------------------------------------------
integrator = CheapSynchronousRK2Integrator(dataBase)
for p in packages:
    integrator.appendPhysicsPackage(p)
control = SpheralController(integrator, WT)

#-------------------------------------------------------------------------------
# Step two times
#-------------------------------------------------------------------------------
control.step(2)

#-------------------------------------------------------------------------------
# Get interpolant
#-------------------------------------------------------------------------------

if funcType == "constant":
    def func(x):
        return 2.0
elif funcType == "linear":
    def func(x):
        return 4.0 * np.sum(x)
else:
    raise ValueError, "function type {} not found".format(funcType)

#-------------------------------------------------------------------------------
# Try interpolation
#-------------------------------------------------------------------------------
position = dataBase.fluidPosition
H = dataBase.fluidHfield
volume = rk.volume

A = rk.A
dA = rk.gradA
ddA = rk.hessA
B = rk.B
dB = rk.gradB
ddB = rk.hessB
C = rk.C
dC = rk.gradC
ddC = rk.hessC
D = rk.D
dD = rk.gradD
ddD = rk.hessD

b = Vector.zero
db = Tensor.zero
ddb = ThirdRankTensor.zero
c = Tensor.zero
dc = ThirdRankTensor.zero
ddc = FourthRankTensor.zero
d = ThirdRankTensor.zero
dd = FourthRankTensor.zero
ddd = FifthRankTensor.zero

dxij = Tensor.zero
dxij.Identity()

vals = np.zeros((nodes.numNodes, 2))
dvals = np.zeros((nodes.numNodes, dimension, 2))
ni = 0
nj = 0

for i in range(nodes.numNodes):
    xi = position(ni, i)
    a = A(ni, i)
    da = dA(ni, i)
    dda = ddA(ni, i)
    if correctionOrder >=LinearOrder:
        b = B(ni, i)
        db = dB(ni, i)
        ddb = ddB(ni, i)
        if correctionOrder >= QuadraticOrder:
            c = C(ni, i)
            dc = dC(ni, i)
            ddc = ddC(ni, i)
            if correctionOrder >= CubicOrder:
                d = D(ni, i)
                dd = dD(ni, i)
                ddd = ddD(ni, i)
    connectivityi = np.append(connectivity.connectivityForNode(ni, i), i)
    print(a, b)
    for j in connectivityi:
        xj = position(nj, j)
        fj = func(xj)
        xij = xi - xj
        Hij = H(nj, j)
        etaij = Hij * xij
        vj = volume(nj, j)
        w = evaluateRKKernel(WT, correctionOrder,
                             etaij, Hij, xij,
                             a, b, c, d)
        dw = evaluateRKGradient(WT, correctionOrder,
                                etaij, Hij, xij, dxij,
                                a, b, c, d,
                                da, db, dc, dd)
        ddw = evaluateRKHessian(WT, correctionOrder,
                                etaij, Hij, xij, dxij,
                                a, b, c, d,
                                da, db, dc, dd,
                                dda, ddb, ddc, ddd)
        vals[i,0] += w * fj * vj
        # dvals[i,0] += dw * fj * vj
    vals[i,1] = func(xi)
    # dvals[i,1] = dfunc(xi)

    
plt.plot(vals[:,0])
plt.plot(vals[:,1])
plt.show()
                     
    
