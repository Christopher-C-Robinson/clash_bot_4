from object_recognition import *
from constants import *
method = cv2.TM_CCOEFF_NORMED

number_sets = []

class Number():
    def __init__(self, name, directory, confidence=0.75):
        # print("Creating number set:", name)
        self.name = name
        self.numbers = []
        self.confidence = confidence
        files = os.listdir(directory)
        for file in files:
            image = cv2.imread(f'{directory}/{file}', 0)
            x = file[0:-4]
            self.numbers.append((x, image))
        number_sets.append(self)

    def show_numbers(self):
        for x, i in self.numbers:
            show(i, label=str(x))

    def read(self, region, show_image=False, return_number=False):
        pag.screenshot(f'temp/number_set.png', region=region)
        screen = cv2.imread(f"temp/number_set.png", 0)
        return self.read_screen(screen, show_image=show_image, return_number=return_number)

    def read_one(self, region):
        pag.screenshot(f'temp/number_set.png', region=region)
        screen = cv2.imread(f"temp/number_set.png", 0)
        max, best_number = 0, None
        for number, image in self.numbers:
            result = cv2.matchTemplate(screen, image, method)
            min_val, val, min_loc, loc = cv2.minMaxLoc(result)
            if val > max:
                max = val
                best_number = number
        return best_number

    def read_one_screen(self, screen):
        max, best_number = 0, None
        for number, image in self.numbers:
            # show(screen)
            result = cv2.matchTemplate(screen, image, method)
            min_val, val, min_loc, loc = cv2.minMaxLoc(result)
            # print(number, round(val, 2))
            if val > max and val > self.confidence:
                max = val
                best_number = number
        if best_number: return int(best_number)
        return None

    def read_screen(self, screen, show_image=False, return_number=False, return_y=False):
        # print("Read screen - start", show_image)
        found = []
        y_coords = None
        for number, image in self.numbers:
            # print(number)
            h, w = image.shape
            # print(number, image.shape)
            result = cv2.matchTemplate(screen, image, method)

            if show_image:
                min_val, val, min_loc, loc = cv2.minMaxLoc(result)
                # show(image)
                show(screen, label=str(round(val,2)))
            yloc, xloc = np.where(result >= self.confidence)
            z = zip(xloc, yloc)
            rectangles = []
            for (x, y) in z:
                # print("Read number x and y:", x, y)
                rectangles.append([int(x), int(y), int(w), int(h)])
                rectangles.append([int(x), int(y), int(w), int(h)])
                y_coords = y
            rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

            if len(rectangles) > 0:
                for rectangle in rectangles:
                    found.append((str(number), rectangle[0]))
        # print("Number set - read screen (found variable):", found)
        result = ""
        found.sort(key=lambda tup: tup[1])
        # print("Number set - read screen (found variable sorted):", found)
        prev_x = -4
        for y in found:
            # print(prev_x, y[1])
            if y[1] <= prev_x + 3:
                found.remove(y)
                # print("Number set - read screen - removed", y[0])
            prev_x = y[1]
        for y in found:
            result += y[0]
        # print("Number set - read screen (result):", result)
        if return_number:
            result = result.replace("b", "")
            result = result.replace("e", "")
            result = result.replace("g", "")
            result = result.replace("h", "")
            result = result.replace("x", "")

            try:
                result = int(result)
            except:
                result = 0
        # print("Read screen - end")


        if return_y:
            return result, y_coords
        return result


resource_numbers = Number(name="resource_numbers", directory="numbers/resources", confidence=0.89)
available_resource_set = Number(name="available_resource", directory="numbers/available_resources", confidence=0.88 )
cost_numbers = Number(name="cost_numbers", directory="numbers/cost", confidence=0.85)
tower_count = Number(name="tower_count", directory="numbers/tower_count", confidence=0.85)
build_time = Number(name="build_time", directory="numbers/time", confidence=0.89)
research_time = Number(name="research_time", directory="numbers/research", confidence=0.85)
army_time = Number(name="army_time", directory="numbers/army_time", confidence=0.85)
troop_numbers = Number(name="troop_numbers", directory="numbers/troop_numbers", confidence=0.85)
selected_level = Number(name="selected_level", directory="numbers/levels", confidence=0.9)
selected_tower = Number(name="selected_tower", directory="numbers/towers", confidence=0.9)
trophies = Number(name="trophies", directory="numbers/trophies", confidence=0.9)
coin_time = Number(name="coin_time", directory="numbers/coin")
war_donation_count = Number(name="war_donation_count", directory="numbers/war_donation_count", confidence=0.86)
scores = Number(name="war_scores", directory="numbers/scores", confidence=0.85)
chat_new = Number(name="chat_new", directory="numbers/surveillance", confidence=0.85)
members = Number(name="Members", directory="numbers/members", confidence=0.90)
stars = Number(name="Stars", directory="numbers/stars", confidence=0.90)
war_time = Number(name="war_time", directory="numbers/war_time", confidence=0.86)
war_stars = Number(name="war_stars", directory="numbers/war_stars", confidence=0.86)

build_towers = Number(name="build_towers", directory="numbers/build_towers", confidence=0.84)
build_towers_mult = Number(name="build_towers_mult", directory="numbers/build_towers_mult", confidence=0.79)
build_towers_cost = Number(name="build_towers_cost", directory="numbers/build_towers_cost", confidence=0.88)
build_towers_b = Number(name="build_towers_b", directory="numbers/build_towers_b", confidence=0.85)
