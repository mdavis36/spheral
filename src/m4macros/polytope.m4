# -----------------------------------------------------------------
# Polytope
# -----------------------------------------------------------------
AC_DEFUN([SETUP_POLYTOPE],[
AC_SUBST(POLYTOPEFLAGS)
AC_SUBST(POLYTOPELIBS)
AC_SUBST(USE_TRIANGLE)
AC_SUBST(USE_TETGEN)

POLYTOPEFLAGS="prefix=$SPHERALDIR boost_root=$SPHERALDIR"
POLYTOPELIBS="-lpolytope"
# -----------------------------------------------------------------
# Optionally build polytope without Triangle
# -----------------------------------------------------------------
AC_MSG_CHECKING(for --without-triangle)
AC_ARG_WITH(triangle,
[  --without-triangle ....................... optionally build polytope without Triangle],
[
   AC_MSG_RESULT(yes)
   USE_TRIANGLE=0
],
[
   AC_MSG_RESULT(no)
   USE_TRIANGLE=1
]
)

# -----------------------------------------------------------------
# Optionally build polytope without Tetgen
# -----------------------------------------------------------------
AC_MSG_CHECKING(for --without-tetgen)
AC_ARG_WITH(tetgen,
[  --without-tetgen ......................... optionally build polytope without Tetgen],
[
   AC_MSG_RESULT(yes)
   USE_TETGEN=0
],
[
   AC_MSG_RESULT(no)
   USE_TETGEN=1
   POLYTOPELIBS="$POLYTOPELIBS -ltetgen"
]
)

])

