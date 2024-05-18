import base64

from app.png import PNG
from app.rsa import RSA

def show_menu():
    print("\nChoose an option:")
    print("1. Load an image")
    print("2. Show details about the image")
    print("3. Show image")
    print("4. Show spectrum after Fourier transform")
    print("5. Inverse Fourier transform")
    print("6. Anonymize image")
    print("7. Import keys")
    print("8. Encrypt ECB")
    print("9. Decrypt ECB")
    print("10. Exit")


def option_1():
    print("You chose option number 1\n")
    filename = input("Enter the file name ")
    try:
        x = PNG(filename)
    except FileNotFoundError:
        print(f"Error: file {filename} not found.")
        return None if input("Try again? [Y/n] : ") == 'n' else option_1()
    return x


def option_2(x):
    if x is not None:
        print("You chose option number 2\n")
        x.parse()
        x.describe()
        x.process_image()
        with open('test1.txt', 'wb') as f:
            f.write(base64.b64encode(bytes(x.parser.reconstructed_image)))
    else:
        print("\nYou must load the file first!")


def option_3(x):
    if x is not None:
        print("You chose option number 3\n")
        x.show_image()
    else:
        print("\nYou must load the file first!")


def option_4(x):
    if x is not None:
        print("You chose option number 4\n")
        x.show_spectrum()
    else:
        print("\nYou must load the file first!")


def option_5(x):
    if x is not None:
        print("You chose option number 5\n")
        x.show_revert_spectrum()
    else:
        print("\nYou must load the file first!")


def option_6(x):
    if x is not None:
        print("You chose option number 6")
        filename = input('Anonymized file name (in ./anonymized folder) without extension: ')
        if filename is not None:
            try:
                n = input('How many IDAT files should be considered? (default: 1) ')
                t = input('Preserve transparency if tRNS present? (default: False) [0 - False, 1 - True] ')
                slices = 1 if n == '' else int(n)
                trans = False if t == '' else bool(t)
                x.anonymize(filename, slices, trans)
            except Exception as e:
                print(f'Error occurred: {e}')
                print("File not anonymized due to error. Returning to the menu\n")

def option_7():
    key_nr = int(input('Enter key pair number from file. Must be natural [-1 for new keys]: '))
    public, private = None, None
    if key_nr == -1:
        rsa = RSA()
        public, private = rsa.generate_keys()
    elif key_nr > 0:
        with open('keys.txt', 'rb') as f:
            for index, line in enumerate(f):
                if index == key_nr - 1:
                    keys = line.split(b'\t')
                    public = tuple(keys[0].split(b':'))
                    private = tuple(keys[1].strip(b'\n').split(b':'))
                    break
    if public is None or private is None:
        print(f'One of the keys was unable to be loaded.\nPublic: {public}\nPrivate: {private}\n')
    print(f'Public: {public}\nPrivate: {private}\n')
    return public, private

def option_8(x, public):
    if x is not None and public is not None:
        print("You chose option number 8")
        filename = input('Output file name (in ./crypto folder) without extension: ')
        filename = 'crypto' if filename == '' else filename.split('.')[0]
        x.encrypt_ECB(filename, public)
    else:
        print("You did not choose file or public key")

def option_9(x, private):
    if x is not None and private is not None:
        print("You chose option number 9")
        filename = input('Output file name (in ./crypto folder) without extension: ')
        filename = 'decrypto' if filename == '' else filename.split('.')[0]
        x.decrypt_ECB(filename, private)
    else:
        print("You did not choose file or private key")

def main():
    x = None
    private = None
    public = None
    while True:
        show_menu()
        wybor = input("\nEnter the option number: ")

        if wybor == "1":
            x = option_1()
        elif wybor == "2":
            option_2(x)
        elif wybor == "3":
            option_3(x)
        elif wybor == "4":
            option_4(x)
        elif wybor == "5":
            option_5(x)
        elif wybor == "6":
            option_6(x)
        elif wybor == "7":
            public, private = option_7()
        elif wybor == "8":
            option_8(x, public)
        elif wybor == "9":
            option_9(x, private)
        elif wybor == "0":
            x = PNG('crypto/short_dice_crypted.png')
            public, private = option_7()
            option_9(x, private)
        elif wybor == "10":
            print("Exiting.")
            break
        else:
            print("Wrong number. You must choose the number between 1 and 10")


if __name__ == "__main__":
    main()
