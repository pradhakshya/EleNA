from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import osmnx
import json

from .utilities.path_request import PathRequest
from .utilities.path_finder import PathFinder
from .graph_providers.bounded_graph_provider import BoundedGraphProvider
from .graph_providers.loading_graph_provider import LoadingGraphProvider
from .routing_algorithms.a_star import AStar
from .routing_algorithms.dijkstra import Dijkstra


def index(request):
    return render(request, 'nav_sys/index.html', {})

@csrf_exempt
def search(request):
    #data = json.loads(request)
    #print(data)
    place = request.POST['place']
    try:
        coords = osmnx.geocoder.geocode(place)
    except Exception:
        coords = []

    return JsonResponse({"coords": coords})

@csrf_exempt
def get_route(request):
    # Process the request data from the frontend
    origin = request.POST['origin']
    destination = request.POST['destination']
    distance_percent = request.POST['distance']
    ele_setting = request.POST['elevation']
    graph_setting = request.POST['graph']

    # Create a new PathRequest object
    try:
        path_request = PathRequest(origin, destination, distance_percent, ele_setting, graph_setting)
    except ValueError:
        return JsonResponse({"error": "badcoords"})

  
    # Obtain the graph provider
    if(path_request.graph_setting == 'bounded'):
        graph_provider_cls = BoundedGraphProvider
    else:
        graph_provider_cls = LoadingGraphProvider
    graph_provider = graph_provider_cls(path_request.origin, path_request.destination)

    # Get shortest path algorithm
    shortest_path_algo = AStar(graph_provider)

    # Get elevation-based search algorithm
    # For finding the minimal elevation gain path, the AStar algorithm is used
    # For finding the maximal elevation gain path, Dijkstra's algorithm is used


    if path_request.ele_setting == 'minimal':
        ele_search_algo = AStar(graph_provider)
    elif path_request.ele_setting == 'maximal':
        ele_search_algo = Dijkstra(graph_provider)
    else:
        ele_search_algo = None

    # Find path and handle timeout if necessary
    finder = PathFinder(shortest_path_algo, ele_search_algo, graph_provider)
    results = finder.find_path(path_request)
    if results == None:
        return JsonResponse({"error": "timeout"})
    else:
        return JsonResponse(results)