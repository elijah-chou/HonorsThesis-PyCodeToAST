import os

def checkDir(dir):
    originalDir = os.getcwd()
    os.chdir(dir)
    for file in os.listdir(dir):
        if os.path.getsize(file) != 0:
            os.chdir(originalDir)
            return False
    os.chdir(originalDir)
    return True

def main():
    homeDir = "C:/Users/Elijah/Downloads/code-answers-scores-python/code-answers-scores-python"
    faultyProblems = []
    validProblems = []
    for question in os.listdir(homeDir):
        d = os.path.join(homeDir, question)
        if os.path.isdir(d):
            if checkDir(d):
                faultyProblems.append(question)
            else:
                validProblems.append(question)
    print(faultyProblems)
    print(validProblems)

if __name__ == "__main__":
    main()