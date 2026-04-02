from retrieveChapters import extract_chapters_from_pdf_Updated_Better_Version

import time
def testThinkPython2UsingUpdatedVersion():

    chapters = extract_chapters_from_pdf_Updated_Better_Version("./Textbooks/thinkpython2.pdf")
    print("\nTesting Think Python 2 with Updated Version...")

    expected = [
        ("The way of the program", (23, 30)),
        ("Variables, expressions and statements", (31, 38)),
        ("Functions", (39, 50)),
        ("Case study: interface design", (51, 60)),
        ("Conditionals and recursion", (61, 72)),
        ("Fruitful functions", (73, 84)),
        ("Iteration", (85, 92)),
        ("Strings", (93, 104)),
        ("Case study: word play", (105, 110)),
        ("Lists", (111, 124)),
        ("Dictionaries", (125, 136)),
        ("Tuples", (137, 146)),
        ("Case study: data structure selection", (147, 158)),
        ("Files", (159, 168)),
        ("Classes and objects", (169, 176)),
        ("Classes and functions", (177, 182)),
        ("Classes and methods", (183, 192)),
        ("Inheritance", (193, 204)),
        ("The Goodies", (205, 214)),
    ]

    expected_total = len(expected)
    passed = 0
    failed = 0

    actual_total = len(chapters)

    # ⚠️ Count mismatch penalty
    if actual_total != expected_total:
        print(f"⚠️ Chapter count mismatch: expected {expected_total}, got {actual_total}")

    # Compare overlapping indices
    for i in range(min(expected_total, actual_total)):
        expected_title, (exp_start, exp_end) = expected[i]
        actual_title, (act_start, act_end) = chapters[i]

        if (
            actual_title == expected_title and
            act_start == exp_start and
            act_end == exp_end
        ):
            passed += 1
        else:
            failed += 1

    # Missing chapters
    if actual_total < expected_total:
        failed += (expected_total - actual_total)

    # Extra chapters
    if actual_total > expected_total:
        failed += (actual_total - expected_total)

    total_tests = expected_total + max(0, actual_total - expected_total)
    percentage = (passed / total_tests) * 100

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Score: {percentage:.2f}%")

def testDiscreteMathematicsUsingUpdatedVersion():
    chapters = extract_chapters_from_pdf_Updated_Better_Version("./Textbooks/discretemathematics.pdf")
    print("\nTesting Discrete Mathematics With Updated Version...")

    expected = [
        ("Chapter 1: Speaking Mathematically", (29, 50)),
        ("Chapter 2: The Logic of Compound Statements", (51, 123)),
        ("Chapter 3: The Logic of Quantified Statements", (124, 172)),
        ("Chapter 4: Elementary Number Theory and Methods of Proof", (173, 254)),
        ("Chapter 5: Sequences, Mathematical Induction, and Recursion", (255, 363)),
        ("Chapter 6: Set Theory", (364, 410)),
        ("Chapter 7: Functions", (411, 469)),
        ("Chapter 8: Relations", (470, 543)),
        ("Chapter 9: Counting and Probability", (544, 652)),
        ("Chapter 10: Graphs and Trees", (653, 744)),
        ("Chapter 11: Analysis of Algorithm Efficiency", (745, 806)),
        ("Chapter 12: Regular Expressions and Finite-State Automata", (807, 848)),
    ]

    expected_total = len(expected)
    passed = 0
    failed = 0

    actual_total = len(chapters)

    # ⚠️ Count mismatch penalty
    if actual_total != expected_total:
        print(f"⚠️ Chapter count mismatch: expected {expected_total}, got {actual_total}")

    # Compare overlapping indices
    for i in range(min(expected_total, actual_total)):
        expected_title, (exp_start, exp_end) = expected[i]
        actual_title, (act_start, act_end) = chapters[i]

        if (
            actual_title == expected_title and
            act_start == exp_start and
            act_end == exp_end
        ):
            passed += 1
        else:
            failed += 1

    # Missing chapters
    if actual_total < expected_total:
        failed += (expected_total - actual_total)

    # Extra chapters
    if actual_total > expected_total:
        failed += (actual_total - expected_total)

    total_tests = expected_total + max(0, actual_total - expected_total)
    percentage = (passed / total_tests) * 100

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Score: {percentage:.2f}%")

