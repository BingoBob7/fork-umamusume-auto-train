import core.state as state
from core.state import check_current_year, stat_state, check_energy_level, check_aptitudes, check_career_day
from utils.log import info, warning, error, debug
import utils.constants as constants

# Get priority stat from config
def get_stat_priority(stat_key: str) -> int:
  return state.PRIORITY_STAT.index(stat_key) if stat_key in state.PRIORITY_STAT else 999

def check_all_elements_are_same(d):
    sections = list(d.values())
    return all(section == sections[0] for section in sections[1:])

# Will do train with the most support card
# Used in the first year (aim for rainbow)
def most_support_card(results):
  # Seperate wit
  wit_data = results.get("wit")

  # Get all training but wit
  non_wit_results = {
    k: v for k, v in results.items()
    if k != "wit" and int(v["failure"]) <= state.MAX_FAILURE
  }

  # Check if train is bad
  all_others_bad = len(non_wit_results) == 0
  energy_level, max_energy = check_energy_level()
  if energy_level < state.SKIP_TRAINING_ENERGY:
    info("All trainings are unsafe and WIT training won't help go back up to safe levels, resting instead.")
    return None

  if all_others_bad and wit_data and int(wit_data["failure"]) <= state.MAX_FAILURE and wit_data["total_supports"] >= 2:
    info("All trainings are unsafe, but WIT is safe and has enough support cards.")
    return "wit"

  filtered_results ={}
  wit_failure = results.get("wit", {}).get("failure", 100)
  if int(wit_failure) > state.MAX_FAILURE:
    debug("WIT training failure too high, skip training.")
    return None
  else:
    max_failure_stat = max(int(data.get("failure", 0)) for stat, data in results.items() if stat != "wit")
    if max_failure_stat > state.MAX_FAILURE:
      debug("Some trainings have failure too high, only considering WIT training.")
      filtered_results = {
        "wit": results["wit"]
      }
    else:
      filtered_results = results
  if not filtered_results:
      debug("No trainings under MAX_FAILURE.")
      return None
  # if the only filtered result is wit, and it has less than 2 support card, return None
  if len(filtered_results) == 1 and "wit" in filtered_results and filtered_results["wit"]["total_supports"] < 2:
      debug("Only WIT training available with insufficient support.")
      return None

  if not filtered_results:
    info("No safe training found. All failure chances are too high.")
    return None

  # this is the weight adder used for skewing results of training decisions PRIORITY_EFFECTS_LIST[get_stat_priority(x[0])] * PRIORITY_WEIGHTS_LIST[priority_weight]
  # Best training
  best_training = max(filtered_results.items(), key=training_score)

  best_key, best_data = best_training

  if best_data["total_supports"] <= 1:
    if int(best_data["failure"]) == 0:
      # WIT must be at least 2 support cards
      if best_key == "wit":
        if energy_level > state.NEVER_REST_ENERGY:
          info(f"Only 1 support and it's WIT but energy is too high for resting to be worth it. Still training.")
          return "wit"
        else:
          info(f"Only 1 support and it's WIT. Skipping.")
          return None
      info(f"Only 1 support but 0% failure. Prioritizing based on priority list: {best_key.upper()}")
      return best_key
    else:
      if energy_level > state.NEVER_REST_ENERGY:
        info(f"Energy is over {state.NEVER_REST_ENERGY}, train anyway.")
        return best_key
      else:
        info("Low value training (only 1 support). Choosing to rest.")
        return None

  info(f"Best training: {best_key.upper()} with {best_data['total_supports']} support cards and {best_data['failure']}% fail chance")
  return best_key

PRIORITY_WEIGHTS_LIST={
  "HEAVY": 0.75,
  "MEDIUM": 0.5,
  "LIGHT": 0.25,
  "NONE": 0
}

def training_score(x):
  global PRIORITY_WEIGHTS_LIST
  priority_weight = PRIORITY_WEIGHTS_LIST[state.PRIORITY_WEIGHT]
  base = x[1]["total_supports"]
  + x[1]["trainer"]
  if x[1]["total_hints"] > 0:
      base += 0.5
  multiplier = 1 + state.PRIORITY_EFFECTS_LIST[get_stat_priority(x[0])] * priority_weight
  total = base * multiplier

  # Debug output
  debug(f"{x[0]} -> base={base}, multiplier={multiplier}, total={total}, priority={get_stat_priority(x[0])}")

  return (total, -get_stat_priority(x[0]))

