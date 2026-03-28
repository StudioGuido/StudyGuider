from retrieveChapters import extract_chapters_from_pdf

def testThinkPython2():
    chapters = extract_chapters_from_pdf("./Textbooks/thinkpython2.pdf")
    assert chapters[0][0] == "The way of the program" and chapters[0][1][0] == 23 and chapters[0][1][1] == 30
    assert chapters[1][0] == "Variables, expressions and statements" and chapters[1][1][0] == 31 and chapters[1][1][1] == 38
    assert chapters[2][0] == "Functions" and chapters[2][1][0] == 39 and chapters[2][1][1] == 50
    assert chapters[3][0] == "Case study: interface design" and chapters[3][1][0] == 51 and chapters[3][1][1] == 60
    assert chapters[4][0] == "Conditionals and recursion" and chapters[4][1][0] == 61 and chapters[4][1][1] == 72
    assert chapters[5][0] == "Fruitful functions" and chapters[5][1][0] == 73 and chapters[5][1][1] == 84
    assert chapters[6][0] == "Iteration" and chapters[6][1][0] == 85 and chapters[6][1][1] == 92
    assert chapters[7][0] == "Strings" and chapters[7][1][0] == 93 and chapters[7][1][1] == 104
    assert chapters[8][0] == "Case study: word play" and chapters[8][1][0] == 105 and chapters[8][1][1] == 110
    assert chapters[9][0] == "Lists" and chapters[9][1][0] == 111 and chapters[9][1][1] == 124
    assert chapters[10][0] == "Dictionaries" and chapters[10][1][0] == 125 and chapters[10][1][1] == 136
    assert chapters[11][0] == "Tuples" and chapters[11][1][0] == 137 and chapters[11][1][1] == 146
    assert chapters[12][0] == "Case study: data structure selection" and chapters[12][1][0] == 147 and chapters[12][1][1] == 158
    assert chapters[13][0] == "Files" and chapters[13][1][0] == 159 and chapters[13][1][1] == 168
    assert chapters[14][0] == "Classes and objects" and chapters[14][1][0] == 169 and chapters[14][1][1] == 176
    assert chapters[15][0] == "Classes and functions" and chapters[15][1][0] == 177 and chapters[15][1][1] == 182
    assert chapters[16][0] == "Classes and methods" and chapters[16][1][0] == 183 and chapters[16][1][1] == 192
    assert chapters[17][0] == "Inheritance" and chapters[17][1][0] == 193 and chapters[17][1][1] == 204
    assert chapters[18][0] == "The Goodies" and chapters [18][1][0] == 205 and chapters[18][1][1] == 214

def testDiscreteMathematics():
    chapters = extract_chapters_from_pdf("./Textbooks/discretemathematics.pdf")
    assert chapters[0][0] == "Speaking Mathematically" and chapters[0][1][0] == 29 and chapters[0][1][1] == 50
    assert chapters[1][0] == "The Logic of Compound Statements" and chapters[1][1][0] == 51 and chapters[1][1][1] == 123
    assert chapters[2][0] == "The Logic of Quantified Statements" and chapters[2][1][0] == 124 and chapters[2][1][1] == 172
    assert chapters[3][0] == "Elementary Number Theory and Methods of Proof" and chapters[3][1][0] == 173 and chapters[3][1][1] == 254
    assert chapters[4][0] == "Sequences, Mathematical Induction, and Recursion" and chapters[4][1][0] == 255 and chapters[4][1][1] == 363
    assert chapters[5][0] == "Set Theory" and chapters[5][1][0] == 364 and chapters[5][1][1] == 410
    assert chapters[6][0] == "Functions" and chapters[6][1][0] == 411 and chapters[6][1][1] == 469
    assert chapters[7][0] == "Relations" and chapters[7][1][0] == 470 and chapters[7][1][1] == 543
    assert chapters[8][0] == "Counting and Probability" and chapters [8][1][0] == 544 and chapters [8][1][1] == 652
    assert chapters[9][0] == "Graphs and Trees" and chapters[9][1][0] == 653 and chapters[9][1][1] == 744
    assert chapters[10][0] == "Analysis of Algorithm Efficiency" and chapters[10][1][0] == 745 and chapters[10][1][1] == 806
    assert chapters[11][0] == "Regular Expressions and Finite-State Automata" and chapters[11][1][0] == 807 and chapters[11][1][1] == 848


def main():
    testThinkPython2()
    testDiscreteMathematics()




if __name__ == "__main__":
    testThinkPython2()
    testDiscreteMathematics()