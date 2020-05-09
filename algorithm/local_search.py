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
                        'stochastic-2opt',
                        'first-delta-improvement']
        self.cost_func   = self.simple_cost
        self.cost_params = None

    @property
    def name(self):
        return 'LocalSearch'

    @staticmethod
    def simple_cost(problem, solution, params):
        return tools.compute_solution(problem, solution)

    def set_params(self, params):
        self.solution = copy.copy(params['solution'])
        self.method   = params['method']
        self.cur_cost = self.cost_func(self.problem, self.solution, self.cost_params)
        self.n_iter   = params['n_iter']
        self.verbose  = params['verbose']


    def set_cost_func(self, cost_function, param):
        self.cost_func   = cost_function
        self.cost_params = param


    def solve(self):
        if self.method == self.methods[0]:
            return self.first_improvement()
        elif self.method == self.methods[1]:
            return self.best_improvement()
        elif self.method == self.methods[2]:
            return self.stochastic_2opt()
        elif self.method == self.methods[3]:
            return self.first_delta_improvement()
        else:
            raise 'Method must be one of {}'.format(self.methods)


    def first_delta_improvement(self):
        if self.verbose:
            print('Start cost {}'.format(self.cur_cost))

        dont_look  = {x:np.zeros(self.n, dtype=np.int32) for x in range(self.n)}
        for i in tqdm_notebook(range(self.n_iter),
                               position=0,
                               total=self.n_iter,
                               disable=not self.verbose):
            flag = True
            for opt in combinations(np.arange(self.n, dtype=np.int32), 2):
                if (sum(dont_look[opt[0]]) >= 19 or
                    sum(dont_look[opt[1]]) >= 19):
                    continue
                diff = self.__delta__(opt[0], opt[1])
                if diff < 0:
                    self.cur_cost += diff
                    self.solution[list(opt)] = self.solution[list(opt)][::-1]
                    flag = False
                    break
                dont_look[opt[0]][opt[1]] = 1
                dont_look[opt[1]][opt[0]] = 1
            if flag and self.verbose:
                print('No better solutions, stoping...')
                break
        if self.verbose:
            print('End cost {}'.format(self.cur_cost))

        return self.solution


    def __delta__(self, r, s):
        diff = 0
        pi = self.solution
        for k in range(self.n):
            if k != r and k != s:
                diff += (self.flow[k, r] + self.flow[r, k]) * \
                        (self.dist[pi[s], pi[k]] - self.dist[pi[r], pi[k]]) + \
                        (self.flow[k,s] + self.flow[s, k]) * \
                        (self.dist[pi[r], pi[k]] - self.dist[pi[s], pi[k]])
        if self.cost_params:
            # print('Yes')
            _lambda = 1.0 #self.cur_cost / (self.n**4)
            mu = self.cost_params['mu']
            penalty = self.cost_params['penalty']
            diff += mu * _lambda * ((penalty[r][pi[s]] + penalty[s][pi[r]]) - \
                                    (penalty[r][pi[r]] + penalty[s][pi[s]]))
        return diff

    def first_improvement(self):

        if self.verbose:
            print('Start cost {}'.format(self.cur_cost))

        comb       = list(combinations(np.arange(self.n, dtype=np.int32), 2))
        dont_look  = {x:np.zeros(self.n, dtype=np.int32) for x in range(self.n)}
        for i in tqdm_notebook(range(self.n_iter),
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
                cost = self.cost_func(self.problem, tmp_solution, self.cost_params)
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

        if self.verbose:
            end_cost = self.cost_func(self.problem, self.solution, self.cost_params)
            print('End cost {}'.format(end_cost))
        return self.solution


    def stochastic_2opt(self):
        if self.verbose:
            print('Start cost {}'.format(self.cur_cost))

        for i in tqdm_notebook(range(self.n_iter), position=0, disable=not self.verbose):
            flag = True
            for j in range(self.n_iter):
                ind_left, ind_right = randint(0, self.n), randint(0, self.n)

                tmp_solution      = copy.copy(self.solution)
                tmp_solution[ind_left:ind_right] = tmp_solution[ind_left:ind_right][::-1]
                cost = self.cost_func(self.problem, tmp_solution, self.cost_params)
                if cost < self.cur_cost:
                    self.cur_cost = cost
                    self.solution = tmp_solution
                    flag = False

            if flag and self.verbose:
                print('No better solutions, stoping...')
                break

        end_cost = self.cost_func(self.problem, self.solution, self.cost_params)
        if self.verbose:
            print('End cost {}'.format(end_cost))
        return self.solution


    def best_improvement(self):
        if self.verbose:
            print('Start cost {}'.format(self.cur_cost))

        dont_look = np.zeros(self.n)
        comb = list(combinations(np.arange(self.n), 2))
        for i in tqdm_notebook(range(self.n_iter), position=0, disable=not self.verbose):

            best_opt = None
            for opt in comb:
                opt = list(opt)
                tmp_solution      = copy.copy(self.solution)
                tmp_solution[opt] = tmp_solution[opt][::-1]
                cost = self.cost_func(self.problem, tmp_solution, self.cost_params)
                if cost < self.cur_cost:
                    self.cur_cost = cost
                    best_opt      = opt
            if best_opt:
                self.solution[best_opt] = self.solution[best_opt][::-1]
            else:
                print('No better solutions, stoping...')
                break
        end_cost = self.cost_func(self.problem, self.solution, self.cost_params)

        if self.verbose:
            print('End cost {}'.format(end_cost))

        return self.solution
