
from ..util.F90io import Namelist, Card
import warnings
import numpy as np

class QuantumEspressoInput(object):

    _structure = None 
    _pseudos = list()

    def __init__(self):

        self.control = Namelist('control')
        self.system = Namelist('system')
        self.electrons = Namelist('electrons')
        self.ions = Namelist('ions')
        self.cell = Namelist('cell')
        self.atomic_species = Card('ATOMIC_SPECIES', '')
        self.atomic_positions = Card('ATOMIC_POSITIONS', 'crystal')
        self.k_points = Card('K_POINTS', '')
        self.cell_parameters = Card('CELL_PARAMETERS', 'angstrom')
        self.constraints = Card('CONSTRAINTS', '')
        self.occupations = Card('OCCUPATIONS', '')
        self.atomic_forces = Card('ATOMIC_FORCES', '')

    def _isrelax(self):
        """True if this is a relaxation calculation."""
        calculation = str(self.control.get('calculation')).lower()
        return calculation in ('relax', 'md', 'vc-relax', 'vc-md' )

    def _isvc(self):
        """True if the volume of the cell can change."""
        calculation = str(self.control.get('calculation')).lower()
        return calculation in ('vc-relax', 'vc-md' )

    def _isfreebrav(self):
        """True if the bravais lattis is free."""
        ibrav = self.system.get('ibrav')
        if ibrav is None:
            return False
        return int(ibrav) == 0

    def _isconstrained(self):
        """True if the ion dynamics is constrained."""
        return self.ions.get('ion_dynamics') in ('verlet', 'damp')

    def _is_manual_occ(self):
        """True if the occupation is specified manually."""
        return str(self.system.get('occupations','')).lower() == 'from_input'

    def __str__(self):

        # Perform checks
        self.check_pseudos_names()

        S = ''
        S += str(self.control)
        S += str(self.system)
        S += str(self.electrons)

        if self.ions or self._isrelax():
            S += str(self.ions)

        if self.cell or self._isvc():
            S += str(self.cell)

        S += str(self.atomic_species)
        S += str(self.atomic_positions)
        S += str(self.k_points)

        if self.cell_parameters or self._isfreebrav():
            S += str(self.cell_parameters)

        if self.constraints or self._isconstrained():
            S += str(self.constraints)

        if self.occupations or self._is_manual_occ():
            S += str(self.occupations)

        if self.atomic_forces:
            S += str(self.atomic_forces)

        return S

    def set_kpoints_crystal(self, kpts, wtks):
        self.k_points.option = 'crystal'
        self.k_points.append(len(kpts))
        for k, w in zip(kpts, wtks):
            self.k_points.append(list(k) + [w])

    @property
    def structure(self):
        return self._structure

    @structure.setter
    def structure(self, structure):
        """A pymatgen.Structure object."""
        self._structure = structure

        # Set system specifications
        self.system['ibrav'] = 0
        self.system['nat'] = structure.num_sites
        self.system['ntyp'] = structure.ntypesp

        # Set cell parameters
        self.cell_parameters.option = 'angstrom'
        for vec in structure.lattice_vectors():
            self.cell_parameters.append(np.round(vec, 8))

        # Set atomic species
        for element in structure.types_of_specie:
            self.atomic_species.append([element.symbol, float(element.atomic_mass)])

        if self.pseudos:
            for i, pseudo in enumerate(self.pseudos):
                self.atomic_species[i].append(pseudo)

        # Set atomic positions
        self.atomic_positions.option = 'crystal'
        for site in structure.sites:
            frac_coords = list(site.frac_coords)
            for i in range(3):
                if abs(frac_coords[i]) > .5:
                    frac_coords[i] += -1. * np.sign(frac_coords[i])
            self.atomic_positions.append([site.specie.symbol] + frac_coords)

    @property
    def pseudos(self):
        return self._pseudos

    @pseudos.setter
    def pseudos(self, pseudos):
        self._pseudos = pseudos
        if self.atomic_species:
            for i, pseudo in enumerate(pseudos):
                self.atomic_species[i].append(pseudo)

    def check_pseudos_names(self):
        for symbol, mass, pseudo in self.atomic_species:
            if symbol.lower() not in pseudo.lower():
                warnings.warn('Suspicious pseudo name for atom {}: {}'.format(symbol, pseudo))
