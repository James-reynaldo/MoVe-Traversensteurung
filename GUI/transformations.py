import numpy as np

def transform_positions_to_rotations_stepwise(x = None, y = None, z = None, r = None, phi = None):
    if x and y and z and not r and not phi:
        pass
    elif not x and not y and not z and r and phi:
        pass
    else:  # Koordinaten gemischt angegeben
        print("Error: Format does not match")

def transform_settings_to_cartesian(r, phi):
    return r*np.sin(np.deg2rad(phi)), r*np.cos(np.deg2rad(phi))