from structures import *
import CycleEnumerators
import structures
import numpy as np
import qsoptex
import z3


def vass1():
    V = list(range(5))
    #    E = {0:{1:set([np.array([-1,-1])]),3:set([(1,0)])},1:{2:set([(0,0)]),3:set([(1,-3)])},
    # 2:{0:set([(0,0)])},3:{4:set([(0,0)])},4:{0:set([(0,0)])}}
    x = VASS(2, V, None)
    x.add_edge(0, [-1, -1], 1)
    x.add_edge(0, [1, 0], 3)
    x.add_edge(1, [0, 0], 2)
    x.add_edge(1, [1, -3], 3)
    x.add_edge(2, [0, 0], 0)
    x.add_edge(3, [0, 0], 4)
    x.add_edge(4, [0, 0], 0)
    x.pretty_print()
    # print(reachability(x, 0, (1,1)))
    return x


def set_equals(s1, s2):
    """
    Takes 2 1-dimension np.array that we assumes to have unique elements (non-hashable elements such as numpy arrays are ok). Test the set equality between both.
    :param s1:
    :param s2:
    :return:
    """
    if len(s1) == len(s2):
        x = list(s1)
        for y in s2:
            if not y in x:
                return False
            x.remove(y)
        return True
    return False


def inSemiLinearSet(x, dimension, b, Y):
    """
    Is x in the semi-linear set {b + sum_{y_i in Y} c_i * y_i} where c_i are non-negative integers.
    :param x
    :param dimension
    :param Y: must be an ordered iterable of 2-tuples with integers
    :return:
    """
    if len(Y) == 0:
        return False
    s = z3.Solver()
    c = [z3.Int('c_%i' % i) for i in range(len(Y))]
    for i in c:
        s.add(i >= 0)

    for u in range(dimension):
        enumerate(Y)
        z3.Sum([c[i] * y[u] for i, y in enumerate(Y)])
        z3.Sum([c[i] * y[u] for i, y in enumerate(Y)]) + b[u]
        z3.Sum([c[i] * y[u] for i, y in enumerate(Y)]) + b[u] == x[u]
        s.add((z3.Sum([c[i] * y[u] for i, y in enumerate(Y)]) + b[u]) == x[u])
    if s.check() == z3.sat:
        return True
    return False


