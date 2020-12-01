## George Philbrick
## 11/29/2020
## Code to simulate the behavior of a LVDT in FEMM
## ///////////////////////////////////////////////

import numpy as np
import matplotlib.pyplot as plt
import femm

###### HELPER FUNCTIONS ######
# Convert a rectangular function to polar form
def rectToPolar(imaginary):
    print(abs(imaginary), "< ", 180 * np.angle(imaginary) / np.pi)

# Convert a polar form imagnary number to rectangular form
def polarToRect(mag, angle):
    return mag*np.cos(np.radians(angle)) + mag*np.sin(np.radians(angle))*1j

###### IMPORTANT CONSTANTS ######
FREQ = 60 # Hz
FREQ_RAD = FREQ * 2 * np.pi # radians
N_PRIMARY = 200 # turns
N_SECONDARY = 200 # turns

###### SIMULATION CODE ######
distances = np.linspace(-0.1, 0.1, num=50)
fluxPerRadianTop = []
fluxPerRadianBottom = []
i = 0

for d in distances:
    # open FEMM
    femm.openfemm()
    femm.main_maximize()

    # True Steady State
    # New MagnetoStatics Document
    femm.newdocument(0)

    # Define the problem type.  60 Hz; Units of inches; Axisymmetric;
    # Precision of 10^(-8) for the linear solver; a placeholder of 0 for
    # the depth dimension, and an angle constraint of 30 degrees
    femm.mi_probdef(FREQ, 'inches', 'axi', 1.e-8, 0, 30)

    # Import materials
    femm.mi_getmaterial('Air')
    femm.mi_getmaterial('Pure Iron')
    femm.mi_getmaterial('30 AWG')

    # Draw Rectangles
    femm.mi_drawrectangle(0, d-0.2, 0.04, d+0.2) # Iron Core 0.6" height 0.04" inner radius
    femm.mi_drawrectangle(0.05, -0.1, 0.1, 0.1) # Primary Coil 0.2" Height, 0.05" inner radius, 0.1" outer radius
    femm.mi_drawrectangle(0.05, 0.11, 0.1, 0.31) # Top Secondary Coil 0.2" Height, 0.05" inner radius, 0.1" outer radius
    femm.mi_drawrectangle(0.05, -0.31, 0.1, -0.11) # Bottom Secondary Coil 0.2" Height, 0.05" inner radius, 0.1" outer radius

    # Add Block Labels, materials, and circuits

    # Air Label
    femm.mi_addblocklabel(0.3, 0)
    femm.mi_selectlabel(0.3, 0)
    femm.mi_setblockprop('Air', 1, 0, '<None>', 0, 0, 0)

    # Pure Iron Label
    femm.mi_clearselected()
    femm.mi_addblocklabel(0.02, d)
    femm.mi_selectlabel(0.02, d)
    femm.mi_setblockprop('Pure Iron', 1, 0, '<None>', 0, 0, 0)

    # Secondary Coil Copper Labels
    femm.mi_clearselected()
    femm.mi_addblocklabel(0.075, 0.21)
    femm.mi_addblocklabel(0.075, -0.21)
    femm.mi_selectlabel(0.075, 0.21)
    femm.mi_selectlabel(0.075, -0.21)
    femm.mi_setblockprop('30 AWG', 1, 0, '<None>', 0, 0, 0)

    # Primary Coil Circuit and Block Labels
    femm.mi_clearselected()
    femm.mi_addcircprop('Primary', 1, 1) # Primary coil, 1A current, series
    femm.mi_addblocklabel(0.075, 0)
    femm.mi_selectlabel(0.075, 0)
    femm.mi_setblockprop('30 AWG', 1, 0, 'Primary', 0, 0, 200)

    # Lets make a default open air boundary
    femm.mi_makeABC()

    input('Press enter to continue...')

    # Save so we can analyze
    femm.mi_saveas('lvdt_sweep.fem')
    femm.mi_analyze()
    femm.mi_loadsolution()

    # Show the density plot
    femm.mo_showdensityplot(1, 0, 0.15, 0, 'mag')

    ###### MEASURE FLUX IN SIMULATION ######
    # Take line integral over radius to get flux / radian in each secondary core
    # Top Core
    femm.mo_addcontour(0, 0.21) 
    femm.mo_addcontour(0.05, 0.21)
    fluxPerRadianTop.append(femm.mo_lineintegral(0)[0]) # flux/radian (indexing 0 because mo_lineintegral returns both average and total)

    # Top Core
    femm.mo_clearcontour()
    femm.mo_addcontour(0, -0.21) 
    femm.mo_addcontour(0.05, -0.21)
    fluxPerRadianBottom.append(femm.mo_lineintegral(0)[0]) # flux/radian (indexing 0 because mo_lineintegral returns both average and total)

    ###### EXPORT IMAGES FOR GIF ######
    filename = 'Bplot_' + str(i) + '.png'
    femm.mo_savebitmap(filename)
    i += 1

###### Calculate Induced Voltage ######
# Total Flux
totalFluxTop = 2*np.pi*np.array(fluxPerRadianTop) # Eq 5
totalFluxBottom = 2*np.pi*np.array(fluxPerRadianBottom) # Eq 5

# EMF Top and Bottom
emfTop = -N_SECONDARY * totalFluxTop * FREQ_RAD * 1j # Eq 3
emfBottom = -N_SECONDARY * totalFluxBottom * FREQ_RAD * 1j # Eq 3

# Total EMF
emf = np.subtract(emfTop, emfBottom) # Eq. 6
emf_mag = np.abs(emf) # Get the magnitude of the voltage
emf_phase = 180 * np.angle(emf) / np.pi # Get the phase of the voltage

###### Plotting ######
plt.plot(distances, emf_mag)
plt.xlabel('Distance (in)')
plt.ylabel('Voltage Magnitude (V)')
plt.show()

plt.plot(distances, emf_phase)
plt.xlabel('Distance (in)')
plt.ylabel('Voltage Phase Shift (Degrees)')
plt.show()

input('Press enter to exit...')