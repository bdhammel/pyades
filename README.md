# pyades

A python post-processing wrapper for the HYADES radiation hydrodynamics code by Cascade Applied Sciences

**Note** This script is still in development and there are undoubtedly some bugs and errors. A list of know problems is included at the bottom of this readme. 
If you have any questions, please feel free to contact me.

This Python script was developed by Ben Hammel in cooperation with Cascade Applied 
Sciences, Inc. (CAS).  CAS does not warrant the accuracy or suitability of this 
script for any application, nor does it guarantee the script to be error free.

## Installation

Set up virtual environment and activate it   

~~~bash
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $
~~~  


`cd` into the site-packages directory and install pyades  

~~~bash
(venv) $ cd venv/lib/python3.5/site-packages/
(venv) $ git clone https://github.com/bdhammel/pyades.git
~~~  

Now, whenever this environment is active, pyades can be imported as a standard python module 


## Example usage

Import pyades and load a .ppf file from a Hyades run 

~~~Python
>>> import pyades
>>> dmps = pyades.PPF("hyades_run.ppf")
~~~

## Get Help on pyades functions

When using iPython, add a "question mark" at the end of any function call to view the documentation for it

~~~bash
>>>  pyades.PPF?

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
>>>  dmps.arrays
['R', 'U', 'RCM', 'RHO', 'TE', 'TI', 'PRES'] 
~~~

### The pyades array format

collect an array from the simulation output 

~~~python
>>>  p = dmps.collect("PRES")
~~~

Arrays have the dimensions: (number of zones, number of dumps)

~~~python
>>> dmps.nzones
250
>>> dmps.count
500
>>> p.shape
(250, 500)
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

Plot every 10th dump using standard numpy array indexing

~~~python
>>> plt.plot(x[1:-1,::10], p[:,::10])
~~~

### Animate Hyades output

~~~python
>>> fig, ax, ani = ph.animate(x[1:-1], den)
~~~

To start, stop, start over from the begining, or step through one frame at a time the following commands can be used:

~~~python
>>> ani.event_source.stop() # stop the animation
>>> ani.event_source.start() # restart a stoped animation
>>> ani.frame_seq = ani.new_frame_seq() # restart an animation from the begining
>>> ani._step() # Step through an animation one frame at a time (you'll need to stop the animation first)
~~~

I plan to build these into a control bar as buttons. If you're reading this and want to see it happen, shoot me a message. 

## Known issues

 1. The script does not include a complete list of arrays. If a problem consist of a global array which is not included, the code will throw the error: `"Was not able to calculate size of {array name} type array, add it to the list`, If this is the case, the array type can be added to `GET_ARRAY_SIZE` dictionary in the `PPFDump` Class, with dimensions corresponding to step 5 in appendix 5 of the user manual.
 2. The code does not correctly import the photon group boundary energies or the photon group center energies (step 1. Appendix 5 in the User manual)
    - Using ioniz breaks the parser -- this is related to the issue with the photon group energies --