def reachability(vass, p0, x0):
    """

    :param vass: a vass object.
    :param q0: initial state
    :param x0: an initial marking
    :return:
    """
    assert vass.dimension == 2

    # This call is very important. it calculates all the elementary cycle in the inputed vass.
    vass.cycles = CycleEnumerators.tarjan_cycles(vass)
    shorts_path = {}
    accessibility_set = {}  # A dictionnary where the key is a state and the value is a list of nodes

    def getShortPath(p, x):
        """
        Returns x'-x for every elementary cycle that can be take from p,x to p,x'

        """
        if not p in shorts_path.keys():
            sp = []
            for c in vass.cycles:
                if c.is_element_in(p):
                    loop = c.sequence_from(p)
                    s = []
                    i = p
                    for z in loop[1:]:
                        s.append(vass.E[i][z])
                        i = z
                    s.append(vass.E[i][p])
                    sp.append(s)
            shorts_path[p] = sp

        positive_sp = []
        non_positive_sp = []
        for c in shorts_path[p]:
            y = [x]
         

            for transition in c:
                if len(y) == 0:
                    # the cycle is not activable
                    break
                tmp = []
                for m in transition:
                    tmp += [u + m for u in y]
                y = filter(lambda x: all(i >= 0 for i in x), tmp)

            #Sorting positive short path and negative short path
            for i in y:
                if any(i < x):
                    non_positive_sp.append(i - x)
                else:
                    positive_sp.append(i - x)

        return positive_sp, non_positive_sp

    class Node:

        unmarked_leaves = []
        accessibility_set = {}
        """
        cycles must be a set of cycle elements

        marking must be a numpy array
        """

        def __init__(self, parent, state, marking, cycles):
            if not state in Node.accessibility_set.keys():
                accessibility_set[state] = [self]
            elif all(n.marking != marking for n in Node.accessibility_set[q]):
                accessibility_set[state].append(self)
            else:
                print('Node already exists!')
                print(cycles, 'vs.', list(filter(lambda x: x.marking == marking, accessibility_set[state]))[0].cycles)
                return

            self.parent = parent
            self.state = state
            self.marking = marking
            self.cycles = list(cycles)
            self.childrens = []
            self.marked = False
            if not parent is None:
                parent.childrens.append(self)
            Node.unmarked_leaves.append(self)
            print('Added a new node' + str(self))

        def __str__(self):
            return 'p: ' + str(self.state) + ", x: " + str(self.marking) + ', cycles: ' + str(self.cycles)

        def isMarkingReachable(self, marking):
            if self.marking != marking:
                s = z3.Solver()
                b = [z3.Int('b_%i' % i) for i in range(len(c.cycles))]
                y = [z3.Int('y0'), z3.Int('y1')]

                for u in range(vass.dimension):
                    s.add(z3.Sum([b[i] * x[u] for i, x in enumerate(c.cycles)]) + self.marking[u] == marking[u])
                    s.add(y[u] >= 0)

                if z3.check() == z3.sat:
                    return True
                return False

            return False

    root = Node(None, p0, x0, [])
    while (len(Node.unmarked_leaves) != 0):
        print('Popping a node')
        c = Node.unmarked_leaves.pop(0)

        # Adding periods
        positive_sp, non_positive_sp = getShortPath(p0, x0)
        print('+sp', positive_sp)
        print('-sp', non_positive_sp)

        c.cycles += list(filter(lambda x: not any(all(x == l) for l in c.cycles), positive_sp))

        if len(c.cycles) != 0 and len(non_positive_sp) != 0:
            #

            s = z3.Solver()
            alpha = z3.Int('alph')
            beta = z3.Int('beta')
            a1, a2 = z3.Int('a1'), z3.Int('a2')
            b1, b2 = z3.Int('b1'), z3.Int('b2')
            axe = z3.Int('x')

            s.add(alpha >= 0)
            s.add(beta >= 0)
            s.add(z3.Or(*[a1 == i and a2 == x for i, x in non_positive_sp]))
            s.add(z3.Or(*[b1 == i and b2 == x for i, x in c.cycles]))
            s.add(axe >= 0)
            s.add(z3.Or(alpha * a1 + beta * b1 == 0 and alpha * a2 + beta * b2 == axe,
                        alpha * a1 + beta * b1 == axe and alpha * a2 + beta * b2 == 0))

            # if exists alpha,beta in naturals, exists (a1,a2) in non_positive_sp, exist (b1,b2) in c.cycles
            if s.check() == z3.sat:
                print("Solution found")
                m = s.model()

                alpha, beta = m[alpha], m[beta]
                a1, a2, b1, b2 = m[a1], m[a2], m[b1], m[b2]
                print(alpha, beta, a1, a2, b1, b2)
                y = np.array([alpha * a1 + beta * b1, alpha * a2 + beta * b2])
                print('y : ', y)

                if all([y[0] / x[0] != y[1] / x[1] for x in c.cycles]):
                    c.cycles.append(y)
            else:
                print('No solution found')

        # Test based on ancestors
        print('Ancestor based test')
        x = c.parent
        while not x is None:
            if x.state == c.state:
                print('ccycle', c.cycles)
                print('xcycle', x.cycles)

                if set_equals(c.cycles, x.cycles) and inSemiLinearSet(x.marking, 2, c.marking,
                                                                      x.cycles):  # is in semi-linear set
                    c.marked = True

                elif all(x.marking < c.marking):
                    y = c.marking - x.marking
                    print('cycle', c.cycles)
                    if len(c.cycles) == 0 or (
                                (y[0] == 0 or y[1] == 0) and all([y[0] / i[0] != y[1] / i[1] for i in c.cycles])):
                        c.cycles.append((y[0], y[1]))
            x = x.parent


        # Calculating childrens
        print('Calculating childrens')
        if (c.marked == False):
            print(vass.E[c.state])
            print('cycle', c.cycles)
            for q, vs in vass.E[c.state].items():
                print('Outgoing arc', q, vs)
                for v in vs:
                    solutions = []
                    s = z3.Solver()
                    b = [z3.Int('b_%i' % i) for i in range(len(c.cycles))]
                    y = [z3.Int('y0'), z3.Int('y1')]
                    d = [z3.Int('d_%i' % i) for i in range(len(c.cycles))]
                    z = [z3.Int('z0'), z3.Int('z1')]

                    if len(c.cycles) == 0:
                        x = c.marking + v
                        if all(i >= 0 for i in x):
                            n = Node(c, q, c.marking + v, [])
                            print('Added children '+str(n))
                            print(n.marking.dtype)
                        continue
                    else:


                        for u in range(vass.dimension):
                            #                 print(b)
                            #                  x = c.cycles[0]
                            #                print(b[0]*x[0])
                            #               print(b[0]*x[1])
                            #              print(z3.Sum([b[i]*x[u] for i,x in enumerate(c.cycles)]))
                            #             print(z3.Sum([b[i]*x[u] for i,x in enumerate(c.cycles)])+c.marking[u])
                            #            print(z3.Sum([b[i]*x[u] for i,x in enumerate(c.cycles)])+c.marking[u]+v[u])
                            #           print(z3.Sum([b[i]*x[u] for i,x in enumerate(c.cycles)])+c.marking[u]+v[u] == y[u])

                            s.add(z3.Sum([b[i] * x[u] for i, x in enumerate(c.cycles)]) + c.marking[u] + v[u] == y[u])
                            s.add(y[u] >= 0)
                            s.add(z3.Sum([d[i] * x[u] for i, x in enumerate(c.cycles)]) + c.marking[u] + v[u] == z[u])
                            s.add(z[u] >= 0)

                        if s.check() != z3.sat:
                            print('Not satisfiable')
                            break
                        i =0
                        z3.Or([b[i] < d[i], z3.And([z3.Or([d[j] < b[j] for j in range(len(c.cycles))]),d[i] == b[i]])])
                        [z3.ForAll(z, z3.Or([b[i] < d[i], z3.And([z3.Or([d[j] < b[j] for j in range(len(c.cycles))]),d[i] == b[i]])])) for i in range(len(c.cycles))]
                        z3.Or([z3.ForAll(z, z3.Or([b[i] < d[i], z3.And([z3.Or([d[j] < b[j] for j in range(len(c.cycles))]),d[i] == b[i]])])) for i in range(len(c.cycles))])
                        z3.ForAll(y, z3.Or([z3.ForAll(z, z3.Or([b[i] < d[i], z3.And([z3.Or([d[j] < b[j] for j in range(len(c.cycles))]),d[i] == b[i]])])) for i in range(len(c.cycles))]))

                        s.add(z3.ForAll(y, z3.Or([z3.ForAll(z, z3.Or([b[i] < d[i], z3.And([z3.Or([d[j] < b[j] for j in range(len(c.cycles))]),d[i] == b[i]])])) for i in range(len(c.cycles))])))

