"""Post-processing script for the Hyades rad-hydro code by Cascade Applied Sciences

    __author__ = "Ben Hammel"
    __email__ = "bdhammel@gmail.com"
    __status__ = "Development"

    This Python script was developed by Ben Hammel in cooperation with Cascade Applied 
    Sciences, Inc. (CAS).  CAS does not warrant the accuracy or suitability of this 
    script for any application, nor does it guarantee the script to be error free.

    This script is written to read in hyades dump files corresponding hyades
    version PP.11.xx

    See Appendix IV in Hyades User's Guide Version PP.11.xx for more detailed information
    on the extracted information
"""
import os
import numpy as np
import struct
import time

class PPF:
    """Wrapper class to read in .ppf hyades file

    Extracts each hyades dump from the .ppf file, and stores the relevant information 
    within a "PPFDump" class.

    Operations for extracting dump information are contained within PPFDump     

    Properties
    ----------
    dumps [PPFDump] : array of PPF Dump classes containing the relevant information
        from a hyades dump
    """

    def __init__(self, path=None, debug=False):
        """Initialize PPF model
        If user supplies path variable, call the "read" method

        ARGS
        ----
        path (str) : absolute or relative path to hyades .ppf file to be read
        debug (bool) : (false) set debug mode on or off.

        Examples
        --------
        >>> dmps = PPF("hyades_run.ppf")
        """
        if path:
            self.read_ppf(path, debug)
            self.validate()

    def read_ppf(self, path, debug=False):
        """Read the supplied ppf file

        ARGS
        ----
        path (str) : absolute or relative path to hyades .ppf file to be read
        debug (bool) : (false) set debug mode on or off.

        Examples
        --------
        >>> dmps = PPF()
        >>> dmps.read_ppf("hyades_run.ppf")
        """

        f = open(path, "rb")
        f_size = os.path.getsize(path)

        # Attempt to read in a "dump" until the end of the file is reached
        self.dumps = []
        while f.tell() < f_size:
            try:
                self.dumps.append(PPFDump(f))
            except Exception as e:
                print("Something has failed with reading in the ppf file, \n \
                        breaking at {}/{}".format(f.tell(), f_size))
                print("To run in debug mode, pass debug = True to PPF class")
                if debug:
                    raise e
                else:
                    break
            f.seek(4, 1) # fast forward to the next dump

        f.close()

    def validate(self):
        """Check to see if there were any problems during parsing of the dump file
        """

        errors = []

        print("\n" + "-"*50)
        print("Running validation checker to see if there were mistakes during post processing\n")
        # Assert that the number of regions matches the expected number
        for dump in self.dumps:
            try:
                assert len(set(dump.IREG)) == dump.NREG
            except:
                errors.append("zone region has been imported incorrectly, \n\
                        --this is an issue when using ioniz--")

        for error in set(errors): 
            print(error)

        print("...done")

    @property
    def count(self):
        """Return the number of dumps saved

        Returns
        -------
        int : number of dumps read from binary ppf file

        Examples
        --------
        >>> dmps.count
        65
        """
        return len(self.dumps)

    @property
    def nzones(self):
        """Return the number of zones in the problem

        Returns
        -------
        int : number of zones in the problem

        Examples
        --------
        >>> dmps.nzones
        250
        """
        return self.dumps[0].NZONE

    def get_material(self):
        return self.dumps[0]._materials



    def summary(self):
        """Return a summery of the problem
        """
        pass

    def get_times(self):
        """Return all times corresponding to a dump"

        Returns
        -------
        numpy array [float] :  list of times dumps were made

        Examples
        --------
        >>> dmps.get_times()
        """
        return np.array([dump.TIME for dump in self.dumps])

    def collect(self, array_name):
        """Return all dumps for a given global array

        Args
        ----
        array_name (str) : Name of the array to extract from the dump record

        Returns
        -------
        2D numpy array [float, float]: shape = (nzones, dump number)

        Examples
        --------
        >>> rcm = dmps.collect("RCM")
        >>> pres = dmps.collect("PRES")
        >>> pres[:,10] # pressure across all zones for the 10th dump
        """
        array = [] 
        for dump in self.dumps:
            array.append(dump.parrays[array_name])

        return np.array(array).T

    @property
    def arrays(self):
        """List of all the global array in the problem 

        Return:
        [str] : list of global array names in dumped in the problem

        Examples
        --------
        >>> dmps.arrays
        ["RCM", "R", "PRES", "RHO"]
        """
        return self.dumps[0].parray_names

    def tidx(self, t):
        """Time index
        Find the index of a dump at time, t 
        Args
        ----
        t (float) : time at which to find the dump index

        Returns
        -------
        int : array index corresponding to dump at time, t

        TODO : Except list of times, and return index list

        Examples
        --------
        >>> dmps.tidx(1e-9)
        10
        """
        times = self.get_times()
        return np.argmin(np.abs(times - t))

    @property
    def ireg(self):
        """Return numpy array of region numbers with dimensions matching problem 
        zones
        """
        return self.dumps[0].IREG


