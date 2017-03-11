// Put Python includes first to avoid compile warnings about redefining _POSIX_C_SOURCE
#include "pybind11/pybind11.h"
#include "pybind11/stl_bind.h"
#include "pybind11/operators.h"

#include <vector>
#include <string>

#include "Boundary/Boundary.hh"
#include "Boundary/PlanarBoundary.hh"
#include "Boundary/ReflectingBoundary.hh"
#include "Boundary/RigidBoundary.hh"
#include "Boundary/PeriodicBoundary.hh"
#include "Boundary/ConstantVelocityBoundary.hh"
#include "Boundary/ConstantXVelocityBoundary.hh"
#include "Boundary/ConstantYVelocityBoundary.hh"
#include "Boundary/ConstantZVelocityBoundary.hh"
#include "Boundary/ConstantRVelocityBoundary.hh"
#include "Boundary/ConstantBoundary.hh"
#include "Boundary/SphericalBoundary.hh"
#include "Boundary/CylindricalBoundary.hh"
#include "Boundary/AxialSymmetryBoundary.hh"
#include "Boundary/AxisBoundaryRZ.hh"

#include "PyAbstractBoundary.hh"
#include "PyAbstractBoundaryMesh.hh"
#include "PyBoundary.hh"
#include "PyPlanarBoundary.hh"
#include "Pybind11Wraps/DataOutput/PyRestartMethods.hh"

namespace py = pybind11;
using namespace pybind11::literals;

using namespace Spheral::BoundarySpace;

//------------------------------------------------------------------------------
// 1D
//------------------------------------------------------------------------------
PYBIND11_MAKE_OPAQUE(std::vector<Boundary<Spheral::Dim<1>>*>);

//------------------------------------------------------------------------------
// 2D
//------------------------------------------------------------------------------
PYBIND11_MAKE_OPAQUE(std::vector<Boundary<Spheral::Dim<2>>*>);

//------------------------------------------------------------------------------
// 3D
//------------------------------------------------------------------------------
PYBIND11_MAKE_OPAQUE(std::vector<Boundary<Spheral::Dim<3>>*>);