def testBiologyRavenUsingUpdatedVersion():
    chapters = extract_chapters_from_pdf_Updated_Better_Version("./Textbooks/biologyraven.pdf")
    print("\nTesting Biology Raven Using Updated Version...")

    expected = [
        ("Part I The Origin of Living Things", (2, 75)),
        ("Part II Biology of the Cell", (76, 141)),
        ("Part III Energetics", (142, 205)),
        ("Part IV Reproduction and Heredity", (206, 277)),
        ("Part V Molecular Genetics", (278, 419)),
        ("Part VI Evolution", (420, 493)),
        ("Part VII Ecology and Behavior", (494, 569)),
        ("Part VIII The Global Environment", (570, 647)),
        ("Part IX Viruses and Simple Organisms", (648, 733)),
        ("Part X Plan Form and Function", (734, 793)),
        ("Part XI Plant Growth and Reproduction", (794, 873)),
        ("Part XII Animal Diversity", (874, 981)),
        ("Part XIII Animal Form and Function", (982, 1071)),
        ("Part XIV Regulating the Animal", (1072, 1239)),
    ]

    expected_total = len(expected)
    passed = 0
    failed = 0

    actual_total = len(chapters)

    # ⚠️ Count mismatch penalty
    if actual_total != expected_total:
        print(f"⚠️ Chapter count mismatch: expected {expected_total}, got {actual_total}")

    # Compare overlapping indices
    for i in range(min(expected_total, actual_total)):
        expected_title, (exp_start, exp_end) = expected[i]
        actual_title, (act_start, act_end) = chapters[i]

        if (
            actual_title == expected_title and
            act_start == exp_start and
            act_end == exp_end
        ):
            passed += 1
        else:
            failed += 1

    # Missing chapters
    if actual_total < expected_total:
        failed += (expected_total - actual_total)

    # Extra chapters
    if actual_total > expected_total:
        failed += (actual_total - expected_total)

    total_tests = expected_total + max(0, actual_total - expected_total)
    percentage = (passed / total_tests) * 100

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Score: {percentage:.2f}%")

def testEnglishGrammarUsingUpdatedVersion():
    chapters = extract_chapters_from_pdf_Updated_Better_Version("./Textbooks/englishgrammar.pdf")
    print("\nTesting English Grammar With Updated Version...")

    expected = [
        ("1. BASIC CONCEPTS", (24, 54)),
        ("2. THE SKELETON OF THE MESSAGE: INTRODUCTION TO CLAUSE STRUCTURE", (55, 103)),
        ("3. THE DEVELOPMENT OF THE MESSAGE: COMPLEMENTATION OF THE VERB", (104, 142)),
        ("4. CONCEPTUALISING PATTERNS OF EXPERIENCE: PROCESSES, PARTICIPANTS, CIRCUMSTANCES", (143, 196)),
        ("5. INTERACTION BETWEEN SPEAKER AND HEARER: LINKING SPEECH ACTS AND GRAMMAR", (197, 242)),
        ("6. ORGANISING THE MESSAGE: THEMATIC AND INFORMATION STRUCTURES OF THE CLAUSE", (243, 292)),
        ("7. EXPANDING THE MESSAGE: CLAUSE COMBINATIONS", (293, 337)),
        ("8. TALKING ABOUT EVENTS: THE VERBAL GROUP", (338, 372)),
        ("9. VIEWPOINTS ON EVENTS: TENSE, ASPECT AND MODALITY", (373, 421)),
        ("10. TALKING ABOUT PEOPLE AND THINGS: THE NOMINAL GROUP", (422, 495)),
        ("11. DESCRIBING PERSONS, THINGS AND CIRCUMSTANCES: ADJECTIVAL AND ADVERBIAL GROUPS", (496, 551)),
        ("12. SPATIAL, TEMPORAL AND OTHER RELATIONSHIPS: THE PREPOSITIONAL PHRASE", (552, 586)),
    ]

    expected_total = len(expected)
    passed = 0
    failed = 0

    actual_total = len(chapters)

    # ⚠️ Count mismatch penalty
    if actual_total != expected_total:
        print(f"⚠️ Chapter count mismatch: expected {expected_total}, got {actual_total}")

    # Compare overlapping indices
    for i in range(min(expected_total, actual_total)):
        expected_title, (exp_start, exp_end) = expected[i]
        actual_title, (act_start, act_end) = chapters[i]

        if (
            actual_title == expected_title and
            act_start == exp_start and
            act_end == exp_end
        ):
            passed += 1
        else:
            failed += 1

    # Missing chapters
    if actual_total < expected_total:
        failed += (expected_total - actual_total)

    # Extra chapters
    if actual_total > expected_total:
        failed += (actual_total - expected_total)

    total_tests = expected_total + max(0, actual_total - expected_total)
    percentage = (passed / total_tests) * 100

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Score: {percentage:.2f}%")

