from app.png import PNG
from app.fourier import Fourier


def print_hi(name):
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
