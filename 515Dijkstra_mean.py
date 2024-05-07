import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

# Constants
car_speed = 10  # car speed in miles per hour
weather_condition = "clear"

# Weather conditions effects
weather_speed_reduction = {
    "clear": 1,
    "windy": 0.9,
    "rainy": 0.8,
    "stormy": 0.7
}

# Pedestrian and traffic light parameters
pedestrian_crossing_parameters = {
    "clear": {'mean_delay': 90},  # Mean delay in seconds
    "windy": {'mean_delay': 70},
    "rainy": {'mean_delay': 50},
    "stormy": {'mean_delay': 30},
    "moderate": {'mean_delay': 30},
    "empty": {'mean_delay': 0}
}

traffic_light_parameters = {
    "mean_delay": 15  # Mean delay in seconds
}

# Define edges and node properties
edges = {
    ('A', 'B', 0.5),
    ('B', 'A', 0.5),
    ('B', 'C', 0.1),
    ('C', 'B', 0.1),
    ('A', 'D', 0.2),
    ('D', 'A', 0.2),
    ('D', 'E', 0.2),
    ('E', 'D', 0.2),
    ('E', 'F', 0.2),
    ('F', 'E', 0.2),
    ('C', 'F', 0.1),
    ('F', 'C', 0.1),
    ('F', 'G', 0.2),
    ('G', 'F', 0.2),
    ('D', 'H1', 0.3),
    ('H1', 'D', 0.3),
    ('D', 'H2', 0.2),
    ('H2', 'D', 0.2),
    ('H1', 'I', 0.3),
    ('I', 'H1', 0.3),
    ('H2', 'I', 0.3),
    ('I', 'H2', 0.3),
    ('I', 'J', 0.1),
    ('J', 'I', 0.1),
    ('F', 'J', 0.2),
    ('J', 'F', 0.2)
}

node_indices = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H1': 7, 'H2': 8, 'I': 9, 'J': 10}
num_nodes = len(node_indices)

# Calculate and store weights
weights = np.full((num_nodes, num_nodes), np.inf)
for (start, end, distance) in edges:
    start_idx = node_indices[start]
    end_idx = node_indices[end]
    
    # Weather speed reduction
    car_speed_reduction_factor = weather_speed_reduction[weather_condition]
    # Car travel time in hours
    car_travel_time = distance / (car_speed * car_speed_reduction_factor)
    
    # Pedestrian crossing time
    pedestrian_crossing_time_hour = 0
    if end in ['D', 'E', 'H2', 'I']:
        pedestrian_crossing_time_hour = pedestrian_crossing_parameters[weather_condition]['mean_delay'] / 3600
    
    # Traffic light delay time
    traffic_light_time_hour = 0
    if end in ['A', 'B', 'D', 'F', 'H1', 'H2', 'J']:
        traffic_light_time_hour = traffic_light_parameters['mean_delay'] / 3600
    
    # Total time in minutes
    total_time_minutes = (car_travel_time + pedestrian_crossing_time_hour + traffic_light_time_hour) * 60
    weights[start_idx][end_idx] = total_time_minutes

# Create sparse matrix and apply Dijkstra's algorithm
graph = csr_matrix(weights)
distances, predecessors = dijkstra(csgraph=graph, directed=False, indices=node_indices['A'], return_predecessors=True)

# Retrieve the shortest path from 'A' to 'I'
i = node_indices['I']
path = []
while i != node_indices['A']:
    path.append(i)
    i = predecessors[i]
path.append(node_indices['A'])
path.reverse()
path = [list(node_indices.keys())[idx] for idx in path]

# Output results
print(f"Optimal Route: {path}")
print(f"Optimal Time: {distances[node_indices['I']]:.2f} minutes")
