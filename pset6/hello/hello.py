from cs50 import get_string


def main():

    # in case the user actually enter something
    while True:
        name = get_string("What is your name?\n")

        if len(name) != 0:
            print(f"hello, {name}")
            break
print(1,2)

if __name__ == "__main__":
    main()