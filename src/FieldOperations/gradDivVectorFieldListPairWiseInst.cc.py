text = """
//------------------------------------------------------------------------------
// Explicit instantiation.
//------------------------------------------------------------------------------
#include "FieldOperations/gradDivVectorFieldListPairWise.cc"
#include "Geometry/Dimension.hh"

namespace Spheral {

//============================== gradDivVectorFieldList() ==============================
template 
FieldList<Dim< %(ndim)s >, Dim< %(ndim)s >::Vector> 
gradDivVectorFieldListPairWise< Dim< %(ndim)s > >
(const FieldList<Dim< %(ndim)s >, Dim< %(ndim)s >::Vector>& fieldList,
 const FieldList<Dim< %(ndim)s >, Dim< %(ndim)s >::Vector>& position,
 const FieldList<Dim< %(ndim)s >, Dim< %(ndim)s >::Scalar>& weight,
 const FieldList<Dim< %(ndim)s >, Dim< %(ndim)s >::Scalar>& mass,
 const FieldList<Dim< %(ndim)s >, Dim< %(ndim)s >::Scalar>& density,
 const FieldList<Dim< %(ndim)s >, Dim< %(ndim)s >::SymTensor>& Hfield,
 const TableKernel< Dim< %(ndim)s > >& kernel);

}
"""
