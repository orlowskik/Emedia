from app.parser import Parser


class PNG:

    def __init__(self, filename=None):
        print(f'Opening {filename}')

        try:
            self.file = open(filename, 'rb')
            self.file.read().hex()
        except (IOError, TypeError) as e:
            print(f'Error opening {filename}: {e}')

        self.parser = None
        self.chunks_critical = {}
        self.chunks_ancillary = {}
        self.chunks_IDAT = []

    def parse(self):
        self.parser = Parser(self)
        self.parser.find_chunks()

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

    def __str__(self):
        return 'Returns a string representation of class'
