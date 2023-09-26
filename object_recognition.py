import pyautogui as pag
import cv2
from constants import *
import numpy as np
method = cv2.TM_CCOEFF_NORMED
import time
from datetime import datetime, timedelta
from collections import Counter

OBJECTS_B = dir_to_list('attack_b/objects')
BUSHES = dir_to_list('trees')
MINES = dir_to_list('mines')


def get_screenshot(region=None, colour=0, filename="temp"):
    try:
        pag.screenshot(f'temp/{filename}.png', region=region)
        return cv2.imread(f'temp/{filename}.png', colour)
    except:
        return None

def attack_screenshot(region=None, colour=0, filename="temp"):
    try:
        pag.screenshot(f'{filename}.png', region=region)
        return cv2.imread(f'{filename}.png', colour)
    except:
        return None

def find(image, screen, text="", show_image=False):
    if image is None:
        # print("Find - No image provided:", text)
        return 0,0,0
    if show_image:
        show(image)
        show(screen)
    y, x = image.shape
    # print("Find", image.shape, screen.shape)
    try:
        result = cv2.matchTemplate(screen, image, method)
        min_val, val, min_loc, loc = cv2.minMaxLoc(result)
        rect = (loc[0], loc[1], x, y)
        # print("Find", text, round(val,2))
        return round(val, 2), loc, rect
    except:
        return 0,0,0

def click(image, region=None, confidence=0.6, show_image=False):
    if image is None:
        print("No image provided")
        return 0
    screen = get_screenshot(region)
    if show_image:
        show(image)
        show(screen)
    y, x = image.shape
    result = cv2.matchTemplate(screen, image, method)
    min_val, val, min_loc, loc = cv2.minMaxLoc(result)
    if region:
        spot = (int(region[0] + loc[0] + x / 2), int(region[1] + loc[1] + y / 2))
    else:
        spot = (int(loc[0] + x / 2), int(loc[1] + y / 2))
    outcome = False
    if val > confidence:
        pag.click(spot)
        outcome = True
        # print("Click spot", spot)
    return val, outcome

def wait(templates, regions, dur=5):
    for x in range(dur):
        result = find_images_bool(templates, regions, show_image=False)
        if result: return True
        time.sleep(1)
    return result

def find_images_bool(templates, regions=None, val_min=0.6, val_max=1.0, return_val=False, show_image=False):
    if len(templates) == 0:
        print("Find image: no image provided")
        return None
    if show_image:
        for template in templates:
            show(template, scale=0.7)

    best_val = 0
    best_rect = None
    found = False
    if regions is None or len(regions) == 0:
        screen = get_screenshot()
        if show_image:
            show(screen, scale=0.7)

        for template in templates:
            if template is not None:
                result = cv2.matchTemplate(screen, template, method)
                min_val, val, min_loc, loc = cv2.minMaxLoc(result)
                if val_min <= val <= val_max:
                    found = True
                    best_val = val
                    y, x = template.shape
                    best_rect = (loc[0], loc[1], x, y)
    else:
        for region in regions:
            screen = get_screenshot(region)
            if show_image:
                show(screen, scale=0.7)

            for template in templates:
                if template is not None:
                    if template.shape[0] > screen.shape[0]:
                        # print(region, template)
                        print("Find Images Bool - Region too small", region[2], region[3], template.shape)
                        region = [region[0], region[1], template.shape[1], region[3]]
                        screen = get_screenshot(region)
                    if template.shape[1] > screen.shape[1]:
                        print("Find Images Bool - Region too small", region[2], region[3], template.shape)
                        region = [region[0], region[1], region[2], template.shape[0],]
                        screen = get_screenshot(region)

                    # print("Find images bool:", screen.shape, template.shape)
                    result = cv2.matchTemplate(screen, template, method)
                    min_val, val, min_loc, loc = cv2.minMaxLoc(result)
                    if val_min <= val <= val_max:
                        found = True
                        best_val = val
                        best_loc = None
                    # print("Find images bool: ", val_min, round(val,2), val_max, found)
                else:
                    print("Find images bool: Template not found")
    if return_val:
        return found, best_val, best_rect
    else:
        return found


