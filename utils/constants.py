import json

MOOD_REGION=(705, 125, 835 - 705, 150 - 125)
TURN_REGION=(260, 65, 370 - 260, 140 - 65)
FAILURE_REGION=(250, 770, 855 - 295, 835 - 770)
YEAR_REGION=(255, 35, 420 - 255, 60 - 35)
CRITERIA_REGION=(455, 55, 765 - 455, 115 - 55)
SKILL_PTS_REGION=(760, 780, 825 - 760, 815 - 780)
SKIP_BTN_BIG_REGION_LANDSCAPE=(1500, 750, 1920-1500, 1080-750)
SCREEN_BOTTOM_REGION=(125, 800, 1000-125, 1080-800)
SCREEN_MIDDLE_REGION=(125, 300, 1000-125, 800-300)
SCREEN_TOP_REGION=(125, 0, 1000-125, 300)
RACE_INFO_TEXT_REGION=(285, 335, 810-285, 370-335)
RACE_LIST_BOX_REGION=(260, 580, 850-265, 870-580)

FULL_STATS_STATUS_REGION=(265, 575, 845-265, 940-575)
FULL_STATS_APTITUDE_REGION=(395, 340, 820-395, 440-340)

SCROLLING_SELECTION_MOUSE_POS=(560, 680)
SKILL_SCROLL_BOTTOM_MOUSE_POS=(560, 850)
RACE_SCROLL_BOTTOM_MOUSE_POS=(560, 850)

SPD_STAT_REGION = (310, 723, 55, 20)
STA_STAT_REGION = (405, 723, 55, 20)
PWR_STAT_REGION = (500, 723, 55, 20)
GUTS_STAT_REGION = (595, 723, 55, 20)
WIT_STAT_REGION = (690, 723, 55, 20)

MOOD_LIST = ["AWFUL", "BAD", "NORMAL", "GOOD", "GREAT", "UNKNOWN"]

SUPPORT_CARD_ICON_BBOX=(845, 155, 945, 700)
ENERGY_BBOX=(440, 120, 800, 160)
RACE_BUTTON_IN_RACE_BBOX_LANDSCAPE=(800, 950, 1150, 1050)

OFFSET_APPLIED = False
def adjust_constants_x_coords(offset=405):
  """Shift all region tuples' x-coordinates by `offset`."""

  global OFFSET_APPLIED
  if OFFSET_APPLIED:
    return

  g = globals()
  for name, value in list(g.items()):
    if (
      name.endswith("_REGION")   # only touch REGION constants
      and isinstance(value, tuple)
      and len(value) >= 2
    ):
      # Adjust only the x-coordinates (0 and 2)
      new_value = (
        value[0] + offset,
        value[1],
        value[2],
        value[3],
      )
      # Drop None if length was originally 3
      g[name] = tuple(x for x in new_value if x is not None)

    if (
      name.endswith("_MOUSE_POS")   # only touch REGION constants
      and isinstance(value, tuple)
      and len(value) >= 2
    ):
      # Adjust only the x-coordinates (0 and 2)
      new_value = (
        value[0] + offset,
        value[1],
      )
      # Drop None if length was originally 3
      g[name] = tuple(x for x in new_value if x is not None)

    if (
      name.endswith("_BBOX")   # only touch REGION constants
      and isinstance(value, tuple)
      and len(value) >= 2
    ):
      # Adjust only the x-coordinates (0 and 2)
      new_value = (
        value[0] + offset,
        value[1],
        value[2] + offset,
        value[3],
      )
      # Drop None if length was originally 3
      g[name] = tuple(x for x in new_value if x is not None)
  OFFSET_APPLIED = True

# Load all races once to be used when selecting them
RACES = ""
with open("data/races.json", "r", encoding="utf-8") as file:
  RACES = json.load(file)

# Build a lookup dict for fast (year, date) searches
RACE_LOOKUP = {}
for year, races in RACES.items():
  for name, data in races.items():
    key = f"{year} {data['date']}"
    race_entry = {"name": name, **data}
    RACE_LOOKUP.setdefault(key, []).append(race_entry)

