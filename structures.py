import numpy as np
__author__ = 'ntak'
class VASS:
    """
    E is a dictionnary within a dictionnary
    """
    def __init__(self,dimension, V=None, E=None):


        self.dimension = dimension
        if V is None :
            self.V = set()
        else :
            self.V = V

        if E is None:
            self.E = {}
        else:
            self.E = E
        self.validate()

    def validate(self):
        print(self.V)
        print(self.E)
        for q,v in self.E.items() :
            assert q in self.V
            print('q',q)
            for i,x in v.items():
                assert i in self.V
                print(i,x)
                for y in x:
                    assert len(y) == self.dimension and all(type(z) is int for z in y)


    def pretty_print(self):
        print("Dimension : "+str(self.dimension))
        print("States : "+str(self.V))
        print("Transitions : ")
        s = ''
        for q,x in self.E.items():
            s += str(q) + ", " + str(x) + " \n"
        print(s)




    def add_edge(self, q, v, p):
        assert len(v) == self.dimension
        assert all(type(x) == int for x in v)
        assert p in self.V and q in self.V

        if q in self.E.keys():
            if p in self.E[q]:
                self.E[q][p].append(np.array(v))
            else :
                self.E[q][p] = [np.array(v)]
        else:
            self.E[q] = {p:[np.array(v)]}

    def add_vertice(self, v):
        self.V.add(v)
        self.E[v] = {}

class cycle:
    def __init__(self, elements):

        self.elements = elements


    def __str__(self):
        return str(self.elements)

    def is_element_in(self, el):
        return el in self.elements

    def sequence_from(self, a):
        i = self.elements.index(a)
        return self.elements[i:] + self.elements[:i]

    def sub_sequence(self, a,b):
        """
        Return the subsequence from a to b (included). a and b must be in self.elements.
        """
        i = self.elements.index(a)
        j = self.elements.index(b)

        if i <= j :
            return self.elements[i:j+1]
        else :
            return self.elements[i:] + self.elements[:j+1]

    @staticmethod
    def test():
        c = cycle(list(range(5)))
        assert c.sequence_from(2) == [2,3,4,0,1]
        assert c.sub_sequence(3,1) == [3,4,0,1]
        assert c.sub_sequence(2,3) == [2,3]
        assert c.sub_sequence(2,2) == [2]


#
#   vass for testing purpose
#
def vass1():
    d = 3
    V = set(range(4))
#    E = {0:[(1,[0 for i in range(d)])],1: [(2,[0 for i in range(d)]),(3,[0 for i in range(d)])],2:[(0,[0 for i in range(d)])],3:[(0,[0 for i in range(d)])]}
    E = {0:{1:set([(0,0,0)])}, 1: {2: set([(0,0,0)]),3:set([(0,0,0)])}, 2:{0:set([(0,0,0)])},3:{0:set([(0,0,0)])}}

    v = VASS(d, V,E)
    v.pretty_print()
    return v

#   Update those?
#

def vass2():
    d = 3
    V = set(range(6))
    E = {0:[(1,[0 for i in range(d)]),(5,[0 for i in range(d)])], 1: [(2,[0 for i in range(d)]),(3,[0 for i in range(d)])],2:[(0,[0 for i in range(d)])],3:[(4,[0 for i in range(d)])],4:[(2,[0 for i in range(d)])],5:[(3,[0 for i in range(d)]),(1,[0 for i in range(d)])]}
    v = VASS(d, V,E)
    v.pretty_print()
    return v

def vass3():
    d = 3
    V = set(range(6))
    E = {0:[(2,[0 for i in range(d)])], 1: [(0,[0 for i in range(d)])],2:[(1,[0 for i in range(d)]),(3,[0 for i in range(d)])],3:[(0,[0 for i in range(d)]),(4,[0 for i in range(d)])],4:[(2,[0 for i in range(d)]),(5,[0 for i in range(d)])],5:[]}
    v = VASS(d, V,E)
    v.pretty_print()
    return v

def vass4():
    #[[8, 2, 7, 6], [2, 7], [9, 7, 6, 8], [10, 9, 7, 6, 8], [8, 10, 13, 12], [11, 12, 8], [12, 8]]
    #
    d = 3
    V = set(range(14))
    E = {0:[],1:[(8,[0 for i in range(d)])],
         2:[(5,[0 for i in range(d)]),(7,[0 for i in range(d)])],
         3:[(2,[0 for i in range(d)]),(5,[0 for i in range(d)]),(4,[0 for i in range(d)]),(1,[0 for i in range(d)])],
         4:[(7,[0 for i in range(d)])],
         5:[(2,[0 for i in range(d)])],
         6:[(8,[0 for i in range(d)])],
         7:[(6,[0 for i in range(d)]),(2,[0 for i in range(d)])],
         8:[(2,[0 for i in range(d)]),(9,[0 for i in range(d)]),
            (10,[0 for i in range(d)]),(11,[0 for i in range(d)]),(12,[0 for i in range(d)])],
         9:[(7,[0 for i in range(d)])],
         10:[(9,[0 for i in range(d)]),(13,[0 for i in range(d)])],
         11:[(12,[0 for i in range(d)])],
         12:[(8,[0 for i in range(d)])],

         13:[(12,[0 for i in range(d)])]}
    v = VASS(d, V,E)
    v.pretty_print()
    return v

def vass5():
    d = 3
    V = set(range(14))
    E = {0:[],1:[(8,[0 for i in range(d)])],
         2:[(5,[0 for i in range(d)]),(7,[0 for i in range(d)])],
         3:[(1,[0 for i in range(d)]),(2,[0 for i in range(d)]),(5,[0 for i in range(d)]),(4,[0 for i in range(d)])],
         4:[(7,[0 for i in range(d)]),(7,[1 for i in range(d)])],
         5:[(2,[0 for i in range(d)]),(7,[0 for i in range(d)])],
         6:[(8,[0 for i in range(d)])],
         7:[(6,[0 for i in range(d)]),(3,[0 for i in range(d)]),(2,[0 for i in range(d)])],
         8:[(2,[0 for i in range(d)]),(9,[0 for i in range(d)]),
            (10,[0 for i in range(d)]),(11,[0 for i in range(d)]),(12,[0 for i in range(d)])],
         9:[(7,[0 for i in range(d)])],
         10:[(9,[0 for i in range(d)]),(13,[0 for i in range(d)])],
         11:[(12,[0 for i in range(d)])],
         12:[(8,[0 for i in range(d)])],
         13:[(12,[0 for i in range(d)])]}
    v = VASS(d, V,E)
    v.pretty_print()
    return v

def vass6():
    d=1
    V = set(range(3))
    E = {0:[(1,[0 for i in range(d)]),(2,[0 for i in range(d)])],1:[(0,[0 for i in range(d)]),(2,[0 for i in range(d)])],2:[(0,[0 for i in range(d)]),(1,[0 for i in range(d)])]}
    v = VASS(d,V,E)
    v.pretty_print()

    return v