#                        s.add(z3.ForAll(y, z3.Or([z3.ForAll(z, z3.Or(y[i] < x[i], z3.And([x[j] < d[j] for j in range(len(c.cycles))].append(y[i] == x[i])))) for i in range(len(c.cycles))])) )
 #                           z3.Or([z3.And([b[j] < d[j] if i==j else b[j] <= d[j] for j in range(len(c.cycles))]) for i in range(len(c.cycles))])))

                        #s.add(z3.ForAll(y, z3.And([z3.Implies() for i, x in enumerate(c.cycles)]), [b] <= z[0], y[1] <= z[1])))

#                        s.add(z3.ForAll(z, z3.And(y[0] <= z[0], y[1] <= z[1])))
#                        s.add(z3.ForAll(y, z3.Or(y[0] < z[0], y[1] < z[1])))


      #                  m = s.model()


                        #iteration over elements of result set
#                        for u in range(0, vass.dimension):
      #                      s.use_pp()
  #                          s.push()
       #                     s.add(z3.ForAll(z, z3.Implies(y[u] > z[u], False)))
                        new_rules = []
                        while s.check() == z3.sat:
                            sol = s.model()
                            print(type(sol[y[0]]))
                            print(sol[y[0]].as_long())

                            sol = np.array([sol[y[i]].as_long() for i in range(0, vass.dimension)])
                            solutions.append(sol)
                            print('sol',sol, sol.dtype)

                            n = z3.Or([int(sol[i]) != y[i] for i in [0, 1]])
                            new_rules.append(n)
                            s.add(n)
    #                       s.pop()
     #                       s.add(z3.And(new_rules))

                        print('sol :', solutions)
                        for x in solutions:
                            print(x.dtype)
                            n = Node(c, q, x, c.cycles)

            if c.childrens is None or len(c.childrens) == 0:
                c.marked = True

    return root


def parse_root_to_state_hash(hash, root):
    if root.state in hash.keys():
        hash[root.state].append(root)
    else:
        hash[root.state] = [root]
    for c in root.childrens:
        parse_root_to_state_hash(hash, c)


v = vass1()
v.pretty_print()
x = reachability(v, 0, np.array([0, 0]))
p = {}
y = parse_root_to_state_hash(p, x)


def semilinearsettest():
    #    y = [(2,3),(0,5),(-2,-1),(100,1)]
    y = [np.array([2, 3]), np.array([-2, -1])]
    b = np.array([0, 0])
    assert (inSemiLinearSet((4, 8), 2, b, y)) is True
    assert (inSemiLinearSet((4, 10), 2, b, y)) is True
    assert (inSemiLinearSet((4, 9), 2, b, y)) is False
