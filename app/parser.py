import zlib
import numpy as np
import matplotlib.pyplot as plt
from app.chunks import IDAT, CRITICAL, ANCILLARY, tEXt, iTXt


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
                chunk = ANCILLARY[chunk_type](length, chunk_type, data, crc)
                if isinstance(chunk, tEXt):
                    self.png.chunks_tEXt.append(chunk)
                elif isinstance(chunk, iTXt):
                    if chunk.keyword == 'XML:com.adobe.xmp':
                        xmp = ANCILLARY[b'XMP'](length, chunk_type, data, crc, self.png.filename)
                        self.png.chunks_ancillary[b'XMP'] = xmp
                else:
                    self.png.chunks_ancillary[chunk_type] = chunk
            if chunk_type == b'IEND':
                break
        if len(self.png.chunks_tEXt) != 0:
            self.png.chunks_ancillary[b'tEXT'] = self.png.chunks_tEXt

    def process_image(self):
        data = zlib.decompress(b''.join(chunk.data for chunk in self.png.chunks_IDAT))
        data_proper_length = self.png.height * (1 + self.png.width * self.png.pixel_size)
        if data_proper_length != len(data):
            raise ValueError("Decompressed image data corrupted. Data length mismatch pixels.")
        scanline = self.png.width * self.png.pixel_size

        def paeth():
            abc = [byte_a(), byte_b(), byte_c()]
            p = abc[0] + abc[1] - abc[2]
            V = np.asarray([abs(p - bt) for bt in abc])
            return abc[np.argmin(V)]

        def byte_a():
            return self.reconstructed_image[i * scanline + j - self.png.pixel_size] if j >= self.png.pixel_size else 0

        def byte_b():
            return self.reconstructed_image[(i - 1) * scanline + j] if i > 0 else 0

        def byte_c():
            return self.reconstructed_image[
                (i - 1) * scanline + j - self.png.pixel_size] if i > 0 and j >= self.png.pixel_size else 0

        n = 0
        for i in range(self.png.height):
            filter_type = data[n]
            n += 1
            for j in range(scanline):
                tmp = data[n]
                n += 1
                match filter_type:
                    case 0:
                        pass
                    case 1:
                        tmp += byte_a()
                    case 2:
                        tmp += byte_b()
                    case 3:
                        tmp += (byte_a() + byte_b()) // 2
                    case 4:
                        tmp += paeth()
                    case _:
                        raise TypeError('Unknown filter type: ' + str(filter_type))
                self.reconstructed_image.append(tmp & 0xff)

    def print_image(self):
        if self.reconstructed_image is None:
            self.process_image()

        if self.png.pixel_size == 1:
            plt.imshow(np.array(self.reconstructed_image).reshape((self.png.height, self.png.width)),
                       cmap='gray',
                       vmin=0,
                       vmax=255)
        elif self.png.pixel_size == 2:
            self.reconstructed_image = np.array(self.reconstructed_image).reshape(
                (self.png.height, self.png.width, self.png.pixel_size))
            grayscale = self.reconstructed_image[:, :, 0]
            alpha = self.reconstructed_image[:, :, 1]
            rgb_img = np.dstack((grayscale, grayscale, grayscale, alpha))
            plt.imshow(rgb_img)
        elif self.png.pixel_size in {3, 4}:
            plt.imshow(
                np.array(self.reconstructed_image).reshape((self.png.height, self.png.width, self.png.pixel_size)))
        else:
            raise ValueError(f'Number of pixels bytes must be in (1, 2, 3, 4), got {self.png.pixel_size}')
        plt.show()