# ==========================
# === Object recognition ===
# ==========================

def simplify(i, gradients=2):
    factor = 256 / gradients
    new = i
    l = []
    for row in new:
        for pixel in row:
            for c in range(3):
                pixel[c] = int(pixel[c] / factor) * factor
            l.append((pixel[0],pixel[1],pixel[2]))
    return new, Counter(l)

def check_colour_rect(region, show_image=False, text=""):
    # print("Check colour rect")
    pag.screenshot('temp/temp_colour.png', region)
    image = cv2.imread('temp/temp_colour.png', 1)
    if show_image: show(image)

    y, x, channels = image.shape

    count = 0
    spots =[(1/4, 1/4), (1/4, 3/4), (3/4, 1/4), (3/4, 3/4),(7/8, 1/8), (0.95, 0.05)]
    for s_x, s_y in spots:
        pixel = image[int(y * s_y)][int(x * s_x)]
        blue, green, red = int(pixel[0]), int(pixel[1]), int(pixel[2])
        # print(text, s_x, s_y, blue, green, red)
        if abs(blue-green) > 5 or abs(blue-red) > 5: count += 1
    colour = False
    if count > 1: colour = True
    return colour

def check_colour(image_str):
    pag.screenshot('temp/temp_colour.png')
    screen = cv2.imread('temp/temp_colour.png', 0)
    template = cv2.imread(f'images/{image_str}.png', 0)
    if template is None:
        print("check_colour: couldn't find file:", image_str)
        return 0
    y, x = template.shape
    result = cv2.matchTemplate(screen, template, method)
    min_val, val, min_loc, loc = cv2.minMaxLoc(result)
    region = (loc[0], loc[1], x, y)
    pag.screenshot('temp/temp.png', region=region)
    image = cv2.imread('temp/temp.png', 1)

    colour = False
    spots =[(1/4, 1/4), (1/4, 3/4), (3/4, 1/4), (3/4, 3/4),]
    for s_x, s_y in spots:
        pixel = image[int(y * s_y)][int(x * s_x)]
        # print(pixel)
        if -5 < pixel[0] - pixel[1] < 5: colour = True
        if -5 < pixel[0] - pixel[2] < 5: colour = True
        # print("Check colour (pixel):", pixel, colour)
    # print("Check colour", image_str, colour)
    return colour

def find_cv2(image_str, region='all', screen="screenshot"):
    # if not PRINT_CV2:
    #     print("Find cv2", image_str)
    if screen == "screenshot":
        if region == 'all':
            try:
                pag.screenshot('temp/temp_find_cv2.png')
                screen = cv2.imread('temp/temp_find_cv2.png', 0)
            except:
                return 0, (0, 0), (0, 0, 0, 0)
        else:
            try:
                pag.screenshot('temp/temp_find_cv2.png', region=region)
                screen = cv2.imread('temp/temp_find_cv2.png', 0)
            except:
                return 0, (0, 0), (0, 0, 0, 0)

    template = cv2.imread(f'images/{image_str}.png', 0)
    if template is None:
        if PRINT_CV2:
            print("click_cv2: couldn't find file:", image_str)
        return 0, (0,0), (0,0,0,0)
    if image_str == "suggested_upgradesx":
        show(screen, dur=10000)
        show(template)

    y, x = template.shape
    # print("Find cv2 - shapes", image_str, template.shape, screen.shape)
    result = cv2.matchTemplate(screen, template, method)
    min_val, val, min_loc, loc = cv2.minMaxLoc(result)
    val = round(val,2)
    if region == 'all':
        region_start = (0,0)
    else:
        region_start = (region[0],region[1])

    loc = (region_start[0] + loc[0], region_start[1] + loc[1])
    rect = (loc[0], loc[1], x, y)
    # print(f"find_cv2: {image_str} val={round(val,2)} loc={loc} rect={rect}")
    return val, loc, rect

