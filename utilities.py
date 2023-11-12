from datetime import datetime, timedelta
from number_sets import *
from pathlib import Path
import numpy as np


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def in_time_zone(start, end):
    current_hour = datetime.now().hour
    return current_hour >= start and current_hour < end

def wait(minutes):
    for x in range(minutes):
        print(f"Waiting: {x} of {minutes} minutes")
        time.sleep(60)

def combine_image_horizontal(images):
    max_height = 0
    for image in images:
        if image is None: continue
        height, width, channels = image.shape
        max_height = max(max_height, height)

    line = np.zeros((max_height, 3, 3), np.uint8)
    line.fill(255)
    combined = np.zeros((max_height, 1, 3), np.uint8)

    for image in images:
        if image is None: continue
        height, width, channels = image.shape
        if height < max_height:
            buffer = np.zeros((max_height - height, width, 3), np.uint8)
            image = np.concatenate((image, buffer), axis=0)
        combined = np.concatenate((combined, line, image), axis=1)
    combined = np.concatenate((combined, line), axis=1)

    # show(combined)
    return combined[:, 1:]

def combine_image_vertical(images):
    max_width = 0
    for image in images:
        height, width, channels = image.shape
        max_width = max(max_width, width)

    line = np.zeros((3, max_width, 3), np.uint8)
    line.fill(255)
    combined = np.zeros((1, max_width, 3), np.uint8)

    for image in images:
        height, width, channels = image.shape
        if width < max_width:
            buffer = np.zeros((height, max_width - width, 3), np.uint8)
            image = np.concatenate((image, buffer), axis=1)
        combined = np.concatenate((combined, line, image), axis=0)
    combined = np.concatenate((combined, line), axis=0)

    # show(combined)
    return combined[1:, :]

def time_to_army_ready():
    time = army_time()
    print("Time to army ready:", time)
    return time



def text_to_time(string):
    print(f"text_to_time:{string}")
    space = string.find(" ")

    if space == -1: return
    if string[space-1].isdigit():
        if string[-1] == "M":
            string = string.replace(" ", "H ")
            space = string.find(" ")
        if string[-1] == "s":
            string = string.replace(" ", "M ")
            space = string.find(" ")

    days, hours, minutes, seconds = 0,0,0,0
    mode = string[space-1]
    print("Mode:", mode)
    if mode == "t": mode = "H"
    if mode == "M":
        minutes = string[0:space-1]
        seconds = string[space+1:-2]
    if mode.lower() == "h":
        hours = string[0:space-1]
        minutes = string[space+1:-2]
    if mode == "d":
        days = string[0:space-1]
        hours = string[space+1:-2]

    try:
        days = int(days)
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
    except:
        return None
    if days == 0 and hours == 0 and minutes == 0 and seconds == 0: return None
    print("Clean time", days, hours, minutes, seconds)
    finish = datetime.now() + timedelta(days=days) + timedelta(hours=hours) + timedelta(minutes=minutes) + timedelta(seconds=seconds)
    print("Finish time", finish)

    return finish

def text_to_time_2(string, return_duration=False):
    # print(f"text_to_time_2: {string}")
    string = string.replace("hh", "h")
    string = string.replace("b", "")
    days_x = string.find("d")
    hours_x = string.find("h")
    minutes_x = string.find("m")
    seconds_x = string.find("s")
    # print(days_x, hours_x, minutes_x)

    days, hours, minutes, seconds = 0,0,0,0
    if days_x != -1:
        days = string[0:days_x]
        hours = string[days_x+1:-1]
        # print("Days")
    elif hours_x != -1:
        hours = string[:hours_x]
        minutes = string[hours_x+1:-1]
        # print("Hours")
    elif minutes_x != -1:
        minutes = string[0:minutes_x]
        seconds = string[minutes_x+1:-1]
        # print("Minutes")
    elif seconds_x != -1:
        seconds = string[0:seconds_x-1]
    else:
        if return_duration:
            return timedelta(minutes=5)
        else:
            return datetime.now() + timedelta(minutes=5)

    try:
        days = int(days)
        days = min(7, days)
    except:
        days = 0
    try:
        hours = int(hours)
        hours = min(24, hours)
    except:
        hours = 0
    try:
        minutes = int(minutes)
        minutes = min(60, minutes)
    except:
        minutes = 0
    try:
        seconds = int(seconds)
        seconds = min(60, seconds)
    except:
        seconds = 0

    if days == 0 and hours == 0 and minutes == 0 and seconds == 0: return None
    # print("Clean time", days, hours, minutes, seconds)
    duration = timedelta(days=days) + timedelta(hours=hours) + timedelta(minutes=minutes) + timedelta(seconds=seconds)
    if return_duration:
        return duration
    else:
        return datetime.now() + duration

def text_to_time_3(string):
    days_x = string.find("d")
    hours_x = string.find("h")
    minutes_x = string.find("m")
    seconds_x = string.find("s")
    # print(days_x, hours_x, minutes_x, seconds_x)

    days, hours, minutes, seconds = 0,0,0,0
    cursor = 0
    if days_x != -1:
        try:
            days = int(string[cursor:days_x])
        except:
            pass
        cursor = days_x + 1
        # print("Days", days)
    if hours_x != -1:
        try:
            hours = int(string[cursor:hours_x])
        except:
            pass
        cursor = hours_x + 1
        # print("Hours", hours)
    if minutes_x != -1:
        print(string[cursor:minutes_x])
        try:
            minutes = int(string[cursor:minutes_x])
        except:
            pass
        cursor = minutes_x + 1
        # print("Minutes", minutes)
    if seconds_x != -1:
        # print(cursor, seconds_x)
        # print(string[cursor:seconds_x])
        try:
            seconds = int(string[cursor:seconds_x])
        except:
            pass
        # print("Seconds", seconds)

    # print(days, hours, minutes)

    if days == 0 and hours == 0 and minutes == 0 and seconds == 0: return None
    finish = datetime.now() + timedelta(days=days) + timedelta(hours=hours) + timedelta(minutes=minutes) + timedelta(seconds=seconds)

    return finish



def string_to_time(time):
    try:
        return datetime.fromisoformat(time)
    except:
        return datetime.now()

def time_to_string(time):
    if time is None: return "Now"
    if time <= datetime.now():
        return "Now"
    elif time <= datetime.now() + timedelta(hours=24):
        return time.strftime('%I:%M%p')
    elif time <= datetime.now() + timedelta(hours=48):
        return time.strftime('%d %b %I:%M%p')
    else:
        return time.strftime('%d %b')



