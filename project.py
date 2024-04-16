from itertools import product

# Define attributes for state space
locations = list(range(1, 11))
traffic_conditions = ['free-flowing', 'moderate', 'heavy', 'stagnant']
times_of_day = [f"{h:02}:{m:02}-{h:02}:{(m+15)%60:02}" for h in range(24) for m in range(0, 60, 15)]
weather_conditions = ['clear', 'rainy', 'stormy']
traffic_lights_count = [0, 1, 2, 3]
pedestrian_levels = ['empty', 'moderate', 'crowded']

# Generate state space
state_space = list(product(locations, traffic_conditions, times_of_day, weather_conditions, traffic_lights_count, pedestrian_levels))

# Define terminal state and action
terminal_location = 10
terminal_state = (terminal_location, '*', '*', '*', '*', '*')
actions = ['move to next location', 'stay']
terminal_action = 'end route'

# Check current state and define available actions
current_state = (10, 'moderate', '12:00-12:15', 'clear', 1, 'crowded')
if current_state[0] == terminal_location:
    available_actions = [terminal_action]
else:
    available_actions = actions

print("Available Actions:", available_actions)
