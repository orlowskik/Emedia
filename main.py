from app.png import PNG


def show_menu():
    print("\nChoose an option:")
    print("1. Load an image")
    print("2. Show details about the image")
    print("3. Show image")
    print("4. Show spectrum after Fourier transform")
    print("5. Inverse Fourier transform")
    print("6. Anonymize image")
    print("7. Encrypt ECB")
    print("8. Exit")


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


def option_7(x):
    if x is not None:
        print("You chose option number 7")
        # filename = input('Encrypted file name (in ./anonymized folder) without extension: ')
        # if filename is not None:
        filename = 'test'
        x.encrypt_ECB(filename)

def main():
    x = None
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
            option_7(x)
        elif wybor == "8":
            print("Exiting.")
            break
        else:
            print("Wrong number. You must choose the number between 1 and 7")


if __name__ == "__main__":
    main()
