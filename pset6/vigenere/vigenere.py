from cs50 import get_string
from sys import argv
import sys


def main():

    if (len(argv) == 2 and argv[1].isalpha()):

        # count for ith alphabet
        alphCount = 0
        key = argv[1]
        # prompt plaintext from the user
        plainText = get_string("plaintext: ")
        print("ciphertext: ", end="")

        # iterate every character in the plaintext
        for i in range(len(plainText)):
            p = plainText[i]
            if p.isalpha():
                c = cipher(p, alphCount, key)
                print(c, end="")
                # +1 only if the character is an letter
                alphCount += 1
            else:
                # print the char directly
                print(plainText[i], end="")

        print("")

    else:
        print('Usage: python vigenere.py "KEY"')
        sys.exit(1)


def cipher(p, alphCount, key):

    # calculate which char in key should we take
    indexK = alphCount % len(key)
    # calculate the moving distance from plaintext char by the key char
    k = ord(key[indexK].upper()) - 65

    # calculate for the ciphertext
    if p.isupper():
        c = chr(65 + ((ord(p) - 65) + k) % 26)
    else:
        c = chr(97 + ((ord(p) - 97) + k) % 26)

    return c


if __name__ == "__main__":
    main()