def find_cv2_image(image_str, screen_colour):
    screen = cv2.cvtColor(screen_colour, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(f'images/{image_str}.png', 0)
    # show(template)
    # show(screen)
    if template is None:
        if PRINT_CV2:
            print("find_cv2: couldn't find file:", image_str)
        return 0, (0,0), (0,0,0,0)

    y, x = template.shape
    result = cv2.matchTemplate(screen, template, method)
    min_val, val, min_loc, loc = cv2.minMaxLoc(result)
    val = round(val,2)

    rect = (loc[0], loc[1], x, y)
    return val, loc, rect

def find_many_number(template, i, confidence=0.75):
    file_name = f'numbers2/{template}.png'
    template = cv2.imread(file_name, 0)
    h, w = template.shape

    result = cv2.matchTemplate(i, template, method)
    yloc, xloc = np.where(result >= confidence)
    z = zip(xloc, yloc)

    rectangles = []
    for (x, y) in z:
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])
    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

    return rectangles

def find_many_troop_number(template, i, confidence=0.75):
    file_name = f'numbers3/{template}.png'
    template = cv2.imread(file_name, 0)
    h, w = template.shape

    result = cv2.matchTemplate(i, template, method)
    yloc, xloc = np.where(result >= confidence)
    z = zip(xloc, yloc)

    rectangles = []
    for (x, y) in z:
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])
    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

    return rectangles

def find_many_number_2(i, numbers_directory, number, confidence=0.75):
    file_name = f'{numbers_directory}/{number}.png'
    template = cv2.imread(file_name, 0)
    h, w = template.shape

    result = cv2.matchTemplate(i, template, method)
    yloc, xloc = np.where(result >= confidence)
    z = zip(xloc, yloc)

    rectangles = []
    for (x, y) in z:
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])
    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

    return rectangles

def find_many_image(template, i, confidence=0.6):
    template = cv2.imread(f'numbers/{template}.png', 0)
    h, w = template.shape

    result = cv2.matchTemplate(i, template, method)
    yloc, xloc = np.where(result >= confidence)
    z = zip(xloc, yloc)

    rectangles = []
    for (x, y) in z:
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])
    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

    return rectangles

def find_many(image_str, region='all', confidence=0.6):
    if region == 'all':
        pag.screenshot('temp/temp.png')
    else:
        pag.screenshot('temp/temp.png', region=region)
    screen = cv2.imread('temp/temp.png', 0)
    template = cv2.imread(f'images/{image_str}.png', 0)
    # show(screen)
    # show(template)
    if template is None:
        print("Find many: couldn't find file:", image_str)
        return []
    h, w = template.shape
    result = cv2.matchTemplate(screen, template, method)
    yloc, xloc = np.where(result >= confidence)
    if region == "all":
        z = zip(xloc, yloc)
    else:
        # print(region[0], xloc, region[1], yloc)
        z = zip(region[0]+xloc, region[1]+yloc)

    rectangles = []
    for (x, y) in z:
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])
    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

    # print("find_many", image_str, z)
    return rectangles

def find_many_img(templates, img, confidence=0.6):
# Set up output array
    rects = []

# Loop through templates
    for template_str in templates:
        template = cv2.imread(f'images/{template_str}.png', 0)
        if template is None:
            print("Find many img: couldn't find file:", template_str)
        else:
            h, w = template.shape
            # print("Image shape:", img.shape)
            # print("Template shape:", template.shape)
            result = cv2.matchTemplate(img, template, method)
            yloc, xloc = np.where(result >= confidence)
            z = zip(xloc, yloc)

            for (x, y) in z:
                rects.append([int(x), int(y), int(w), int(h)])
                rects.append([int(x), int(y), int(w), int(h)])
    rects, weights = cv2.groupRectangles(rects, 1, 0.2)
    return rects