def testUsHistoryUsingUpdatedVersion():
    chapters = extract_chapters_from_pdf_Updated_Better_Version("./Textbooks/ushistory.pdf")
    print("\nTesting US History Using Updated Version...")

    expected = [
        ("Chapter 1 The Americas, Europe, and Africa Before 1492", (21, 44)),
        ("Chapter 2 Early Globalization: The Atlantic World, 1492–1650", (45, 70)),
        ("Chapter 3 Creating New Social Orders: Colonial Societies, 1500–1700", (71, 98)),
        ("Chapter 4 Rule Britannia! The English Empire, 1660–1763", (99, 124)),
        ("Chapter 5 Imperial Reforms and Colonial Protests, 1763-1774", (125, 152)),
        ("Chapter 6 America's War for Independence, 1775-1783", (153, 178)),
        ("Chapter 7 Creating Republican Governments, 1776–1790", (179, 204)),
        ("Chapter 8 Growing Pains: The New Republic, 1790–1820", (205, 230)),
        ("Chapter 9 Industrial Transformation in the North, 1800–1850", (231, 256)),
        ("Chapter 10 Jacksonian Democracy, 1820–1840", (257, 282)),
        ("Chapter 11 A Nation on the Move: Westward Expansion, 1800–1860", (283, 310)),
        ("Chapter 12 Cotton is King: The Antebellum South, 1800–1860", (311, 338)),
        ("Chapter 13 Antebellum Idealism and Reform Impulses, 1820–1860", (339, 366)),
        ("Chapter 14 Troubled Times: the Tumultuous 1850s", (367, 392)),
        ("Chapter 15 The Civil War, 1860–1865", (393, 420)),
        ("Chapter 16 The Era of Reconstruction, 1865–1877", (421, 448)),
        ("Chapter 17 Go West Young Man! Westward Expansion, 1840-1900", (449, 476)),
        ("Chapter 18 Industrialization and the Rise of Big Business, 1870-1900", (477, 504)),
        ("Chapter 19 The Growing Pains of Urbanization, 1870-1900", (505, 534)),
        ("Chapter 20 Politics in the Gilded Age, 1870-1900", (535, 562)),
        ("Chapter 21 Leading the Way: The Progressive Movement, 1890-1920", (563, 592)),
        ("Chapter 22 Age of Empire: American Foreign Policy, 1890-1914", (593, 618)),
        ("Chapter 23 Americans and the Great War, 1914-1919", (619, 650)),
        ("Chapter 24 The Jazz Age: Redefining the Nation, 1919-1929", (651, 678)),
        ("Chapter 25 Brother, Can You Spare a Dime? The Great Depression, 1929-1932", (679, 708)),
        ("Chapter 26 Franklin Roosevelt and the New Deal, 1932-1941", (709, 736)),
        ("Chapter 27 Fighting the Good Fight in World War II, 1941-1945", (737, 766)),
        ("Chapter 28 Post-War Prosperity and Cold War Fears, 1945-1960", (767, 796)),
        ("Chapter 29 Contesting Futures: America in the 1960s", (797, 828)),
        ("Chapter 30 Political Storms at Home and Abroad, 1968-1980", (829, 860)),
        ("Chapter 31 From Cold War to Culture Wars, 1980-2000", (861, 890)),
        ("Chapter 32 The Challenges of the Twenty-First Century", (891, 918)),
    ]

    expected_total = len(expected)
    passed = 0
    failed = 0

    actual_total = len(chapters)

    # ⚠️ Count mismatch penalty
    if actual_total != expected_total:
        print(f"⚠️ Chapter count mismatch: expected {expected_total}, got {actual_total}")

    # Compare overlapping indices
    for i in range(min(expected_total, actual_total)):
        expected_title, (exp_start, exp_end) = expected[i]
        actual_title, (act_start, act_end) = chapters[i]

        if (
            actual_title == expected_title and
            act_start == exp_start and
            act_end == exp_end
        ):
            passed += 1
        else:
            failed += 1

    # Missing chapters
    if actual_total < expected_total:
        failed += (expected_total - actual_total)

    # Extra chapters
    if actual_total > expected_total:
        failed += (actual_total - expected_total)

    total_tests = expected_total + max(0, actual_total - expected_total)
    percentage = (passed / total_tests) * 100

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Score: {percentage:.2f}%")

