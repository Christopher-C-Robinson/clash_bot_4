from troops import *
from towers_load import *

# ================
# === ATTACK_B ===
# ================

barb5 = (i_barb_b, 5, 6)
barb_bulk = (i_barb, 5, 13)
machine = (i_machine, 2, 1)
chopper = (i_chopper, 2, 1)
bomb3 = (i_bomber, 3, 1)
bomb4 = (i_bomber, 4, 1)
bomb5 = (i_bomber, 5, 1)
cannon2 = (i_cannon, 2, 1)
cannon3 = (i_cannon, 3, 1)
cannon4 = (i_cannon, 4, 1)
cannon5 = (i_cannon, 5, 1)
giant4 = (i_giant, 4, 1)
pekka1 = (i_pekka, 1, 1)

troops4 = [machine, chopper, barb5]
troops3 = [barb5, machine, bomb3, barb5, barb5, cannon5, barb5, barb5, barb5, cannon4, barb5, barb5, ]
troops2 = [barb5, machine, bomb5, barb5, barb5, cannon5, barb5, barb5, barb5, cannon4, barb5, barb5, barb5, ]
troops1 = [barb5, bomb5, giant4, barb5, pekka1, barb5, cannon3, machine, cannon3, barb5]

TROOPS_B = ["Fail", troops1, troops2, troops3]

# === ATTACKS ===
war1 = ["edrag",] * 2 + ["dragon"] * 12 + ["freeze"] * 11
war2 = ["dragon"] * 12 + ["lightening"] * 11
war3 = ["dragon"] * 12 + ["bloons"] * 3 + ["lightening"] * 11
war = [None, war1, war2, war3]

BARB50 = {
            "name": "barb50",
            "max_th": 4,
            "wizard_check": True,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": False,
            "bomb_target": None,
            "bomb_target2": None,
            "lightening": 0,
            "initial_troops": [],
            "troop_group": [(barb, 10), ],
            "troop_groups": 5,
            "final_troops": [],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": True,
        }

BARB70 = {
            "name": "barb70",
            "max_th": 4,
            "wizard_check": True,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": False,
            "bomb_target": None,
            "bomb_target2": None,
            "lightening": 0,
            "initial_troops": [],
            "troop_group": [(barb, 8), (bomber, 1),],
            "troop_groups": 7,
            "final_troops": [],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": True,
        }

BARB80 = {
            "name": "barb80",
            "max_th": 4,
            "wizard_check": True,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": False,
            "bomb_target": None,
            "bomb_target2": None,
            "lightening": 0,
            "initial_troops": [clan],
            "troop_group": [(barb, 8), (bomber, 1),],
            "troop_groups": 8,
            "final_troops": [],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": True,
        }

BARB100 = {
            "name": "barb100",
            "max_th": 4,
            "wizard_check": True,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": False,
            "bomb_target": None,
            "bomb_target2": None,
            "lightening": 0,
            "initial_troops": [clan],
            "troop_group": [(barb, 8), (bomber, 1),],
            "troop_groups": 10,
            "final_troops": [],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": True,
        }

GIANT130 = {
            "name": "giant130",
            "max_th": 6,
            "wizard_check": True,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 7,
            "initial_troops": [giant, giant, clan],
            "troop_group": [(giant, 2), (bomber, 1), (wizard, 2), ],
            "spells": [],
            "troop_groups": 6,
            "final_troops": [],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": ["super_goblin,"],
            "th_gold_adj": True,
        }

GIANT150 = {
            "name": "giant150",
            "max_th": 7,
            "wizard_check": True,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 7,
            "initial_troops": [giant, giant, clan],
            "troop_group": [(giant, 2), (bomber, 1), (wizard, 2), ],
            "spells": [],
            "troop_groups": 7,
            "final_troops": [],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": ["super_goblin,"],
            "th_gold_adj": True,
        }

GIANT200 = {
            "name": "giant200",
            "max_th": 7,
            "wizard_check": True,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 7,
            "initial_troops": [king, log_thrower, queen, warden],
            "troop_group": [(giant, 2), (bomber, 1), (wizard, 2), ],
            "spells": [],
            "troop_groups": 10,
            "final_troops": [],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": ["super_goblin,"],
            "th_gold_adj": True,
        }

GIANT240 = {
            "name": "giant240",
            "max_th": 7,
            "wizard_check": True,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 7,
            "initial_troops": [king, log_thrower, queen, warden],
            "troop_group": [(giant, 2), (bomber, 1), (wizard, 2), ],
            "spells": [],
            "troop_groups": 12,
            "final_troops": [],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": ["super_goblin,"],
            "th_gold_adj": True,
        }

