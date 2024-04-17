from app.png import PNG
from app.fourier import Fourier


def print_hi(name):
    x = PNG('files/linux.png')
    x.parse()
    x.describe()

    x.show_image()
    x.show_spectrum()
    x.show_revert_spectrum()


if __name__ == '__main__':
    print_hi('PyCharm')