def find_many_array(templates, region='all', confidence=0.6):
# Get screen
    if region == 'all':
        pag.screenshot('temp/temp.png')
    else:
        pag.screenshot('temp/temp.png', region=region)
    screen = cv2.imread('temp/temp.png', 0)

# Set up output array
    rects = []

# Loop through templates
    for template_str in templates:
        template = cv2.imread(f'images/{template_str}.png', 0)
        if template is None:
            print("click_cv2: couldn't find file:", template_str)
        else:
            h, w = template.shape
            result = cv2.matchTemplate(screen, template, method)
            yloc, xloc = np.where(result >= confidence)
            z = zip(xloc, yloc)

            for (x, y) in z:
                rects.append([int(x), int(y), int(w), int(h)])
                rects.append([int(x), int(y), int(w), int(h)])
            # print(template_str, len(xloc))
    rects, weights = cv2.groupRectangles(rects, 1, 0.2)

    return rects

def wait_cv2(image_str, region='all', confidence=0.7, max_time=20):
    template = cv2.imread(f'images/{image_str}.png', 0)
    if template is None:
        print("click_cv2: couldn't find file:", image_str)
        return 0
    found = False
    count = 0
    while not found:
        if region == 'all':
            pag.screenshot('temp/temp.png')
        else:
            pag.screenshot('temp/temp.png', region=region)
        screen = cv2.imread('temp/temp.png', 0)

        result = cv2.matchTemplate(screen, template, method)
        min_val, val, min_loc, loc = cv2.minMaxLoc(result)
        val = round(val, 2)

        if val > confidence:
            # print("wait_cv2", image_str, val)
            return val
        else:
            time.sleep(1)
            count += 1
        if count > max_time:
            return False
    return

def wait_many(images, confidence=0.7, max_time=10):
    # print("Wait many")
    templates = []
    for x, region in images:
        template = cv2.imread(f'images/{x}.png', 0)
        if template is None:
            print("Wait many: couldn't find file:", x)
        else:
            templates.append((template, region))

    found = False
    count = 0
    while not found:
        # Update the screenshot
        for template, region in templates:
            if region == 'all':
                pag.screenshot('temp/temp_wait.png')
            else:
                pag.screenshot('temp/temp_wait.png', region=region)
            try:
                time.sleep(0.1)
                screen = cv2.imread('temp/temp_wait.png', 0)
            except:
                return False

            # Loop through the templates
            result = cv2.matchTemplate(screen, template, method)
            min_val, val, min_loc, loc = cv2.minMaxLoc(result)
            if val > confidence:
                # print("Wait many", images, round(val, 2))
                return val

        # Iterate every second
        time.sleep(1)
        count += 1
        if count > max_time:
            print("Wait many failure")
            return False

