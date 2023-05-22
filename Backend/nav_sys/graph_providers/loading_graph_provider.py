import osmnx
import networkx as nx
from collections import defaultdict
import math

from ..utilities.keys import api_key
from .graph_provider import GraphProvider

# Side length of chunk in degrees
MAP_CHUNK_SIZE = 0.01

# The keys to the loaded_chunks dict are given as integers in units of CHUNK_SIZE
# (e.g. if CHUNK_SIZE=0.01, then the bool describing whether chunk with...
# ...northeast corner (12deg, 12deg) would be stored in loaded_chunks[1200][1200])
cache = {
    'loaded_chunks': defaultdict(lambda: defaultdict(lambda: False)),
    'graph': nx.MultiDiGraph()
}

cache_entry_counter = 0
CACHE_CLEAR_THRESHOLD = 200

def clear_cache():
    """Clear the cache"""
    cache['loaded_chunks'] = defaultdict(lambda: defaultdict(lambda: False))
    cache['graph'] = nx.MultiDiGraph()
    global cache_entry_counter
    cache_entry_counter = 0

def add_to_cache():
    """Add an entry to the cache and check if it's time to clear the cache"""
    global cache_entry_counter
    cache_entry_counter += 1
    if cache_entry_counter >= CACHE_CLEAR_THRESHOLD:
        clear_cache()

