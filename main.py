from front.index import Menu
from front.crypto import Crypto

def main():
    index = Menu()
    crypto = Crypto()
    current = index
    while True:
        print(current)
        option = input("Chose option: ")
        if option == 'exit':
            print('Ending program\n')
            break
        if current.chose(option):
            current = crypto if isinstance(current, Menu) else index
            crypto.image = index.image
            continue
        input('Press Enter to continue...\n')
if __name__ == "__main__":
    main()
