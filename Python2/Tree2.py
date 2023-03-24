from __future__ import division
from __future__ import with_statement
from __future__ import absolute_import
import pandas as pd
import numpy as np
import ast
import os
from io import open

class RootTransformer(ast.NodeTransformer):
    def __init__(self, listOfNodes):
        self.listOfNodes = listOfNodes
    def visit_Name(self, node):
        self.listOfNodes.append(node)
        ast.NodeVisitor.generic_visit(self, node)
        
class Tree2(object):
    TD = []
    
    def __init__(self, path):
        self.root = None
        self.l = []
        self.keyroots = []
        self.labels = []
        self.indexes = {}
        self.leftmosts = {}
        with open(path, u"r") as source:
            tmp = ast.parse(source.read())
            self.root = Tree2.replace(tmp)
            
    def getroot(self):
        return self.root
    
    def traverse(self):
        self.traverse1(self.root, u"root", self.labels)
        
    def traverse1(self, node, name, labels):
        attributes = []
        subNodes = []
        subLists = []
        
        for attribute in ast.iter_fields(node):
            if isinstance(attribute[1], ast.AST):
                subNodes.append(attribute)
            elif type(attribute[1]) == type([]):
                subLists.append(attribute)
            else:
                attributes.append(attribute[1])
        
        for attribute in attributes:
            if type(attribute) == type(u''):
                name += attribute
            else:
                name += unicode(attribute)
            
        for child in subNodes:
            self.traverse1(child[1], child[0], labels)
        
        for subList in subLists:
            if len(subList[1]) != 0:
                for node in subList[1]:
                    self.traverse1(node, subList[0], labels)
            
        labels.append(name)
    
    def index(self):
        self.index1(self.root, 0)
        
    def index1(self, node, index):
        
        for child in ast.iter_child_nodes(node):
            self.index1(child, index)
        
        index += 1
        self.indexes.update({node: index})
        return index
    
    def l_func(self):
        self.leftmost()
        self.l = self.l1(self.root, self.l)
        
    def l1(self, node, l):
        for child in ast.iter_child_nodes(node):
            l = self.l1(child, l)
            
        if self.indexes[self.leftmosts[node]] is not None:
            l.append(self.indexes[self.leftmosts[node]])
            
        return l
        
    def leftmost(self):
        self.leftmost1(self.root)
    
    def leftmost1(self, node):
        if node == None:
            return
        for child in ast.iter_child_nodes(node):
            self.leftmost1(child)
        if len(list(ast.iter_child_nodes(node))) == 0:
            self.leftmosts.update({node: node})
        else:   
            children = list(ast.iter_child_nodes(node))
            self.leftmosts.update({node: self.leftmosts[children[0]]})
            
    def keyroots_func(self):
        for i in xrange(len(self.l)):
            flag = 0
            for j in xrange(i+1, len(self.l)):
                if self.l[j] == self.l[i]:
                    flag = 1
            if flag == 0:
                self.keyroots.append(i + 1)
    
    @staticmethod
    def ZhangShasha(tree1, tree2):
        tree1.index()
        tree1.l_func()
        tree1.keyroots_func()
        tree1.traverse()
        tree2.index()
        tree2.l_func()
        tree2.keyroots_func()
        tree2.traverse()
        
        l1 = tree1.l
        keyroots1 = tree1.keyroots
        l2 = tree2.l
        keyroots2 = tree2.keyroots
        
        Tree2.TD = np.zeros(shape=(len(l1) + 1, len(l2) + 1))
        
        for i1 in xrange(len(keyroots1) + 1):
            for j1 in xrange(len(keyroots2) + 1):
                i = keyroots1[i1-1]
                j = keyroots2[j1-1]
                Tree2.TD[i,j] = Tree2.treedist(l1, l2, i, j, tree1, tree2)
        
        return Tree2.TD[len(l1), len(l2)]
    
    @staticmethod
    def treedist(l1, l2, i, j, tree1, tree2):
        forestdist = np.zeros(shape=(i+1, j+1))
        
        delete = 1
        insert = 1
        relabel = 1
        
        forestdist[0,0] = 0
        for i1 in xrange(l1[i-1], i + 1):
            forestdist[i1, 0] = forestdist[i1-1, 0] + delete
            
        for j1 in xrange(l2[j-1], j + 1):
            forestdist[0, j1] = forestdist[0, j1-1] + insert
            
        for i1 in xrange(l1[i-1], i + 1):
            for j1 in xrange(l2[j-1], j+1):
                i_temp = 0 if (l1[i-1] > i1 - 1) else i1 - 1
                j_temp = 0 if (l2[j-1] > j1 - 1) else j1 - 1
                if l1[i1-1] == l1[i-1] and l2[j1-1] == l2[j-1]:
                    cost = 0 if tree1.labels[i1-1] == tree2.labels[j1-1] else relabel
                    forestdist[i1, j1] = min(min(forestdist[i_temp, j1] + delete, forestdist[i1, j_temp] + insert), 
                                            forestdist[i_temp, j_temp] + cost)
                    Tree2.TD[i1, j1] = forestdist[i1,j1]
                else:
                    i1_temp = l1[i1-1] - 1
                    j1_temp = l2[j1-1] - 1
                    
                    i2_temp = 0 if l1[i-1] > i1_temp else i1_temp
                    i2_temp = 0 if l2[j-1] > j1_temp else j1_temp
                    
                    forestdist[i1, j1] = min(min(forestdist[i_temp, j1] + delete), forestdist[i1, j_temp] + insert,
                                            forestdist[i2_temp, j2_temp] + Tree2.TD[i1, j1])
        return forestdist[i,j]
    
    @staticmethod
    def replace(node):
        listOfNameNodes = []
        visitor = RootTransformer(listOfNameNodes)
        visitor.visit(node)
        mapping = {}
        i = 0
        for a in listOfNameNodes:
            if a.id not in mapping.keys():
                mapping[a.id] = u"v" + unicode(i)
                a.id = u"v" + unicode(i)
                i += 1
            else:
                a.id = mapping[a.id]
        return node
