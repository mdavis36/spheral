//---------------------------------Spheral++----------------------------------//
// ConstantRVelocityBoundary -- A boundary condition to enforce a constant 
// radial velocity component on a given set of nodes.
//
// This boundary is very specialized -- it explicitly works on only one 
// NodeList.
//
// Created by JMO, Fri Aug  1 17:10:34 PDT 2008
//----------------------------------------------------------------------------//
#ifndef ConstantRVelocityBoundary_HH
#define ConstantRVelocityBoundary_HH

#include "ConstantVelocityBoundary.hh"

#include <vector>

namespace Spheral {

template<typename Dimension> class NodeList;
template<typename Dimension, typename DataType> class Field;
template<typename Dimension, typename DataType> class FieldList;
template<typename Dimension> class DataBase;
class FileIO;

template<typename Dimension>
class ConstantRVelocityBoundary: 
    public ConstantVelocityBoundary<Dimension> {

public:
  //--------------------------- Public Interface ---------------------------//
  typedef typename Dimension::Scalar Scalar;
  typedef typename Dimension::Vector Vector;
  typedef typename Dimension::Tensor Tensor;
  typedef typename Dimension::SymTensor SymTensor;
  typedef typename Dimension::ThirdRankTensor ThirdRankTensor;

  // Constructors and destructors.
  ConstantRVelocityBoundary(const NodeSpace::NodeList<Dimension>& nodeList,
                            const std::vector<int>& nodeIndicies);
  virtual ~ConstantRVelocityBoundary();

  //**********************************************************************
  // Override the vector enforceBoundary method.
  // Use the given NodeList's neighbor object to select the ghost nodes.
  virtual void enforceBoundary(FieldSpace::Field<Dimension, Vector>& field) const;

  //******************************************************************************
  // Restart methods.
  // Dump the objects state to the given file.
  virtual std::string label() const { return "ConstantRVelocityBoundary"; }
  virtual void dumpState(FileIOSpace::FileIO& file, const std::string& pathName) const;
  virtual void restoreState(const FileIOSpace::FileIO& file, const std::string& pathName);
  //******************************************************************************

protected:
  //--------------------------- Protected Interface ---------------------------//

private:
  //--------------------------- Private Interface ---------------------------//
  std::vector<Scalar> mRadialVelocity;
};

}

#else

// Forward declaration.
namespace Spheral {
  template<typename Dimension> class ConstantRVelocityBoundary;
}

#endif
