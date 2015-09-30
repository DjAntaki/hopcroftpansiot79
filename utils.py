import numpy as np
import qsoptex
import pulp

def solve_pulp(c, A_up, b_up):
    """
    Will minimize
    :param c: The objective
    :param A_up:
    :param b_up:
    :return: null if no solution, a numpy array containing the solution if there is
    """

def solve_with_qsopt(c, A_eq, b_eq, A_up=None, b_up=None, objective=None):
    """Solve using QSopt_ex the following

    (Max | Min) cx
    in respect of constraints :
    A_eq*x = b_eq and A_up*x >= b_up

    objective is to minimize by default.
    """
    assert A_eq.shape[0] == len(b_eq)
    import qsoptex

    if objective==None:
        objective = qsoptex.ObjectiveSense.MINIMIZE


    p = qsoptex.ExactProblem()
    names = []
    n = len(c)

    for i, x in enumerate(c):
        names.append(bytes([i]))
        p.add_variable(name=names[i],objective=x,lower=0)

    Atype = type(A_eq)
    if Atype == np.matrix :
        for index, line in enumerate(A_eq) :
            d = {} # dictionnary representing the equality constraints
            for x in range(0, n):
                d[x] = int(line.getA1()[x])
            p.add_linear_constraint(qsoptex.ConstraintSense.EQUAL, d, int(b_eq[index]))

    elif Atype == np.recarray or Atype == np.ndarray or Atype == np.array :
        for index, line in enumerate(A_eq) :
            d = {} # dictionnary representing the equality constraints
            for x in range(0, n):
                d[x] = int(line[x])

            p.add_linear_constraint(qsoptex.ConstraintSense.EQUAL, d, int(b_eq[index]))

    else :
        raise TypeError("A_eq type is not recognize.")

    if A_up is not None and b_up is not None :
        assert A_up.shape[0] == len(b_up)
        for index, line in enumerate(A_up) :
            d = {} # dictionnary representing the inequality constraints
            flat = line.flatten()
            for x in range(0, n):
                d[x] = int(flat[x])

            p.add_linear_constraint(qsoptex.ConstraintSense.GREATER, d, int(b_up[index]))

    p.set_objective_sense(objective)
    p.set_param(qsoptex.Parameter.SIMPLEX_DISPLAY, 0)
    result = Bunch(status=p.solve(),x=[])

    if result.status == qsoptex.SolutionStatus.OPTIMAL :
        # récupération de la valeur de la solution
        for j in range(0, n):
            result.x.append(p.get_value(names[j]))

    return result
