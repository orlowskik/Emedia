from app.parser import Parser
from app.chunks import IHDR


class PNG:

    def __init__(self, filename=None):
        print(f'Opening {filename}')

        try:
            self.file = open(filename, 'rb')
            self.file.read().hex()
        except (IOError, TypeError) as e:
            raise FileNotFoundError(f'Error opening {filename}: {e}')

        self.parser = None
        self.chunks_critical = {}
        self.chunks_ancillary = {}
        self.chunks_IDAT = []

        self.width = None
        self.height = None
        self.pixel_size = None

    def __del__(self):
        if not self.file.closed:
            self.file.close()

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

    def show_image(self):
        if self.parser is None:
            self.parse()
        self.parser.process_image()
        self.parser.print_image()

    def __str__(self):
        return 'Returns a string representation of class'
