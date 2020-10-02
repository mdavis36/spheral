text = """
//------------------------------------------------------------------------------
// Explicit instantiation.
//------------------------------------------------------------------------------
#include "SolidMaterial/FullyDamagedCollinsStrength.cc"
#include "Geometry/Dimension.hh"

namespace Spheral {
  template class FullyDamagedCollinsStrength<Dim< %(ndim)s > >;
}
"""
