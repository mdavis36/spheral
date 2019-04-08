"""
Spheral Damage module.

Provides the damage physics models and interface for Spheral.
"""

from PYB11Generator import *
from SpheralCommon import *
from spheralDimensions import *
dims = spheralDimensions()

from DamageModel import *
from TensorDamageModel import *
from JohnsonCookDamage import *

#-------------------------------------------------------------------------------
# Includes
#-------------------------------------------------------------------------------
PYB11includes += ['"NodeList/SolidNodeList.hh"',
                  '"Strength/SolidFieldNames.hh"',
                  '"Damage/DamageModel.hh"',
                  '"Damage/TensorDamageModel.hh"',
                  '"Damage/JohnsonCookDamage.hh"',
                  '"Damage/weibullFlawDistribution.hh"',
                  '"Damage/computeFragmentField.hh"',
                  '"FileIO/FileIO.hh"']

#-------------------------------------------------------------------------------
# Namespaces
#-------------------------------------------------------------------------------
PYB11namespaces = ["Spheral"]

#-------------------------------------------------------------------------------
# enums
#-------------------------------------------------------------------------------
TensorStrainAlgorithm = PYB11enum(("BenzAsphaugStrain", 
                                   "StrainHistory", 
                                   "MeloshRyanAsphaugStrain", 
                                   "PlasticStrain",
                                   "PseudoPlasticStrain"), export_values=True)
EffectiveDamageAlgorithm = PYB11enum(("CopyDamage",
                                      "MaxDamage",
                                      "SampledDamage"), export_values=True)
EffectiveFlawAlgorithm = PYB11enum(("FullSpectrumFlaws",
                                    "MinFlaw",
                                    "MaxFlaw",
                                    "InverseSumFlaws",
                                    "SampledFlaws"), export_values=True)

#-------------------------------------------------------------------------------
# Methods
#-------------------------------------------------------------------------------
@PYB11template("Dimension")
def weibullFlawDistributionBenzAsphaug(volume = "double",
                                       volumeStretchFactor = "const double",
                                       seed = "const unsigned",
                                       kWeibull = "const double",
                                       mWeibull = "const double",
                                       nodeList = "const FluidNodeList<%(Dimension)s>&",
                                       minFlawsPerNode = "const int",
                                       minTotalFlaws = "const int",
                                       mask = "const Field<%(Dimension)s, int>&"):
    "Implements the Benz-Asphaug algorithm, starting with a minimum based on the volume of the simulation."
    return "Field<%(Dimension)s, std::vector<double>>"

@PYB11template("Dimension")
def weibullFlawDistributionOwen(seed = "const unsigned",
                                kWeibull = "const double",
                                mWeibull = "const double",
                                nodeList = "const FluidNodeList<%(Dimension)s>&",
                                minFlawsPerNode = "const int",
                                volumeMultiplier = "const double",
                                mask = "const Field<%(Dimension)s, int>&"):
    """Implements the Owen algorithm, stochastically seeding flaws with a maximum
value per node chosen based on the volume of the node."""
    return "Field<%(Dimension)s, std::vector<double>>"

@PYB11template("Dimension")
def computeFragmentField(nodeList = "const NodeList<%(Dimension)s>&",
                         linkRadius = "const double",
                         damage = "const Field<%(Dimension)s, typename %(Dimension)s::SymTensor>&",
                         damageThreshold = "const double",
                         assignDustToFragments = "const bool"):
    """Flag the nodes commonly connected within the given H radius as distinct
fragments.  Result returned as an integer Field of fragement IDs."""
    return "Field<%(Dimension)s, int>"

#-------------------------------------------------------------------------------
# Instantiate our types
#-------------------------------------------------------------------------------
for ndim in dims:
    exec('''
DamageModel%(ndim)id = PYB11TemplateClass(DamageModel, template_parameters="%(Dimension)s")
TensorDamageModel%(ndim)id = PYB11TemplateClass(TensorDamageModel, template_parameters="%(Dimension)s")
JohnsonCookDamage%(ndim)id = PYB11TemplateClass(JohnsonCookDamage, template_parameters="%(Dimension)s")

weibullFlawDistributionBenzAsphaug%(ndim)id = PYB11TemplateFunction(weibullFlawDistributionBenzAsphaug, template_parameters="%(Dimension)s")
weibullFlawDistributionOwen%(ndim)id = PYB11TemplateFunction(weibullFlawDistributionOwen, template_parameters="%(Dimension)s")
computeFragmentField%(ndim)id = PYB11TemplateFunction(computeFragmentField, template_parameters="%(Dimension)s")
''' % {"ndim"      : ndim,
       "Dimension" : "Dim<" + str(ndim) + ">",
       "Vector"    : "Dim<" + str(ndim) + ">::Vector"})