def dist(a,b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    dist = (x**2 + y**2) ** 0.5
    return dist

def click_move(a):
    b = pag.position()
    distance = dist(a,b)
    pag.moveTo(a[0], a[1], distance/2400)
    pag.click(a)

def click_cv2(image_str, region='all', confidence=0.6):
    try:
        if region == 'all':
            pag.screenshot('temp/temp.png')
        else:
            pag.screenshot('temp/temp.png', region=region)
    except:
        pass
    screen = cv2.imread('temp/temp.png', 0)
    template = cv2.imread(f'images/{image_str}.png', 0)
    if template is None:
        print("click_cv2: couldn't find file:", image_str)
        return
    y, x = template.shape
    # print(x,y)
    result = cv2.matchTemplate(screen, template, method)
    min_val, val, min_loc, loc = cv2.minMaxLoc(result)
    val = round(val,2)
    # if PRINT_CV2:
    # print("click_cv:", image_str, val, loc)
    if val > confidence:
        if region == 'all':
            a = (loc[0] + x/2, loc[1] + y/2)
            # print(loc)
        else:
            a = region[0] + loc[0] + x / 2, region[1] + loc[1] + y / 2

        click_move(a)

        time.sleep(0.25)
        return val, True
    # print(f"click_cv2: {image_str} val={round(val,2)} (vs {confidence}) loc={loc}")
    return val, False

def wait_and_click(image, confidence=0.6):
    # print("Wait and click:", image)
    found = False
    count = 0
    while not found:
        val, loc, rect = find_cv2(image)
        # print("Wait and click:", image, val)
        if val > confidence:
            click_cv2(image, confidence=confidence)
            return True
        else:
            # print(f"{image} {count}")
            time.sleep(1)
            count += 1
        if count == 60:
            wait_and_click('bluestacks_icon')
        if count > 120:
            return
    return


def click_rect(rectangle,region=None):
    if not region: region = (0,0,0,0)
    x, y, w, h = rectangle
    x_coord = region[0] + x + w/2
    y_coord = region[1] + y + h/2
    # pag.moveTo(x_coord, y_coord, 0.3)
    pag.click(x_coord, y_coord)
    return

def town_hall(img):
    if img is None:
        print("Town hall - no image")
        return "No image", "No image"
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_str = []
    for x in TH7: template_str.append((x,7))
    for x in TH8: template_str.append((x,8))
    for x in TH9: template_str.append((x,9))
    for x in TH10: template_str.append((x,10))
    for x in TH11: template_str.append((x,11))
    for x in TH12: template_str.append((x,12))
    for x in TH13: template_str.append((x,13))
    for x in TH14: template_str.append((x,14))

    # print(template_str)

    templates = []
    for name, number in template_str: templates.append((number, cv2.imread(f'images/{name}.png', 0)))
    method = cv2.TM_CCOEFF_NORMED

    max_value = 0.5
    max_th = 100
    max_loc = None
    for number, template in templates:
        h, w = template.shape
        result = cv2.matchTemplate(img, template, method)
        min_val, val, min_loc, location = cv2.minMaxLoc(result)
        # print(number, round(val,2), location)
        if val > max_value:
            max_value = val
            max_th = number
            x = int(location[0] + w / 2)
            y = int(location[1] + h / 2)
            max_loc = (x, y)
    # print("Town Hall Identified as:", max_th)
    return max_th, max_loc

def find_best(images, screen):
    val_max = 0
    val_name = None
    for image_str,image_name in images:
        template = cv2.imread(f'images/{image_str}.png', 0)
        if template is None:
            print("Find best: couldn't find file:", image_str)
        try:
            result = cv2.matchTemplate(screen, template, method)
        except:
            if screen is None:
                print("Find best: No screen")
            elif template is None:
                print("Find best: No template")
            else:
                print("Find best. Template didn't fit", screen.shape, template.shape)
            return "Not Found", 0
        _, val, _, _ = cv2.minMaxLoc(result)
        if val > val_max:
            val_max = val
            val_name = image_name
    return val_name, val_max

def bad_wizards():
    img = cv2.imread(f'attacks/attack.png', 0)
    template_str = [("wizard8",8), ]
    templates = []
    for name, number in template_str: templates.append((number, cv2.imread(f'templates/{name}.png', 0)))
    method = cv2.TM_CCOEFF_NORMED

    max_value = 0
    for number, template in templates:
        result = cv2.matchTemplate(img, template, method)
        min_val, val, min_loc, location = cv2.minMaxLoc(result)
        if val > max_value:
            max_value = val
    if max_value > 0.7:
        # print("Found a bad wizard")
        return True
    return False


def get_many(img, template, confidence):
    result = cv2.matchTemplate(img, template, method)
    yloc, xloc = np.where(result >= confidence)
    z = zip(xloc, yloc)

    h, w, channel = template.shape

    rectangles = []
    for (x, y) in z:
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])
    rectangles, _ = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def find_tower(i, templates):
    i = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)
    max_val = 0
    max_rect = None
    for template in templates:
        val, loc, rect = find_cv2(template, screen=i)
        if val > max_val:
            max_val = val
            max_rect = rect
    return max_val, max_rect



