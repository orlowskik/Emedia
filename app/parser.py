from app.chunks import IHDR, CRITICAL, ANCILLARY


class Parser:

    def __init__(self, png_object=None):
        self.CHUNK_BASE_LENGTH = 4
        if png_object is None:
            raise ValueError
        else:
            self.png = png_object
        self.magic_number = b'\x89PNG\r\n\x1a\n'

        if not self.validate():
            raise TypeError(f'Error: [{png_object.file.name}] is not a valid png file')

    def __str__(self):
        return f"Parsing file: {self.png.file.name}"

    def validate(self):
        self.png.file.seek(0)
        if self.png.file.read(len(self.magic_number)) != self.magic_number:
            return False
        return True

    def find_chunks(self):
        self.png.file.seek(len(self.magic_number))
        while True:
            length = self.png.file.read(self.CHUNK_BASE_LENGTH)
            chunk_type = self.png.file.read(self.CHUNK_BASE_LENGTH)
            data = self.png.file.read(int.from_bytes(length, 'big'))
            crc = self.png.file.read(self.CHUNK_BASE_LENGTH)

            if chunk_type in CRITICAL.keys():
                self.png.chunks_critical.append(CRITICAL[chunk_type](length, chunk_type, data, crc))
            elif chunk_type in ANCILLARY.keys():
                self.png.chunks_ancillary.append(ANCILLARY[chunk_type](length, chunk_type, data, crc))

            if chunk_type == b'IEND':
                break
