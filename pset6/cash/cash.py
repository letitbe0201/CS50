from cs50 import get_float

# coins we can use
coins = [25, 10, 5, 1]


def main():

    # make sure the user type a positive float num in
    while True:
        money = get_float("Change owed: ")

        if money > 0:
            # coin count from zero; money times 100 for calculation
            count = 0
            money *= 100

            # iterate each type of coin we have
            for i in coins:
                count = count + (money // i)
                money = money % i
            print(int(count))
            break


if __name__ == "__main__":
    main()