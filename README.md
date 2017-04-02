# pyades - A python post-processing wrapper for the HYADES radiation hydrodynamics code by Cascade Applied Sciences

## Example usage

~~~Python
>>> import pyades
>>> import matplotlib.pyplot as plt
>>> dmps = pyades.PPF("")
~~~

## Get Help on pyades functions

~~~bash
>>>  dmps.parrays?

Init signature: pyades.PPF(path=None, debug=False)

Docstring:     
Wrapper class to read in .ppf hyades file

Extracts each hyades dump from the .ppf file, and stores the relevant information 
within a "PPFDump" class.

Operations for extracting dump information are contained within PPFDump     

Properties
----------
dumps [PPFDump] : array of PPF Dump classes containing the relevant information
    from a hyades dump

Init docstring:
    Initialize PPF model
    If user supplies path variable, call the "read" method

    ARGS
    ----
    path (str) : absolute or relative path to hyades .ppf file to be read
    debug (bool) : (false) set debug mode on or off.

    Examples
    --------
    >>> dmps = PPF("hyades_run.ppf")
    File:           ~/lib/pyades/post_process.py
    Type:           typej
~~~


## Hyades problem arrays 

### list all arrays dumped in the problem 

~~~python
>>>  dmps.parrays
~~~

### The pyades array format

collect an array from the simulation output 

~~~python
>>>  pres = dmps.collect("PRES")
~~~

### Dealing with dump times

#### Get times at each dump

~~~python
>>> t = dmps.get_times()
~~~

#### Get dump at closest time

Get the dump index closest to the desired time (2 ns)

~~~python
>>> tidx = dmps.tidx(2e-9)
~~~

## Visualizations

### Plot at a given time index

~~~python
>>> x = dmps.collect("RCM")
>>> tidx = dmps.tidx(2e-9)
>>> pyades.tplot(x[1:-1], p, tidx)
~~~

Show different regions in the problem 

~~~python
>>> ireg = dmps.ireg
>>> pyades.tplot(x[1:-1], p, tidx, ireg)
~~~

### Plot at dump intervals

Plot every 10th dump with standard numpy array indexing

~~~python
>>> plt.plot(x[1:-1,::10], p[:,::10])
~~~





