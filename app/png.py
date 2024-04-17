from app.parser import Parser
from app.fourier import Fourier
from app.chunks import IEND


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

        self.width = None
        self.height = None
        self.pixel_size = None

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
                print(chunk)

    def process_image(self):
        self.parser.process_image()

        plte = self.chunks_critical.get(b'PLTE', None)
        if plte:
            palette = plte.create_palette()
            self.parser.reconstructed_image = [pixel
                                               for index in self.parser.reconstructed_image
                                               for pixel in palette[index]]
        self.pixel_size = 3

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

    def anonymize(self, filename):
        basedir = 'anonymize/'

        with open(basedir + filename, 'wb') as f:
            f.write(self.parser.magic_number)
            chunks = list(self.chunks_critical.values())
            for idat in self.chunks_IDAT:
                chunks.insert(-1, idat)
            print(chunks)
            for chunk in chunks:
                f.write(chunk.length)
                f.write(chunk.type)
                f.write(chunk.data)
                f.write(chunk.crc)

    def __str__(self):
        return f'PNG file: {self.filename}.'
