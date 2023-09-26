from images import *

# -----------------
# ---- GENERAL ----
# -----------------

def multi_image_find(screen, images, show_results=False):
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    max_val = 0
    max_image = None
    max_loc = None
    for image in images:
        result, val, loc = image.find_screen(screen, return_location=True, return_result=True)
        if show_results:
            print("Multi image find:", image, val, loc)
        if val > max_val:
            max_val = val
            max_loc = loc
            max_image = image
    return max_image, max_val, max_loc

def to_bw(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

# ------------------
# ---- ATTACK_B ----
# ------------------

def th_b():
    th_size = 120
    img = cv2.imread('temp/attack_b/attacking_b.png')
    print("Identify Builder Town Hall")
    if img is None:
        print("Th_b - Couldn't read screen")
        return

    image, val, loc = multi_image_find(img, town_halls_b, show_results=False)
    result = False
    if val > 0.6:
        cv2.rectangle(img, (loc[0], loc[1], th_size, th_size), (255, 255, 255), 2)
        result = True

    # save the image
    cv2.imwrite('temp/attack_b/attacking_b2.png', img)

    if result == False: return False
    return loc[0] + th_size // 2, loc[1] + th_size // 2

def objects_b(loc_th):
    print("Testing objects b")
    scale = 0.73  # this is to allow for the x / y perspective
    gap = 200     # this is the add to the lines
    img = cv2.imread('temp/attack_b/attacking_b2.png')
    print("Identify Builder Extremities")
    if img is None:
        print("Objects_b - Couldn't read screen")
        return

    rects = find_tower_many(img, OBJECTS_B, confidence=0.65)
    for rect in rects:
        cv2.rectangle(img, rect, (255, 255, 255), 1)

    dist_tl = 0
    dist_tr = 0
    dist_bl = 0
    dist_br = 0
    for rect in rects:
        # print(rect)
        # if not rect: continue
        loc = pag.center(rect)
        # print("Objects b", loc, loc_th)
        try:
            dist = abs(loc[0]-loc_th[0]) + int((abs(loc[1]-loc_th[1])) / scale)
        except:
            continue
        if dist > 650: dist = 0
        if loc[0] < loc_th[0]:
            if loc[1] < loc_th[1]:
                if dist > dist_tl: dist_tl = dist
            else:
                if dist > dist_bl: dist_bl = dist
        else:
            if loc[1] < loc_th[1]:
                if dist > dist_tr: dist_tr = dist
            else:
                if dist > dist_br: dist_br = dist

    dist_tl += gap
    dist_tr += gap
    dist_bl += int(gap * 1.3) * 1000  # * 1000 to turn off attacks from the south
    dist_br += int(gap * 1.3) * 1000  # * 1000 to turn off attacks from the south
    min_dist = min(dist_tl, dist_bl, dist_br, dist_tr)

    attack_a, attack_b = None, None
    # lines = [(dist_tl, -1, -1), (dist_tr, 1, -1), (dist_bl, -1, 1), (dist_br, 1, 1), ]
    lines = [(dist_tl, -1, -1), (dist_tr, 1, -1)]
    for dist, x_dir, y_dir in lines:
        try:
            a = (loc_th[0], loc_th[1] + int(dist * scale) * y_dir)
            b = (loc_th[0] + dist * x_dir, loc_th[1])
            closest = (dist == min_dist)
            img = add_lines_and_spots(img, a, b, closest)
            if closest:
                attack_a = a
                attack_b = b
        except:
            pass

    # save and show the image
    cv2.imwrite('temp/attack_b/attacking_b3.png', img)
    # show(img_orig, dur=10000)
    return attack_a, attack_b

# print("Result:", objects_b(th_b()))


# ----------------
# ---- ATTACK ----
# ----------------


def get_double_screen():
    # print("Get double screen: Going up")
    for _ in range(2): pag.scroll(300)
    pag.moveTo(1000, 500, 0.2)
    # time.sleep(0.2)
    pag.screenshot('temp/attack/attacking1.png')
    # print("Get double screen: Going down")
    time.sleep(0.2)
    for _ in range(3): pag.scroll(-300)
    time.sleep(0.2)
    pag.screenshot('temp/attack/attacking2.png')
    time.sleep(0.2)
    for _ in range(5): pag.scroll(300)

def create_double_screen(update_screen=True):
    if update_screen:
        get_double_screen()
    print("Create double screen")
    global scroll_adj
    x_end = 2040
    y1_end = 600
    y2_end = 900

    # read screenshots
    img1 = cv2.imread('temp/attack/attacking1.png', 1)
    img2 = cv2.imread('temp/attack/attacking2.png', 1)

    # find TH for alignment
    image1, val1, loc1 = multi_image_find(img1, town_halls)
    image2, val2, loc2 = multi_image_find(img2, town_halls)
    try:
        y_adj = loc1[1] - loc2[1]
        y2_start = y1_end - y_adj
        scroll_adj = y_adj
        print("Scroll adjustment:", scroll_adj)
    except:
        y2_start = 180
        if val2 and not val1:
            y1_end = 500
            y2_start = y1_end - 360 # 180 is the extra bit (the size of the combined less the standard size)
            y2_end = y2_start + 900
            print("Current Scenario")
        # print("Scroll adjustment not set", loc1, loc2)
        # return None

    # crop and combine images
    print("Create double screen - crop and combine", 0, y1_end, y2_start, y2_end)
    img1 = img1[0:        y1_end, 0: x_end]
    img2 = img2[y2_start: y2_end, 0: x_end]
    img = np.concatenate((img1, img2), axis=0)

    # save the image
    # post = datetime.now().strftime('%I%M%p')
    x = f'temp/attack/attacking.png'
    print("Create double screen - save the image:", x)
    cv2.imwrite(x, img)
    # show(img)
    print("Create double screen - return")
    return img

def ram_drop_point(img):
    # return
    # print("Ram drop point")
    if img is None:
        # print("Ram drop point - Create double screen didn't return image")
        return

    img_orig = img.copy()

    image, val, loc = multi_image_find(img, town_halls)
    print("TH Image", image)
    rect = (loc[0], loc[1], 80, 80)

    result_th, result_eagle = False, False
    if val > 0:
        cv2.rectangle(img, rect, (255, 255, 255), 2)
        result_th = True
    x_th, y_th = loc[0] + 40, loc[1] + 40
    image, val, loc = multi_image_find(img, eagles)
    print("Eagle Image", image)
    rect = (loc[0], loc[1], 80, 80)
    if val > 0:
        cv2.rectangle(img, rect, (255, 255, 255), 2)
        result_eagle = True
    x_eagle, y_eagle = loc[0] + 40, loc[1] + 40

    print("Ram drop point - TH and Eagle results", result_th, result_eagle)
    if not (result_eagle and result_th):
        # print("Ram drop point - Couldn't find TH or Eagle")
        return
    if x_eagle == x_th:
        m_eagle = 100
    else:
        m_eagle = (y_eagle - y_th) / (x_eagle - x_th)

    best_dp_distance = 1000
    best_dp = None

    for x0, y0, m0 in lines:
        try:
            x_dp = int((y_eagle - y0 + m0 * x0 - m_eagle * x_eagle) / (m0 - m_eagle))
        except:
            return
        y_dp = int(m0 * (x_dp - x0) + y0)
        distance = ((x_dp - x_eagle) ** 2 + (y_dp - y_eagle) ** 2) ** 0.5
        if (x_th < x_eagle < x_dp or x_th > x_eagle > x_dp) and distance < best_dp_distance:
            best_dp_distance = distance
            best_dp = [x_dp, y_dp]

        cv2.circle(img, best_dp, 20, (255, 255, 255), -1)

    cv2.line(img, top, right, (255, 255, 255), 2)
    cv2.line(img, bottom, right, (255, 255, 255), 2)
    cv2.line(img, top, left, (255, 255, 255), 2)
    cv2.line(img, bottom, left, (255, 255, 255), 2)

    # show(img_orig)

    # save the image
    # post = datetime.now().strftime('%I%M%p')
    file = "temp/attack/attacking_th_eagle.png"
    # x = f'images/attacks{account.number}/attack.png'

    # cv2.imwrite(x, img_orig)
    cv2.imwrite(file, img)
    print("Ram drop point image saved", file)

    return best_dp

def get_th_level(image, show_result=False):
    if image is None: return
    image = to_bw(image)
    level = -1
    for town_hall in town_halls:
        if town_hall.find_screen(image):
            level = town_hall.level
        if show_result:
            print("Get TH level:", town_hall, town_hall.find_screen(image, show_image=False,  return_result=True))
    return level

def test_get_th_level():
    image = cv2.imread('temp/attack/attacking.png', 1)
    show(image)
    print(get_th_level(image))