class LoadingGraphProvider(GraphProvider):
    """Graph provider implementation that lazily loads sections of the world map.

    Attributes:
        start: the id of the node closest to the origin
        end: the id of the node closest to the destination
        lazy_loading_enabled: controls whether additional chunks should be automatically loaded
    """

    def __init__(self, origin_coords, destination_coords):
        initial_chunks = self._compute_initial_area(origin_coords, destination_coords)
        self._load_chunk(initial_chunks['x'], initial_chunks['y'], initial_chunks['w'], initial_chunks['h'])
        self.start = osmnx.distance.get_nearest_node(cache['graph'], origin_coords, method='euclidean')
        self.end = osmnx.distance.get_nearest_node(cache['graph'], destination_coords, method='euclidean')
        self.lazy_loading_enabled = True

    def get_all_nodes(self):
        return cache['graph'].nodes
    
    def get_neighbors(self, node):
        """Lazily load necessary chunks before returning neighbors of a node

        If the passed node has neighbors which are outside the currently loaded portion
        of the map, this function will load the chunks they're in.

        Args:
            node: the id of the node to get the neighbors of

        Returns:
            The neighbors of the passed node.

        """
        neighbors = list(cache['graph'].neighbors(node))
        if self.lazy_loading_enabled:
            # If any of the node's neighbors fall outside the loaded chunks...
            # ...then load the chunk they belong to first
            for neighbor in neighbors:
                coords = cache['graph'].nodes[neighbor]
                x_coordinate = math.floor(coords['x'] / MAP_CHUNK_SIZE) * MAP_CHUNK_SIZE
                y_coordinate = math.floor(coords['y'] / MAP_CHUNK_SIZE) * MAP_CHUNK_SIZE
                if not self._is_chunk_loaded(x_coordinate, y_coordinate):
                    self._load_chunk(x_coordinate, y_coordinate)
        return neighbors

    def get_distance_estimate(self, node1, node2):
        """Estimate the distance between any two nodes, no edge necessary.

        This is useful as a heuristic. Using simple trigonometry, it 
        calculates the distance as the crow flies.

        Args:
            n1: The first node (its integer id).
            n1: The second node (its integer id).

        Returns:
            The estimated distance between the nodes expressed as a number.
        """
        point1 = self.get_coords(node1)
        point2 = self.get_coords(node2)
        # d = sqrt((x - x')^2 + (y - y')^2 + (z - z')^2)
        return math.sqrt(
            (point1['x'] - point2['x']) ** 2 +
            (point1['y'] - point2['y']) ** 2 +
            (point1['z'] - point2['z']) ** 2
        )

    # Compute actual distance between two adjacent nodes
    def get_edge_distance(self, node1, node2):
        return cache['graph'].get_edge_data(node1, node2)[0]['length']

    # Get x, y, and z coordinates from a node id
    def get_coords(self, node):
        node_data = cache['graph'].nodes[node]
        return {
            'x': node_data['x'],
            'y': node_data['y'],
            'z': node_data['elevation']
        }
    
    # Load and merge the map chunk at (x, y) into the cache['graph'] if it is not already loaded
    def _load_chunk(self, x, y, w = 1, h = 1):
        """Download the map associated with the chunk at (x, y) and merge it into cache['graph']

        Args:
            x: The longitude of the chunk to load
            y: The latitude of the chunk to load
            w: The width (in chunks) to load
            h: The height (in chunks) to load
        """
        # Don't do anything if the chunks are already loaded
        if self._is_chunk_loaded(x, y, w, h):
            return
        # Get the northwest corner of the chunk
        x1 = math.floor(x / MAP_CHUNK_SIZE) * MAP_CHUNK_SIZE
        y1 = math.floor(y / MAP_CHUNK_SIZE) * MAP_CHUNK_SIZE
        # Get the southeast corner of the chunk
        x2 = x1 + MAP_CHUNK_SIZE * w
        y2 = y1 + MAP_CHUNK_SIZE * h
        compose = nx.algorithms.operators.binary.compose
        # Download the chunk as a graph, including edges that cross the chunk boundary
        subgraph = osmnx.graph.graph_from_bbox(y2, y1, x2, x1, simplify=False, truncate_by_edge=True)
        # Add elevation data to the loaded chunk
        osmnx.elevation.add_node_elevations(subgraph, api_key)
        # Merge the loaded chunk into the current graph
        cache['graph'] = compose(cache['graph'], subgraph)
        # Mark all the chunks as loaded
        for i in range(w):
            for j in range(h):
                self._set_chunk_loaded(x1 + MAP_CHUNK_SIZE * i, y1 + MAP_CHUNK_SIZE * j)

    # Helper methods for checking whether a chunk is loaded and marking it as loaded

    def _is_chunk_loaded(self, x, y, w = 1, h = 1):
        """Check whether a given area is loaded

        Args:
            x: The longitude of the chunk to check
            y: The latitude of the chunk to check
            w: The width (in chunks) to check
            h: The height (in chunks) to check

        Returns:
            True if all the chunks in the specified area are loaded
        """
        x_coordinate = math.floor(x / MAP_CHUNK_SIZE)
        y_coordinate = math.floor(y / MAP_CHUNK_SIZE)
        for i in range(w):
            for j in range(h):
                if not cache['loaded_chunks'][x_coordinate + i][y_coordinate + j]:
                    return False
        return True

    def _set_chunk_loaded(self, x, y):
        """Marks the chunk at (x, y) as loaded"""
        x_coordinate = math.floor(x / MAP_CHUNK_SIZE)
        y_coordinate = math.floor(y / MAP_CHUNK_SIZE)
        cache['loaded_chunks'][x_coordinate][y_coordinate] = True

    # Compute the initial bounding box based on the start and end coordinates
    def _compute_initial_area(self, start, end):
        """Computes the initial bounding box to load"""
        north = max(start[0], end[0])
        south = min(start[0], end[0])
        east = max(start[1], end[1])
        west = min(start[1], end[1])
        longer_diff = max(abs(east - west), abs(north - south))
        chunk_north = math.ceil((north + longer_diff) / MAP_CHUNK_SIZE)
        chunk_south = math.floor((south - longer_diff) / MAP_CHUNK_SIZE)
        chunk_east = math.ceil((east + longer_diff) / MAP_CHUNK_SIZE)
        chunk_west = math.floor((west - longer_diff) / MAP_CHUNK_SIZE)
        return {
            'x': chunk_west * MAP_CHUNK_SIZE,
            'y': chunk_south * MAP_CHUNK_SIZE,
            'w': chunk_east - chunk_west,
            'h': chunk_north - chunk_south
        }