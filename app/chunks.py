import numpy as np


class Chunk:

    def __init__(self, length, chunk_type, data, crc):
        self.length = length
        self.type = chunk_type
        self.data = data
        self.crc = crc

    def __str__(self):
        return f"Data of chunk {self.type}\n\n" \
               f"Length: {int.from_bytes(self.length, 'big')}; Type: {self.type};\nData: {self.data.hex(' ')};\n" \
               f"CRC: {self.crc.hex(' ')}\n\n"


class IHDR(Chunk):

    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)

        self.width = int.from_bytes(self.data[:4], 'big')
        self.height = int.from_bytes(self.data[4:8], 'big')
        self.depth = self.data[8]
        self.color = self.data[9]
        self.compression = self.data[10]
        self.filter_method = self.data[11]
        self.interlace = self.data[12]

    def __str__(self):
        data = f"The IHDR chunk has the following information:\n" \
               f"image size - {self.width}x{self.height}\n" \
               f"bit depth - {self.depth}\n" \
               f"color type - {self.color}\n" \
               f"compression method - {self.compression}\n" \
               f"filter method - {self.filter_method}\n" \
               f"interlace method - {self.interlace}\n"
        return super(IHDR, self).__str__() + data


class IEND(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)

    def __str__(self):
        data = f"The IEND chunk ends the file. Data field length:{int.from_bytes(self.length, 'big')}\n"
        return super(IEND, self).__str__() + data


class IDAT(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)

    def __str__(self):
        return f"Chunk IDAT without data (unreadable):\n\n" \
               f"Length:{int.from_bytes(self.length, 'big')}; " \
               f"Type:{self.type}; CRC:{self.crc.hex(' ')}\n"


class PLTE(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)

    def __str__(self):
        palette = self.create_palette()
        return super(PLTE, self).__str__() + f'\n PLTE palette:\nnumber of entries: {len(palette)}\n Data:{palette}'

    def create_palette(self):
        length = int.from_bytes(self.length, 'big')
        if length % 3:
            raise ValueError(f'Error:[{self.type}] Length must be a multiple of 3')
        decimal = np.array([int(entry, 16) for entry in self.data.hex(' ').split(' ')]).reshape((length // 3, 3))
        return [tuple(entry) for entry in decimal]


CRITICAL = {
    b'IHDR': IHDR,
    b'IEND': IEND,
    b'IDAT': IDAT,
    b'PLTE': PLTE
}

ANCILLARY = {

}
