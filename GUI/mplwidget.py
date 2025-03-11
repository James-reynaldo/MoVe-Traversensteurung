# Based on: https://stackoverflow.com/questions/43947318/plotting-matplotlib-figure-inside-qwidget-using-qt-designer-form-and-pyqt5 (letzter Zugriff: 06.04.2024)
# Imports
from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib
import matplotlib.pyplot
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import transformations

# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')

# Matplotlib canvas class to create figure
class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

    

    def reload_plot(self, gitter_object: 'Grid', settings: dict):
        """
                      deg  manuell cart
        not visited: blue, yellow, cyan
        visited: black
        """
        #self.ax.plot([settings["dimensions"]["min_deviation"]])

        if gitter_object.type == "radial":
            self.fig.clear()
            self.ax = self.fig.add_subplot(111, projection='polar')
            self.ax.set_theta_offset(np.pi/2)
            self.ax.set_theta_direction(-1)
            print(gitter_object.coordinates)
            # self.ax.plot(gitter_object.coordinates, "g")
            transposed = gitter_object.coordinates.T
            try:
                self.ax.plot((transposed[0]/90)*np.pi/2,transposed[1], ".-g")
            except:
                if transposed == None:
                    pass
        elif gitter_object.type == "manuell":
            self.ax.plot(0, 0, "r")
        elif gitter_object.type == "cart":
            self.ax.plot(gitter_object.coordinates, "b")
        self.ax.set_xlim(np.deg2rad(settings["dimensions"]["min_deflection"]), np.deg2rad(settings["dimensions"]["max_deflection"]))
        # self.ax.set_ylim([settings["dimensions"]["inner_radius"], settings["dimensions"]["outer_radius"]])
        self.draw_begrenzung(gitter_object.type, settings)
        self.draw()

    def save_plot(self):
        self.fig.savefig("plot_of_grid.pdf")

    def draw_begrenzung(self, gitter_type, settings: dict):

        r1, phi1 = float(settings['dimensions']['outer_radius']), float(settings['dimensions']['min_deflection']) # Ecke links oben
        r2, phi2 = float(settings['dimensions']['inner_radius']), float(settings['dimensions']['min_deflection']) # Ecke links unten
        r3, phi3 = float(settings['dimensions']['outer_radius']), float(settings['dimensions']['max_deflection']) # Ecke rechts oben
        r4, phi4 = float(settings['dimensions']['inner_radius']), float(settings['dimensions']['max_deflection']) # Ecke rechts unten

        winkel = np.linspace(float(settings['dimensions']['min_deflection']), float(settings['dimensions']['max_deflection']), 500)
        print(winkel)
        x1_values, y1_values = transformations.transform_settings_to_cartesian(r1, winkel)
        x2_values, y2_values = transformations.transform_settings_to_cartesian(r2, winkel)

        if gitter_type == "radial":
            self.ax.plot([np.deg2rad(phi1), np.deg2rad(phi2)], [r1, r2], "--r")
            self.ax.plot([np.deg2rad(phi3), np.deg2rad(phi4)], [r3, r4], "--r")
            self.ax.plot(np.deg2rad(winkel), [r1 for _ in winkel], "--r")
            self.ax.plot(np.deg2rad(winkel), [r2 for _ in winkel], "--r")
        elif gitter_type == "manuell":
            self.ax.plot(0, 0, "r")
        elif gitter_type == "cart":
            pass
        self.draw()


# Matplotlib widget
class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
        self.canvas = MplCanvas()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

    # Pass reload request to child class
    def reload_plot(self, gitter_object: 'Grid', settings: dict):
        self.canvas.reload_plot(gitter_object, settings)