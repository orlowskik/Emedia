import numpy as np
import zlib
# from libxmp import XMPFiles, consts
# from libxmp.utils import object_to_dict

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

    def color_type_to_bytes(self):
        match self.color:
            case 0:
                return 1
            case 2:
                return 3
            case 3:
                return 1
            case 4:
                return 2
            case 6:
                return 4
            case _:
                return None

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


class tIME(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)

        self.year = int.from_bytes(self.data[:2], 'big')
        self.month = self.data[2]
        self.day = self.data[3]
        self.hour = self.data[4]
        self.min = self.data[5]
        self.sec = self.data[6]

    def __str__(self):
        return super(tIME, self).__str__() + f'tIME modification time:{self.utc_time()}\n'

    def utc_time(self):
        month = self.month if int(self.month) > 9 else f'0{self.month}'
        day = self.day if int(self.day) > 9 else f'0{self.day}'
        hour = self.hour if int(self.hour) > 9 else f'0{self.hour}'
        minute = self.min if int(self.min) > 9 else f'0{self.min}'
        sec = self.sec if int(self.sec) > 9 else f'0{self.sec}'
        return f'{self.year}-{month}-{day}T{hour}:{minute}:{sec}'


class pHYs(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)

        self.x_pixels = int.from_bytes(self.data[:4], 'big')
        self.y_pixels = int.from_bytes(self.data[4:8], 'big')
        self.unit = 'meters' if self.data[8] else 'undefined'

    def __str__(self):
        hdpi = 'unknown'
        vdpi = 'unknown'
        if self.unit == 'meters':
            inch = 0.0254
            hdpi = round(self.x_pixels * inch)
            vdpi = round(self.y_pixels * inch)
        return super(pHYs, self).__str__() + f'pHYs information:\n' \
               + f'Horizontal: {self.x_pixels} pixels per unit (DPI: {hdpi})\n' \
               + f'Vertical: {self.y_pixels} pixels per unit (DPI: {vdpi})\n' \
               + f'Unit: {self.unit}\n'


class tEXt(Chunk):

    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)

        self.sep_index = self.data.find(b'0')
        self.keyword = self.data[:self.sep_index-1].decode('UTF-8')
        self.text = self.data[self.sep_index+1:].decode('UTF-8')

    def __str__(self):
        return super(tEXt, self).__str__() + f'Keyword: {self.keyword}\nText: {self.text}\n'


class iTXt(Chunk):

    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)

        decoded_data = self.data.decode('utf')
        sep_index1 = decoded_data.find('\x00')
        sep_index2 = decoded_data.find('\x00', sep_index1 + 3)
        sep_index3 = decoded_data.find('\x00', sep_index2 + 1)

        self.sep_index1 = sep_index1
        self.sep_index2 = sep_index2
        self.sep_index3 = sep_index3

        self.keyword = self.data[:sep_index1].decode('UTF-8')
        self.compression = self.data[sep_index1 + 1]
        self.comp_method = self.data[sep_index1 + 2]
        self.language_tag = self.data[sep_index1 + 3:sep_index2 - 1].decode('ascii')
        self.trans_keyword = self.data[sep_index2 + 1:sep_index3 - 1].decode('utf')

        self.text = zlib.decompress(self.data[sep_index3 + 1:]) if self.compression else self.data[sep_index3 + 1:]
        self.text = self.text.decode('utf')

    def __str__(self):
        return super(iTXt, self).__str__() + '\n' + self.show_data()

    def show_data(self):
        compression = str(self.compression)
        compression += ' Compressed' if self.compression else ' Uncompressed'
        method = str(self.comp_method)
        method += ' zlib datastream with deflate' if self.compression else ' Uncompressed'
        return f'Keyword: {self.keyword}\nCompression: {compression}, Compression method: {method}\n' \
               f'Language tag: {self.language_tag}\nTranslated keyword: {self.trans_keyword}\nText:\n{self.text}\n'


class XMP(Chunk):

    def __init__(self, length, chunk_type, data, crc, filename):
        super().__init__(length, chunk_type, data, crc)

        self.xmpfile = XMPFiles(file_path=filename, open_forupdate=False)
        self.xmp = self.xmpfile.get_xmp()

    def __str__(self):
        return super(XMP, self).__str__() + "This chunk includes XMP data:" + '\n\n' + self.show_data() + '\n'

    def show_data(self):
        result = ''
        xmp = object_to_dict(self.xmp)
        for key in xmp.keys():
            for prop in xmp[key]:
                result += prop[0] + ': ' + prop[1] + '\n'
        return result


class tRNS(Chunk):
    def __init__(self, length, chunk_type, data, crc):
        super().__init__(length, chunk_type, data, crc)

        self.transparency = []
        for byte in self.data:
            self.transparency.append(byte)

    def __str__(self):
        return super(tRNS, self).__str__() + 'Transparency table:\n' + self.show_data() + '\n'

    def show_data(self):
        return self.transparency.__str__()

CRITICAL = {
    b'IHDR': IHDR,
    b'IEND': IEND,
    b'IDAT': IDAT,
    b'PLTE': PLTE,
}

ANCILLARY = {
    b'tIME': tIME,
    b'pHYs': pHYs,
    b'tEXt': tEXt,
    b'iTXt': iTXt,
    b'XMP': XMP,
    b'tRNS': tRNS,

}
