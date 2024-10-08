from app.parser import Parser
from app.fourier import Fourier
from app.chunks import IDAT
import numpy as np


class PNG:

    def __init__(self, filename=None):
        print(f'Opening {filename}')
        self.filename = filename

        try:
            self.file = open(filename, 'rb')
            self.file.read().hex()
        except (IOError, TypeError) as e:
            raise FileNotFoundError(f'Error opening {filename}: {e}')

        self.parser = None
        self.fourier = None

        self.chunks_critical = {}
        self.chunks_ancillary = {}
        self.chunks_IDAT = []
        self.chunks_tEXt = []

        self.width = None
        self.height = None
        self.pixel_size = None
        self.alpha = None

    def __del__(self):
        try:
            if not self.file.closed:
                self.file.close()
        except (Exception, AttributeError):
            pass

    def parse(self):
        self.parser = Parser(self)
        self.parser.find_chunks()

        ihdr = self.chunks_critical.get(b'IHDR', None)
        if not ihdr:
            raise AttributeError('IHDR not found')

        self.width = ihdr.width
        self.height = ihdr.height
        self.pixel_size = ihdr.color_type_to_bytes()

        if self.width < 1:
            raise ValueError(f'Width must be positive, got {self.width}')
        if self.height < 1:
            raise ValueError(f'Height must be positive, got {self.height}')
        if self.pixel_size is None or self.pixel_size not in {1, 2, 3, 4}:
            raise ValueError(f'Number of pixels bytes must be in (1, 2, 3, 4), got {self.pixel_size}')

    def describe(self):
        print('Critical chunks:\n')
        for chunk in self.chunks_critical.values():
            print(chunk)
        for index, chunk in enumerate(self.chunks_IDAT):
            print(f'IDAT{index + 1}\n{chunk}')
        print('Ancillary chunks:\n')
        if len(self.chunks_ancillary) == 0:
            print('None')
        else:
            for chunk in self.chunks_ancillary.values():
                if isinstance(chunk, list):
                    print('tEXt chunks:\n')
                    for index, text in enumerate(chunk):
                        print(f'tEXt{index + 1}\n{text}')
                else:
                    print(chunk)

    def process_image(self):
        self.parser.process_image()

        ihdr = self.chunks_critical.get(b'IHDR', None)
        if not ihdr:
            raise AttributeError('IHDR not found')

        trns = self.chunks_ancillary.get(b'tRNS', None)
        match ihdr.color:
            case 0:
                if trns:
                    self.alpha = [1] * len(self.parser.reconstructed_image)
                    for i in range(len(self.alpha)):
                        if self.parser.reconstructed_image[i] == trns.transparency[0]:
                            self.alpha[i] = 0
            case 3:
                plte = self.chunks_critical.get(b'PLTE', None)
                if plte:
                    palette = plte.create_palette()
                    if trns:
                        size = len(palette) - len(trns.transparency)
                        trns.transparency.extend([255] * size )
                        for i in range(len(palette)):
                            palette[i] += (trns.transparency[i],)
                        print(palette)
                    self.parser.reconstructed_image = [pixel
                                                       for index in self.parser.reconstructed_image
                                                       for pixel in palette[index]]
                    self.pixel_size = 4 if trns else 3

    def show_image(self):
        if self.parser is None:
            self.parse()
        if len(self.parser.reconstructed_image) == 0:
            self.process_image()

        self.parser.print_image()

    def fourier_transform(self):
        self.fourier = Fourier(self.filename)

    def show_spectrum(self):
        if self.fourier is None:
            self.fourier_transform()

        self.fourier.transform()
        self.fourier.show()

    def show_revert_spectrum(self):
        if self.fourier is None:
            self.fourier_transform()

        if self.fourier.fft_shifted is None:
            self.fourier.transform()

        self.fourier.invert_and_show()

    def resize_data(self, slices, chunks):
        data = b''
        for idat in self.chunks_IDAT:
            data += idat.data
        slice_len = len(data) // slices
        if slice_len == 0:
            raise ValueError(f'Number of slices greater than number of bytes. Data length: {len(data)}')
        rest = len(data) % slices
        slice_last = len(data) - slice_len * (slices - 1) if rest else slice_len

        length = slice_len.to_bytes(length=4)
        for i in range(slices):
            if i == slices - 1:
                data_slice = data[slice_len * i:slice_len * i + slice_last]
                length = slice_last.to_bytes(length=4)
            else:
                data_slice = data[slice_len * i:slice_len * i + slice_len]
            idat = IDAT(length, b'IDAT', data_slice, self.chunks_IDAT[0].crc)
            chunks.insert(-1, idat)

    def anonymize(self, filename, slices=1, transparent=False):
        basedir = 'anonymized/'

        if self.parser is None:
            self.parse()

        with open(basedir + filename + '.png', 'wb') as f:
            f.write(self.parser.magic_number)
            chunks = list(self.chunks_critical.values())
            if (trns := self.chunks_ancillary.get(b'tRNS', None)) and transparent:
                chunks.insert(-1, trns)
            self.resize_data(slices, chunks)
            for chunk in chunks:
                f.write(chunk.length)
                f.write(chunk.type)
                f.write(chunk.data)
                f.write(chunk.crc)

    def __str__(self):
        return f'PNG file: {self.filename}.'