class PPFDump:
    """Reads, parses, and stores the information pertaining to one dump 

    Parameters
    ----------
    GET_ARRAY_SIZE {str: lambda function} : dictionary with keys corresponding 
        to PPARRAY names and values as labda functions to calculate array lengths
        Used as a function call. e.g. GET_ARRAY_SIZE["PRES"](self.NZONE)
    BYTES_PER_PACKET (int) : Arbitrary definition of chunk size to be read in 
        from hyades binary file 
    BYTES_PER_ITEM {"str":int} : Dictionary with keys corresponding to data type
        of which a given packet(s) will be converted to, and values as the number 
        of bytes required to represent the given data type.
    """

    BYTES_PER_PACKET = 4
    BYTES_PER_ITEM = {"s":1, "I":4, "d":8, "f":4}
    GET_ARRAY_SIZE = {
            "R":lambda nzone: (nzone+1), # [1, nmesh + 1]
            "RCM":lambda nzone: (nzone+1) + 1, # [0, nmesh + 1]
            "U":lambda nzone: (nzone+1), # [1, nmesh + 1]
            "PRES":lambda nzone: (nzone), # [1, nzone]
            "RHO":lambda nzone: (nzone), # [1, nzone]
            "TE":lambda nzone: (nzone), # [1, nzone]
            "TI":lambda nzone: (nzone), # [1, nzone]
            "QTOT":lambda nzone: (nzone), # [1, nzone]
            "STRTOT":lambda nzone: (nzone+1) + 1, # [0, nzone+1]
            }

    def __init__(self, f):
        """Read in the five records for each dump
        Appendix IV user guide Version PP.11.xx October, 2013

        Args
        ----
        f (binary file) : pointer to the binary file currently being read

        """
        self._f = f

        self._extract_array_lengths()
        self._extract_header()
        self._extract_material_composition()
        self._extract_global_variables()
        self._extract_global_variable_arrays()

        del self._f

    def _extract_packet_values(self, packets, dtype, as_array=False):
        """Extract some number of packets from the binary file

        Args
        ----
        packets (int) : number of packets to be read in
        dtype (str) : data type to convert the bytes to 
        as_array (bool) : Return the extracted data in numpy array form 
        """
        byte_number = packets * self.BYTES_PER_PACKET
        items = byte_number // self.BYTES_PER_ITEM[dtype]
        byte_format = "<{}{}".format(items, dtype)

        value =  struct.unpack(byte_format, self._f.read(byte_number))

        if dtype == "s":
            value = list(map(lambda x: x.decode("utf-8"), value))

        if not as_array:
            return value[0]
        else:
            return np.array(value)

    def _extract_array_lengths(self):
        """Extract the information about the problem for the current dump

        Properties
        ----------
        NGRPMXX - macimum number of photon groups
        NIONMXX - maximum numper of ion types
        NLVLMXX - maximum number of atomic physical levels
        NMATMXX - maximum number of elements per region
        NPPARMXX    - maximum numper of post processor arrays
        NRMAXX  - maximum number of regions
        """

        _ = self._extract_packet_values(1, "I", as_array=True)

        self.NGRPMXX = self._extract_packet_values(1, "I")
        self.NIONMXX = self._extract_packet_values(1, "I")
        self.NLVLMXX = self._extract_packet_values(1, "I")
        self.NMATMXX = self._extract_packet_values(1, "I")
        self.NPPARMXX = self._extract_packet_values(1, "I")
        self.NTNPARTMXX = self._extract_packet_values(1, "I")
        self.NTNREACMXX = self._extract_packet_values(1, "I")
        self.NRMAXX = self._extract_packet_values(1, "I")
        self.NZMAXX = self._extract_packet_values(1, "I")

        # Unsure why this is necessary
        _ = self._extract_packet_values(2, "I", as_array=True)

    def _extract_header(self):
        """Extract the header for this specific dump
        """

        self.NAMEP = self._extract_packet_values(8, "s")
        self.TBUF = self._extract_packet_values(2, "s")
        self.DBUF = self._extract_packet_values(2, "s")
        _ = self._extract_packet_values(1, "I")
        self.IVER1 = self._extract_packet_values(2, "s")
        self.IVER2 = self._extract_packet_values(2, "s")
        self.MACHNE = self._extract_packet_values(2, "s")
        self.TIME = self._extract_packet_values(2, "d")
        self.NCYCL = self._extract_packet_values(1, "I")
        self.IALPHA = self._extract_packet_values(1, "I")
        self.NREG = self._extract_packet_values(1, "I")
        self.NZONE = self._extract_packet_values(1, "I")
        self.NGROUP = self._extract_packet_values(1, "I")
        _ = self._extract_packet_values(5, "I")
        self.NPPARY = self._extract_packet_values(1, "I")
        _ = self._extract_packet_values(8, "I")

        self.CPPBUF = self._extract_packet_values(2*self.NPPARY, "s")
        self.parray_names = self.CPPBUF.split()
        _ = self._extract_packet_values(2*(self.NPPARMXX-self.NPPARY), "s")

        self.PHGRPBND = self._extract_packet_values(self.NGRPMXX, "f", as_array=True)
        self.PHGRPCEN = self._extract_packet_values(self.NGRPMXX, "f", as_array=True)

    def _extract_material_composition(self):
        """Extract the material composition for the problem

        TODO : Fix problem with importing photon groups
        """

        # Might be 2 4byte buffer, and 1 4 byte package belongs to PHGRPBND
        _ = self._extract_packet_values(3, "I", as_array=True)

        # Get region numbers
        self.IREG = self._extract_packet_values(self.NZONE, "I", as_array=True)


        _ = self._extract_packet_values(1, "I")

        self._materials = {}

        for region in range(1,self.NREG+1):
            elements = self._extract_packet_values(1, "I")
            self._materials[region] = []
            # Number of elements
            for element in range(elements):
                # Atomic Fraction, atomic number, atomic weight
                self._materials[region].append({
                        "atmfrc":self._extract_packet_values(2, "d"),
                        "atmnum":self._extract_packet_values(2, "d"),
                        "atmwgt":self._extract_packet_values(2, "d")
                        })

    def _extract_global_variables(self):
        """Extract all parameters and global variables for the problem at this 
        dump

        properties
        ----------
        global_variables [float]: numpy array of values of global variables, in 
            order documented by step 4 in Apperndix IV of Hyades user manual. Such
            values as:
                dt      - current delta t
                dtave   - avg of previous and current delta t
                dtold   - previous delta t
                eelas   - laser energy to electrons
                eelcis  - initial electron energy 
                eepdv   - electron energy PdV work  
                eesrc   - source energy to electrons

        TODO : Convert this to a dictionary with the global_variables as keys
        """
        self.global_variables = self._extract_packet_values(48*2, "d", as_array=True)

    def _extract_global_variable_arrays(self):
        """Extract all arrays the user requested be dumped
        """

        assert len(self.parray_names) == self.NPPARY

        _ = self._extract_packet_values(2, "d")

        self.parrays = {}

        for parray_name in self.parray_names:
            _ = self._extract_packet_values(2, "d")
            try:
                parray_size = self.GET_ARRAY_SIZE[parray_name](self.NZONE)
            except:
                print("Was not able to calculate size of {} type array,\n \
                        add it to the list".format(parray_name))
            else:
                self.parrays[parray_name] = self._extract_packet_values(    
                    2*parray_size, "d", as_array=True)

class PArray:

    def __call__(self):
        pass

    @property
    def name(self):
        return self._name

