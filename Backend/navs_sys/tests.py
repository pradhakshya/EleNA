from .graph_providers.loading_graph_provider import LoadingGraphProvider
from .graph_providers.mock_provider import MockProvider
from .routing_algorithms.dijkstra import Dijkstra
from .routing_algorithms.a_star import AStar
import osmnx
from django.test import TestCase

class GraphProviderTestCase(TestCase):
    def setUp(self):
        self.origin = (42.3732, 72.5199)
        self.destination = (42.1015, 72.5898)
        self.graph_provider = LoadingGraphProvider(self.origin, self.destination)

    def test_nodes_in_graph(self):
        assert 4546625833 in self.graph_provider.get_all_nodes()
    
    def test_num_nodes(self):
        assert len(self.graph_provider.get_all_nodes()) == 9247
    
    def test_neighbors(self):
        assert self.graph_provider.get_neighbors(4546625833) == [4546625834, 4546625844, 4546625832]
    
    def test_xyz_coordinate_system(self):
        coordinates = self.graph_provider.get_coords(7012795619)
        assert coordinates == {'x': 72.253918, 'y': 42.5119354, 'z': 1255.898}
        coordinates = self.graph_provider.get_coords(8637056741)
        assert coordinates == {'x': 72.3611156, 'y': 42.5148111, 'z': 1325.365}

    def tearDown(self):
        pass

 

class DijkstraTestCase(TestCase):
    def setUp(self):
        nodes = [1,2,3,4,5]

        neighbors = {}
        neighbors[1] = [2,3,4,5]
        neighbors[2] = [1,5]
        neighbors[3] = [1,4]
        neighbors[4] = [5]
        neighbors[5] = [3,4]

        edges = {}
        edges[(1,2)] = 1
        edges[(1,3)] = 1
        edges[(1,4)] = 6
        edges[(1,5)] = 2
        edges[(2,1)] = 8
        edges[(2,5)] = 2
        edges[(3,1)] = 4
        edges[(3,4)] = 7
        edges[(4,5)] = 5
        edges[(5,3)] = 6
        edges[(5,4)] = 9
        for n1, lst in neighbors.items():
            for n2 in lst:
                if (n1, n2) in edges and (n2, n1) not in edges:
                    edges[(n2,n1)] = edges[(n1,n2)]

        node2ele = {}
        node2ele[1] = 7.
        node2ele[2] = 0.
        node2ele[3] = 5.
        node2ele[4] = 10.
        node2ele[5] = 2.

        coords = {}
        coords[1] = [0,0]
        coords[2] = [2,0]
        coords[3] = [3,1]
        coords[4] = [1,-1]
        coords[5] = [2,-2]

        self.graph_provider = MockProvider(nodes, neighbors, edges, node2ele, coords)
    
    def test_ssp(self):
        dijkstra = Dijkstra(self.graph_provider)
        result = dijkstra.single_source(1)
        prev = result['prev']
        dist = result['dist']
        ele_diff = result['ele_diff']
        
        assert prev[1] == None
        assert prev[2] == prev[3] == prev[4] == prev[5] == 1

        assert dist[1] == 0.0
        assert dist[2] == 1.0
        assert dist[3] == 1.0
        assert dist[4] == 6.0
        assert dist[5] == 2.0    

        assert ele_diff[1] == 0.0
        assert ele_diff[2] == -7.0
        assert ele_diff[3] == -2.0
        assert ele_diff[4] == 3.0
        assert ele_diff[5] == -5.0

    def test_path_correctness(self):
        dijkstra = Dijkstra(self.graph_provider)
        # Test that we find a fairly non-trivial path
        res = dijkstra.search(3, 5)
        assert res.path == [3,1,5]
        assert res.path_len == 6.0
        assert res.ele_gain == 2.0

        # Test of right values
        res = dijkstra.search(2, 4)
        assert res.path == [2,5,4]
        assert res.path_len == 11.0
        assert res.ele_gain == 10.0
    
    def test_reverse_path_correct(self):
        dijkstra = Dijkstra(self.graph_provider)
        res = dijkstra.search(2, 5, end_is_source=True)
        assert res.path == [2,1,3,5]
        assert res.path_len == 11.0
        assert res.ele_gain == 7.0


class AStarTestCase(TestCase):
    def setUp(self):
        nodes = [1,2,3,4,5]

        neighbors = {}
        neighbors[1] = [2,3,4,5]
        neighbors[2] = [1,5]
        neighbors[3] = [1,4]
        neighbors[4] = [5]
        neighbors[5] = [3,4]

        edges = {}
        edges[(1,2)] = 1
        edges[(1,3)] = 1
        edges[(1,4)] = 6
        edges[(1,5)] = 2
        edges[(2,1)] = 8
        edges[(2,5)] = 2
        edges[(3,1)] = 4
        edges[(3,4)] = 7
        edges[(4,5)] = 5
        edges[(5,3)] = 6
        edges[(5,4)] = 9
        for n1, lst in neighbors.items():
            for n2 in lst:
                if (n1, n2) in edges and (n2, n1) not in edges:
                    edges[(n2,n1)] = edges[(n1,n2)]

        node2ele = {}
        node2ele[1] = 7.
        node2ele[2] = 0.
        node2ele[3] = 5.
        node2ele[4] = 10.
        node2ele[5] = 2.

        coords = {}
        coords[1] = [0,0]
        coords[2] = [2,0]
        coords[3] = [3,1]
        coords[4] = [1,-1]
        coords[5] = [2,-2]

        self.graph_provider = MockProvider(nodes, neighbors, edges, node2ele, coords)

    def test_path_correctness(self):
        astar = AStar(self.graph_provider)
        # Test that we find a fairly non-trivial path
        res = astar.search(3, 5)
        assert res.path == [3,1,5]
        assert res.path_len == 6.0
        assert res.ele_gain == 2.0

        # Test of right values
        res = astar.search(2, 4)
        assert res.path == [2,1,3,4]
        assert res.path_len == 16.0
        assert res.ele_gain == 12.0
    
    def test_min_ele_gain(self):
        astar = AStar(self.graph_provider)

        # Test of right values
        res = astar.search(2, 4)
        assert res.path == [2,1,3,4]
        assert res.path_len == 16.0
        assert res.ele_gain == 12.0

        # case where elevation gain is reduced by choosing a shorter path
        res = astar.search(2, 4, 15)
        assert res.path == [2,5,3,4]
        assert res.path_len == 15.0
        assert res.ele_gain == 10.0

    def test_astar_no_result(self):
        # no path found with desired properties
        astar = AStar(self.graph_provider)
        res = astar.search(2, 4, 8)
        assert res.path == []
        assert res.path_len == 0.0
        assert res.ele_gain == 0.0