import networkx as nx

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

# Add edges with weights representing the travel time assuming no red light stop.
# Weight is the travel distance in miles.
edges = {
    ('A', 'B', 0.5),
    ('B', 'C', 0.1),
    ('A', 'D', 0.2),
    ('D', 'E', 0.2),
    ('E', 'F', 0.2),
    ('C', 'F', 0.1),
    ('F', 'G', 0.2),
    ('D', 'H1', 0.3),
    ('D', 'H2', 0.2),
    ('H1', 'I', 0.3),
    ('H2', 'I', 0.3),
    ('I', 'J', 0.1),
    ('F', 'J', 0.2),
}

# Nodes with pedestrian crossings
nodes_with_crossings = ['D', 'E', 'H2', 'I']

# Nodes with traffic lights
nodes_with_traffic_lights = ['A', 'B', 'D', 'F', 'H1','H2', 'J']

pedestrian_crossing_parameters = {
    "clear": {'mean_delay': 90},  # Mean delay in seconds
    "windy": {'mean_delay': 70},
    "rainy": {'mean_delay': 50},
    "stormy": {'mean_delay': 30}
}

traffic_light_parameters = {
    "mean_delay": 15  # Mean delay in seconds
}

# Adjust weights for car speed reduction, pedestrian crossing time distribution, and traffic lights
for edge in edges:
    start, end, distance = edge
    # Adjust car speed reduction factor for the edge based on weather condition
    car_speed_reduction_factor = weather_speed_reduction[weather_condition]
    # Calculate car travel time for the edge in hours
    car_travel_time = distance / (car_speed * car_speed_reduction_factor)
    
    # Calculate potential pedestrian crossing time
    pedestrian_crossing_time_hour = 0
    if end in nodes_with_crossings:
        pedestrian_crossing_time_hour = pedestrian_crossing_parameters[weather_condition]['mean_delay'] / 3600
    
    # Calculate potential traffic light delay time
    traffic_light_time_hour = 0
    if end in nodes_with_traffic_lights:
        traffic_light_time_hour = traffic_light_parameters['mean_delay'] / 3600
    
    # Total travel time for the edge in hours, converting to minutes for precision
    total_time_minutes = (car_travel_time + pedestrian_crossing_time_hour + traffic_light_time_hour) * 60
    G_undirected.add_edge(start, end, weight=total_time_minutes)

# Solve the shortest path problem using Dijkstra's algorithm
ssp_path = nx.dijkstra_path(G_undirected, source='A', target='I', weight='weight')
ssp_path_time = nx.dijkstra_path_length(G_undirected, source='A', target='I', weight='weight')

print(f"Optimal Route: {ssp_path}")
print(f"Optimal Time: {ssp_path_time:.2f} minutes")
