from app.png import PNG
import base64

class Menu:
    def __init__(self):
        self.image = PNG()

    def __str__(self):
        print("\nChoose an option:")
        print(self.image)
        print("1. Load an image")
        print("2. Show details about the image")
        print("3. Show image")
        print("4. Show spectrum after Fourier transform")
        print("5. Inverse Fourier transform")
        print("6. Anonymize image")
        print("7. Crypto")
        print("Write 'exit' to end program")

        return ''

    def option_1(self):
        print("You chose option number 1")
        filename = input("Enter the file name ")
        try:
            self.image.load_file(filename)
            print("Image loaded successfully")
        except FileNotFoundError:
            print(f"Error: file {filename} not found.")
            if input("Try again? [Y/n] : ") == 'Y': self.option_1()

    def option_2(self):
        if self.image is not None:
            print("You chose option number 2")
            self.image.parse()
            self.image.describe()
        else:
            print("You must load the file first!")


    def option_3(self):
        if self.image is not None:
            print("You chose option number 3")
            self.image.show_image()
            self.image.cleanup()
        else:
            print("You must load the file first!")


    def option_4(self):
        if self.image is not None:
            print("You chose option number 4")
            self.image.show_spectrum()
        else:
            print("You must load the file first!")


    def option_5(self):
        if self.image is not None:
            print("You chose option number 5")
            self.image.show_revert_spectrum()
        else:
            print("You must load the file first!")


    def option_6(self):
        if self.image is not None:
            print("You chose option number 6")
            filename = input('Anonymized file name (in ./anonymized folder) without extension: ')
            if filename is not None:
                try:
                    n = input('How many IDAT files should be considered? (default: 1) ')
                    t = input('Preserve transparency if tRNS present? (default: False) [0 - False, 1 - True] ')
                    slices = 1 if n == '' else int(n)
                    trans = False if t == '' else bool(t)
                    self.image.anonymize(filename, slices, trans)
                    print('Anonymized file name: ' + filename)
                except Exception as e:
                    print(f'Error occurred: {e}')
                    print("File not anonymized due to error. Returning to the menu")


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
                return True
            case _ :
                print('Unknown function\n')
                return False