namespace {  // anonymous

//------------------------------------------------------------------------------
// Common virtual methods of Boundary objects.
//------------------------------------------------------------------------------
template<typename Dimension, typename Obj, typename PB11Obj>
void virtualBoundaryBindings(py::module& m, const std::string suffix, PB11Obj& obj) {

  typedef typename Dimension::Scalar Scalar;
  typedef typename Dimension::Vector Vector;
  typedef typename Dimension::Tensor Tensor;
  typedef typename Dimension::SymTensor SymTensor;
  typedef typename Dimension::ThirdRankTensor ThirdRankTensor;
  typedef Spheral::GeomPlane<Dimension> Plane;

  obj

    // Methods
    .def("setAllGhostNodes", (void (Obj::*)(DataBase<Dimension>&)) &Obj::setAllGhostNodes, "dataBase"_a)
    .def("setAllViolationNodes", (void (Obj::*)(DataBase<Dimension>&)) &Obj::setAllViolationNodes, "dataBase"_a)
    .def("cullGhostNodes", (void (Obj::*)(const FieldList<Dimension, int>&, FieldList<Dimension, int>&, std::vector<int>&)) &Obj::cullGhostNodes, "flagSet"_a, "old2newIndexMap"_a, "numNodesRemoved"_a)
    .def("setGhostNodes", (void (Obj::*)(NodeList<Dimension>&)) &Obj::setGhostNodes, "nodeList"_a)
    .def("updateGhostNodes", (void (Obj::*)(NodeList<Dimension>&)) &Obj::updateGhostNodes)

    .def("applyGhostBoundary", (void (Obj::*)(Field<Dimension, int>&) const) &Obj::applyGhostBoundary, "field"_a)
    .def("applyGhostBoundary", (void (Obj::*)(Field<Dimension, Scalar>&) const) &Obj::applyGhostBoundary, "field"_a)
    .def("applyGhostBoundary", (void (Obj::*)(Field<Dimension, Vector>&) const) &Obj::applyGhostBoundary, "field"_a)
    .def("applyGhostBoundary", (void (Obj::*)(Field<Dimension, Tensor>&) const) &Obj::applyGhostBoundary, "field"_a)
    .def("applyGhostBoundary", (void (Obj::*)(Field<Dimension, SymTensor>&) const) &Obj::applyGhostBoundary, "field"_a)
    .def("applyGhostBoundary", (void (Obj::*)(Field<Dimension, ThirdRankTensor>&) const) &Obj::applyGhostBoundary, "field"_a)
    .def("applyGhostBoundary", (void (Obj::*)(Field<Dimension, std::vector<Scalar>>&) const) &Obj::applyGhostBoundary, "field"_a)

    .def("setViolationNodes", &Obj::setViolationNodes)
    .def("updateViolationNodes", &Obj::updateViolationNodes)

    .def("enforceBoundary", (void (Obj::*)(Field<Dimension, int>&) const) &Obj::enforceBoundary, "field"_a)
    .def("enforceBoundary", (void (Obj::*)(Field<Dimension, Scalar>&) const) &Obj::enforceBoundary, "field"_a)
    .def("enforceBoundary", (void (Obj::*)(Field<Dimension, Vector>&) const) &Obj::enforceBoundary, "field"_a)
    .def("enforceBoundary", (void (Obj::*)(Field<Dimension, Tensor>&) const) &Obj::enforceBoundary, "field"_a)
    .def("enforceBoundary", (void (Obj::*)(Field<Dimension, SymTensor>&) const) &Obj::enforceBoundary, "field"_a)
    .def("enforceBoundary", (void (Obj::*)(Field<Dimension, ThirdRankTensor>&) const) &Obj::enforceBoundary, "field"_a)

    .def("initializeProblemStartup", &Obj::initializeProblemStartup)
    .def("finalizeGhostBoundary", &Obj::finalizeGhostBoundary)
    .def("reset", &Obj::reset)
    .def("numGhostNodes", &Obj::numGhostNodes)
    .def("clip", &Obj::clip)

    .def("addNodeList", &Obj::addNodeList)
    ;
}

//------------------------------------------------------------------------------
// Per dimension bindings.
//------------------------------------------------------------------------------
template<typename Dimension>
void dimensionBindings(py::module& m, const std::string suffix) {

  typedef typename Dimension::Scalar Scalar;
  typedef typename Dimension::Vector Vector;
  typedef typename Dimension::Tensor Tensor;
  typedef typename Dimension::SymTensor SymTensor;
  typedef typename Dimension::ThirdRankTensor ThirdRankTensor;
  typedef Spheral::GeomPlane<Dimension> Plane;
  using Spheral::NodeSpace::NodeList;

  //............................................................................
  // Boundary
  typedef Boundary<Dimension> Bound;
  py::class_<Bound,
             PyAbstractBoundary<Dimension, Bound>,
             PyAbstractBoundaryMesh<Dimension, Bound>> boundaryPB11(m, ("Boundary" + suffix).c_str());
  virtualBoundaryBindings<Dimension, Bound>(m, suffix, boundaryPB11);
  boundaryPB11
    
    // Constructors
    .def(py::init<>())

    // Methods
    .def("boundaryNodeMap", &Bound::boundaryNodeMap)
    .def("haveNodeList", &Bound::haveNodeList)

    .def("controlNodes", &Bound::controlNodes, "nodeList"_a)
    .def("ghostNodes", &Bound::ghostNodes, "nodeList"_a)
    .def("violationNodes", &Bound::violationNodes, "nodeList"_a)

    .def("applyFieldListGhostBoundary", (void (Bound::*)(FieldList<Dimension, Scalar>&) const) &Bound::applyFieldListGhostBoundary, "fieldList"_a)
    .def("applyFieldListGhostBoundary", (void (Bound::*)(FieldList<Dimension, Vector>&) const) &Bound::applyFieldListGhostBoundary, "fieldList"_a)
    .def("applyFieldListGhostBoundary", (void (Bound::*)(FieldList<Dimension, Tensor>&) const) &Bound::applyFieldListGhostBoundary, "fieldList"_a)
    .def("applyFieldListGhostBoundary", (void (Bound::*)(FieldList<Dimension, SymTensor>&) const) &Bound::applyFieldListGhostBoundary, "fieldList"_a)

    .def("enforceFieldListBoundary", (void (Bound::*)(FieldList<Dimension, Scalar>&) const) &Bound::enforceFieldListBoundary, "fieldList"_a)
    .def("enforceFieldListBoundary", (void (Bound::*)(FieldList<Dimension, Vector>&) const) &Bound::enforceFieldListBoundary, "fieldList"_a)
    .def("enforceFieldListBoundary", (void (Bound::*)(FieldList<Dimension, Tensor>&) const) &Bound::enforceFieldListBoundary, "fieldList"_a)
    .def("enforceFieldListBoundary", (void (Bound::*)(FieldList<Dimension, SymTensor>&) const) &Bound::enforceFieldListBoundary, "fieldList"_a)

    .def("accessBoundaryNodes", (typename Bound::BoundaryNodes& (Bound::*)(NodeList<Dimension>&)) &Bound::accessBoundaryNodes, "nodeList"_a)

    .def("enforceBoundary", (void (Bound::*)(std::vector<int>&, const Mesh<Dimension>&) const) &Bound::enforceBoundary, "faceField"_a, "mesh"_a)
    .def("enforceBoundary", (void (Bound::*)(std::vector<Scalar>&, const Mesh<Dimension>&) const) &Bound::enforceBoundary, "faceField"_a, "mesh"_a)
    .def("enforceBoundary", (void (Bound::*)(std::vector<Vector>&, const Mesh<Dimension>&) const) &Bound::enforceBoundary, "faceField"_a, "mesh"_a)
    .def("enforceBoundary", (void (Bound::*)(std::vector<Tensor>&, const Mesh<Dimension>&) const) &Bound::enforceBoundary, "faceField"_a, "mesh"_a)
    .def("enforceBoundary", (void (Bound::*)(std::vector<SymTensor>&, const Mesh<Dimension>&) const) &Bound::enforceBoundary, "faceField"_a, "mesh"_a)
    .def("enforceBoundary", (void (Bound::*)(std::vector<ThirdRankTensor>&, const Mesh<Dimension>&) const) &Bound::enforceBoundary, "faceField"_a, "mesh"_a)

    .def("swapFaceValues", (void (Bound::*)(Field<Dimension, std::vector<Scalar>>&, const Mesh<Dimension>&) const) &Bound::swapFaceValues, "field"_a, "mesh"_a)
    .def("swapFaceValues", (void (Bound::*)(Field<Dimension, std::vector<Vector>>&, const Mesh<Dimension>&) const) &Bound::swapFaceValues, "field"_a, "mesh"_a)

    .def("meshGhostNodes", &Bound::meshGhostNodes)
    ;

  //............................................................................
  // Boundary::BoundaryNodes
  py::class_<typename Bound::BoundaryNodes>(m, ("BoundaryNodes" + suffix).c_str())
    .def_readwrite("controlNodes", &Bound::BoundaryNodes::controlNodes)
    .def_readwrite("ghostNodes", &Bound::BoundaryNodes::ghostNodes)
    .def_readwrite("violationNodes", &Bound::BoundaryNodes::violationNodes)
    ;

  //............................................................................
  // PlanarBoundary
  typedef PlanarBoundary<Dimension> PlanarB;
  py::class_<PlanarB,
             PyPlanarBoundary<Dimension, PyAbstractBoundary<Dimension, PlanarB>>,
             Spheral::PyRestartMethods<PlanarB>> pbPB11(m, ("PlanarBoundary" + suffix).c_str());
  // virtualBoundaryBindings<Dimension, Bound>(m, suffix, boundaryPB11);
  Spheral::restartMethodBindings<PlanarB>(m, pbPB11);
  pbPB11

    // Constructors
    .def(py::init<>())
    .def(py::init<const Plane&, const Plane&>(), "enterPlane"_a, "exitPlane"_a)
    .def("mapPosition", &PlanarB::mapPosition)
    .def("facesOnPlane", &PlanarB::facesOnPlane)

    // Virtual methods
    .def("setGhostNodes", (void (PlanarB::*)(NodeList<Dimension>&)) &PlanarB::setGhostNodes, "nodeList"_a)
    .def("updateGhostNodes", (void (PlanarB::*)(NodeList<Dimension>&)) &PlanarB::updateGhostNodes, "nodeList"_a)
    .def("setViolationNodes", (void (PlanarB::*)(NodeList<Dimension>&)) &PlanarB::setViolationNodes, "nodeList"_a)
    .def("updateViolationNodes", (void (PlanarB::*)(NodeList<Dimension>&)) &PlanarB::updateViolationNodes, "nodeList"_a)
    .def("setGhostNodes", (void (PlanarB::*)(NodeList<Dimension>&, const std::vector<int>&)) &PlanarB::setGhostNodes, "nodeList"_a, "presetControlNodes"_a)
    .def("clip", &PlanarB::clip)
    .def("valid", &PlanarB::valid)

    // Attributes
    .def_property("enterPlane", &PlanarB::enterPlane, &PlanarB::setEnterPlane)
    .def_property("exitPlane", &PlanarB::exitPlane, &PlanarB::setExitPlane)
    ;

  //............................................................................
  // ReflectingBoundary
  typedef ReflectingBoundary<Dimension> ReflectB;
  py::class_<ReflectB, PlanarB,
             PyBoundary<Dimension, PyAbstractBoundary<Dimension, ReflectB>>> rbPB11(m, ("ReflectingBoundary" + suffix).c_str());
  virtualBoundaryBindings<Dimension, ReflectB>(m, suffix, rbPB11);
  Spheral::restartMethodBindings<PlanarB>(m, rbPB11);
  rbPB11

    // Constructors
    .def(py::init<>())
    .def(py::init<const Plane&>(), "plane"_a)

    // Attributes
    .def_property_readonly("reflectOperator", &ReflectB::reflectOperator)
    ;

  //............................................................................
  // RigidBoundary
  typedef RigidBoundary<Dimension> RigidB;
  py::class_<RigidB, PlanarB,
             PyBoundary<Dimension, PyAbstractBoundary<Dimension, RigidB>>> rigidbPB11(m, ("RigidBoundary" + suffix).c_str());
  virtualBoundaryBindings<Dimension, RigidB>(m, suffix, rigidbPB11);
  Spheral::restartMethodBindings<RigidB>(m, rigidbPB11);
  rigidbPB11

    // Constructors
    .def(py::init<>())
    .def(py::init<const Plane&>(), "plane"_a)
    ;

  //............................................................................
  // The STL containers of Boundary objects.
  py::bind_vector<std::vector<Bound*>>(m, "vector_of_Boundary" + suffix);
}

} // anonymous

//------------------------------------------------------------------------------
// Make the module
//------------------------------------------------------------------------------
PYBIND11_PLUGIN(SpheralBoundary) {
  py::module m("SpheralBoundary", "Spheral Boundary module.");

  //............................................................................
  // Per dimension bindings.
#ifdef SPHERAL1D
  dimensionBindings<Spheral::Dim<1>>(m, "1d");
#endif
// #ifdef SPHERAL2D
//   dimensionBindings<Spheral::Dim<2>>(m, "2d");
// #endif
// #ifdef SPHERAL3D
//   dimensionBindings<Spheral::Dim<3>>(m, "3d");
// #endif

  return m.ptr();
}
