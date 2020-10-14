//---------------------------------Spheral++------------------------------------
// Compute the SPH mass density summation.
//------------------------------------------------------------------------------
#ifndef __Spheral__computeSPHSumMassDensity_FSI__
#define __Spheral__computeSPHSumMassDensity_FSI__

namespace Spheral {

  // Forward declarations.
  template<typename Dimension> class ConnectivityMap;
  template<typename Dimension> class TableKernel;
  template<typename Dimension, typename DataType> class FieldList;

  template<typename Dimension>
  void
  computeSPHSumMassDensity_FSI(const ConnectivityMap<Dimension>& connectivityMap,
                           const TableKernel<Dimension>& W,
                           const bool sumOverAllNodeLists,
                           const FieldList<Dimension, typename Dimension::Vector>& position,
                           const FieldList<Dimension, typename Dimension::Scalar>& mass,
                           const FieldList<Dimension, typename Dimension::SymTensor>& H,
                           FieldList<Dimension, typename Dimension::Scalar>& massDensity);

}

#endif
