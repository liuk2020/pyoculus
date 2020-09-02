## @file spec_problem.py
#  @brief Setup the Abstract SPEC class for ODE solver
#  @author Zhisong Qu (zhisong.qu@anu.edu.au)
#
from .base_problem import BaseProblem
import numpy as np

## Abstract class to setup the SPEC system for interfacing Fortran, used in ODE solver.
class SPECProblem(BaseProblem):
    def __init__(self, spec_data, lvol):
        """! Set up the equilibrium for use of the fortran module
        @param spec_data the SPEC data generated by py_spec.SPECout
        @param lvol which volume we are interested in, from 1 to spec_data.input.Mvol
        """
        from .SPECfortran import fortran_module

        self.fortran_module = fortran_module

        # check the version of SPEC output file. Only >=2.2 is accepted
        if spec_data.version < 2.2:
            raise Exception("SPEC version >=2.2 is needed")

        # setting up the fortran module
        fortran_module.specvariables.mvol = spec_data.output.Mvol
        fortran_module.specvariables.ntor = spec_data.input.physics.Ntor
        fortran_module.specvariables.mpol = spec_data.input.physics.Mpol
        fortran_module.specvariables.igeometry = spec_data.input.physics.Igeometry
        fortran_module.specvariables.mn = spec_data.output.mn
        fortran_module.specvariables.notstellsym = (
            spec_data.input.physics.Istellsym == 0
        )
        fortran_module.specvariables.nfp = spec_data.input.physics.Nfp
        fortran_module.specvariables.im = spec_data.output.im
        fortran_module.specvariables.in1 = spec_data.output.in1

        fortran_module.specvariables.irbc = spec_data.output.Rbc.T
        fortran_module.specvariables.izbc = spec_data.output.Zbc.T
        fortran_module.specvariables.irbs = spec_data.output.Rbs.T
        fortran_module.specvariables.izbs = spec_data.output.Zbs.T

        # saving some quantities for self as well
        self.Mvol = spec_data.output.Mvol
        self.Ntor = spec_data.input.physics.Ntor
        self.Mpol = spec_data.input.physics.Mpol
        self.Igeometry = spec_data.input.physics.Igeometry
        self.NOTstellsym = spec_data.input.physics.Istellsym == 0
        self.Nfp = spec_data.input.physics.Nfp

        # rpol and rtol, in case they are not saved into SPEC output
        try:
            self.rpol = spec_data.input.physics.rpol
            self.rtor = spec_data.input.physics.rtor
        except:
            self.rpol = 1.0
            self.rtor = 1.0

        if lvol > 0 and lvol <= spec_data.output.Mvol:
            # setting up the fortran module
            fortran_module.specvariables.rpol = self.rpol
            fortran_module.specvariables.rtor = self.rtor
            fortran_module.specvariables.ivol = lvol
            fortran_module.specvariables.lrad = spec_data.input.physics.Lrad[lvol - 1]
            fortran_module.specvariables.ate = spec_data.vector_potential.Ate[
                lvol - 1
            ].T
            fortran_module.specvariables.ato = spec_data.vector_potential.Ato[
                lvol - 1
            ].T
            fortran_module.specvariables.aze = spec_data.vector_potential.Aze[
                lvol - 1
            ].T
            fortran_module.specvariables.azo = spec_data.vector_potential.Azo[
                lvol - 1
            ].T
            fortran_module.specvariables.lcoordinatesingularity = (
                spec_data.input.physics.Igeometry >= 2 and lvol == 1
            )

            # saving some quantities for self as well
            self.ivol = lvol
            self.Lrad = spec_data.input.physics.Lrad[lvol - 1]
            self.Lcoordinatesingularity = (
                spec_data.input.physics.Igeometry >= 2 and lvol == 1
            )

        else:
            raise Exception("Volume number lvol out of bound")