//---------------------------------Spheral++----------------------------------//
// CollinsYieldStrength -- Implements a pressure dependent yield strength
// model appropriate for geological materials.
//
// Since this is solely a yield strength model it takes another StrengthModel
// as an argument to compute the shear modulus.  Perhaps at some point we should
// just split up the ideas of what provides shear modulus and yield strength?
// 
//    See Collins, Melosh, Ivanov, 2004 Appendix, MAPS
//
// Created by JMO, Thu Jan 14 16:40:21 PST 2016
//     Based on python implementation by Megan Syal and Cody Raskin
//----------------------------------------------------------------------------//
#ifndef __Spheral_FullyDamagedCollinsStrength_hh__
#define __Spheral_FullyDamagedCollinsStrength_hh__

#include "StrengthModel.hh"

namespace Spheral {

template<typename Dimension>
class FullyDamagedCollinsStrength: public StrengthModel<Dimension> {

public:
  //--------------------------- Public Interface ---------------------------//
  typedef typename Dimension::Scalar Scalar;

  // Constructors, destructor.
  FullyDamagedCollinsStrength(const StrengthModel<Dimension>& shearModulusModel,  // Used to compute the shear modulus
                  const double mui);                                   // von Mises plastic limit
  virtual ~FullyDamagedCollinsStrength();

  // Override the required generic interface.
  virtual bool providesSoundSpeed() const override { return mShearModulusModel.providesSoundSpeed(); }
  virtual void shearModulus(Field<Dimension, Scalar>& shearModulus,
                            const Field<Dimension, Scalar>& density,
                            const Field<Dimension, Scalar>& specificThermalEnergy,
                            const Field<Dimension, Scalar>& pressure) const override;

  virtual void yieldStrength(Field<Dimension, Scalar>& yieldStrength,
                             const Field<Dimension, Scalar>& density,
                             const Field<Dimension, Scalar>& specificThermalEnergy,
                             const Field<Dimension, Scalar>& pressure,
                             const Field<Dimension, Scalar>& plasticStrain,
                             const Field<Dimension, Scalar>& plasticStrainRate) const override;

  virtual void soundSpeed(Field<Dimension, Scalar>& soundSpeed,
                          const Field<Dimension, Scalar>& density,
                          const Field<Dimension, Scalar>& specificThermalEnergy,
                          const Field<Dimension, Scalar>& pressure,
                          const Field<Dimension, Scalar>& fluidSoundSpeed) const override;

  // Access the strength parameters.
  const StrengthModel<Dimension>& shearModulusModel() const;
  double mui() const;

private:
  //--------------------------- Private Interface ---------------------------//
  const StrengthModel<Dimension>& mShearModulusModel;
  double mmui;

  // No copying or assignment.
  FullyDamagedCollinsStrength(const FullyDamagedCollinsStrength&);
  FullyDamagedCollinsStrength& operator=(const FullyDamagedCollinsStrength&);
};

}

#else

// Forward declaration.
namespace Spheral {
  template<typename Dimension> class FullyDamagedCollinsStrength;
}

#endif

