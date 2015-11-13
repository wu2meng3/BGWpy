from __future__ import print_function
import os

from .bgwtask import BGWTask
from .kgrid   import get_kpt_grid
from .inputs  import KernelInput

# Public
__all__ = ['KernelTask']


class KernelTask(BGWTask):
    """Kernel calculation for BSE."""

    _TASK_NAME = 'Kernel task'

    _input_fname  = 'kernel.inp'
    _output_fname = 'kernel.out'

    def __init__(self, dirname, **kwargs):
        """
        Arguments
        ---------

        dirname : str
            Directory in which the files are written and the code is executed.
            Will be created if needed.


        Keyword arguments
        -----------------
        (All mandatory unless specified otherwise)

        nbnd_val : int
            Number of valence bands.
        nbnd_cond : int
            Number of conduction bands.
        wfn_co_fname : str
            Path to the wavefunction file produced by pw2bgw.
        eps0mat_fname : str
            Path to the eps0mat file produced by epsilon.
        epsmat_fname : str
            Path to the epsmat file produced by epsilon.
        extra_lines : list, optional
            Any other lines that should appear in the input file.
        extra_variables : dict, optional
            Any other variables that should be declared in the input file.


        Properties
        ----------

        bsedmat_fname : str
            Path to the bsedmat file produced.
        bsedmat_h5_fname : str
            Path to the bsedmat.h5 file produced.
        bsexmat_fname : str
            Path to the bsexmat file produced.
        bsexmat_h5_fname : str
            Path to the bsexmat.h5 file produced.

        """

        super(KernelTask, self).__init__(dirname, **kwargs)

        # Compute k-points grids

        # Input file
        self.input = KernelInput(
            kwargs['nbnd_val'],
            kwargs['nbnd_cond'],
            *kwargs.get('extra_lines',[]),
            **kwargs.get('extra_variables',{}))

        self.input.fname = self._input_fname

        # Set up the run script
        self.wfn_co_fname = kwargs['wfn_co_fname']
        self.eps0mat_fname = kwargs['eps0mat_fname']
        self.epsmat_fname = kwargs['epsmat_fname']

        self.runscript['KERNEL'] = 'kernel.cplx.x'
        self.runscript['KERNELOUT'] = self._output_fname
        self.runscript.append('$MPIRUN $KERNEL &> $KERNELOUT')

    @property
    def wfn_co_fname(self):
        return self._wfn_co_fname

    @wfn_co_fname.setter
    def wfn_co_fname(self, value):
        self._wfn_co_fname = value
        self.update_link(value, 'WFN_co')

    @property
    def eps0mat_fname(self):
        return self._eps0mat_fname

    @eps0mat_fname.setter
    def eps0mat_fname(self, value):
        self._eps0mat_fname = value
        dest = 'eps0mat'
        if value.endswith('.h5'):
            dest += '.h5'
        self.update_link(value, dest)

    @property
    def epsmat_fname(self):
        return self._epsmat_fname

    @epsmat_fname.setter
    def epsmat_fname(self, value):
        self._epsmat_fname = value
        dest = 'epsmat'
        if value.endswith('.h5'):
            dest += '.h5'
        self.update_link(value, dest)

    def write(self):
        super(KernelTask, self).write()
        with self.exec_from_dirname():
            self.input.write()

    @property
    def bsedmat_fname(self):
        return os.path.join(self.dirname, 'bsedmat')
    
    @property
    def bsedmat_h5_fname(self):
        return os.path.join(self.dirname, 'bsedmat.h5')
    
    @property
    def bsexmat_fname(self):
        return os.path.join(self.dirname, 'bsexmat')
    
    @property
    def bsexmat_h5_fname(self):
        return os.path.join(self.dirname, 'bsexmat.h5')
    