def calculateDistanceForProblem(dir, question, resultsPath):
    print u"Now calculating tree edit distances for " + question
    originalDir = os.getcwdu()
    os.chdir(dir)
    files = os.listdir(dir)
    finalFiles = []
    for file in files:
        try:
            test = Tree2(file)
            finalFiles.append(file)
        except:
            print u"Could not parse " + file
    curDis = 0
    score_distance = []
    count = 0
    for i in xrange(len(finalFiles)):
        total = 0
        totalFiles = 0
        for j in xrange(len(finalFiles)):
            if i != j:
                min = 99999999999999999999999999999 #fake max size
                file1Tree = Tree2(finalFiles[i])
                file2Tree = Tree2(finalFiles[j])
                try:
                    curDis = Tree2.ZhangShasha(file1Tree, file2Tree)
                    if (curDis < min):
                        min = curDis
                    total += min
                    totalFiles += 1
                except:
                    print u"Could not calculate distance between " + finalFiles[i] + " and " + finalFiles[j]
        avg = 0
        if totalFiles != 0:
            avg = total / totalFiles
        score_distance.append(avg)
        print u"The average distance for " + finalFiles[i] + u" is " + unicode(avg)
    columns = [u'Year', u'Semester', u'Quiz/Exam', u'Student ID', u'Coding Problem', u'Earned Score', u'Maximum Score', u'Distance']
    lst = []
    for i in xrange(len(finalFiles)):
        split = finalFiles[i].split(u".")
        lst.append([split[0], split[2], split[3], split[4], split[5], split[6], split[7], score_distance[i]])
    data = pd.DataFrame(lst, columns=columns)
    data.to_csv(resultsPath + u".csv", index=False)
    os.chdir(originalDir)

def main():
    homeDir = u"C:/Users/Elijah/Downloads/code-answers-scores-python/code-answers-scores-python"
    resultsDir = u"C:/Users/Elijah/Downloads/code-answers-scores-python/Results"
    validProblems = [u'BodyType', u'BounceCounter', u'BreakDownNumber', u'Cardio', u'Cheaper', u'DashSquare', u'DoubleLen', u'DoublePentagon', u'ExclusiveOR', u'FactorialFor', u'FactorialWhile', u'FromNto1', u'GrowingSquares', u'GrowingStairs', u'Highway', u'InsertNumber', u'LineOfHexagons', u'MixHalf', u'MultiTri', u'MultOddsFor', u'MultOddsWhile', u'Power', u'ProdAll', u'PulsingCircles', u'PulsingCircles3', u'RedBouncingBall', u'RemoveEndDots', u'RotatingSticks', u'SquareLine', u'Stairs', u'StarLine', u'Target', u'TinyTweet', u'TkFractal', u'Towers', u'Triangles', u'TriSpiral', u'TurtleFractal', u'TurtlePath', u'WindEffect', u'Younger']
    for question in os.listdir(homeDir):
        if question in validProblems:
            d = os.path.join(homeDir, question)
            resultPath = os.path.join(resultsDir, question)
            if os.path.isdir(d):
                calculateDistanceForProblem(d, question, resultPath)

if __name__ == u"__main__":
    main()