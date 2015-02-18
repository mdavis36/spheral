//------------------------------------------------------------------------------
// Explicit instantiation.
//------------------------------------------------------------------------------
#include "Geometry/Dimension.hh"
#include "Boundary/Boundary.hh"
#include "computeHullSumMassDensity.cc"

namespace Spheral {
  namespace CRKSPHSpace {
    template void computeHullSumMassDensity(const ConnectivityMap<Dim<1> >&, 
                                            const TableKernel<Dim<1> >&,
                                            const FieldList<Dim<1>, Dim<1>::Vector>&,
                                            const FieldList<Dim<1>, Dim<1>::Scalar>&,
                                            const FieldList<Dim<1>, Dim<1>::SymTensor>&,
                                            FieldList<Dim<1>, Dim<1>::Scalar>&);
    template void computeHullSumMassDensity(const ConnectivityMap<Dim<2> >&, 
                                            const TableKernel<Dim<2> >&,
                                            const FieldList<Dim<2>, Dim<2>::Vector>&,
                                            const FieldList<Dim<2>, Dim<2>::Scalar>&,
                                            const FieldList<Dim<2>, Dim<2>::SymTensor>&,
                                            FieldList<Dim<2>, Dim<2>::Scalar>&);
    template void computeHullSumMassDensity(const ConnectivityMap<Dim<3> >&, 
                                            const TableKernel<Dim<3> >&,
                                            const FieldList<Dim<3>, Dim<3>::Vector>&,
                                            const FieldList<Dim<3>, Dim<3>::Scalar>&,
                                            const FieldList<Dim<3>, Dim<3>::SymTensor>&,
                                            FieldList<Dim<3>, Dim<3>::Scalar>&);
  }
}

