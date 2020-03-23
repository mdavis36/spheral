#-------------------------------------------------------------------------------
# Master cmake file for handling third party library installation via spack
#-------------------------------------------------------------------------------
include(ExternalProject)

#-------------------------------------------------------------------------------
# Set the basic paths
#-------------------------------------------------------------------------------
set(TPL_SRC_DIR ${PROJECT_SOURCE_DIR}/thirdPartyLibs)
set(CACHE_DIR ${PROJECT_SOURCE_DIR}/thirdPartyLibs/cache)

set(SPHERAL_TPL_DIR ${SPHERAL_INSTALL_DIR})
if(SPHERAL_TPL_DIR)
  if(NOT EXISTS SPHERAL_TPL_DIR)
    get_filename_component(SPHERAL_TPL_DIR_PARENT ${SPHERAL_TPL_DIR} DIRECTORY)
    if(NOT EXISTS "${SPHERAL_TPL_DIR_PARENT}/")
      set(SPHERAL_TPL_DIR ${PROJECT_SOURCE_DIR}/..)
      message(FATAL_ERROR "No Directory ${SPHERAL_TPL_DIR_PARENT}/")
    endif()
  endif()
else()
  set(SPHERAL_TPL_DIR ${PROJECT_SOURCE_DIR}/..)
endif()
set(SPHERAL_TPL_DIR ${SPHERAL_TPL_DIR}/tpl)
message(STATUS "TPL Install Dir at: ${SPHERAL_TPL_DIR}")

set(SPACK ${SPHERAL_TPL_DIR}/spack/bin/spack -k)

#-------------------------------------------------------------------------------
# Prepare spack in the TPL installation directory
#-------------------------------------------------------------------------------
if (INSTALL_TPLS AND NOT EXISTS ${SPHERAL_TPL_DIR}/spack)
  message("\n---------- BUILDING SPACK ----------")
  file(COPY ${TPL_SRC_DIR}/spack DESTINATION ${SPHERAL_TPL_DIR})

  # Gotta patch spack to allow longer timeouts when downloading packages
  execute_process(COMMAND patch -t ${SPHERAL_TPL_DIR}/spack/lib/spack/spack/fetch_strategy.py ${TPL_SRC_DIR}/spack_fetch_strategy_0.14.0.patch)

  # Tell spack to use our local mirror of cached packages if available
  message("EXECUTING ${SPACK} mirror add local_spheral_cache file://${CACHE_DIR}")
  execute_process(COMMAND ${SPACK} mirror add local_spheral_cache file://${CACHE_DIR})
  message("--------------------------------------\n")
endif()

#-------------------------------------------------------------------------------
# A generic rule for installing spack managed packages
# 
# If passed more than the required arguments, assume any extras are targets
# that are expected to be produced.  Hopefully cmake checks that those are
# produced for successful passage?
#-------------------------------------------------------------------------------
function(SpackTarget TARGET PKGNAME)
  message("\n---------- BUILDING ${TARGET} ----------")
  message("Running ${SPACK} install ${PKGNAME} ${ARGN}")
  execute_process(COMMAND ${SPACK} install ${PKGNAME} ${ARGN})
  execute_process(
    COMMAND ${SPACK} location -i ${PKGNAME}
    OUTPUT_VARIABLE ${SpackTarget}_base
    )
  set_property(GLOBAL PROPERTY ${SpackTarget}_base "${SpackTarget}_base")
  if (EXISTS ${SpackTarget}_base/include)
    set_property(GLOBAL PROPERTY ${SpackTarget}_include "${SpackTarget}_base/include")
  endif()
  if (EXISTS ${SpackTarget}_base/lib)
    set_property(GLOBAL PROPERTY ${SpackTarget}_lib "${SpackTarget}_base/lib")
  endif()
  if (EXISTS ${SpackTarget}_base/bin)
    set_property(GLOBAL PROPERTY ${SpackTarget}_bin "${SpackTarget}_base/bin")
  endif()
  message("--------------------------------------\n")
endfunction()

# function(SpackTarget TARGET PKGNAME)
#   set(dummytarget .${TARGET}.date)
#   add_custom_command(
#     OUTPUT ${dummytarget}
#     COMMAND ${SPACK} install ${PKGNAME}
#     COMMAND file(TOUCH ${dummytarget})
#     COMMENT spack building ${TARGET} ${PKGNAME}...
#     BYPRODUCTS ${ARGV}
#     )
#   add_custom_target(
#     ${dummytarget}-gen
#     DEPENDS ${dummytarget}
#     )
#   set(spheral_tpl_depends ${spheral_tpl_depends} ${dummytarget}-gen)
#   set(spheral_tpl_depends "${spheral_tpl_depends}" PARENT_SCOPE)
# endfunction()

#-------------------------------------------------------------------------------
# Macro to help adding tpl dependencies for all Spheral object files
#-------------------------------------------------------------------------------
MACRO(add_tpl_depends)
  #message("files: ${ARGN}")
  foreach(file ${ARGN})
    #message("Adding ${file} -> ${spheral_tpl_depends}")
    SET_SOURCE_FILES_PROPERTIES(
      ${file}
      PROPERTIES OBJECT DEPENDS ${spheral_tpl_depends}
      )
  endforeach(file)
endmacro(add_tpl_depends)

#-------------------------------------------------------------------------------
# Add the spack packages as targets now.
#-------------------------------------------------------------------------------
SpackTarget(python python@2.7.16)
SpackTarget(eigen eigen)
#SpackTarget(scipy py-scientificpython)   # <-- Not until we go to python 3 apparently
SpackTarget(numpy py-numpy@1.16.6)
SpackTarget(boost boost@1.72.0 cxxstd=11)

# Note we have to specify where to put the python site packages
set(PYTHON_SITE_PACKAGE_DIR ${SPHERAL_INSTALL_DIR}/site-packages)
