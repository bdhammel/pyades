# pyades - A python post-processing wrapper for the HYADES radiation hydrodynamics code by Cascade Applied Sciences

## Example usage

~~~Python
>>> import pyades
>>> import matplotlib.pyplot as plt
>>> dmps = pyades.PPF("")
>>> 
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



