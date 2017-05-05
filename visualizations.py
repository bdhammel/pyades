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

import matplotlib.pyplot as plt
import matplotlib.animation as animation

def animate(xarray, yarray, tarray=None):
    """Generate and animation of of two hyades arrays for each timestep

    Args
    ----
    xarray (collected array from pyades dumps) : shape=(nzones,times) X array to plot
    yarray (collected array from pyades dumps) : shape=(nzones,times) Y array to plot

    Examples
    --------
    >>> ani = pyades.animate(rcm[1:-1,:], pres)

    TODO
    -----
    Make start, stop, step, and restart commands into buttons
    """

    def update_animation(t, line, xdata, ydata, tdata=None):
        """Update the animation to the next frame 
        Args
        ----
        t (int) : index of frame count
        line
        xdata
        ydata
        tdata
        """
        line.set_data(xdata[:,t], ydata[:,t])

        # Write the time step to the figure
        if tdata is not None:
            text_str = "time: {:.2E} ns".format(tdata[t]*1e9)
            fig = line.get_figure()
            texts = fig.texts

            if len(texts) != 0:
                texts[0].set_text(text_str)
            else:
                plt.figtext(0,0, text_str)

        plt.draw()
        return line,

    if not plt.isinteractive():
        print("Turning interactive mode on")
        plt.ion()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.ylim(yarray.min(), yarray.max())
    plt.xlim(xarray.min(), xarray.max())

    line, = ax.plot(xarray[:,0], yarray[:,0])
    frame_count = len(xarray[0,1:])
    ani = animation.FuncAnimation(
            fig, update_animation, frame_count, 
            fargs=(line, xarray[:,1:], yarray[:,1:], tarray), 
            repeat=True, interval=10)


    plt.show()

    ani.stop = ani.event_source.stop
    ani.start = ani.event_source.start  
    ani.step = ani._step

    # Dynamically add a restart method
    def restart(self): 
        self.frame_seq = self.new_frame_seq()

    ani.restart = restart.__get__(ani)

    return ani

def plot_with_ireg(xdata, ydata, ireg):
    """Plot with indicators of the different regions in the problem 
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for reg in set(ireg):
        reg_xdata = xdata[ireg==reg]
        reg_ydata = ydata[ireg==reg]
        l = ax.plot(reg_xdata, reg_ydata)
        ax.fill_between(reg_xdata, 0, reg_ydata, alpha=.5)

    return l

def tplot(xdata, ydata, tidx, ireg=None):
    """Plot data at a given time index

    Args
    ----
    xdata
    ydata
    tidx (int) : index of the dump number to plot 
    ireg ([int]) : (None) plot with indicators of the different regions in the problem 

    Returns
    -------
    matplotlib line object
    """

    if ireg is not None:
        plotter = lambda x, y: plot_with_ireg(x, y, ireg=ireg)
    else:
        plotter = plt.plot

    line, = plotter(xdata[:,tidx], ydata[:,tidx])

    return line