def focus_max_friendships(results):
  # Make filter based on failure rate. Return all training, or wit, or none.
  # First, check if wit is greater than MAX_FAILURE. If so, return none. if not, go to second step.
  # Second, getting the max failure from all stats. if it's grater than MAX_FAILURE, return wit. if not, safe to return all stats.
  filtered_results ={}
  wit_failure = results.get("wit", {}).get("failure", 100)
  if int(wit_failure) > state.MAX_FAILURE:
    debug("WIT training failure too high, skip training.")
    return None, 0
  else:
    max_failure_stat = max(int(data.get("failure", 0)) for stat, data in results.items() if stat != "wit")
    if max_failure_stat > state.MAX_FAILURE:
      debug("Some trainings have failure too high, only considering WIT training.")
      filtered_results = {
        "wit": results["wit"]
      }
    else:
      filtered_results = results

  # filtered_results = {
  #     stat: data for stat, data in results.items()
  #     if int(data["failure"]) <= state.MAX_FAILURE
  # }

  if not filtered_results:
      debug("No trainings under MAX_FAILURE.")
      return None, 0
  
  # if the only filtered result is wit, and it has less than 2 support card, return None
  if len(filtered_results) == 1 and "wit" in filtered_results and filtered_results["wit"]["total_supports"] < 2:
      debug("Only WIT training available with insufficient support.")
      return None, 0

  for stat_name in filtered_results:
    data = filtered_results[stat_name]
    # order of importance gray > blue > green, because getting greens to max is easier than blues (gray is very low blue)
    possible_friendship = (
                            data["total_friendship_levels"]["green"]
                            # + data["total_friendship_levels"]["blue"] * 1.01
                            + data["total_friendship_levels"]["blue"]
                            + data["total_friendship_levels"]["gray"] * 1.02
                          )

    # hints are worth a little more than half a training
    if data["total_hints"] > 0:
      # hint_values = { "gray": 0.612, "blue": 0.606, "green": 0.6 }
      hint_values = { "gray": 0.02, "blue": 0.01, "green": 0.01 }
      for level, bonus in hint_values.items():
        if data["hints_per_friend_level"].get(level, 0) > 0:
            possible_friendship += bonus
            break

    debug(f"{stat_name} : gray={data['total_friendship_levels']['gray']}, blue={data['total_friendship_levels']['blue']}, green={data['total_friendship_levels']['green']}, total={possible_friendship:.3f}")
    filtered_results[stat_name]["possible_friendship"] = possible_friendship

  best_key = max(filtered_results, key=lambda k: (filtered_results[k]["possible_friendship"], -get_stat_priority(k)))
  best_score = filtered_results[best_key]["possible_friendship"]
  return best_key, best_score

# Do rainbow training
def rainbow_training(results):
  # filter out failure first
  filtered_results ={}
  wit_failure = results.get("wit", {}).get("failure", 100)
  if int(wit_failure) > state.MAX_FAILURE:
    debug("WIT training failure too high, skip training.")
    return None
  else:
    max_failure_stat = max(int(data.get("failure", 0)) for stat, data in results.items() if stat != "wit")
    if max_failure_stat > state.MAX_FAILURE:
      debug("Some trainings have failure too high, only considering WIT training.")
      filtered_results = {
        "wit": results["wit"]
      }
    else:
      filtered_results = results
  if not filtered_results:
      debug("No trainings under MAX_FAILURE.")
      return None
  # if the only filtered result is wit, and it has less than 2 support card, return None
  if len(filtered_results) == 1 and "wit" in filtered_results and filtered_results["wit"]["total_supports"] < 2:
      debug("Only WIT training available with insufficient support.")
      return None

  global PRIORITY_WEIGHTS_LIST
  priority_weight = PRIORITY_WEIGHTS_LIST[state.PRIORITY_WEIGHT]
  # 2 points for rainbow supports, 1 point for normal supports, stat priority tie breaker
  rainbow_candidates = filtered_results
  for stat_name in rainbow_candidates:
    multiplier = 1 + state.PRIORITY_EFFECTS_LIST[get_stat_priority(stat_name)] * priority_weight
    data = rainbow_candidates[stat_name]
    total_rainbow_friends = data[stat_name]["friendship_levels"]["yellow"] + data[stat_name]["friendship_levels"]["max"]
    #adding total rainbow friends on top of total supports for two times value nudging the formula towards more rainbows
    rainbow_points = total_rainbow_friends + data["total_supports"]
    if total_rainbow_friends > 0:
      rainbow_points = rainbow_points + 0.5
    rainbow_points = rainbow_points * multiplier
    rainbow_candidates[stat_name]["rainbow_points"] = rainbow_points
    rainbow_candidates[stat_name]["total_rainbow_friends"] = total_rainbow_friends

  # # Get rainbow training
  # rainbow_candidates = {
  #   stat: data for stat, data in results.items()
  #   if int(data["failure"]) <= state.MAX_FAILURE
  #      and data["rainbow_points"] >= 2
  #      and not (stat == "wit" and data["total_rainbow_friends"] < 1)
  # }

  if not rainbow_candidates:
    info("No rainbow training found under failure threshold.")
    return None

  # Find support card rainbow in training
  best_rainbow = max(
    rainbow_candidates.items(),
    key=lambda x: (
      x[1]["rainbow_points"],
      -get_stat_priority(x[0])
    )
  )

  best_key, best_data = best_rainbow
  # if best_key == "wit":
  #   #if we get to wit, we must have at least 1 rainbow friend
  #   if data["total_rainbow_friends"] < 1:
  #     info(f"Wit training has most rainbow points but it doesn't have any rainbow friends, skipping.")
  #     return None

  info(f"Rainbow training selected: {best_key.upper()} with {best_data['rainbow_points']} rainbow points and {best_data['failure']}% fail chance")
  return best_key

