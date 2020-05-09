import copy
import random
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm, tqdm_notebook
from algorithm.base import Algorithm
from itertools import combinations
from algorithm import local_search
from utils import tools


class Iterated(Algorithm):

    def __init__(self, problem):
        self.n = problem['n']
        self.dist = problem['dists']
        self.flow = problem['flows']
        self.problem = problem
        self.history = []

    @property
    def name(self):
        return 'Iterated'


    def set_params(self, params):
        self.solution  = copy.copy(params['solution'])
        self.method    = params['method']
        self.cur_cost  = tools.compute_solution(self.problem, self.solution)
        self.history.append(self.cur_cost)
        self.n_iter    = params['n_iter']
        self.n_iter_ls = params['n_iter_ls']
        self.verbose   = params['verbose']
        self.k_bounds  = {'min': int(self.n * 0.5),
                          'max': int(self.n * 0.75),
                          'curr': int(self.n * 0.5)}

    def refresh_params(self):
        self.params = dict(solution=self.solution,
                           method = self.method,
                           n_iter = self.n_iter_ls,
                           verbose = False)

    def perturbation(self):
        start_ind = random.randint(0, self.n - self.k_bounds['curr'])
        end_ind = start_ind + self.k_bounds['curr']
        if end_ind > self.n:
            end_ind = int(end_ind % self.n)
            self.solution[start_ind:self.n] = np.random.permutation(self.solution[start_ind:end_ind])
            self.solution[0:end_ind] = np.random.permutation(self.solution[0:end_ind])
        else:
            self.solution[start_ind:end_ind] = np.random.permutation(self.solution[start_ind:end_ind])

    def LocalSearchSolver(self):
        alg = local_search.LocalSearch(self.problem)
        alg.set_params(self.params)
        local_search_solve = alg.solve()
        return local_search_solve, alg.cur_cost

    def solve(self):
        if self.verbose:
            print('Start cost: {}'.format(self.cur_cost))

        self.solution, self.cur_cost = self.LocalSearchSolver()
        self.last_state = 0
        self.best_solution = self.solution
        for i in tqdm_notebook(range(self.n_iter),
                               position=0,
                               disable=not self.verbose):
            self.perturbation()
            self.refresh_params()
            local_search_solve, cost = self.LocalSearchSolver()
            self.history.append(cost)
            if cost < self.cur_cost:
                self.cur_cost = cost
                self.solution = copy.copy(local_search_solve)
                self.best_solution = copy.copy(local_search_solve)
                self.last_state = i

                self.k_bounds['curr'] += 1
                if self.k_bounds['curr'] == self.k_bounds['max']:
                    self.k_bounds['curr'] = self.k_bounds['min']
            else:
                self.k_bounds['curr'] = self.k_bounds['min']

        if self.verbose:
            print('End cost: {}'.format(self.cur_cost))
        self.solution = self.best_solution
        return self.solution


    def get_history(self):
        plt.figure(figsize=(10, 4))
        plt.plot(self.history, label='cost_function')
        plt.plot(self.last_state+1,
                 self.history[self.last_state+1],
                 'o', label='chosen optimum')
        plt.grid()
        plt.legend()
        plt.title(self.name)
        # plt.show()
        return self.history