def testIntroToLawUsingUpdatedVersion():
    chapters = extract_chapters_from_pdf_Updated_Better_Version("./Textbooks/introtolaw.pdf")
    print("\nTesting Intro To Law Using Updated Version...")

    expected = [
        ("1 Law and society", (33, 57)),
        ("2 Law and morality", (58, 99)),
        ("3 Law and the regulation of economic activity", (100, 121)),
        ("4 Some important legal concepts", (122, 141)),
        ("5 Law and property", (142, 181)),
        ("6 Law and the settlement of disputes", (182, 221)),
        ("7 The making of legal rules", (222, 246)),
        ("8 The European dimension of English law", (247, 272)),
        ("9 Liability in English law: the law of tort", (273, 337)),
        ("10 Liability in English law: crime and the criminal justice system", (338, 380)),
        ("11 The development and role of the contract", (381, 417)),
        ("12 Law and government", (418, 451)),
        ("13 The legal profession", (452, 476)),
        ("14 The judges", (477, 504)),
    ]

    expected_total = len(expected)
    passed = 0
    failed = 0

    actual_total = len(chapters)

    # ⚠️ Count mismatch penalty
    if actual_total != expected_total:
        print(f"⚠️ Chapter count mismatch: expected {expected_total}, got {actual_total}")

    # Compare overlapping indices
    for i in range(min(expected_total, actual_total)):
        expected_title, (exp_start, exp_end) = expected[i]
        actual_title, (act_start, act_end) = chapters[i]

        if (
            actual_title == expected_title and
            act_start == exp_start and
            act_end == exp_end
        ):
            passed += 1
        else:
            failed += 1

    # Missing chapters
    if actual_total < expected_total:
        failed += (expected_total - actual_total)

    # Extra chapters
    if actual_total > expected_total:
        failed += (actual_total - expected_total)

    total_tests = expected_total + max(0, actual_total - expected_total)
    percentage = (passed / total_tests) * 100

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Score: {percentage:.2f}%")

