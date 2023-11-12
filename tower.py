from images import *

files = os.listdir("numbers/build_towers")
towers = []
missing_file_count = 0


def get_image_from_file(object, village, style):
    global missing_file_count
    file = f'{object}_{style}.png'
    if style == "": file = f'{object}.png'
    if village == "main": directory = 'numbers/build_towers/'
    else: directory = 'images/towers_b/'
    image = None
    if file in files:
        image = cv2.imread(directory + file, 0)
    elif village == "main":
        missing_file_count += 1
        print(f"Adding image ({missing_file_count}): could not find '{directory + file}'")
    return image

class Tower():
    def __init__(self, name, village, category, resource, priority, yolo_code):
        self.name = name
        self.village = village
        self.category = category
        self.resource = resource
        self.priority = priority
        self.yolo_code = yolo_code
        self.i_text = get_image_from_file(name, village, "")
        self.images = []
        self.levels = []
        towers.append(self)

    def __str__(self):
        return f"{self.name}"

    def get_images(self):
        self.images = []
        dir = f"towers/{self.name}/"
        files = dir_to_list(dir)
        for file in files:
            new = Image(name=file, file='images/' + file + ".png", threshold=0.7)

            self.images.append(new)

    def print_tower(self):
        print("Tower:", self.name)
        for x in self.levels:
            print(" -", x)

    def add_level(self, tower, number, th, gold, elixir, dark, days):
        self.Level(tower=tower, number=number, th=th, gold=gold, elixir=elixir, dark=dark, days=days)

    def return_level(self, number):
        for level in self.levels:
            if level.number == number: return level

    def remaining_time(self, current_level, th):
        if current_level is None:
            current_level = self.return_level(1)
        time_left = timedelta(days=0)
        for level in self.levels:
            if level.th <= th and level.number > current_level.number:
                # print("Remaining time:", level.th, th, level.number, current_level.number)
                # print("Adding:", level.days)
                time_left += level.days
        return time_left

    def get_level_from_cost(self, cost):
        for level in self.levels:
            # print("Get level from cost", level.cost, cost)
            if level.cost >= cost:
                next_level = level
                return self.return_level(next_level.number - 1)

    class Level():
        def __init__(self, tower, number, th, gold, elixir, dark, days):
            self.tower = tower
            self.number = number
            self.th = th
            self.gold = gold
            self.elixir = elixir
            self.dark = dark
            self.cost = max(gold, elixir, dark)
            self.days = timedelta(days=days)
            tower.levels.append(self)

        def __str__(self):
            return f"Level: {self.number}. Time: {self.days}. Cost: {self.cost:,.0f}"


