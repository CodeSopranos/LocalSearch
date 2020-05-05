import numpy as np
from algorithm.base import Algorithm
from itertools import combinations
from utils import tools
from tqdm import tqdm
import copy


class LocalSearch(Algorithm):

    def __init__(self, problem):
        self.n = problem['n']
        self.dist = problem['distances']
        self.flow = problem['flows']
        self.problem = problem
        pass


    @property
    def name(self):
        return 'BruteForce'


    def set_params(self, params):
        self.solution = params['solution']
        self.n_iter   = params['n_iter']
        self.patience = params['patience']


    def solve(self):

        cur_cost = tools.compute_solution(self.problem, self.solution)
        print('Start cost {}'.format(cur_cost))

        indexes = np.arange(self.n)
        for i in tqdm(range(self.n_iter), total=self.n_iter):
            comb = list(combinations(indexes, 2))
            flag = False
            for c in comb:
                c = list(c)
                tmp_solution = copy.copy(self.solution)
                tmp_solution[c] = tmp_solution[c][::-1]
                cost = tools.compute_solution(self.problem, tmp_solution)
                if cost < cur_cost:
                    cur_cost = cost
                    self.solution = tmp_solution
                    flag = True
                    break
            if not flag:
                self.patience -= 1
                flag = False
            if self.patience == 0:
                print('patience is over!')
                break
        end_cost = tools.compute_solution(self.problem, self.solution)
        print('End cost {}'.format(end_cost))
        return self.solution
