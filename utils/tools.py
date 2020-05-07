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


def generate_stat(algorithms,
                  benchmarks,
                  alg_params,
                  n_observations=3,
                  **params):

    for algorithm, params in zip(algorithms, alg_params):
        test_knap = dict(benchmarks[1], **params)
        assert isinstance(algorithm(test_knap), Algorithm)

    info_dct    = {
                     'algorithm':     [],
                     'benchmark':     [],
                     'capacity':      [],
                     'preprocessing': [],
                     'execution':     [],
                     'observation':   [],
                     'optim_weight':  [],
                     'optim_profit':  [],
                   }
    for observation in range(n_observations):

        for key in benchmarks:

            knapsack = benchmarks[key]

            for algorithm, params in zip(algorithms, alg_params):

                knapsack = dict(knapsack, **params)

                start_time = datetime.now()
                alg = algorithm(knapsack)
                preprocess = datetime.now() - start_time

                start_time = datetime.now()
                optimal    = alg.solve()
                execution  = datetime.now() - start_time

                w, p = compute_knapsack(knapsack, optimal)


                info_dct['algorithm']     += [alg.name]
                info_dct['benchmark']     += [key]
                info_dct['capacity']      += [knapsack['capacity'][0]]
                info_dct['preprocessing'] += [preprocess.total_seconds()]
                info_dct['execution']     += [execution.total_seconds()]
                info_dct['observation']   += [observation]
                info_dct['optim_weight']  += [w]
                info_dct['optim_profit']  += [p]
    return pd.DataFrame.from_dict(info_dct)
