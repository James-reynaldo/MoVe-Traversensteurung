import csv
import file_operations
import numpy as np

class Grid:
    def __init__(self, filename = None, type = "radial", coordinates = []) -> None:
        # [value, value, (value), boolean]

        self.type = type
        # Load grid from file
        if filename:
            try:
                coordinates = file_operations.load_txt(filename)
            except FileNotFoundError:
                print("Error: Please provide a valid file name.")
                return
        else:
            pass
        
        # Set every coordinate to False (not visited yet)
        self.coordinates = np.asarray([(x, y, 0) for (x, y) in coordinates])

    def __str__(self):
        string = ""
        for x, y, boolean in self.coordinates:
            # Use float formatting (https://stackoverflow.com/questions/1995615/how-can-i-format-a-decimal-to-always-show-2-decimal-places) 06.04
            string += f"{x:.3f}; {y:.3f}\n"
        return string
    
    # https://blog.finxter.com/python-__iter__-magic-method/ (02.09.2024)
    def __iter__(self):
        self.current_index = 1
        return self
    
    def __next__(self):
        if self.current_index < len(self.coordinates):
            self.current_index += 1
            return self.coordinates[self.current_index -1][0:-1]
        raise StopIteration

    def generate(self, type = "polar") -> None:
        if type == "cartesian":
            pass
        elif type == "polar":
            pass
        else:
            print("Error: Please provide a valid coordinate type.")
            return

    def save_to_file(self, filename) -> None:
        pass

    def insert_point(self, point, index_to_insert, insert_ordered = False) -> None:
        if not insert_ordered:
            self.coordinates.append((point[0], point[1], False))

    def status(self) -> float:
        """
        This is an example of Google style.

        Args:
            param1: This is the first param.
            param2: This is a second param.

        Returns:
            This is a description of what is returned.

        Raises:
            KeyError: Raises an exception.
        """
        pass

    def run(self) -> None:
        # If no coordinates are given
        if not self.coordinates:
            print("No coordinates given.")
        else:
            pass