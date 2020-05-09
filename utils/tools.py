import requests
import numpy as np
import pandas as pd
from datetime import datetime
from algorithm.base import Algorithm


def compute_solution(problem, solution):
    cost = 0
    for i in range(problem['n']):
        for j in range(problem['n']):
            # dist = problem['dists'][i][solution[j]]
            dist = problem['dists'][solution[i]][solution[j]]
            flow = problem['flows'][i][j]
            cost += flow * dist
    return cost


def get_problem_dct(path) -> dict:

    with open(path, 'r') as f:
        file = f.read().split('\n')

    n = int(file[0])
    distances = np.zeros((n, n),dtype=np.int32)
    flows     = np.zeros((n, n),dtype=np.int32)
    for i in range(n):
        distances[i, :] = [int(x) for x in file[1+i].split(' ') if x]
        flows[i, :]     = [int(x) for x in file[2+i+n].split(' ') if x]
    return dict(n=n,
                dists=distances,
                flows=flows)
