from nltk.tokenize import sent_tokenize


def lines(a, b):
    """Return lines in both a and b"""
    # split the string into sets(a list without duplicate) of lines
    setA = set(a.split('\n'))
    setB = set(b.split('\n'))
    # & look for the element appears both in a and b
    return list(setA & setB)


def sentences(a, b):
    """Return sentences in both a and b"""
    # tokenize two input string and remove the duplicate sentences
    setA = set(sent_tokenize(a, language='english'))
    setB = set(sent_tokenize(b, language='english'))
    # & look for the element appears both in a and b
    return list(setA & setB)


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""
    # slice each string with a factor n and save them in a set
    setA = set([a[i:i+n] for i in range(len(a)-n+1)])
    setB = set([b[i:i+n] for i in range(len(b)-n+1)])
    # & look for the element appears both in a and b
    return list(setA & setB)
