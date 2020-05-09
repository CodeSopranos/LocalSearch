import copy
import random
import numpy as np
import matplotlib.pyplot as plt
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
        self.penalty = np.zeros((self.n, self.n), dtype=np.int32)
        self.history = []

    @property
    def name(self):
        return 'Guided'

    def set_params(self, params):
        self.solution  = copy.copy(params['solution'])
        self.method    = params['method']
        self.cur_cost  = tools.compute_solution(self.problem, self.solution)
        self.history.append(self.cur_cost)
        self.n_iter    = params['n_iter']
        self.n_epoch   = params['n_epoch']
        self.verbose   = params['verbose']
        self.mu        = params['mu']
        self.patience  = params['patience']


    def solve(self):
        solution = np.arange(self.n, dtype=np.int32)
        solution = np.random.permutation(solution)
        self.solution = solution

        self.solution, self.cur_cost = self.LocalSearchSolver()
        self.history.append(self.cur_cost)
        self.last_state = 0
        no_improve_counter = 0
        for epoch in tqdm(range(self.n_epoch),
                                   position=0,
                                   total=self.n_epoch,
                                   disable=not self.verbose):
            tmp_solution, h = self.LocalSearchSolver(self.augmented_cost)
            cost = tools.compute_solution(self.problem, tmp_solution)
            self.history.append(cost)
            if self.cur_cost > cost:
                # print('less')
                self.solution = tmp_solution
                self.cur_cost = cost
                self.last_state = epoch
                unimprove_counter = 0
            else:
                # self.solution = tmp_solution
                # self.cur_cost = cost
                no_improve_counter += 1
            self.update_penalty()
            self.refresh_params()
            if no_improve_counter > self.patience:
                if self.verbose:
                    print('No better solutions, stoping...')
                break

        if self.verbose:
            print('End cost: {}'.format(self.cur_cost))

        return self.solution


    def update_penalty(self):
        self.utility = np.zeros((self.n, self.n), dtype=np.float32)
        for i in range(self.n):
            for j in range(self.n):
                # dist = self.dist[self.solution[i]][self.solution[j]]
                dist = self.dist[i][self.solution[i]]
                flow = self.flow[i][j]
                c    = dist * flow
                # self.utility[self.solution[i]][self.solution[j]] = \
                #         c / (1 + self.penalty[self.solution[i]][self.solution[j]])
                self.utility[i][self.solution[i]] = \
                        c / (1 + self.penalty[i][self.solution[i]])
        maximized = self.utility.max()
        for i in range(self.n):
            # for j in range(self.n):
            #     if self.utility[self.solution[i]][self.solution[j]] == maximized:
            #         self.penalty[self.solution[i]][self.solution[j]] += 1
            if self.utility[i][self.solution[i]] == maximized:
                self.penalty[i][self.solution[i]] += 1

    @staticmethod
    def augmented_cost(problem, solution, params):
        cost    = tools.compute_solution(problem, solution)
        penalty = params['penalty']
        mu      = params['mu']
        n       = params['n']
        total_penalty = 0
        # for i in range(n):
        #     for j in range(n):
        #         total_penalty += penalty[solution[i]][solution[j]]
        for i in range(n):
            total_penalty += penalty[i][solution[i]]
        _lambda = cost / n
        # print( mu * _lambda )
        return cost + mu * _lambda * total_penalty


    def refresh_params(self):
        self.params = dict(solution=self.solution,
                           method = self.method,
                           n_iter = self.n_iter,
                           verbose = False)


    def LocalSearchSolver(self, cost_func=None):
        alg = local_search.LocalSearch(self.problem)
        alg.set_params(self.params)
        if cost_func:
            cost_params = {'penalty': self.penalty,
                           'mu': self.mu,
                           'n': self.n}
            alg.set_cost_func(cost_func, cost_params)
        local_search_solve = alg.solve()
        return local_search_solve, alg.cur_cost


    def get_history(self):
        plt.figure(figsize=(10, 4))
        plt.plot(self.history, label='cost_function')
        plt.plot(self.last_state+2,
                 self.history[self.last_state+2],
                 'o', label='chosen optimum')
        plt.grid()
        plt.legend()
        plt.title(self.name)
        # plt.show()
        return self.history
