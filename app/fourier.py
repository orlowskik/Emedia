import numpy as np
import matplotlib.pyplot as plt


class Fourier:
    def __init__(self, filename=None):
        try:
            image_temp = plt.imread(filename)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: {e}")

        self.image = image_temp[:, :, :3].mean(axis=2)
        self.fft_transform = None
        self.fft_shifted = None
        self.magnitude_spectrum = None

    def transform(self):
        self.fft_transform = np.fft.fft2(self.image)
        self.fft_shifted = np.fft.fftshift(self.fft_transform)
        self.magnitude_spectrum = np.log(np.abs(self.fft_shifted))

    def show(self):
        try:
            plt.subplot(1, 2, 1), plt.imshow(self.image, cmap='gray')
            plt.title('Original image'), plt.xticks([]), plt.yticks([])
            plt.subplot(1, 2, 2), plt.imshow(self.magnitude_spectrum, cmap='gray')
            plt.title('Image spectrum'), plt.xticks([]), plt.yticks([])
            plt.show()
        except AttributeError:
            raise ValueError(f'Error using function: magnitude_spectrum has no value')

    def invert_and_show(self):
        try:
            fft_unshifted = np.fft.ifftshift(self.fft_shifted)
            ifft = np.fft.ifft2(fft_unshifted)
            image = np.abs(ifft)
            plt.imshow(image, cmap='gray'), plt.xticks([]), plt.yticks([])
            plt.title('Image after reversed transformation')
            plt.show()
        except ValueError:
            raise ValueError(f'Error using function: fft_shifted has no value')
