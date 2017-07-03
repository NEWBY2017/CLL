import numpy as np

rand = np.random.rand
randint = np.random.randint
choice = np.random.choice

## re-write eval function
class GeneticAlgorithm():
    '''
    在N个选项中选择k个，选择标准是data根据结果的切片和最大
    e.g:
        num_choice = 2
        data:
             1  2  3  4
             5  6  7  8
             9 10 11 12
            13 14 15 16
        则切片[2,3]的和最大，切片[2,3]为
            11 12
            15 16
    '''
    def __init__(self, num_genes, num_population, num_choice, max_iter, cross_p=0.8, mutate_p=0.1):
        self.m = num_genes
        self.max_iter = max_iter
        self.n = num_population
        self.k = num_choice
        self.pop = np.arange(self.n)
        self.cross_p = cross_p
        self.mutate_p = mutate_p

    def fit(self, data, density=None, **kwargs):
        self.init_prep(**kwargs)
        if density is None:
            density = np.ones([self.n]).astype(float)
        else:
            density = np.array(density).astype(float)
        self.init_density(density)

        self.pool = np.array([self.init_gene() for _ in range(self.m)])
        best_gene, best_score = self.pool[0], -np.inf
        cross, mutate, eval = self.cross, self.mutate, self.eval

        for _ in range(self.max_iter):
            cross(); mutate()
            self.pool.sort(1)
            scores = eval(data)
            i = scores.argmax()
            if scores[i] > best_score:
                best_score = scores[i]
                best_gene = self.pool[i]
                print("Current iteration:",_, "\tCurrent best score", best_score, "\tbest gene", best_gene)
            scores = scores/scores.sum()
            index = choice(range(len(scores)), self.m-1, replace=True, p=scores)
            self.pool = np.r_[[best_gene], self.pool[index]]
        # print(pool)
        self.best_gene, self.best_score = best_gene, best_score
        print(self.best_gene, self.best_score)

    def eval(self, data, **kwargs):
        gene_eval = self.gene_eval
        L = np.array([gene_eval(data, gene, **kwargs) for gene in self.pool])
        return L

    def mutate(self, **kwargs):
        pool = self.pool
        for i, gene in enumerate(pool):
            pool[i] = self.gene_mutate(gene, **kwargs)

    def cross(self, **kwargs):
        pool = self.pool
        n = self.m//2
        for i in range(n):
            if rand() >= self.cross_p: continue
            gene1, gene2 = pool[i*2], pool[i*2+1]
            cut = randint(self.n)
            gene1[cut:], gene2[cut:] = gene2[cut:], gene1[cut:]
            pool[i*2]   = self.gene_sanity(gene1, **kwargs)
            pool[i*2+1] = self.gene_sanity(gene2, **kwargs)

    def init_prep(self, **kwargs):
        pass

    def init_density(self, density=None, **kwargs):
        '''
        Modity self.density, and normalize so as to sum to 1
        '''
        self.density = density/density.sum()

    def init_gene(self, **kwargs):
        '''
        :return: a gene, as a numpy array
        '''
        return choice(self.pop, self.k, replace=False, p=self.density)

    def gene_eval(self, data, gene, **kwargs):
        '''
        :return: a non-negative score shows the fit of the gene
        '''
        score = data[gene][:, gene].sum()
        return score

    def gene_mutate(self, gene, **kwargs):
        '''
        a gene that shows the
        :return:
        '''
        for i, num in enumerate(gene):
            if np.random.rand() > self.mutate_p: continue
            ind = choice(self.pop, 1, p=self.density)
            while ind in gene:
                ind = choice(self.pop, 1, p=self.density)
            gene[i] = ind
        return gene

    def gene_sanity(self, gene, **kwargs):
        s = set(gene)
        if len(s) == len(gene):
            pass
        else:
            n = len(gene) - len(s)
            density = self.density.copy()
            density[gene] = 0
            density /= density.sum()
            inds = choice(self.pop, n, replace=False, p = density)
            gene = np.r_[np.unique(gene), inds]
        return gene



def solver_ga(trans_mat, density, r=3, max_iter=500):
    genetic = GeneticAlgorithm(20, len(trans_mat), r, max_iter)
    genetic.fit(trans_mat, density)
    return genetic.best_gene, genetic.best_score


def solver_all_comb(trans_mat, r=3):
    from itertools import combinations
    n = len(trans_mat)
    L = []
    for val in combinations(range(n), r):
        ind = np.zeros(n).astype(bool)
        ind[list(val)] = True
        score = trans_mat[ind][:,ind].sum()
        L.append([val, score])
    return sorted(L, key=lambda x:x[1])

if __name__ == '__main__':
    n = 100
    data = np.arange(n**2).reshape([n, -1])
    density = np.arange(n)

    ga = GeneticAlgorithm(20, n, 2, 100, 0.6, 0.1)
    ga.fit(data, density)