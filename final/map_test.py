import unittest
from fib import memo
from random import randrange
from map import dijkstra
from itertools import product
import numpy as np
import random

class DijkstraTest(unittest.TestCase):

    def lattice(self, width, height):
        def graph(vertex):
            x,y=vertex
            res=[]
            if(x<width):
                res.append(((x+1,y),1))
            if(x>0):
                res.append(((x-1,y),1))
            if(y<height):
                res.append(((x,y+1),2))
            if(y>0):
                res.append(((x,y-1),2))
            return res
        return graph

    def random(self, n):
        @memo
        def graph(x):
            return [(i,1) for i in range(n) if random.random()<0.2]
        return graph

    def setUp(self):
        pass
    


    def test_fixed_graph(self):
        #TODO
        pass

    def test_lattice(self):
        n=20
        graph=self.lattice(n,n)
        for i in range(100):
            start=(randrange(n), randrange(n))
            end=(randrange(n), randrange(n))
            dist, _ = dijkstra(graph, start, end)
            self.assertEqual(dist, abs(start[0]-end[0])+2*abs(start[1]-end[1]))

    def test_random_graph(self):
        n=100
        graph=self.random(n)
        vertices=random.sample(list(product(range(n), range(n))),1000)
        mean_distance=np.mean([dijkstra(graph, i, j)[0] for i,j in vertices]) 
        self.assertGreater(mean_distance,1.5)
        self.assertLess(mean_distance,2.5)

unittest.main()