def testIntroToArtUsingUpdatedVersion():
    chapters = extract_chapters_from_pdf_Updated_Better_Version("./Textbooks/introtoart.pdf")
    print("\nTesting Intro To Art Using Updated Version...")
    expected = [
        ("Chapter 1 - Defining Art", (12, 21)),
        ("Chapter 2 - The Purpose of Art", (22, 25)),
        ("Chapter 3 - The Elements of Design", (26, 50)),
        ("Chapter 4 - The Principles of Design", (51, 65)),
        ("Chapter 5 - Finding Meaning", (66, 77)),
        ("Chapter 6 - Drawing", (79, 85)),
        ("Chapter 7 - Painting", (86, 94)),
        ("Chapter 8 - Printmaking", (95, 101)),
        ("Chapter 9 - Photography", (102, 114)),
        ("Chapter 10 - Time Based Media - Film Video Digital", (115, 117)),
        ("Chapter 11 - Sculpture", (118, 126)),
        ("Chapter 12 - Craft and Design Media", (127, 139)),
        ("Chapter 13 - Architecture", (140, 157)),
        ("Chapter 14 - The Stone Age", (160, 171)),
        ("Chapter 15 - Ancient Near East", (172, 181)),
        ("Chapter 16 - Ancient Africa", (182, 194)),
        ("Chapter 17 - Ancient Mediterranean", (195, 212)),
        ("Chapter 18 - Ancient South Asia", (213, 223)),
        ("Chapter 19 - Ancient East Asia", (224, 235)),
        ("Chapter 20 - Early Art of Oceania and the Americas", (236, 253)),
        ("Chapter 21 - Medieval Europe and Byzantium", (254, 271)),
        ("Chapter 22 - Arts of the Islamic World", (272, 291)),
        ("Chapter 23 - Arts of Asia 5th - 15th Centuries", (292, 314)),
        ("Chapter 24 - Arts of Africa 5th - 15th Centuries", (315, 322)),
        ("Chapter 25 - Oceania and the Americas 5th - 15th Centuries", (323, 341)),
        ("Chapter 26 - Renaissance and Baroque Europe", (342, 366)),
        ("Chapter 27 - Eighteenth and Nineteenth Centuries", (367, 388)),
        ("Chapter 28 - Early Twentieth Century", (389, 403)),
        ("Chapter 29 - Between World Wars", (404, 433)),
        ("Chapter 30 - Postwar Modern Movements", (434, 457)),
        ("Chapter 31 - Postmodernity and Global Cultures", (458, 473)),
    ]

    expected_total = len(expected)
    passed = 0
    failed = 0

    actual_total = len(chapters)

    # ⚠️ Count mismatch penalty
    if actual_total != expected_total:
        print(f"⚠️ Chapter count mismatch: expected {expected_total}, got {actual_total}")

    # Compare overlapping indices
    for i in range(min(expected_total, actual_total)):
        expected_title, (exp_start, exp_end) = expected[i]
        actual_title, (act_start, act_end) = chapters[i]

        if (
            actual_title == expected_title and
            act_start == exp_start and
            act_end == exp_end
        ):
            passed += 1
        else:
            failed += 1

    # Missing chapters
    if actual_total < expected_total:
        failed += (expected_total - actual_total)

    # Extra chapters
    if actual_total > expected_total:
        failed += (actual_total - expected_total)

    total_tests = expected_total + max(0, actual_total - expected_total)
    percentage = (passed / total_tests) * 100

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Score: {percentage:.2f}%")
    #for ch in chapters:
    #    print(ch)

def testIntroToPsychUsingUpdatedVersion():
    chapters = extract_chapters_from_pdf_Updated_Better_Version("./Textbooks/introtopsych.pdf")
    print("\nTesting Intro To Psych Using Updated Version...")
    expected = [
        ("Introducing Psychology", (6, 41)),
        ("Psychological Science", (42, 94)),
        ("Brains, Bodies, and Behavior", (95, 145)),
        ("Sensing and Perceiving", (146, 205)),
        ("States of Consciousness", (206, 255)),
        ("Growing and Developing", (256, 313)),
        ("Learning", (314, 351)),
        ("Remembering and Judging", (352, 413)),
        ("Intelligence and Language", (414, 470)),
        ("Emotions and Motivations", (471, 535)),
        ("Personality", (536, 591)),
        ("Defining Psychological Disorders", (592, 665)),
        ("Treating Psychological Disorders", (666, 718)),
        ("Psychology in Our Social Lives", (719, 783)),
    ]

    expected_total = len(expected)
    passed = 0
    failed = 0

    actual_total = len(chapters)

    # ⚠️ Count mismatch penalty
    if actual_total != expected_total:
        print(f"⚠️ Chapter count mismatch: expected {expected_total}, got {actual_total}")

    # Compare overlapping indices
    for i in range(min(expected_total, actual_total)):
        expected_title, (exp_start, exp_end) = expected[i]
        actual_title, (act_start, act_end) = chapters[i]

        if (
            actual_title == expected_title and
            act_start == exp_start and
            act_end == exp_end
        ):
            passed += 1
        else:
            failed += 1

    # Missing chapters
    if actual_total < expected_total:
        failed += (expected_total - actual_total)

    # Extra chapters
    if actual_total > expected_total:
        failed += (actual_total - expected_total)

    total_tests = expected_total + max(0, actual_total - expected_total)
    percentage = (passed / total_tests) * 100

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Score: {percentage:.2f}%")
    # for ch in chapters:
    #     print(ch)

