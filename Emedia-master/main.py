from app.png import PNG
from app.fourier import Fourier

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    x = PNG('files/dog_rgba.png')
    x.parse()
    x.describe()
    x.show_image()

    y = Fourier('files/dog_rgba.png')
    y.transform()
    y.show()
    y.invert_and_show()

if __name__ == '__main__':
    print_hi('PyCharm')
