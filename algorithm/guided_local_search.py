import copy
import random
import numpy as np
from tqdm import tqdm, tqdm_notebook
from algorithm.base import Algorithm
from itertools import combinations
from algorithm import local_search
from utils import tools


class Guided(Algorithm):

    def __init__(self, problem):
        self.n = problem['n']
        self.dist = problem['dists']
        self.flow = problem['flows']
        self.problem = problem
        self.penalty = np.zeros((self.n, self.n))

    @property
    def name(self):
        return 'Guided'

    def set_params(self, params):
        self.solution  = copy.copy(params['solution'])
        self.method    = params['method']
        self.cur_cost  = tools.compute_solution(self.problem, self.solution)
        self.n_iter    = params['n_iter']
        self.n_epoch   = params['n_epoch']
        self.verbose   = params['verbose']
        self.mu        = params['mu']

    def solve(self):
        solution = np.arange(self.n)
        solution = np.random.permutation(solution)
        self.solution = solution

        self.solution, self.cur_cost = self.LocalSearchSolver()
        for epoch in tqdm(range(self.n_epoch),
                          position=0,
                          disable=not self.verbose):
            tmp_solution, cost = self.LocalSearchSolver()
            cost = self.augmented_cost(cost)
            if self.cur_cost > cost:
                self.solution = tmp_solution
                self.cur_cost = cost
            self.update_penalty()
            self.refresh_params()

        if self.verbose:
            print('End cost: {}'.format(self.cur_cost))

        return self.solution


    def update_penalty(self):
        self.utility = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                dist = self.dist[self.solution[i]][self.solution[j]]
                flow = self.flow[i][j]
                c    = dist * flow
                self.utility[self.solution[i]][self.solution[j]] = \
                        c / (1 + self.penalty[self.solution[i]][self.solution[j]])
        maximized = self.utility.max()
        for i in range(self.n):
            for j in range(self.n):
                if self.utility[self.solution[i]][self.solution[j]] == maximized:
                    self.penalty[self.solution[i]][self.solution[j]] += 1


    def augmented_cost(self, cost):
        total_penalty = 0
        for i in range(self.n):
            for j in range(self.n):
                total_penalty += self.penalty[self.solution[i]][self.solution[j]]
        return cost + self.mu * total_penalty


    def refresh_params(self):
        self.params = dict(solution=self.solution,
                           method = self.method,
                           n_iter = self.n_iter,
                           verbose = False)

    def LocalSearchSolver(self):
        alg = local_search.LocalSearch(self.problem)
        alg.set_params(self.params)
        local_search_solve = alg.solve()
        return local_search_solve, alg.cur_cost
