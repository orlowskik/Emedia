import math
import zlib
import base64
import numpy as np
import secrets

from pathlib import Path

from app.parser import Parser
from app.fourier import Fourier
from app.chunks import IDAT, tEXt
from app.rsa import RSA



class PNG:

    def __init__(self, filename=None):
        print(f'Opening {filename}')
        self.filename = filename
        self.file = None

        self.load_file()

        self.parser = None
        self.fourier = None
        self.processed = False

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

    def load_file(self, filename=None):
        if filename is not None:
            to_open = filename
        elif self.filename is None:
            return
        else:
            to_open = self.filename
        try:
            self.file = open(to_open, 'rb')
            self.filename = to_open
            self.cleanup()
        except (IOError, TypeError) as e:
            raise FileNotFoundError(f'Error opening {to_open}: {e}')

    def cleanup(self):
        self.parser = None
        self.fourier = None
        self.processed = False

        self.chunks_critical = {}
        self.chunks_ancillary = {}
        self.chunks_IDAT = []
        self.chunks_tEXt = []

        self.width = None
        self.height = None
        self.pixel_size = None
        self.alpha = None

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
        if self.processed:
            return
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
                        trns.transparency.extend([255] * size)
                        for i in range(len(palette)):
                            palette[i] += (trns.transparency[i],)
                    self.parser.reconstructed_image = [pixel
                                                       for index in self.parser.reconstructed_image
                                                       for pixel in palette[index]]
                    self.pixel_size = 4 if trns else 3
        self.processed = True

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

    def resize_data(self, slices, chunks, data):
        slice_len = len(data) // slices
        if slice_len == 0:
            raise ValueError(f'Number of slices greater than number of bytes. Data length: {len(data)}')
        rest = len(data) % slices
        slice_last = len(data) - slice_len * (slices - 1) if rest else slice_len

        length = slice_len.to_bytes(length=4, byteorder='big')
        for i in range(slices):
            if i == slices - 1:
                data_slice = data[slice_len * i:slice_len * i + slice_last]
                length = slice_last.to_bytes(length=4, byteorder='big')
            else:
                data_slice = data[slice_len * i:slice_len * i + slice_len]
            idat = IDAT(length, b'IDAT', data_slice, secrets.token_bytes(4))
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
            data = b''
            for idat in self.chunks_IDAT:
                data += idat.data
            self.resize_data(slices, chunks, data)
            for chunk in chunks:
                f.write(chunk.length)
                f.write(chunk.type)
                f.write(chunk.data)
                f.write(chunk.crc)

    def encrypt_ECB(self, filename, public_key=None):
        basedir, rsa = self.init_encryption(public_key)
        cipher, extended = rsa.encrypt_ECB(self.parser.reconstructed_image)

        keyword = b'EXTENSION'
        data = keyword + b'\x00' + base64.b64encode(bytes(extended))
        ext_data = tEXt(len(data).to_bytes(4, 'big'), b'tEXt', data, secrets.token_bytes(4))

        chunks = self.prepare_data(cipher)
        chunks.insert(-1, ext_data)

        self.create_file(basedir, filename, chunks)

    def decrypt_ECB(self, filename, private_key=None):
        original_len = self.height * self.width * self.pixel_size

        basedir, rsa, extension = self.init_decryption(private_key)

        if extension is None:
            raise ValueError('Extension chunk must be specified to decipher. File corrupted')

        extended_data = base64.b64decode(extension.text)

        decrypted_data = rsa.decrypt_ECB(data=self.parser.reconstructed_image, extended_bytes=extended_data,
                                         original_data_length=original_len)

        chunks = self.prepare_data(decrypted_data)
        self.create_file(basedir, filename, chunks)

    def encrypt_CBC(self, filename, private_key=None):
        basedir, rsa = self.init_encryption(private_key)
        cipher, extended, init_vector = rsa.encrypt_CBC(self.parser.reconstructed_image)

        keyword = b'EXTENSION'
        data = keyword + b'\x00' + base64.b64encode(init_vector + bytes(extended))
        ext_data = tEXt(len(data).to_bytes(4, 'big'), b'tEXt', data, secrets.token_bytes(4))

        chunks = self.prepare_data(cipher)
        chunks.insert(-1, ext_data)

        self.create_file(basedir, filename, chunks)

    def decrypt_CBC(self, filename, private_key=None):
        basedir, rsa, extension = self.init_decryption(private_key)
        original_len = self.height * self.width * self.pixel_size

        if extension is None:
            raise ValueError('Extension chunk must be specified to decipher. File corrupted')

        text = base64.b64decode(extension.text)
        initial_vector = text[:rsa.block_bytes_size + 1]
        extended_data = text[rsa.block_bytes_size + 1:]


        decrypted_data = rsa.decrypt_CBC(data=self.parser.reconstructed_image, extended_bytes=extended_data,
                                         original_data_length=original_len, init_vector=initial_vector)

        chunks = self.prepare_data(decrypted_data)
        self.create_file(basedir, filename, chunks)

    def init_encryption(self, public_key=None):
        basedir = 'crypto/'

        if public_key is None:
            rsa = RSA()
            rsa.generate_keys(common_e=True)
        elif not isinstance(public_key, int):
            public_key = int.from_bytes(base64.b64decode(public_key[0]), 'big'), int.from_bytes(
                base64.b64decode(public_key[1]), 'big')
            rsa = RSA(public_key=public_key)
        else:
            rsa = RSA(public_key=public_key)

        if self.parser is None:
            self.parse()

        if not self.processed:
            self.process_image()

        return basedir, rsa

    def init_decryption(self, private_key=None):
        basedir = 'crypto/'
        extension = None

        if private_key is None:
            raise ValueError('Private key must be specified')
        if not isinstance(private_key, int):
            private_key = int.from_bytes(base64.b64decode(private_key[0]), 'big'), int.from_bytes(
                base64.b64decode(private_key[1]), 'big')
            rsa = RSA(private_key=private_key)
        else:
            rsa = RSA(private_key=private_key)

        if self.parser is None:
            self.parse()

        if not self.processed:
            self.process_image()

        for chunk in self.chunks_tEXt:
            if chunk.keyword == 'EXTENSION':
                extension = chunk
                break

        return basedir, rsa, extension

    def prepare_data(self, data):
        chunks = list(self.chunks_critical.values())
        slices = len(self.chunks_IDAT)

        for i in range(self.height):
            data.insert(i * self.width * self.pixel_size + i, 0)
        compressed = zlib.compress(bytes(data))

        for anc in self.chunks_ancillary.values():
            if not isinstance(anc, list):
                chunks.insert(-1, anc)

        self.resize_data(slices, chunks, compressed)
        for txt in self.chunks_tEXt:
            if txt.keyword != 'EXTENSION':
                chunks.insert(-1, txt)
        return chunks

    def create_file(self, basedir, filename, chunks):
        with open(basedir + filename + '.png', 'wb') as f:
            f.write(self.parser.magic_number)
            for chunk in chunks:
                f.write(chunk.length)
                f.write(chunk.type)
                f.write(chunk.data)
                f.write(chunk.crc)

    def __str__(self):
        return f'PNG file: {self.filename}.'