# Build day dict
CAREER_DAY = {
    "Junior Year Pre Debut": {"day": 12, "month": "Pre Debut"},
    "Junior Year Early Jul": {"day": 13, "month": "Early Jul"},
    "Junior Year Late Jul": {"day": 14, "month": "Late Jul"},
    "Junior Year Early Aug": {"day": 15, "month": "Early Aug"},
    "Junior Year Late Aug": {"day": 16, "month": "Late Aug"},
    "Junior Year Early Sep": {"day": 17, "month": "Early Sep"},
    "Junior Year Late Sep": {"day": 18, "month": "Late Sep"},
    "Junior Year Early Oct": {"day": 19, "month": "Early Oct"},
    "Junior Year Late Oct": {"day": 20, "month": "Late Oct"},
    "Junior Year Early Nov": {"day": 21, "month": "Early Nov"},
    "Junior Year Late Nov": {"day": 22, "month": "Late Nov"},
    "Junior Year Early Dec": {"day": 23, "month": "Early Dec"},
    "Junior Year Late Dec": {"day": 24, "month": "Late Dec"},
    "Classic Year Early Jan": {"day": 25, "month": "Early Jan"},
    "Classic Year Late Jan": {"day": 26, "month": "Late Jan"},
    "Classic Year Early Feb": {"day": 27, "month": "Early Feb"},
    "Classic Year Late Feb": {"day": 28, "month": "Late Feb"},
    "Classic Year Early Mar": {"day": 29, "month": "Early Mar"},
    "Classic Year Late Mar": {"day": 30, "month": "Late Mar"},
    "Classic Year Early Apr": {"day": 31, "month": "Early Apr"},
    "Classic Year Late Apr": {"day": 32, "month": "Late Apr"},
    "Classic Year Early May": {"day": 33, "month": "Early May"},
    "Classic Year Late May": {"day": 34, "month": "Late May"},
    "Classic Year Early Jun": {"day": 35, "month": "Early Jun"},
    "Classic Year Late Jun": {"day": 36, "month": "Late Jun"},
    "Classic Year Early Jul": {"day": 37, "month": "Early Jul"},
    "Classic Year Late Jul": {"day": 38, "month": "Late Jul"},
    "Classic Year Early Aug": {"day": 39, "month": "Early Aug"},
    "Classic Year Late Aug": {"day": 40, "month": "Late Aug"},
    "Classic Year Early Sep": {"day": 41, "month": "Early Sep"},
    "Classic Year Late Sep": {"day": 42, "month": "Late Sep"},
    "Classic Year Early Oct": {"day": 43, "month": "Early Oct"},
    "Classic Year Late Oct": {"day": 44, "month": "Late Oct"},
    "Classic Year Early Nov": {"day": 45, "month": "Early Nov"},
    "Classic Year Late Nov": {"day": 46, "month": "Late Nov"},
    "Classic Year Early Dec": {"day": 47, "month": "Early Dec"},
    "Classic Year Late Dec": {"day": 48, "month": "Late Dec"},
    "Senior Year Early Jan": {"day": 49, "month": "Early Jan"},
    "Senior Year Late Jan": {"day": 50, "month": "Late Jan"},
    "Senior Year Early Feb": {"day": 51, "month": "Early Feb"},
    "Senior Year Late Feb": {"day": 52, "month": "Late Feb"},
    "Senior Year Early Mar": {"day": 53, "month": "Early Mar"},
    "Senior Year Late Mar": {"day": 54, "month": "Late Mar"},
    "Senior Year Early Apr": {"day": 55, "month": "Early Apr"},
    "Senior Year Late Apr": {"day": 56, "month": "Late Apr"},
    "Senior Year Early May": {"day": 57, "month": "Early May"},
    "Senior Year Late May": {"day": 58, "month": "Late May"},
    "Senior Year Early Jun": {"day": 59, "month": "Early Jun"},
    "Senior Year Late Jun": {"day": 60, "month": "Late Jun"},
    "Senior Year Early Jul": {"day": 61, "month": "Early Jul"},
    "Senior Year Late Jul": {"day": 62, "month": "Late Jul"},
    "Senior Year Early Aug": {"day": 63, "month": "Early Aug"},
    "Senior Year Late Aug": {"day": 64, "month": "Late Aug"},
    "Senior Year Early Sep": {"day": 65, "month": "Early Sep"},
    "Senior Year Late Sep": {"day": 66, "month": "Late Sep"},
    "Senior Year Early Oct": {"day": 67, "month": "Early Oct"},
    "Senior Year Late Oct": {"day": 68, "month": "Late Oct"},
    "Senior Year Early Nov": {"day": 69, "month": "Early Nov"},
    "Senior Year Late Nov": {"day": 70, "month": "Late Nov"},
    "Senior Year Early Dec": {"day": 71, "month": "Early Dec"},
    "Senior Year Late Dec": {"day": 72, "month": "Late Dec"}
}
