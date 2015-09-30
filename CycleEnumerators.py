from numpy.core.umath import left_shift
from structures import *
"""
'CycleEnumerator' that totally sound like some java stuff.
"""
def brute_force(vass,state):
    """
    Brute force procedure to enumerate elementary cycles in a vass.
    Very ineffective.
    :param vass:
    :param state:
    :return:
    """
    cycles = {}
    def visit(visited, path, current_state):
        visited.add(current_state)
        for s, c in vass.E[current_state]:
            if s in visited:
               cycles.add(path.append((s,c)))
            else :
                visit(visited.copy(),path.append(s), s)
    return cycles


"""
Modified an implementation found on github :
"""
def tarjan_cycles(vass):

    E = vass.E.copy()


    point_stack = list()
    marked = dict()
    marked_stack = list()
    cycles = []


    def backtrack(v):
        f = False
        point_stack.append(v)
        marked[v] = True
        marked_stack.append(v)
        for w in E[v].keys():
            if w<s:
                E[w] = 0
            elif w==s:
                cycles.append(list(point_stack))
                f = True
            elif not marked[w]:
                f = backtrack(w) or f
        if f:
            while marked_stack[-1] != v:
                u = marked_stack.pop()
                marked[u] = False
            marked_stack.pop()
            marked[v] = False
        point_stack.pop()
        return f

    for i in range(len(E)):
        marked[i] = False

    for s in range(len(E)):
        backtrack(s)
        while marked_stack:
            u = marked_stack.pop()
            marked[u] = False

    return [cycle(i) for i in cycles]