GIANT200_GAMES = {
            "name": "giant200",
            "max_th": 7,
            "wizard_check": True,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 7,
            "initial_troops": [king, giant, giant, giant, giant],
            "troop_group": [(giant, 3), (bomber, 1), (wizard, 2), ],
            "spells": [],
            "troop_groups": 6,
            "final_troops": [],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": True,
        }

GIANT220 = {
            "name": "giant220",
            "resource_objective": [400000,0,000],
            "max_th": 10,
            "wizard_check": True,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 9,
            "initial_troops": [king, log_thrower, queen, giant, giant, giant, giant],
            "troop_group": [(giant, 3), (bomber, 1), (wizard, 2), ],
            "troop_groups": 8,
            "final_troops": [],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": True,
        }

# GIANT240 = {
#             "name": "giant240",
#             "resource_objective": [400000,0,2000],
#             "max_th": 10,
#             "wizard_check": True,
#             "towers_to_avoid": INFERNO_HIGH,
#             "bomb": True,
#             "bomb_target": wizard_tower,
#             "bomb_target2": None,
#             "lightening": 11,
#             "spells": [],
#             "initial_troops": [king, log_thrower, queen, warden],
#             "troop_group": [(giant, 3), (bomber, 1), (wizard, 2), ],
#             "troop_groups": 9,
#             "final_troops": [wizard, wizard, wizard, goblin, goblin, goblin],
#             "troop_pause": 0,
#             "drop_points": False,
#             "drop_point_troops": [],
#             "th_gold_adj": False,
#         }

