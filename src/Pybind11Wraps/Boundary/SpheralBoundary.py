"""
Spheral Boundary module.

Provides the Boundary base class and many boundary implementations.
"""

from PYB11Generator import *
from spheralDimensions import *
dims = spheralDimensions()

#-------------------------------------------------------------------------------
# Includes
#-------------------------------------------------------------------------------
includes = ['"Boundary/Boundary.hh"',
            '"Boundary/PlanarBoundary.hh"',
            '"Boundary/ReflectingBoundary.hh"',
            '"Boundary/RigidBoundary.hh"',
            '"Boundary/PeriodicBoundary.hh"',
            '"Boundary/ConstantVelocityBoundary.hh"',
            '"Boundary/ConstantXVelocityBoundary.hh"',
            '"Boundary/ConstantYVelocityBoundary.hh"',
            '"Boundary/ConstantZVelocityBoundary.hh"',
            '"Boundary/ConstantRVelocityBoundary.hh"',
            '"Boundary/ConstantBoundary.hh"',
            '"Boundary/SphericalBoundary.hh"',
            '"Boundary/CylindricalBoundary.hh"',
            '"Boundary/AxialSymmetryBoundary.hh"',
            '"Boundary/AxisBoundaryRZ.hh"',
            '"Boundary/CRKSPHVoidBoundary.hh"',
            '"Field/Field.hh"',
            '"Field/FieldList.hh"',
            '"FileIO/FileIO.hh"',
            '<vector>',
            '<string>']

#-------------------------------------------------------------------------------
# Namespaces
#-------------------------------------------------------------------------------
namespaces = ["Spheral"]

#-------------------------------------------------------------------------------
# Do our dimension dependent instantiations.
#-------------------------------------------------------------------------------
from Boundary import *
from PlanarBoundary import *
from ReflectingBoundary import *
from RigidBoundary import *
from PeriodicBoundary import *
from ConstantVelocityBoundary import *
from ConstantXVelocityBoundary import *
from ConstantYVelocityBoundary import *
from ConstantZVelocityBoundary import *
from ConstantRVelocityBoundary import *
from ConstantBoundary import *
from CRKSPHVoidBoundary import *

for ndim in dims:
    exec('''
Boundary%(ndim)id = PYB11TemplateClass(Boundary, template_parameters="Dim<%(ndim)i>")
PlanarBoundary%(ndim)id = PYB11TemplateClass(PlanarBoundary, template_parameters="Dim<%(ndim)i>")
ReflectingBoundary%(ndim)id = PYB11TemplateClass(ReflectingBoundary, template_parameters="Dim<%(ndim)i>")
RigidBoundary%(ndim)id = PYB11TemplateClass(RigidBoundary, template_parameters="Dim<%(ndim)i>")
PeriodicBoundary%(ndim)id = PYB11TemplateClass(PeriodicBoundary, template_parameters="Dim<%(ndim)i>")
ConstantVelocityBoundary%(ndim)id = PYB11TemplateClass(ConstantVelocityBoundary, template_parameters="Dim<%(ndim)i>")
ConstantXVelocityBoundary%(ndim)id = PYB11TemplateClass(ConstantXVelocityBoundary, template_parameters="Dim<%(ndim)i>")
ConstantBoundary%(ndim)id = PYB11TemplateClass(ConstantBoundary, template_parameters="Dim<%(ndim)i>")
CRKSPHVoidBoundary%(ndim)id = PYB11TemplateClass(CRKSPHVoidBoundary, template_parameters="Dim<%(ndim)i>")
''' % {"ndim" : ndim})

if 2 in dims:
    ConstantYVelocityBoundary2d = PYB11TemplateClass(ConstantYVelocityBoundary, template_parameters="Dim<2>")

if 3 in dims:
    ConstantYVelocityBoundary2d = PYB11TemplateClass(ConstantYVelocityBoundary, template_parameters="Dim<2>")
    ConstantYVelocityBoundary3d = PYB11TemplateClass(ConstantYVelocityBoundary, template_parameters="Dim<3>")
    ConstantZVelocityBoundary3d = PYB11TemplateClass(ConstantZVelocityBoundary, template_parameters="Dim<3>")
    from CylindricalBoundary import *
