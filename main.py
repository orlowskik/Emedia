from app.png import PNG

def show_menu():
    print("\nChoose an option:")
    print("1. Load an image")
    print("2. Show details about the image")
    print("3. Show image")
    print("4. Show spectrum after Fourier transform")
    print("5. Inverse Fourier transform")
    print("6. ")
    print("7. Wyjście")

def option_1():
    print("You chose option number 1")
    filename = input("Enter the file name \n")
    x = PNG('files/' + filename)
    return x

def option_2(x):
    if x != None:
        print("You chose option number 2")
        x.parse()
        x.describe()
    else:
        print("\nYou must load the file first!\n")

def option_3(x):
    if x != None:
        print("You chose option number 3")
        x.show_image()
    else:
        print("\nYou must load the file first!\n")        

def option_4(x):
    if x != None:
        print("You chose option number 4")
        x.show_spectrum()
    else:
        print("\nYou must load the file first!\n")  

def option_5(x):
    if x != None:
        print("You chose option number 5")
        x.show_revert_spectrum()
    else:
        print("\nYou must load the file first!\n")  

def option_6(x):
    print("You chose option number 6")


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
            print("Exiting.")
            break
        else:
            print("Wrong number. You must choose the number between 1 and 7")

if __name__ == "__main__":
    main()