import networkx as nx
import numpy as np
import heapq
from scipy.stats import truncnorm

# Constants for the simulation
NUM_SIMULATIONS = 10
START_NODE = 'A'
TARGET_NODE = 'I'
UPDATE_INTERVAL = 3  # Frequency of weight updates

# Vehicle speed and weather condition settings
car_speed = 10  # speed in miles per hour
weather_condition = "clear"

# Reduction factors for different weather conditions
weather_speed_reduction = {
    "clear": 1,
    "windy": 0.9,
    "rainy": 0.8,
    "stormy": 0.7
}

# Parameters for pedestrian crossings under various weather conditions
pedestrian_params = {
    "clear": {'min_delay': 30, 'max_delay': 180, 'mean_delay': 90, 'std_dev': 35},
    "windy": {'min_delay': 25, 'max_delay': 160, 'mean_delay': 70, 'std_dev': 30},
    "rainy": {'min_delay': 10, 'max_delay': 120, 'mean_delay': 50, 'std_dev': 25},
    "stormy": {'min_delay': 0, 'max_delay': 80, 'mean_delay': 30, 'std_dev': 20},
    "moderate": {'min_delay': 0, 'max_delay': 60, 'mean_delay': 30, 'std_dev': 10},
    "empty": {'min_delay': 0, 'max_delay': 0, 'mean_delay': 0, 'std_dev': 0}
}

traffic_light_choices = [30, 0]  # Possible durations of traffic lights in seconds

# Specified nodes that have pedestrian crossings and traffic lights
nodes_with_crossings = ['D', 'E', 'H2', 'I']
nodes_with_traffic_lights = ['A', 'B', 'D', 'F', 'H1', 'H2', 'J']

# Graph initialization with edges and distances
G_undirected = nx.Graph()
edges_tuples = {
    ('A', 'B', 0.5), ('B', 'A', 0.5), ('B', 'C', 0.1), ('C', 'B', 0.1),
    ('A', 'D', 0.2), ('D', 'A', 0.2), ('D', 'E', 0.2), ('E', 'D', 0.2),
    ('E', 'F', 0.2), ('F', 'E', 0.2), ('C', 'F', 0.1), ('F', 'C', 0.1),
    ('F', 'G', 0.2), ('G', 'F', 0.2), ('D', 'H1', 0.3), ('H1', 'D', 0.3),
    ('D', 'H2', 0.2), ('H2', 'D', 0.2), ('H1', 'I', 0.3), ('I', 'H1', 0.3),
    ('H2', 'I', 0.3), ('I', 'H2', 0.3), ('I', 'J', 0.1), ('J', 'I', 0.1),
    ('F', 'J', 0.2), ('J', 'F', 0.2)
}

# Add edges to the graph
for start, end, distance in edges_tuples:
    G_undirected.add_edge(start, end, distance=distance, weight=0)

# Initialize the update counts for each edge considering undirected nature
update_counts = {}
for start, end, _ in edges_tuples:
    if (start, end) not in update_counts and (end, start) not in update_counts:
        update_counts[(start, end)] = 0
        update_counts[(end, start)] = 0  # Ensure symmetry for undirected graph

# Main simulation loop
for simulation in range(NUM_SIMULATIONS):
    current_node = START_NODE
    step_count = 0
    path = [current_node]

    while current_node != TARGET_NODE:
        if step_count % UPDATE_INTERVAL == 0 or current_node == START_NODE:
            for neighbor in G_undirected.neighbors(current_node):
                # Consistently order the tuple to avoid KeyError
                edge_key = tuple(sorted((current_node, neighbor)))
                distance = G_undirected.edges[current_node, neighbor]['distance']
                car_speed_factor = weather_speed_reduction[weather_condition]
                car_travel_time = distance / (car_speed * car_speed_factor)

                # Pedestrian crossing time
                pedestrian_time = 0
                if neighbor in nodes_with_crossings or current_node in nodes_with_crossings:
                    p_params = pedestrian_params[weather_condition]
                    pedestrian_time = truncnorm.rvs(
                        (p_params['min_delay'] - p_params['mean_delay']) / p_params['std_dev'],
                        (p_params['max_delay'] - p_params['mean_delay']) / p_params['std_dev'],
                        loc=p_params['mean_delay'], scale=p_params['std_dev']) / 3600
                
                traffic_light_time = 0
                if neighbor in nodes_with_traffic_lights or current_node in nodes_with_traffic_lights:
                    # Traffic light time
                    traffic_light_time = np.random.choice(traffic_light_choices) / 3600
                
                # Calculate and update the running average weight
                new_weight = car_travel_time + pedestrian_time + traffic_light_time
                count = update_counts[edge_key]
                existing_weight = G_undirected[current_node][neighbor]['weight']
                updated_weight = (existing_weight * count + new_weight) / (count + 1)
                G_undirected[current_node][neighbor]['weight'] = updated_weight
                update_counts[edge_key] += 1  # Increment the update count

        # Priority queue to determine the next node
        neighbors = [(G_undirected[current_node][n]['weight'], n) for n in G_undirected.neighbors(current_node)]
        heapq.heapify(neighbors)
        min_weight, next_node = heapq.heappop(neighbors)
        path.append(next_node)
        current_node = next_node

        step_count += 1

    # Calculate total path time based on the latest weights
    path_time = sum(G_undirected[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
    print(f"Path found in simulation {simulation+1}: {path} with time: {path_time * 60:.2f} minutes")
