#-------------------------------------------------------------------------------
# FullyDamagedCollinsStrength
#-------------------------------------------------------------------------------
from PYB11Generator import *
from StrengthModel import *
from StrengthModelAbstractMethods import *

@PYB11template("Dimension")
@PYB11module("SpheralSolidMaterial")
class FullyDamagedCollinsStrength(StrengthModel):
    """FullyDamagedCollinsStrength -- Implements a pressure dependent yield strength
model appropriate for fully damaged material with resistance to deviatoric stresses

   See Collins, Melosh, Ivanov, 2004 Appendix, MAPS"""

    PYB11typedefs = """
    typedef typename %(Dimension)s::Scalar Scalar;
    typedef Field<%(Dimension)s, Scalar> ScalarField;
"""

    #...........................................................................
    # Constructors
    def pyinit(self,
               shearModulusModel = "const StrengthModel<%(Dimension)s>&",
               mui = "const double"):
        """FullyDamagedCollinsStrength constructor

mui : Coefficient of internal friction"""

    #...........................................................................
    # Virtual methods
    @PYB11virtual
    @PYB11const
    def providesSoundSpeed(self):
        return "bool"

    @PYB11virtual
    @PYB11const
    def soundSpeed(self,
                   soundSpeed = "Field<%(Dimension)s, Scalar>&",
                   density = "const Field<%(Dimension)s, Scalar>&",
                   specificThermalEnergy = "const Field<%(Dimension)s, Scalar>&",
                   pressure = "const Field<%(Dimension)s, Scalar>&",
                   fluidSoundSpeed = "const Field<%(Dimension)s, Scalar>&"):
        return "void"

    #...........................................................................
    # Properties
    mui = PYB11property("double")

#-------------------------------------------------------------------------------
# Inject Strength interface
#-------------------------------------------------------------------------------
PYB11inject(StrengthModelAbstractMethods, FullyDamagedCollinsStrength, virtual=True, pure_virtual=False)
