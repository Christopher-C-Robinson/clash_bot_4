from images import *

def multi_image_find(screen, images):
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    max_val = 0
    max_image = None
    max_loc = None
    for image in images:
        result, val, loc = image.find_screen(screen, return_location=True, return_result=True)
        # print("Multi image find:", image, val, loc)
        if val > max_val:
            max_val = val
            max_loc = loc
            max_image = image
    return max_image, max_val, max_loc

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
    print("Val", val1, val2)
    print("Loc", loc1, loc2)
    # y_adj = loc1[1] - loc2[1]
    # y2_start = y1_end - y_adj
    # scroll_adj = y_adj
    print("Create double screen - locs", loc1, loc2)
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
    show(img)
    print("Create double screen - return")
    return img

# create_double_screen(1)

def to_bw(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return(image)

def get_th_level(image):
    if image is None: return
    image = to_bw(image)
    level = -1
    for town_hall in town_halls:
        if town_hall.find_screen(image):
            level = town_hall.level
        else:
            if town_hall.level == 14:
                print(town_hall, town_hall.find_screen(image, show_image=False,  return_result=True))
    return level


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

# img = cv2.imread('temp/attacking1.png', 1)
# print(img.shape)
# img = cv2.imread('temp/attacking2.png', 1)
# print(img.shape)
# print(1261-1080)

# create_double_screen(False)
# img = cv2.imread('temp/attack/attacking.png', 1)
# print(ram_drop_point(img))
# print(img.shape)
