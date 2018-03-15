# coding:utf8
"""usage: madLibs892.py [textfile]"""

import re
import sys, os

REGEX_KEYWORD = re.compile(r"\b(?:ADJECTIVE|NOUN|ADVERB|VERB)\b")

if len(sys.argv) == 2:
    if sys.argv[1] in ("--help", "-h"):
        print(__doc__)
        sys.exit(0)
    if not os.path.exists(sys.argv[1]):
        sys.exit(0)

    inputFileTuple = os.path.splitext(sys.argv[1])
    outputFileName = inputFileTuple[0] + "-result" + inputFileTuple[1]

    try:
        with open(sys.argv[1], "r", encoding="utf8") as inputFile:
            with open(outputFileName, "w", encoding="utf8") as outputFile:
                while True:
                    # Read new line from the inputFile.
                    line = inputFile.readline()
                    if not line:
                        break

                    # Search key word and get user input to a list.
                    startPos = 0
                    replacementsList = []
                    while True:
                        matchObject = REGEX_KEYWORD.search(string=line, pos=startPos)
                        if not matchObject:
                            break
                        currentProperty = matchObject.group().lower()
                        userInput = input("Enter %s %s:\n" % (
                            "an" if currentProperty[0] in "aeiou" else "a",
                            currentProperty))
                        replacementsList.append(userInput)
                        startPos = matchObject.end() + 1

                    # Replace.
                    for item in replacementsList:
                        line = REGEX_KEYWORD.sub(repl=item, string=line, count=1)

                    # Write to the outputFile.
                    outputFile.write(line)
    except KeyboardInterrupt:
        pass
else:
    print(__doc__)



