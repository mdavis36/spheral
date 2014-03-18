#include <math.h>

#include "Geometry/Dimension.hh"
#include "VolumeIntegrationFunctions.hh"
#include "Utilities/DBC.hh"

namespace Spheral {
namespace KernelSpace {

//------------------------------------------------------------------------------
// Construct with the given extent in eta.
//------------------------------------------------------------------------------
template<typename Dimension>
inline
SincKernel<Dimension>::SincKernel(const double extent):
  Kernel<Dimension, SincKernel<Dimension> >() {
  this->setKernelExtent(extent);
  this->setInflectionPoint(sqrt(0.5));
  this->setVolumeNormalization(1.0);
  double volumeIntegral = simpsonsVolumeIntegral<Dimension, SincKernel<Dimension> >(*this, 0.0, this->kernelExtent(), 10000);
  CHECK(volumeIntegral > 0.0);
  this->setVolumeNormalization(1.0/volumeIntegral);
}

//------------------------------------------------------------------------------
// Destructor
//------------------------------------------------------------------------------
template<typename Dimension>
inline
SincKernel<Dimension>::~SincKernel() {
}

//------------------------------------------------------------------------------
// Return the kernel weight for a given normalized distance.
//------------------------------------------------------------------------------
template<typename Dimension>
inline
double
SincKernel<Dimension>::kernelValue(double etaMagnitude, double Hdet) const {
  CHECK(etaMagnitude >= 0.0);
  CHECK(Hdet >= 0.0);
  const double thpt = M_PI*etaMagnitude;
  const double ack = thpt/(thpt*thpt + 1e-30);
  return this->volumeNormalization()*Hdet*ack*sin(thpt);
}

//------------------------------------------------------------------------------
// Return the gradient value for a given normalized distance.
//------------------------------------------------------------------------------
template<typename Dimension>
inline
double
SincKernel<Dimension>::gradValue(double etaMagnitude, double Hdet) const {
  CHECK(etaMagnitude >= 0.0);
  CHECK(Hdet >= 0.0);
  const double thpt = M_PI*etaMagnitude;
  const double ack = thpt/(thpt*thpt + 1e-30);
  return M_PI*ack*(this->volumeNormalization()*Hdet*cos(thpt) - 
                   this->kernelValue(etaMagnitude, Hdet));
}

//------------------------------------------------------------------------------
// Return the second derivative value for a given normalized distance.
//------------------------------------------------------------------------------
template<typename Dimension>
inline
double
SincKernel<Dimension>::grad2Value(double etaMagnitude, double Hdet) const {
  CHECK(etaMagnitude >= 0.0);
  CHECK(Hdet >= 0.0);
  const double thpt = M_PI*etaMagnitude;
  const double ack = thpt/(thpt*thpt + 1e-30);
  return -M_PI*(M_PI*kernelValue(etaMagnitude, Hdet) +
                2.0*ack*gradValue(etaMagnitude, Hdet));
}

}
}
