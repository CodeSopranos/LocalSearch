import numpy as np
from algorithm.base import Algorithm
from itertools import combinations
from utils import tools
from random import randint
from tqdm import tqdm, tqdm_notebook
import copy


class LocalSearch(Algorithm):

    def __init__(self, problem):
        self.n = problem['n']
        self.dist = problem['dists']
        self.flow = problem['flows']
        self.problem = problem
        self.methods = ['first-improvement',
                        'best-improvement',
                        'stochastic-2opt']


    @property
    def name(self):
        return 'LocalSearch'

    def set_params(self, params):
        self.solution = copy.copy(params['solution'])
        self.method   = params['method']
        self.cur_cost = tools.compute_solution(self.problem, self.solution)
        self.n_iter   = params['n_iter']
        self.verbose  = params['verbose']


    def solve(self):
        if self.method == self.methods[0]:
            return self.first_improvement()
        elif self.method == self.methods[1]:
            return self.best_improvement()
        elif self.method == self.methods[2]:
            return self.stochastic_2opt()
        else:
            print('Method must be one of {}'.format(self.methods))


    def first_improvement(self):

        if self.verbose:
            print('Start cost {}'.format(self.cur_cost))

        comb = list(combinations(np.arange(self.n), 2))
        dont_look  = {x:np.zeros(self.n) for x in range(self.n)}
        for i in tqdm(range(self.n_iter),
                      position=0,
                      disable=not self.verbose):

            flag = True
            for opt in comb:
                if (sum(dont_look[opt[0]]) >= 19 or
                    sum(dont_look[opt[1]]) >= 19):
                    continue
                opt = list(opt)
                tmp_solution      = copy.copy(self.solution)
                tmp_solution[opt] = tmp_solution[opt][::-1]
                cost = tools.compute_solution(self.problem, tmp_solution)
                if cost < self.cur_cost:
                    self.cur_cost = cost
                    self.solution = tmp_solution
                    flag = False
                    break
                dont_look[opt[0]][opt[1]] = 1
                dont_look[opt[1]][opt[0]] = 1
            if flag and self.verbose:
                print('No better solutions, stoping...')
                break

        end_cost = tools.compute_solution(self.problem, self.solution)
        if self.verbose:
            print('End cost {}'.format(end_cost))
        return self.solution

    def stochastic_2opt(self):
        if self.verbose:
            print('Start cost {}'.format(self.cur_cost))

        for i in tqdm(range(self.n_iter), position=0, disable=not self.verbose):
            flag = True
            for j in range(self.n_iter):
                ind_left, ind_right = randint(0, self.n), randint(0, self.n)

                tmp_solution      = copy.copy(self.solution)
                tmp_solution[ind_left:ind_right] = tmp_solution[ind_left:ind_right][::-1]
                cost = tools.compute_solution(self.problem, tmp_solution)
                if cost < self.cur_cost:
                    self.cur_cost = cost
                    self.solution = tmp_solution
                    flag = False

            if flag and self.verbose:
                print('No better solutions, stoping...')
                break

        end_cost = tools.compute_solution(self.problem, self.solution)
        if self.verbose:
            print('End cost {}'.format(end_cost))
        return self.solution

    def best_improvement(self):
        if self.verbose:
            print('Start cost {}'.format(self.cur_cost))

        dont_look = np.zeros(self.n)
        comb = list(combinations(np.arange(self.n), 2))
        for i in tqdm(range(self.n_iter), position=0, disable=not self.verbose):

            best_opt = None
            for opt in comb:
                opt = list(opt)
                tmp_solution      = copy.copy(self.solution)
                tmp_solution[opt] = tmp_solution[opt][::-1]
                cost = tools.compute_solution(self.problem, tmp_solution)
                if cost < self.cur_cost:
                    self.cur_cost = cost
                    best_opt      = opt
            if best_opt:
                self.solution[best_opt] = self.solution[best_opt][::-1]
            else:
                print('No better solutions, stoping...')
                break
        end_cost = tools.compute_solution(self.problem, self.solution)

        if self.verbose:
            print('End cost {}'.format(end_cost))

        return self.solution
