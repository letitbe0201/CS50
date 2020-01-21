from cs50 import get_string
from sys import argv
# for sys.exit()
import sys
# for re.split
import re


def main():

    # make sure the user type correctly
    if len(argv) != 2:
        print("Usage: python bleep.py dictionary")
        sys.exit(1)

    # oepn and store the banned words in a list
    file = open(argv[1], 'r')
    bannedList = list(file)

    userMessage = get_string("What message would you like to censor?\n")

    # convert the messege to lowercase
    loweredMessage = userMessage.lower
    # get a list of each word and the delimiter
    messageList = re.split('(\W+)', userMessage)
    # print(messageList)

    # iterate over all the words in the message
    for word in messageList:
        # the word is found in the banned file or not
        found = 0
        # looking up the banned words file
        for bannedWord in bannedList:
            if (bannedWord.strip('\n') == word.lower()):
                # banned word found, printing the *
                for i in range(len(word)):
                    print("*", end="")
                found = 1
                break
        # if the word isn't banned, then print the word directly
        if found == 0:
            print(f"{word}", end="")
    print("")


if __name__ == "__main__":
    main()
