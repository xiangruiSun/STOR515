import networkx as nx
import numpy as np
import heapq
from scipy.stats import truncnorm

# Constants
NUM_SIMULATIONS = 3
START_NODE = 'A'
TARGET_NODE = 'I'
UPDATE_INTERVAL = 3  # Updates weights every 3 steps

# Speed of the car in miles per hour
car_speed = 10  # car speed in miles/hour
weather_condition = "clear"

# Weather conditions effects
weather_speed_reduction = {
    "clear": 1,
    "windy": 0.9,
    "rainy": 0.8,
    "stormy": 0.7
}

# Pedestrian and traffic light parameters
pedestrian_params = {
    "clear": {'min_delay': 30, 'max_delay': 180, 'mean_delay': 90, 'std_dev': 35},
    "windy": {'min_delay': 25, 'max_delay': 160, 'mean_delay': 70, 'std_dev': 30},
    "rainy": {'min_delay': 10, 'max_delay': 120, 'mean_delay': 50, 'std_dev': 25},
    "stormy": {'min_delay': 0, 'max_delay': 80, 'mean_delay': 30, 'std_dev': 20}
}
traffic_light_choices = [30, 0]  # Red and Green times

# Nodes with specific conditions
nodes_with_crossings = ['D', 'E', 'H2', 'I']
nodes_with_traffic_lights = ['A', 'B', 'D', 'F', 'H1','H2', 'J']

# Initialize the undirected graph with distances as weights
G_undirected = nx.Graph()
edges_tuples={
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
    ('G','F',0.2),
    ('D','H1',0.3),
    ('H1','D',0.3),
    ('D','H2',0.2),
    ('H2','D',0.2),
    ('H1','I',0.3),
    ('I','H1',0.3),
    ('H2','I',0.3),
    ('I','H2',0.3),
    ('I','J',0.1),
    ('J','I',0.1),
    ('F','J',0.2),
    ('J','F',0.2),
}

for start, end, distance in edges_tuples:
    G_undirected.add_edge(start, end, distance=distance, weight=0)

# Simulation loop
for simulation in range(NUM_SIMULATIONS):
    current_node = START_NODE
    step_count = 0
    path = [current_node]

    while current_node != TARGET_NODE:
        if step_count % UPDATE_INTERVAL == 0 or current_node == START_NODE:
            # Recalculate weights at set intervals
            for neighbor in G_undirected.neighbors(current_node):
                distance = G_undirected[current_node][neighbor]['distance']
                car_speed_factor = weather_speed_reduction[weather_condition]
                car_travel_time = distance / (car_speed * car_speed_factor)

                # Sample pedestrian crossing time
                pedestrian_time = 0
                if neighbor in nodes_with_crossings:
                    p_params = pedestrian_params[weather_condition]
                    pedestrian_time = truncnorm.rvs(
                        (p_params['min_delay'] - p_params['mean_delay']) / p_params['std_dev'],
                        (p_params['max_delay'] - p_params['mean_delay']) / p_params['std_dev'],
                        loc=p_params['mean_delay'], scale=p_params['std_dev']) / 3600
                
                # Sample traffic light time
                traffic_light_time = np.random.choice(traffic_light_choices) / 3600
                
                # Update and average weight
                new_weight = car_travel_time + pedestrian_time + traffic_light_time
                existing_weight = G_undirected[current_node][neighbor]['weight']
                updated_weight = (existing_weight + new_weight) / 2 if existing_weight != 0 else new_weight
                G_undirected[current_node][neighbor]['weight'] = updated_weight

        # Use a priority queue to determine the next node to move to
        neighbors = [(G_undirected[current_node][n]['weight'], n) for n in G_undirected.neighbors(current_node)]
        heapq.heapify(neighbors)
        min_weight, next_node = heapq.heappop(neighbors)
        path.append(next_node)
        current_node = next_node

        step_count += 1

    # Calculate path time using the latest weights
    path_time = sum(G_undirected[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
    print(f"Path found in simulation {simulation+1}: {path} with time: {path_time * 60:.2f} minutes")

# This code maintains stochastic behavior for pedestrian crossings and traffic lights, updating them at set
