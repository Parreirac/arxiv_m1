"""
Then the text extraction can have extra \n and spaces, this find handle them
"""

def Myfind(text: str, sub: str, caseSensitive=True, start:int=None, end:int=None, Reverse = False):  # TODO Reverse
    i = 0  # start index in text string
    ic = 0  # current index in text string
    j = 0  # current index in substring



    imax = len(text)
    jmax = len(sub)

    if not end is None:
        imax = min(imax, end)
    if not start is None:
        i = max(i, start)

    if Reverse:
        rv_b,rv1,rv2 = Myfind(text[::-1], sub[::-1], caseSensitive,start=start, end=end, Reverse = False)
        if rv_b:
            return True,imax-rv2,imax-rv1   # TODO PRA verifier sur un exemple
        else:
            return False,-1,-1

    while i < imax and text[i] != sub[j]:
        i += 1

    if i == imax:  # sub can't be in text
        return False, -1, -1



    while i + ic < imax and j < jmax:
        leftChar = text[i + ic]
        rightChar = sub[j]

        if leftChar == rightChar:  # simple case !
            ic += 1
            j += 1
            continue

        if leftChar == '\n' and rightChar == ' ':
            ic += 1
            j += 1
            continue

        if leftChar == '\n':
            ic += 1
            continue

        if leftChar.lower() == rightChar.lower() and not caseSensitive:
            ic += 1
            j += 1
            continue

        if leftChar == ' ':  # probably an extra ' ' in text
            ic += 1
            continue

        i += 1  # mismatch retry
        ic = 0
        j = 0

    return (i + ic < imax and j == jmax), i, i + ic
