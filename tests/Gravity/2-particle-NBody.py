#-------------------------------------------------------------------------------
# Set up a pair of equal mass N-body points in a simple circular orbit of each
# other.
#-------------------------------------------------------------------------------
from Spheral3d import *
from SpheralTestUtilities import *
from SpheralGnuPlotUtilities import *
from NodeHistory import *
from SpheralVisitDump import dumpPhysicsState
from math import *

print "3-D N-Body Gravity test -- two particle problem"

#-------------------------------------------------------------------------------
# Generic problem parameters
#-------------------------------------------------------------------------------
commandLine(

    # Initial particle stuff
    r0 = 1.0,                      # (AU) Start stuff out at 1 AU from barycenter
    m0 = 1.0,                     # (earth masses) particle mass
    plummerLength = 1.0e-3,        # (AU) Plummer softening scale

    # Problem control
    numOrbits = 2,                 # How many orbits do we want to follow?

    # Output
    dataDir = "Two-Earth-Nbody",
    baseName = "2_particle_nbody",
    restoreCycle = None,
    restartStep = 100,
    numViz = 100,
    )

# Convert to MKS units.
AU = 149597870700.0  # m
Mearth = 5.9722e24   # kg
r0 *= AU
m0 *= Mearth
plummerLength *= AU

# Compute the velocity necessary for a circular orbit.
G = MKS().G
a = 2*r0
M = 2*m0
orbitTime = 2.0*pi*sqrt(a**3/(G*M))
v0 = 2.0*pi*r0/orbitTime

# Miscellaneous problem control parameters.
dt = orbitTime / 90
goalTime = orbitTime * numOrbits
dtMin, dtMax = 0.1*dt, 100.0*dt
dtGrowth = 2.0
maxSteps = None
statsStep = 10
smoothIters = 0
vizTime = goalTime / numViz

restartDir = os.path.join(dataDir, "restarts")
visitDir = os.path.join(dataDir, "visit")
restartBaseName = os.path.join(restartDir, baseName + "_restart")

#-------------------------------------------------------------------------------
# Check if the necessary output directories exist.  If not, create them.
#-------------------------------------------------------------------------------
import os, sys
if mpi.rank == 0:
    if not os.path.exists(restartDir):
        os.makedirs(restartDir)
    if not os.path.exists(visitDir):
        os.makedirs(visitDir)
mpi.barrier()

#-------------------------------------------------------------------------------
# For now we have set up a fluid node list, even though this is collisionless
# problem.  Fix at some point!
# In the meantime, set up the hydro objects this script isn't really going to
# need.
#-------------------------------------------------------------------------------
WT = TableKernel(BSplineKernel(), 1000)
eos = GammaLawGasCGS3d(gamma = 5.0/3.0, mu = 1.0)

#-------------------------------------------------------------------------------
# Make the NodeList, and set our initial properties.
#-------------------------------------------------------------------------------
nodes = makeFluidNodeList("nodes", eos,
                          numInternal = 2,
                          topGridCellSize = 100*r0)
mass = nodes.mass()
pos = nodes.positions()
vel = nodes.velocity()

mass[0] = m0
mass[1] = m0

pos[0] = Vector(-r0, 0.0, 0.0)
pos[1] = Vector( r0, 0.0, 0.0)

vel[0] = Vector(0.0, -v0, 0.0)
vel[1] = Vector(0.0,  v0, 0.0)

# These are fluid variables we shouldn't need.  Just set them to valid values.
H = nodes.Hfield()
rho = nodes.massDensity()
H[0] = r0*SymTensor.one
H[1] = r0*SymTensor.one
rho[0] = 1.0
rho[1] = 1.0

#-------------------------------------------------------------------------------
# DataBase
#-------------------------------------------------------------------------------
db = DataBase()
db.appendNodeList(nodes)

#-------------------------------------------------------------------------------
# Gimme gravity.
#-------------------------------------------------------------------------------
gravity = NBodyGravity(plummerSofteningLength = plummerLength,
                       maxDeltaVelocity = 1e-2*v0,
                       G = G)

#-------------------------------------------------------------------------------
# Construct a time integrator.
#-------------------------------------------------------------------------------
integrator = SynchronousRK2Integrator(db)
integrator.appendPhysicsPackage(gravity)
integrator.lastDt = 1e3    # seconds
if dtMin:
    integrator.dtMin = dtMin
if dtMax:
    integrator.dtMax = dtMax
integrator.dtGrowth = dtGrowth

#-------------------------------------------------------------------------------
# Build the problem controller to follow the problem evolution.
#-------------------------------------------------------------------------------
control = SpheralController(integrator, WT,
                            statsStep = statsStep,
                            restartStep = restartStep,
                            restartBaseName = restartBaseName,
                            vizBaseName = os.path.join(visitDir, baseName),
                            vizTime = vizTime,
                            vizMethod = dumpPhysicsState)

#-------------------------------------------------------------------------------
# Build a diagnostic to maintain the history of our points.
#-------------------------------------------------------------------------------
def sampleMethod(nodes, indices):
    m = nodes.mass()
    pos = nodes.positions()
    vel = nodes.velocity()
    assert nodes.numInternalNodes == 2
    return (m[0], pos[0].x, pos[0].y, pos[0].z, vel[0].x, vel[0].y, vel[0].z, 
            m[1], pos[1].x, pos[1].y, pos[1].z, vel[1].x, vel[1].y, vel[1].z)

sampleNodes = [0, 1]  # We're going to sample both of our nodes!
history = NodeHistory(nodes, sampleNodes, sampleMethod,
                      os.path.join(dataDir, "node_history.txt"))
control.appendPeriodicTimeWork(history.sample, vizTime)

#-------------------------------------------------------------------------------
# If we're restarting, read in the restart file.
#-------------------------------------------------------------------------------
if restoreCycle:
    control.loadRestartFile(restoreCycle)

#-------------------------------------------------------------------------------
# Advance to the end time.
#-------------------------------------------------------------------------------
control.advance(goalTime)

# Plot the final state.
x1 = [stuff[1]/AU for stuff in history.sampleHistory]
y1 = [stuff[2]/AU for stuff in history.sampleHistory]
x2 = [stuff[8]/AU for stuff in history.sampleHistory]
y2 = [stuff[9]/AU for stuff in history.sampleHistory]

import Gnuplot
gdata1 = Gnuplot.Data(x1, y1,
                      with_ = 'linespoints',
                      title = 'Particle 1')
gdata2 = Gnuplot.Data(x2, y2,
                      with_ = 'linespoints',
                      title = 'Particle 2')
plot = Gnuplot.Gnuplot()
plot.plot(gdata1)
plot.replot(gdata2)
plot('set size square; set xrange [-1.1:1.1]; set yrange [-1.1:1.1]')
plot.xlabel = 'x'
plot.ylabel = 'y'
plot.refresh()