GIANT240_GAMES = {
            "name": "giant240",
            "resource_objective": [400000,0,2000],
            "max_th": 9,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 11,
            "spells": [],
            "initial_troops": [king, log_thrower, queen, warden],
            "troop_group": [(giant, 3), (bomber, 1), (wizard, 2), ],
            "troop_groups": 8,
            "final_troops": [wizard, wizard, goblin, goblin],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

GIANT260 = {
            "name": "giant260",
            "resource_objective": [400000,0,0],
            "max_th": 11,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 11,
            "initial_troops": ["king", "clan", "clan_ram", "clan_ram2", "queen", "warden", "giant"],
            "troop_group": [("giant", 6), ("bomb", 2), ("wizard", 6), ],
            "troop_groups": 4,
            "final_troops": ["wizard", "wizard", ],
            "troop_pause": 0,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

GOLEMS_9 = {
            "name": "golems",
            # "resource_objective": [500000,0,0],
            "resource_objective": [0,0,500],
            "max_th": 11,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 0,
            "initial_troops": ["king", "queen", ],
            "troop_group": [("golem", 3), ("witch", 10), ("bomb", 5), ],
            "troop_groups": 1,
            "final_troops": ["clan", ],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

GOLEMS_11 = {
            "name": "golems",
            # "resource_objective": [500000,0,0],
            "resource_objective": [0,0,3000],
            "max_th": 11,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 0,
            "initial_troops": ["king", "queen", ],
            "troop_group": [("golem", 3), ("witch", 13), ("bomb", 13), ],
            "troop_groups": 1,
            "final_troops": ["clan", ],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

GOLEMS_13 = {
            "name": "golems",
            # "resource_objective": [500000,0,0],
            "resource_objective": [0,0,5000],
            "max_th": 11,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 0,
            "initial_troops": ["king", "queen", ],
            "troop_group": [("golem", 3), ("witch", 16), ("bomb", 9), ],
            "troop_groups": 1,
            "final_troops": ["clan", ],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

DRAGONS_200 = {
            "name": "dragons",
            # "resource_objective": [500000,0,0],
            "resource_objective": [00000,0,000],
            "max_th": 7,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": False,
            "bomb_target": air_defence,
            "bomb_target2": inferno,
            "lightening": 11,
            "spells": [],
            "initial_troops": [king, clan, queen, warden],
            "troop_group": [(dragon, 10), ],
            "troop_groups": 1,
            "final_troops": [],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

DRAGONS_220 = {
            "name": "dragons",
            # "resource_objective": [500000,0,0],
            "resource_objective": [00000,0,000],
            "max_th": 10,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": False,
            "bomb_target": air_defence,
            "bomb_target2": inferno,
            "lightening": 11,
            "spells": [],
            "initial_troops": [king, log_thrower, queen, warden],
            "troop_group": [(dragon, 11), ],
            "troop_groups": 1,
            "final_troops": [],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

DRAGONS_240 = {
            "name": "dragons",
            # "resource_objective": [500000,0,0],
            "resource_objective": [00000,0,000],
            "max_th": 9,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": False,
            "bomb_target": air_defence,
            "bomb_target2": inferno,
            "lightening": 11,
            "spells": [],
            "initial_troops": [king, clan, queen, warden],
            "troop_group": [(dragon, 12), ],
            "troop_groups": 1,
            "final_troops": [],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

DRAGONS_260 = {
            "name": "dragons",
            # "resource_objective": [500000,0,0],
            "resource_objective": [00000,0,000],
            "max_th": 11,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": False,
            "bomb_target": air_defence,
            "bomb_target2": inferno,
            "lightening": 11,
            "spells": [],
            "initial_troops": [king, log_thrower, queen, warden],
            "troop_group": [(dragon, 13), ],
            # "troop_group": [(edrag, 8), (dragon, 1), ],
            "troop_groups": 1,
            "final_troops": [],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

BARBS_48 = {
            "name": "barbs",
            # "resource_objective": [500000,0,0],
            "resource_objective": [400000,0,3000],
            "max_th": 11,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 11,
            "spells": [],
            "initial_troops": [king, log_thrower, queen, warden],
            "troop_group": [(super_barb, 48), ],
            "troop_groups": 1,
            "final_troops": [],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

BARBS_52 = {
            "name": "barbs",
            # "resource_objective": [500000,0,0],
            "resource_objective": [400000,0,3000],
            "max_th": 11,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 0,
            "spells": [],
            "initial_troops": [king, log_thrower, queen, warden, champ],
            "troop_group": [(super_barb, 52), ],
            "troop_groups": 1,
            "final_troops": [],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

BARBS_56 = {
            "name": "barbs",
            # "resource_objective": [500000,0,0],
            "resource_objective": [400000,0,3000],
            "max_th": 12,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 11,
            "spells": [],
            "initial_troops": [king, log_thrower, queen, warden, champ],
            "troop_group": [(super_barb, 56), ],
            "troop_groups": 1,
            "final_troops": [],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

BARBS_52_GAMES = {
            "name": "barbs",
            # "resource_objective": [500000,0,0],
            "resource_objective": [400000,0,3000],
            "max_th": 11,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 11,
            "spells": [],
            "initial_troops": [king, log_thrower, queen, warden, champ],
            "troop_group": [(super_barb, 46), ],
            "troop_groups": 1,
            "final_troops": [],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

BARBS_60 = {
            "name": "barbs",
            "resource_objective": [300000,0,5000],
            # "resource_objective": [0,0,5000],
            "max_th": 14,
            "wizard_check": False,
            "towers_to_avoid": NOTHING,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 11,
            "spells": [],
            "initial_troops": [king, log_thrower, queen, warden, champ],
            "troop_group": [(super_barb, 60), ],
            "troop_groups": 1,
            "final_troops": [],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

BARBS_60_GAMES = {
            "name": "barbs",
            "resource_objective": [300000,0,5000],
            # "resource_objective": [0,0,5000],
            "max_th": 13,
            "wizard_check": False,
            "towers_to_avoid": INFERNO_HIGH,
            "bomb": True,
            "bomb_target": wizard_tower,
            "bomb_target2": None,
            "lightening": 11,
            "spells": [],
            "initial_troops": [king, log_thrower, queen, warden, champ],
            "troop_group": [(super_barb, 54), ],
            "troop_groups": 1,
            "final_troops": [],
            "troop_pause": 0.45,
            "drop_points": False,
            "drop_point_troops": [],
            "th_gold_adj": False,
        }

GOBLIN = {
            "name": "goblins",
            "resource_objective": [500000,0,0],
            "max_th": 101,
            "wizard_check": False,
            "towers_to_avoid": [],
            "bomb": False,
            "bomb_target": None,
            "bomb_target2": None,
            "lightening": 0,
            "spells": [],
            "initial_troops": [],
            "troop_group": [("super_goblin", 86), ], # This is used to define the min number required
            "troop_groups": 1,
            "final_troops": [],
            "drop_points": True,
            "drop_point_troops": ["super_goblin",],
            "th_gold_adj": False,
        }

GOBLIN_13 = {
            "name": "goblins",
            "resource_objective": [500000,0,0],
            "max_th": 101,
            "wizard_check": False,
            "towers_to_avoid": [],
            "bomb": False,
            "bomb_target": None,
            "bomb_target2": None,
            "lightening": 0,
            "spells": [],
            "initial_troops": [],
            "troop_group": [("super_goblin", 99), ("bomb", 1),], # This is used to define the min number required
            "troop_groups": 1,
            "final_troops": [],
            "drop_points": True,
            "drop_point_troops": ["super_goblin",],
            "th_gold_adj": False,
        }

# DRAGONS_300 = [dragon] * 28 + [bloon] * 6 + [log_thrower] * 6 + [poison, lightening] + [freeze] * 11
# DRAGONS_260 = [dragon] * 26 + [bloon] + [poison] + [freeze] * 20
# DRAGONS_240 = [dragon] * 24 + [poison] + [lightening] * 20

