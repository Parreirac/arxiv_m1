"""
In pdf file we have different objets.
Then the text extraction can have extra \n and spaces.

"""


def Myfind(text:str, sub:str, caseSensitive = True, start=None, end=None):   # TODO gerer la case
    i = 0 # start index in text string
    ic = 0 # current index in text string
    j = 0 # current index in substring

    i1 = len(text)
    text = text.replace('ﬁ', 'fi') # todo pra faire plus propre
    text = text.replace('ﬂ', 'fl')  # todo pra faire plus propre

    i2 = len(text)

    if i1 != i2:
        pass


    imax = len(text)
    jmax = len(sub)

    while text[i] != sub[j] and i < imax:
        i+=1

    if i == imax: # sub can't be in text
       return False,-1,-1

    while i + ic < imax and j < jmax:
        leftChar= text[i+ic]
        rightChar= sub[j]

        if leftChar == rightChar: # simple case !
            ic+=1
            j+=1
            continue

        if leftChar == '\n'and rightChar == ' ':
            ic+=1
            j+=1
            continue

        if leftChar == '\n':
            ic+=1
            continue

        if leftChar.lower() == rightChar.lower() and not caseSensitive:
            ic += 1
            j += 1
            continue

        if leftChar == ' ': # probably an extra ' ' in text
            ic += 1
            continue

        i +=1 # mismatch retry
        ic= 0
        j = 0



    return (i + ic < imax and j == jmax),i,i+ic

