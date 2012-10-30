import difflib

from . import (
    weights, fuelTanks, lfe
)


ALL = []
ALL.extend(weights.ALL)
ALL.extend(fuelTanks.ALL)
ALL.extend(lfe.ALL)

def findByName(name):
    matcher = difflib.SequenceMatcher()
    matcher.set_seq1(name.lower())

    weighted = []
    for el in ALL:
        matcher.set_seq2(el.name.lower())
        weighted.append((matcher.ratio(), el))

    weighted.sort(key=lambda el: el[0], reverse=True)

    (weight1, best1) = weighted[0]
    (weight2, best2) = weighted[1]

    if (weight1 < 0.5) or ((weight1 < 0.98) and (weight2 * 1.5 > weight1)):
        raise Exception("Unable to map name {!r} to the object. Best guess: {!r} (ratio {}), second best guess: {!r} (ratio {})".format(
            name, best1.name, weight1, best2.name, weight2,
        ))

    return best1
