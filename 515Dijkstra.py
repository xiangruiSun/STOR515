import networkx as nx
import scipy.stats as stats
import numpy as np

# Speed of the car in miles per hour
car_speed = 10  # car speed in miles/hour

weather_condition = "stormy"

# Define the weather conditions and their effects
weather_speed_reduction = {
    "clear": 1,
    "windy": 0.9,
    "rainy": 0.8,
    "stormy": 0.7
}

weather_pedestrian_crowdedness_rank = {
    "clear": 1,
    "windy": 2,
    "rainy": 3,
    "stormy": 4
}

# Initialize the undirected graph
G_undirected = nx.Graph()

# Add edges with weights representing the travel time assuming no red light stop.
# Weight is the travel distance in miles.
# For simplicity, we're adding the edges in both directions with the same weight.
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

# Nodes with pedestrian crossings
nodes_with_crossings = ['D', 'E', 'H2', 'I']

# Nodes with traffic lights
nodes_with_traffic_lights = ['A', 'B', 'D', 'F', 'H', 'J']

pedestrian_crossing_parameters = {
    "clear": {'min_delay': 30, 'max_delay': 180, 'mean_delay': 90, 'std_dev': 35},
    "windy": {'min_delay': 25, 'max_delay': 160, 'mean_delay': 70, 'std_dev': 30},
    "rainy": {'min_delay': 10, 'max_delay': 120, 'mean_delay': 50, 'std_dev': 25},
    "stormy": {'min_delay': 0, 'max_delay': 80, 'mean_delay': 30, 'std_dev': 20}
}

traffic_light_parameters = {
    "red": 30,
    "green": 0
}

# Adjust weights for car speed reduction, pedestrian crossing time distribution, and traffic lights
for edge in edges:
    start, end, distance = edge
    # Adjust car speed reduction factor for the edge based on weather condition
    car_speed_reduction_factor = weather_speed_reduction.get(weather_condition, 1)
    # Calculate car travel time for the edge in hours
    car_travel_time = distance / car_speed
    
    # Check if the end node has pedestrian crossing
    if end in nodes_with_crossings:
        # Get pedestrian crossing time distribution parameters based on weather condition
        pedestrian_params = pedestrian_crossing_parameters.get(weather_condition, {})
        # Sample pedestrian crossing time from truncated normal distribution in seconds
        pedestrian_crossing_time_sec = stats.truncnorm.rvs((pedestrian_params['min_delay'] - pedestrian_params['mean_delay']) / pedestrian_params['std_dev'],
                                                           (pedestrian_params['max_delay'] - pedestrian_params['mean_delay']) / pedestrian_params['std_dev'],
                                                           loc=pedestrian_params['mean_delay'],
                                                           scale=pedestrian_params['std_dev'])
        # Convert pedestrian crossing time from seconds to hours
        pedestrian_crossing_time_hour = pedestrian_crossing_time_sec / 3600
    else:
        # No pedestrian crossing at this edge, pedestrian crossing time is 0
        pedestrian_crossing_time_hour = 0
    
    # Check if the end node has traffic lights
    if end in nodes_with_traffic_lights:
        # Sample traffic light time
        traffic_light_time_sec = np.random.choice([traffic_light_parameters["red"], traffic_light_parameters["green"]])
        # Convert traffic light time from seconds to hours
        traffic_light_time_hour = traffic_light_time_sec / 3600
    else:
        # No traffic lights at this edge, traffic light time is 0
        traffic_light_time_hour = 0
    
    # Calculate total time for the edge in hours
    total_time_hour = car_travel_time + pedestrian_crossing_time_hour + traffic_light_time_hour
    # Adjust edge weight based on total time in hours
    G_undirected.add_edge(start, end, weight=total_time_hour / car_speed_reduction_factor)

# Find the shortest path using Dijkstra's algorithm
# We find the shortest path from node 'A' to 'I' as an example.
ssp_path = nx.dijkstra_path(G_undirected, source='A', target='I', weight='weight')
ssp_path_time = nx.dijkstra_path_length(G_undirected, source='A', target='I', weight='weight')

print("Shortest Path:", ssp_path)
print("Shortest Path Time:", ssp_path_time * 60, "minutes")