def testFinancePrinciplesUsingUpdatedVersion():
    chapters = extract_chapters_from_pdf_Updated_Better_Version("./Textbooks/financeprinciples.pdf")
    print("\nTesting Finance Principles Using Updated Version...")
    expected = [
        ("Chapter 1 Introduction to Finance", (21, 52)),
        ("Chapter 2 Corporate Structure and Governance", (53, 80)),
        ("Chapter 3 Economic Foundations: Money and Rates", (81, 114)),
        ("Chapter 4 Accrual Accounting Process", (115, 142)),
        ("Chapter 5 Financial Statements", (143, 178)),
        ("Chapter 6 Measures of Financial Health", (179, 204)),
        ("Chapter 7 Time Value of Money I: Single Payment Value", (205, 240)),
        ("Chapter 8 Time Value of Money II: Equal Multiple Payments", (241, 276)),
        ("Chapter 9 Time Value of Money III: Unequal Multiple Payment Values", (277, 296)),
        ("Chapter 10 Bonds and Bond Valuation", (297, 332)),
        ("Chapter 11 Stocks and Stock Valuation", (333, 366)),
        ("Chapter 12 Historical Performance of US Markets", (367, 394)),
        ("Chapter 13 Statistical Analysis in Finance", (395, 430)),
        ("Chapter 14 Regression Analysis in Finance", (431, 462)),
        ("Chapter 15 How to Think about Investing", (463, 492)),
        ("Chapter 16 How Companies Think about Investing", (493, 520)),
        ("Chapter 17 How Firms Raise Capital", (521, 548)),
        ("Chapter 18 Financial Forecasting", (549, 578)),
        ("Chapter 19 The Importance of Trade Credit and Working Capital in Planning", (579, 612)),
        ("Chapter 20 Risk Management and the Financial Manager", (613, 636)),
    ]

    expected_total = len(expected)
    passed = 0
    failed = 0

    actual_total = len(chapters)

    # ⚠️ Count mismatch penalty
    if actual_total != expected_total:
        print(f"⚠️ Chapter count mismatch: expected {expected_total}, got {actual_total}")

    # Compare overlapping indices
    for i in range(min(expected_total, actual_total)):
        expected_title, (exp_start, exp_end) = expected[i]
        actual_title, (act_start, act_end) = chapters[i]

        if (
            actual_title == expected_title and
            act_start == exp_start and
            act_end == exp_end
        ):
            passed += 1
        else:
            failed += 1

    # Missing chapters
    if actual_total < expected_total:
        failed += (expected_total - actual_total)

    # Extra chapters
    if actual_total > expected_total:
        failed += (actual_total - expected_total)

    total_tests = expected_total + max(0, actual_total - expected_total)
    percentage = (passed / total_tests) * 100

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Score: {percentage:.2f}%")
    # for ch in chapters:
    #     print(ch)



def main():

    testThinkPython2UsingUpdatedVersion()
    testDiscreteMathematicsUsingUpdatedVersion()
    testBiologyRavenUsingUpdatedVersion()
    testEnglishGrammarUsingUpdatedVersion()
    testUsHistoryUsingUpdatedVersion()
    testIntroToLawUsingUpdatedVersion()
    testIntroToArtUsingUpdatedVersion()
    testIntroToPsychUsingUpdatedVersion()
    testFinancePrinciplesUsingUpdatedVersion()




if __name__ == "__main__":
    main()