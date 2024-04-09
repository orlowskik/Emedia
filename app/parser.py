import zlib
import numpy as np
import matplotlib.pyplot as plt
from app.chunks import IDAT, CRITICAL, ANCILLARY


class Parser:

    def __init__(self, png_object=None):
        self.CHUNK_BASE_LENGTH = 4
        if png_object is None:
            raise ValueError
        else:
            self.png = png_object
        self.magic_number = b'\x89PNG\r\n\x1a\n'
        self.reconstructed_image = []

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
                chunk = CRITICAL[chunk_type](length, chunk_type, data, crc)
                if isinstance(chunk, IDAT):
                    self.png.chunks_IDAT.append(chunk)
                else:
                    self.png.chunks_critical[chunk_type] = chunk
            elif chunk_type in ANCILLARY.keys():
                self.png.chunks_ancillary.append(ANCILLARY[chunk_type](length, chunk_type, data, crc))

            if chunk_type == b'IEND':
                break

    def process_image(self):
        color_type = {
            0: 1,
            2: 3,
            3: 1,
            4: 2,
            6: 4
        }
        chunk_ihdr = self.png.chunks_critical.get(b'IHDR', None)
        if chunk_ihdr is None:
            raise ValueError("No IHDR chunk")
        else:
            pixel_size = color_type[chunk_ihdr.color]

        width, height = chunk_ihdr.width, chunk_ihdr.height

        data = zlib.decompress(b''.join(chunk.data for chunk in self.png.chunks_IDAT))
        data_proper_length = height * (1 + width * pixel_size)
        if data_proper_length != len(data):
            raise ValueError("Decompressed image data corrupted. Data length mismatch pixels.")

        def paeth():
            abc = recon_a(), recon_b(), recon_c()
            p = abc[0] + abc[1] - abc[2]
            return abc[int(np.argmin([abs(p - abc[0]), abs(p - abc[1]), abs(p - abc[2])]))]

        def recon_a():
            return self.reconstructed_image[i * line_width + j - pixel_size] if j >= pixel_size else 0

        def recon_b():
            return self.reconstructed_image[(i - 1) * line_width + j] if i > 0 else 0

        def recon_c():
            return self.reconstructed_image[(i - 1) * line_width + j - pixel_size] if i > 0 and i >= pixel_size else 0

        line_width = width * pixel_size
        for i in range(height):
            base = i * (line_width + 1)
            filter_type = data[base]
            for j in range(line_width):
                filt_x = data[base + j + 1]
                match filter_type:
                    case 0:
                        recon_x = filt_x
                    case 1:
                        recon_x = filt_x + recon_a()
                    case 2:
                        recon_x = filt_x + recon_b()
                    case 3:
                        recon_x = filt_x + (recon_a() + recon_b()) // 2
                    case 4:
                        recon_x = filt_x + paeth()
                    case _:
                        raise Exception('unknown filter type: ' + str(filter_type))
                self.reconstructed_image.append(recon_x & 0xff)  # truncation to byte

        plt.imshow(np.array(self.reconstructed_image).reshape((chunk_ihdr.height, chunk_ihdr.width, pixel_size)))
        plt.show()
