//---------------------------------Spheral++----------------------------------//
// State -- Accumulate and cart the state for a set of physics packages around.
//
// Created by JMO, Fri Aug 27 10:56:40 2004
//----------------------------------------------------------------------------//
#include <string>

#include "State.hh"
#include "StateBase.hh"
#include "StateDerivatives.hh"
#include "DataBase.hh"
#include "UpdatePolicyBase.hh"
#include "FieldUpdatePolicyBase.hh"
#include "Physics/Physics.hh"
#include "Field/Field.hh"
#include "Field/FieldList.hh"
#include "Geometry/Dimension.hh"

namespace Spheral {

using namespace std;
using namespace FieldSpace;
using PhysicsSpace::Physics;

namespace {
//------------------------------------------------------------------------------
// Helper to compare a set of state to a key.
// We assume that wildcards are only applied at the end of a Key!
//------------------------------------------------------------------------------
// template<typename Key, typename Iterator>
// bool keyPresent(const Key& key,
//                 const Key& wildcard,
//                 const Iterator setBegin,
//                 const Iterator setEnd) {
//   const size_t pos = key.find(wildcard);
//   if (pos == string::npos) {
//     Key fieldKey, nodeListKey;
//     Iterator itr = setBegin;
//     while (itr != setEnd) {
//       StateBase<Dim<1> >::splitFieldKey(*itr, fieldKey, nodeListKey);
//       if (fieldKey == key) return true;
//       ++itr;
//     }
//     return false;
//     //return (find(setBegin, setEnd, key) != setEnd);
//   } else {
//     const Key testKey = key.substr(0, pos);
//     Iterator itr = setBegin;
//     while (itr != setEnd) {
//       if (testKey == itr->substr(0, pos)) return true;
//       ++itr;
//     }
//     return false;
//   }
// }

// //------------------------------------------------------------------------------
// // Helper to compare a set of state to a key.
// // We assume that wildcards are only applied at the end of a Key!
// //------------------------------------------------------------------------------
// bool compareKeysByField(const std::string& a,
//                         const std::string& b) {
//   std::string af, bf, an, bn;
//   StateBase<Dim<1> >::splitFieldKey(a, af, an);
//   StateBase<Dim<1> >::splitFieldKey(b, bf, bn);
//   return af < bf;
// }

}

//------------------------------------------------------------------------------
// Default constructor.
//------------------------------------------------------------------------------
template<typename Dimension>
State<Dimension>::
State():
  StateBase<Dimension>(),
  mPolicyMap(),
  mTimeAdvanceOnly(false) {
}

//------------------------------------------------------------------------------
// Construct with the state for the given set of Physics packages.
//------------------------------------------------------------------------------
template<typename Dimension>
State<Dimension>::
State(DataBaseSpace::DataBase<Dimension>& dataBase,
      typename State<Dimension>::PackageList& physicsPackages):
  StateBase<Dimension>(),
  mPolicyMap(),
  mTimeAdvanceOnly(false) {
  // Iterate over the physics packages, and have them register their state.
  for (PackageIterator itr = physicsPackages.begin();
       itr != physicsPackages.end();
       ++itr) (*itr)->registerState(dataBase, *this);
}

//------------------------------------------------------------------------------
// Construct with the state for the given set of Physics packages.
//------------------------------------------------------------------------------
template<typename Dimension>
State<Dimension>::
State(DataBaseSpace::DataBase<Dimension>& dataBase,
      typename State<Dimension>::PackageIterator physicsPackageBegin,
      typename State<Dimension>::PackageIterator physicsPackageEnd):
  StateBase<Dimension>(),
  mPolicyMap(),
  mTimeAdvanceOnly(false) {
  // Iterate over the physics packages, and have them register their state.
  for (PackageIterator itr = physicsPackageBegin;
       itr != physicsPackageEnd;
       ++itr) (*itr)->registerState(dataBase, *this);
}

//------------------------------------------------------------------------------
// Copy constructor.
//------------------------------------------------------------------------------
template<typename Dimension>
State<Dimension>::
State(const State<Dimension>& rhs):
  StateBase<Dimension>(rhs),
  mPolicyMap(rhs.mPolicyMap),
  mTimeAdvanceOnly(rhs.mTimeAdvanceOnly) {
}

//------------------------------------------------------------------------------
// Destructor.
//------------------------------------------------------------------------------
template<typename Dimension>
State<Dimension>::
~State() {
}

//------------------------------------------------------------------------------
// Assignment.
//------------------------------------------------------------------------------
template<typename Dimension>
State<Dimension>&
State<Dimension>::
operator=(const State<Dimension>& rhs) {
  if (this != &rhs) {
    StateBase<Dimension>::operator=(rhs);
    mPolicyMap = rhs.mPolicyMap;
    mTimeAdvanceOnly = rhs.mTimeAdvanceOnly;
  }
  return *this;
}

//------------------------------------------------------------------------------
// operator==
//------------------------------------------------------------------------------
template<typename Dimension>
bool
State<Dimension>::
operator==(const StateBase<Dimension>& rhs) const {
  return StateBase<Dimension>::operator==(rhs);
}

//------------------------------------------------------------------------------
// Update the state with the given derivatives object, according to the per
// state field policies.
//------------------------------------------------------------------------------
template<typename Dimension>
void
State<Dimension>::
update(StateDerivatives<Dimension>& derivs,
       const double multiplier,
       const double t,
       const double dt) {

  // cerr << "################################################################################" << endl;

  // Prepare lists of the keys to be completed.
  vector<KeyType> fieldsToBeCompleted;
  map<KeyType, set<KeyType> > stateToBeCompleted;
  for (typename PolicyMapType::const_iterator itr = mPolicyMap.begin();
       itr != mPolicyMap.end();
       ++itr) {
    for (typename map<KeyType, PolicyPointer>::const_iterator pitr = itr->second.begin();
         pitr != itr->second.end();
         ++pitr) {
      stateToBeCompleted[itr->first].insert(pitr->first);
    }
  }
  for (typename map<KeyType, set<KeyType> >::const_iterator itr = stateToBeCompleted.begin();
       itr != stateToBeCompleted.end();
       ++itr) fieldsToBeCompleted.push_back(itr->first);
  CHECK(fieldsToBeCompleted.size() == stateToBeCompleted.size());

  // Iterate until all state has been updated.
  while (not stateToBeCompleted.empty()) {

    // Walk the remaining state to be completed.
    vector<KeyType> stateToRemove;
    for (typename map<KeyType, set<KeyType> >::iterator itr = stateToBeCompleted.begin();
         itr != stateToBeCompleted.end();
         ++itr) {
      const KeyType fieldKey = itr->first;
      const set<KeyType>& remainingKeys = stateToBeCompleted[fieldKey];

      // Walk the remaining individual keys for this fieldKey.
      for (typename set<KeyType>::const_iterator itr = remainingKeys.begin();
           itr != remainingKeys.end();
           ++itr) {
        const KeyType key = *itr;
        const PolicyPointer policyPtr = mPolicyMap[fieldKey][key];

        // Check if all the dependencies for this state have been satisfied yet.
        bool readyToUpdate = true;
        vector<KeyType> unmetDependencies;
        set_intersection(fieldsToBeCompleted.begin(), fieldsToBeCompleted.end(),
                         policyPtr->dependencies().begin(), policyPtr->dependencies().end(),
                         back_inserter(unmetDependencies));
        if (unmetDependencies.empty()) {

          // We also require that any FieldList policies fire before NodeList specific 
          // versions of the same Field names.
          KeyType fieldKey, nodeListKey;
          this->splitFieldKey(key, fieldKey, nodeListKey);
          bool fire = (nodeListKey == UpdatePolicyBase<Dimension>::wildcard());
          if (not fire) {
            const KeyType wildKey = this->buildFieldKey(fieldKey, UpdatePolicyBase<Dimension>::wildcard());
            fire = (find(remainingKeys.begin(), remainingKeys.end(), wildKey) == remainingKeys.end());
          }

          if (fire) {
            // cerr <<" --> Update " << key << endl;
            if (mTimeAdvanceOnly) {
              policyPtr->updateAsIncrement(key, *this, derivs, multiplier, t, dt);
            } else {
              policyPtr->update(key, *this, derivs, multiplier, t, dt);
            }

            // List this field as completed.
            stateToRemove.push_back(key);
          }
        }
      }
    }

    // Check that the some state has been updated on this iteration.  If not, then *somebody*
    // has specified a circular dependency tree!
    if (stateToRemove.empty()) {
      stringstream message;
      message << "State::update ERROR: someone has specified a circular state dependency.\n"
              << "Remaining State:\n";
      for (typename map<KeyType, set<KeyType> >::const_iterator itr = stateToBeCompleted.begin();
           itr != stateToBeCompleted.end();
           ++itr) message << "   " << itr->first << "\n";
      message << "State dependencies:\n";
      for (typename PolicyMapType::iterator itr = mPolicyMap.begin();
           itr != mPolicyMap.end();
           ++itr) {
        const KeyType fieldKey = itr->first;
        const map<KeyType, PolicyPointer>& keysAndPolicies = itr->second;
        for (typename map<KeyType, PolicyPointer>::const_iterator pitr = keysAndPolicies.begin();
             pitr != keysAndPolicies.end();
             ++pitr) {
          const KeyType key = pitr->first;
          const PolicyPointer policyPtr = pitr->second;
          message << key << " : ";
          for (typename vector<KeyType>::const_iterator depItr = policyPtr->dependencies().begin();
               depItr != policyPtr->dependencies().end();
               ++depItr) message << *depItr << " ";
          message << "\n";
        }
      }
      VERIFY2(not stateToRemove.empty(), message.str());
    }
    
    // Remove the completed state.
    for (typename vector<KeyType>::const_iterator keyItr = stateToRemove.begin();
         keyItr != stateToRemove.end();
         ++keyItr) {
      KeyType fieldKey, nodeListKey;
      this->splitFieldKey(*keyItr, fieldKey, nodeListKey);
      CHECK(stateToBeCompleted.find(fieldKey) != stateToBeCompleted.end());
      stateToBeCompleted[fieldKey].erase(*keyItr);
      if (stateToBeCompleted[fieldKey].empty()) stateToBeCompleted.erase(fieldKey);
    }
    fieldsToBeCompleted = vector<KeyType>();
    for (typename map<KeyType, set<KeyType> >::const_iterator itr = stateToBeCompleted.begin();
         itr != stateToBeCompleted.end();
         ++itr) fieldsToBeCompleted.push_back(itr->first);
    CHECK(fieldsToBeCompleted.size() == stateToBeCompleted.size());
  }
}

//------------------------------------------------------------------------------
// The set of keys for all registered policies.
//------------------------------------------------------------------------------
template<typename Dimension>
vector<typename State<Dimension>::KeyType>
State<Dimension>::
policyKeys() const {
  vector<KeyType> result;
  for (typename PolicyMapType::const_iterator itr = mPolicyMap.begin();
       itr != mPolicyMap.end();
       ++itr) result.push_back(itr->first);
  ENSURE(result.size() == mPolicyMap.size());
  return result;
}

}

