from app.png import PNG


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    x = PNG('files/plte.png')
    x.parse()
    x.describe()
    x.show_image()


if __name__ == '__main__':
    print_hi('PyCharm')
