from datetime import datetime, date, timedelta

# Our menu
menu = "E - Engineering Time\nW - Weather Time\nT - Technical Time\nD - Done"
option = input(menu+"\nChoose from above menu: ")        
        
# The list for containing the calculated time when occured
eng_time = []
weather_time = []
tech_time = []

def time_format(str_time):
    return datetime.strptime(str_time,"%H:%M:%S").time()

def delta_time(time):
    return datetime.combine(date.today(), time)

def time_difference(start, end):
    return datetime.combine(date.today(),end) - datetime.combine(date.today(), start)

def sum_time(time_array):
    total_time = delta_time(time_format("00:00:00"))
    for time in time_array:
        total_time = total_time + time
    return total_time

def timedelta_format(total_time):
    return timedelta(hours=total_time.hour, minutes=total_time.minute, seconds=total_time.second)

while(option != "D"):
    # This is for engineering time
    if (option == "E"):
        eng_start_time = input("Enter the Engineering start time (format (HH:MM:SS)): ")
        start = time_format(eng_start_time)
        eng_end_time = input("Enter the Engineering end time (format (HH:MM:SS)): ")
        end = time_format(eng_end_time)
        eng_time.append(time_difference(start, end))
        
    # This is for weather time
    elif (option == "W"):
        weather_start_time = input("Enter the Weather start time (format (HH:MM:SS)): ")
        start = time_format(weather_start_time)
        weather_end_time = input("Enter the Weather end time (format (HH:MM:SS)): ")
        end = time_format(weather_end_time)
        weather_time.append(time_difference(start, end))
        
    # This is for technical time
    elif (option == "T"):
        tech_start_time = input("Enter the Technical start time (format (HH:MM:SS)): ")
        start = time_format(tech_start_time)
        tech_end_time = input("Enter the Technical end time (format (HH:MM:SS)): ")
        end = time_format(tech_end_time)
        tech_time.append(time_difference(start, end))        
    # Reprompting the user to choose the option from the menu 
    option = input(menu+"\nChoose the option from the menu above: ")

print("Engineering Total Time")
total_eng_time = sum_time(eng_time)
print(total_eng_time.time())

print("Weather Total Time")
total_weather_time = sum_time(weather_time)
print(total_weather_time.time())

print("Technical Total Time")
total_tech_time = sum_time(tech_time)
print(total_tech_time.time())

# Calculating the science time
str_night_length = input("Enter the Night Length  time (format (HH:MM:SS)): ")
time_night_length = time_format(str_night_length)
total_science_time = delta_time(time_night_length) -  timedelta_format(total_eng_time) - timedelta_format(total_weather_time) - timedelta_format(total_tech_time)

print("Science Total Time")
print(total_science_time.time())

print("\nIt is done")
        
            