def filter_by_stat_caps(results, current_stats):
  return {
    stat: data for stat, data in results.items()
    if current_stats.get(stat, 0) < state.STAT_CAPS.get(stat, 1200)
  }

def all_values_equal(dictionary):
    values = list(dictionary.values())
    return all(value == values[0] for value in values[1:])

# Decide training
def do_something(results):
  year = check_current_year()
  current_stats = stat_state()
  day = check_career_day()
  info(f"Current stats: {current_stats}")

  if day > 24:
    state.MAX_FAILURE = 20

  filtered = filter_by_stat_caps(results, current_stats)

  if not filtered:
    info("All stats capped or no valid training.")
    return None

  # if "Junior Year" in year:
  if day <= 36:
    result, best_score = focus_max_friendships(filtered)

    # # If the best option for raising friendship is just one friend, with no hint bonus
    # if best_score <= 1.3:
    #   return most_support_card(filtered)

  else:
    result = rainbow_training(filtered)
    if result is None:
      info("Falling back to most_support_card because rainbow not available.")
      return most_support_card(filtered)
  return result

# Defining Training Strategies
def evaluate_training_strategy(strategy_data):
  """
  screen = string
  energy_level = int
  max_energy = int
  infirmary = bool
  mood = string
  turn = string
  year = string
  day = int
  criteria = string
  year_parts = list
  prioritize_g1 = bool
  race_name = string
  results_training = dict
    key: {
      trainer: int,
      total_supports: int,
      total_hints: int,
      total_friendship_levels: {
        gray: int,
        blue: int,
        green: int,
        yellow: int,
        max: int,
        },
      hints_per_friend_level: {
        gray: int,
        blue: int,
        green: int,
        yellow: int,
        max: int,
        },
      support types: {
        supports: int,
        hints: int,
        friendship_levels: {
          gray: int,
          blue: int,
          green: int,
          yellow: int,
          max: int
        }
      }
    }
  """
# Break strategies into time periods
  # Junior Year Pre-Debut: <= day 12
  # Junior Year Post Debut: <= day 24
  # Classic Year Pre Summer: <= day 36
  # Classic Year Summer: * if there are still non maxed supports, ignore them. day after summer is 41
  # Classic Year Post Summer: <= day 48
  # Senior Year Pre Summer: <= day 60
  # Senior Year Post Summer: <= day 68
  # Last 4 days: <= day 72
  # Final season: > day 72

# determine stat to train
  # Count Support Cards
  # Count Support Points (tie breaker)
  # Stat priority (tie breaker)

# Count Cards
  # non-max
    # Junior Year Pre-Debut: non-max = 1, gray = 2.
    # Classic Year Summer: non-max = 3
  # maxed
    # Junior Year Pre-Debut: maxed = 0
    # Classic Year Summer: maxed = 1
  # Trainers
    # Classic Year Post Summer: trainer = 1

# Count Points
  # Hints
    # Junior Year Pre-Debut: hint = 1
  # Trainers
    # Junior Year Pre-Debut: trainer = 1
  # Rainbows
    # Junior Year Post Debut: rainbow = 1
    # Classic Year Pre Summer: rainbow = 2, 
      # 1st priority stat rainbows: 1 = 1, 2 = 3, 3 = 5
      # Other priority stat rainbows: 1 = 2, 2 = 4, 3 = 6.

# Stat Priority 
  # Order: Wit > 2nd number of support card types > 3rd number of support card types > 1st number of support card types
    # Wit, Power, Stamina, Speed.

