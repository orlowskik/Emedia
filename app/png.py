from app.parser import Parser


class PNG:

    def __init__(self, filename=None):
        print(f'Opening {filename}')

        try:
            self.file = open(filename, 'rb')
            self.file.read().hex()
        except (IOError, TypeError) as e:
            print(f'Error opening {filename}: {e}')

        self.chunks_critical = []
        self.chunks_ancillary = []

    def parse(self):
        parser = Parser(self)
        parser.find_chunks()

    def describe(self):
        print('Critical chunks:\n')
        for chunk in self.chunks_critical:
            print(chunk)
        print('Ancillary chunks:\n')
        for chunk in self.chunks_ancillary:
            print(chunk)

    def __str__(self):
        return 'Returns a string representation of class'
