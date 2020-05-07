import copy
import random
import numpy as np
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

    @property
    def name(self):
        return 'Iterated'


    def set_params(self, params):
        self.solution  = copy.copy(params['solution'])
        self.method    = params['method']
        self.cur_cost  = tools.compute_solution(self.problem, self.solution)
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
        for i in tqdm(range(self.n_iter),
                      position=0,
                      disable=not self.verbose):

            self.perturbation()
            self.refresh_params()
            local_search_solve, cost = self.LocalSearchSolver()

            if cost < self.cur_cost:
                self.cur_cost = cost
                self.solution = copy.copy(local_search_solve)

                self.k_bounds['curr']+=1
                if self.k_bounds['curr'] == self.k_bounds['max']:
                    self.k_bounds['curr'] = self.k_bounds['min']
            else:
                self.k_bounds['curr'] = self.k_bounds['min']

        if self.verbose:
            print('End cost: {}'.format(self.cur_cost))

        return local_search_solve