# Stat priorities. 
  # You should have 3 priority stats. Speed, Stamina, Power. And determine the order of their priority. Should be based on the number of that support card stat type.
  # There is already a specifc optimized number for guts you should have, and it's based on track lenght.
    # Sprint: 210
    # Mile: 260
    # Medium: 320
    # Long: 380 - 440
  # The goal for wit should always be 400 at the end of the career.

# Junior Year Pre-Debut
  # Max failure = 12%
  # Wit is least priority. Only train it once or twice, and only if it has 3+ support cards.
  # Guts is second least priority. Only train guts once or twice, and only if it has 3+ support cards.
  # You want to focus speed, stamina, power.
  # The two main purposes of this is to level up training facilities. You should get one facility to level up before the race. Second, is so you can pass the first race.
    
# Never do Extra Training

# Junior Year Post Debut
  # The goal is to get all support cards maxed out before summer.
  # Wit is now you top priority. This may be the only time you can focus on it.
  # When you have enough energy to train, train the stat with the most support card points. 
  # Tie goes to the most support cards. So a 1 gray vs 2 green would go to the 2 green.
    # If still tied, go to priority stat.
    # Count gray as 2x support cards.
    # Count gray trainers as .5x support cards. Don't count trainers if they go above gray.
    # Count 1 rainbow as .5x support cards. 2 rainbows are 1.5x support cards. 3 = 3.5x support cards.
    # Count hints as 2.5x support cards. We want to focus hints more during this time frame. we will ignore them later.
    # Top two priority stats get +0.5x support cards. Wit gets +1x support cards.
  # When at 50 energy, Only train if you can get 3 support cards points.
    # Use wit if it has 2 support cards.
  # When non wit stats have failure chance over the max, Rest.
    # Only use wit if it has 2.5 support card points. and it's failure chance is under the max.

# Classic Year Pre Summer

# Classic Year Post Summer
  # Do some G1 races
  # Focus wit again. If it has 2+ support cards.

  filtered = filter_by_stat_caps(strategy_data["results_training"], stat_state())

  if not filtered:
    info("All stats capped or no valid training.")
    return None

  if strategy_data["day"] <= 12:
    if not filtered:
      info("All Stats are at cap.")
      return None

    # Determine the stats with the most non-max support cards, return multiple if tied.
    best_training = max(
      filtered.items(),
      key=lambda x: (
        x[1]["total_supports"]
        + x[1]["friendship_levels"].get("gray", 0)
      )
    )

    # if there are more than one best_training, add points from hints and trainers to break the tie.
    if isinstance(best_training, list):
      best_training = max(
        best_training,
        key=lambda x: (
          x[1]["total_hints"]
          + x[1]["trainer"]
        )
      )



    best_key, best_data = best_training

    info(f"Selected training: {best_key.upper()} with {best_data['total_supports']} support cards, {best_data['total_hints']} hints, {best_data['friendship_levels'].get('yellow', 0)} rainbow friends, {best_data['friendship_levels'].get('max', 0)} max friends, and {best_data['failure']}% fail chance")
    return best_key

# helper functions
def decide_race_for_goal(year, turn, criteria, keywords):
  no_race = False, None
  # Check if goals is not met criteria AND it is not Pre-Debut AND turn is less than 10 AND Goal is already achieved
  if year == "Junior Year Pre-Debut":
    return no_race
  if turn >= 10:
    return no_race
  criteria_text = criteria or ""
  if any(word in criteria_text for word in keywords):
    info("Criteria word found. Trying to find races.")
    if "Progress" in criteria_text:
      info("Word \"Progress\" is in criteria text.")
      # check specialized goal
      if "G1" in criteria_text or "GI" in criteria_text:
        info("Word \"G1\" is in criteria text.")
        race_list = constants.RACE_LOOKUP.get(year, [])
        if not race_list:
          return False, None
        else:
          best_race = filter_races_by_aptitude(race_list, state.APTITUDES)
          return True, best_race["name"]
      else:
        return False, "any"
    else:
      # if there's no specialized goal, just do any race
      return False, "any"
  return no_race

def filter_races_by_aptitude(race_list, aptitudes):
  GRADE_SCORE = {"a": 2, "b": 1}

  results = []
  for race in race_list:
    surface_key = f"surface_{race['terrain'].lower()}"
    distance_key = f"distance_{race['distance']['type'].lower()}"

    s = GRADE_SCORE.get(aptitudes.get(surface_key, ""), 0)
    d = GRADE_SCORE.get(aptitudes.get(distance_key, ""), 0)

    if s and d:  # both nonzero (A or B)
      score = s + d
      results.append((score, race["fans"]["gained"], race))

  if not results:
    return None

  # sort best → worst by score, then fans
  results.sort(key=lambda x: (x[0], x[1]), reverse=True)
  return results[0][2]
