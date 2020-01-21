from cs50 import get_int


def main():

    # make sure the user enter the valid input
    while True:
        height = get_int("Height: ")

        # print the pyramid
        if height >= 1 and height <= 8:
            for i in range(1, height + 1):
                for j in range(height - i):
                    print(" ", end="")
                for k in range(i):
                    print("#", end="")
                print("  ", end="")
                for l in range(i):
                    print("#", end="")
                print("")
            break


if __name__ == "__main__":
    main()