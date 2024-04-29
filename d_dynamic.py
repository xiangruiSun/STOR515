import networkx as nx
import scipy.stats as stats
import numpy as np

# Constants
NUM_SIMULATIONS = 5
START_NODE = 'A'
TARGET_NODE = 'I'

# Speed of the car in miles per hour
car_speed = 10  # car speed in miles/hour

weather_condition = "clear"

# Define the weather conditions and their effects
weather_speed_reduction = {
    "clear": 1,
    "windy": 0.9,
    "rainy": 0.8,
    "stormy": 0.7
}

# Initialize the undirected graph
G_undirected = nx.Graph()

# Define the network edges with distances
edges_tuples = {
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
    ('J', 'F', 0.2),
}

# Nodes with pedestrian crossings
nodes_with_crossings = ['D', 'E', 'H2', 'I']
pedestrian_params = {
    "clear": {'min_delay': 30, 'max_delay': 180, 'mean_delay': 90, 'std_dev': 35},
    "windy": {'min_delay': 25, 'max_delay': 160, 'mean_delay': 70, 'std_dev': 30},
    "rainy": {'min_delay': 10, 'max_delay': 120, 'mean_delay': 50, 'std_dev': 25},
    "stormy": {'min_delay': 0, 'max_delay': 80, 'mean_delay': 30, 'std_dev': 20}
}
traffic_light_choices = [30, 0]  # Red and Green times
# Nodes with traffic lights
nodes_with_traffic_lights = ['A', 'B', 'D', 'F', 'H1','H2', 'J']

# Convert edge tuples into a dictionary for easy access
edges = { (start, end): distance for start, end, distance in edges_tuples }

# Initialize graph with edges and default weights
for start, end, distance in edges_tuples:
    G_undirected.add_edge(start, end, distance=distance, weight=0)

# The rest of your simulation code follows here...


# Simulation loop
for _ in range(NUM_SIMULATIONS):
    current_node = START_NODE
    path = [current_node]

    while current_node != TARGET_NODE:
        # Calculate weights for current node edges only once per iteration
        for neighbor in G_undirected.neighbors(current_node):
            edge_key = (current_node, neighbor) if (current_node, neighbor) in edges else (neighbor, current_node)
            distance = edges[edge_key]
            
            # Compute car travel time
            car_speed_factor = weather_speed_reduction[weather_condition]
            car_travel_time = distance / (car_speed * car_speed_factor)
            
            # Compute pedestrian crossing time
            pedestrian_time = 0
            if neighbor in nodes_with_crossings:
                p_params = pedestrian_params[weather_condition]
                pedestrian_time = stats.truncnorm.rvs(
                    (p_params['min_delay'] - p_params['mean_delay']) / p_params['std_dev'],
                    (p_params['max_delay'] - p_params['mean_delay']) / p_params['std_dev'],
                    loc=p_params['mean_delay'], scale=p_params['std_dev']) / 3600
            
            # Compute traffic light time
            traffic_light_time = 0
            if neighbor in nodes_with_traffic_lights:
                traffic_light_time = np.random.choice(traffic_light_choices) / 3600
            
            # Update and average weight
            new_weight = car_travel_time + pedestrian_time + traffic_light_time
            existing_weight = G_undirected[current_node][neighbor]['weight']
            updated_weight = (existing_weight + new_weight) / 2 if existing_weight != 0 else new_weight
            G_undirected[current_node][neighbor]['weight'] = updated_weight

        # Move to the next node with the shortest path from current
        current_node = min(nx.single_source_dijkstra_path(G_undirected, current_node, weight='weight'),
                           key=lambda x: nx.dijkstra_path_length(G_undirected, current_node, x, weight='weight'))
        path.append(current_node)

    # Output the path and time for each simulation
    path_time = nx.dijkstra_path_length(G_undirected, START_NODE, TARGET_NODE, weight='weight')
    print("Path found:", path, "with time:", path_time * 3600, "seconds")
