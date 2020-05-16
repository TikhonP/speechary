import ctypes


def main():
    f = ctypes.POINTER(ctypes.c_float)

    print(type(f))


if __name__ == '__main__':
    main()
