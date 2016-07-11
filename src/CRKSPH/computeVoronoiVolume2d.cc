//---------------------------------Spheral++------------------------------------
// Compute the volume per point based on the Voronoi tessellation.
//------------------------------------------------------------------------------
extern "C" {
#include "r3d/r2d.h"
}

#include "computeVoronoiVolume.hh"
#include "Field/Field.hh"
#include "Field/FieldList.hh"
#include "NodeList/NodeList.hh"
#include "Neighbor/ConnectivityMap.hh"
#include "Utilities/allReduce.hh"

namespace Spheral {
namespace CRKSPHSpace {

using namespace std;

using FieldSpace::Field;
using FieldSpace::FieldList;
using NodeSpace::NodeList;
using NeighborSpace::Neighbor;
using NeighborSpace::ConnectivityMap;

//------------------------------------------------------------------------------
// 2D
//------------------------------------------------------------------------------
void
computeVoronoiVolume(const FieldList<Dim<2>, Dim<2>::Vector>& position,
                     const ConnectivityMap<Dim<2> >& connectivityMap,
                     const Dim<2>::Scalar kernelExtent,
                     FieldList<Dim<2>, Dim<2>::Scalar>& vol) {

  const unsigned numGens = position.numNodes();
  const unsigned numNodeLists = position.size();
  const unsigned numGensGlobal = allReduce(numGens, MPI_SUM, Communicator::communicator());

  typedef Dim<2>::Scalar Scalar;
  typedef Dim<2>::Vector Vector;
  typedef Dim<2>::SymTensor SymTensor;
  typedef Dim<2>::FacetedVolume FacetedVolume;

  if (numGensGlobal > 0) {

    // Walk the points.
    for (unsigned nodeListi = 0; nodeListi != numNodeLists; ++nodeListi) {
      const unsigned n = vol[nodeListi]->numInternalElements();
      const Neighbor<Dim<2> >& neighbor = position[nodeListi]->nodeListPtr()->neighbor();
      for (unsigned i = 0; i != n; ++i) {
        const Vector& ri = position(nodeListi, i);
        const Vector extenti = neighbor.nodeExtent(i);

        // Grab this points neighbors and build all the planes.
        vector<r2d_plane> pairPlanes;
        const vector<vector<int> >& fullConnectivity = connectivityMap.connectivityForNode(nodeListi, i);
        for (unsigned nodeListj = 0; nodeListj != numNodeLists; ++nodeListj) {
          for (vector<int>::const_iterator jItr = fullConnectivity[nodeListj].begin();
               jItr != fullConnectivity[nodeListj].end();
               ++jItr) {
            const unsigned j = *jItr;
            const Vector& rj = position(nodeListj, j);

            // Build the half plane.
            const Vector nhat = (ri - rj).unitVector();
            pairPlanes.push_back(r2d_plane());
            pairPlanes.back().n.x = nhat.x();
            pairPlanes.back().n.y = nhat.y();
            pairPlanes.back().d = 0.5*(rj - ri).magnitude();
          }
        }

        // Start with a bounding box around the H tensor.
        r2d_poly celli;
        r2d_rvec2 bounds[2];
        bounds[0].x = -extenti.x(); bounds[0].y = -extenti.y();
        bounds[1].x =  extenti.x(); bounds[1].y =  extenti.y();
        r2d_init_box(&celli, bounds);
        CHECK2(r2d_is_good(&celli), "Bad polygon!");

        // Clip the local cell.
        r2d_clip(&celli, &pairPlanes[0], pairPlanes.size());

        // Extract the area.
        r2d_real voli[1];
        r2d_reduce(&celli, voli, 0);
        vol(nodeListi, i) = voli[0];
      }
    }
  }
}

}
}
