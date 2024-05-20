from app.png import PNG
from app.rsa import RSA

class Crypto:
    def __init__(self, image=None):
        self.image = image
        self.private = None
        self.public = None

    def __str__(self):
        print("\nCRYPTO")
        print(self.image)
        print("1. Create RSA keys")
        print("2. Import keys")
        print("3. Encrypt ECB")
        print("4. Decrypt ECB")
        print("5. Encrypt CBC")
        print("6. Decrypt CBC")
        print("7. Library encryption RSA")
        print("8. Back to menu")
        print("Write 'exit' to end program")

        return ''

    def option_1(self):
        key_length = input("Enter RSA key bit length [2048-default]: ")
        common_e = input("Common e= 2^16+1? [Y/n] [Y-default]: ")
        min_e = input("Minimum e? [int >= 3] [half of len-default]")
        key_length = None if key_length == '' else int(key_length)
        common_e = None if common_e == '' else common_e
        if common_e is not None:
            common_e = False if common_e == 'n' else True
        min_e = None if min_e == '' else int(min_e)
        try:
            rsa = RSA()
            public, private = rsa.generate_keys(key_length, common_e, min_e)
            self.public = public
            self.private = private
            print('Created RSA keys successfully. Search in keys.txt')
            print(f'Public: {public}\nPrivate: {private}')
        except Exception as e:
            print(e)

    def option_2(self):
        key_nr = int(input('Enter key pair number from file. Must be natural: '))
        public, private = None, None
        try:
            if key_nr > 0:

                with open('keys.txt', 'rb') as f:
                    for index, line in enumerate(f):
                        if index == key_nr - 1:
                            keys = line.split(b'\t')
                            public = tuple(keys[0].split(b':'))
                            private = tuple(keys[1].strip(b'\n').split(b':'))
                            break
        except Exception as e:
            print(e)
        if public is None or private is None:
            print(f'One of the keys was unable to be loaded.\nPublic: {public}\nPrivate: {private}\n')
        print(f'Public: {public}\nPrivate: {private}')
        self.public = public
        self.private = private

    def option_3(self):
        if self.image is not None and self.public is not None:
            try:
                filename = input('Output file name (in ./crypto folder) without extension: ')
                filename = 'crypt_ecb' if filename == '' else filename.split('.')[0]
                self.image.encrypt_ECB(filename, self.public)
                print('Encrypted file')
            except Exception as e:
                print(e)
        else:
            print("You did not choose file or public key")

    def option_4(self):
        if self.image is not None and self.private is not None:
            try:
                filename = input('Output file name (in ./crypto folder) without extension: ')
                filename = 'decrypt_ecb' if filename == '' else filename.split('.')[0]
                self.image.decrypt_ECB(filename, self.private)
                print('Decrypted file')
            except Exception as e:
                print(e)
        else:
          print("You did not choose file or private key")

    def option_5(self):
        if self.image is not None and self.public is not None:
            try:
                filename = input('Output file name (in ./crypto folder) without extension: ')
                filename = 'crypt_cbc' if filename == '' else filename.split('.')[0]
                self.image.encrypt_CBC(filename, self.public)
                print('Encrypted file')
            except Exception as e:
                print(e)
        else:
            print("You did not choose file or public key")

    def option_6(self):
        if self.image is not None and self.private is not None:
            try:
                filename = input('Output file name (in ./crypto folder) without extension: ')
                filename = 'decrypt_cbc' if filename == '' else filename.split('.')[0]
                self.image.decrypt_CBC(filename, self.private)
                print('Decrypted file')
            except Exception as e:
                print(e)
        else:
          print("You did not choose file or private key")

    def option_7(self):
        if self.image is not None and self.public is not None:
            try:
                filename = input('Output file name (in ./crypto folder) without extension: ')
                filename = 'crypt_library_rsa' if filename == '' else filename.split('.')[0]
                self.image.library_encryption_RSA(filename, self.public)
                print('Encrypted file')
            except Exception as e:
                print(e)
        else:
            print("You did not choose file or public key")

    def chose(self, option):
        match option:
            case '1':
                self.option_1()
                return False
            case '2':
                self.option_2()
                return False
            case '3':
                self.option_3()
                return False
            case '4':
                self.option_4()
                return False
            case '5':
                self.option_5()
                return False
            case '6':
                self.option_6()
            case '7':
                self.option_7()
                return False
            case '8':
                return True
            case _:
                print('Unknown function\n')
                return False