def find_tower_many(i, templates, confidence=0.6):
    # i = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)
    rectangles = []
    for template_str in templates:
        file = f"images/{template_str}.png"
        template = cv2.imread(file)
        if template is None:
            print("Couldn't find", file)
        else:
            rects_new = get_many(i, template, confidence)
            for rect in rects_new:
                rectangles.append(rect)
    # rectangles, _ = cv2.groupRectangles(rects, 1, 0.2)
    return rectangles


def check_loc_th(loc_th):
    if loc_th is None:
        pag.keyDown('s')
        time.sleep(1)
        pag.keyUp('s')
        loc_th = th_b()
    if loc_th is None:
        pag.keyDown('w')
        time.sleep(1)
        pag.keyUp('w')
        loc_th = th_b()
    if loc_th is None:
        loc_th = (1000,500)
        print("Failed to find TH - used default of 1000,500")
    return loc_th

def get_spots(a, b, n):
    spots = []
    if n == 1:
        x = int((a[0] + b[0]) / 2)
        y = int((a[1] + b[1]) / 2)
        spots.append((x, y))
        return spots

    try:
        x_gap = (a[0] - b[0]) / (n + 1)
        y_gap = (a[1] - b[1]) / (n + 1)
    except:
        return
    for i in range(1, n + 1):
        x = int(a[0] - x_gap * i)
        y = int(a[1] - y_gap * i)
        spots.append((x, y))
    return spots

def add_lines_and_spots(img, a, b, closest):
    cv2.line(img, a, b, (255,255,255), 2)
    if closest:
        spots = get_spots(a, b, 5)
        for x in spots:
            cv2.circle(img, x, 4, (255,0,0), -1)
    return img



def get_drop_points(account, img, center, target_locs):
    # print("Get drop points")
    if img is None:
        # print("Get drop points - image not supplied")
        return

    cv2.circle(img, center, 20, (255, 0, 0), -1)

    x_center, y_center = center

    drop_points = []

    for target_loc in target_locs:
        x_target, y_target = pag.center(target_loc)
        if x_target == x_center:
            m_target = 100
        else:
            m_target = (y_target - y_center) / (x_target - x_center)
            m_target = int(min(100, m_target))

        best_dp_distance = 1000
        best_dp = None

        for x0, y0, m0 in lines:
            x_dp = int((y_target - y0 + m0 * x0 - m_target * x_target) / (m0 - m_target))
            y_dp = int(m0 * (x_dp - x0) + y0)
            distance = ((x_dp - x_target) ** 2 + (y_dp - y_target) ** 2) ** 0.5
            if (x_center < x_target < x_dp or x_center > x_target > x_dp) and distance < best_dp_distance:
                best_dp_distance = distance
                best_dp = [x_dp, y_dp]

        cv2.rectangle(img, target_loc, (0, 0, 255), 2)
        if best_dp_distance < 150:
            cv2.rectangle(img, target_loc, (255, 255, 255), 2)
            drop_points.append(best_dp)
            cv2.circle(img, best_dp, 20, (255,255,255), -1)

    cv2.line(img, top, right, (255,255,255), 2)
    cv2.line(img, bottom, right, (255,255,255), 2)
    cv2.line(img, top, left, (255,255,255), 2)
    cv2.line(img, bottom, left, (255,255,255), 2)

    # save the image
    post = datetime.now().strftime('%I%M%p')
    x = f'images/attacks{account.number}b/attack {post}.png'

    cv2.imwrite(x, img)
    # print("Get drop points - save the image:", x)


    return drop_points


def show(img, dur=5000, label="Image", scale=1):
    img = cv2.resize(img, (0, 0), fx=scale, fy=scale)
    cv2.imshow(label, img)
    cv2.waitKey(dur)
    cv2.destroyAllWindows()

