"""Maze Crawler heuristic agent."""

from random import choice
from collections import deque


NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
DIRS = (
    ("NORTH", 0, 1, NORTH),
    ("EAST", 1, 0, EAST),
    ("WEST", -1, 0, WEST),
    ("SOUTH", 0, -1, SOUTH),
)


def get_cfg(config, name, default):
    return getattr(config, name, default)


def wall_at(obs, config, col, row):
    idx = (row - obs.southBound) * config.width + col
    if 0 <= idx < len(obs.walls) and obs.walls[idx] != -1:
        return obs.walls[idx]
    return 0


def destination(col, row, move):
    for name, dc, dr, _ in DIRS:
        if name == move:
            return col + dc, row + dr
    return col, row


def parse_points(mapping):
    points = {}
    for key, value in mapping.items():
        try:
            col, row = key.split(",", 1)
            points[(int(col), int(row))] = value
        except Exception:
            pass
    return points


def unit_counts(units):
    counts = {}
    for data in units.values():
        counts[data[0]] = counts.get(data[0], 0) + 1
    return counts


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def choose_build(config, energy, counts, crystal_count, node_count):
    scouts = counts.get(1, 0)
    workers = counts.get(2, 0)
    miners = counts.get(3, 0)

    if scouts < 1 and energy >= get_cfg(config, "scoutCost", 50) + 250:
        return "BUILD_SCOUT"
    if node_count and miners < 1 and energy >= get_cfg(config, "minerCost", 300) + 200:
        return "BUILD_MINER"
    if scouts < 2 and energy >= get_cfg(config, "scoutCost", 50) + 300:
        return "BUILD_SCOUT"
    if workers < 1 and energy >= get_cfg(config, "workerCost", 200) + 300:
        return "BUILD_WORKER"
    if node_count and miners < 2 and energy >= get_cfg(config, "minerCost", 300) + 450:
        return "BUILD_MINER"
    if crystal_count and scouts < 4 and energy >= get_cfg(config, "scoutCost", 50) + 250:
        return "BUILD_SCOUT"
    if workers < 2 and energy >= get_cfg(config, "workerCost", 200) + 450:
        return "BUILD_WORKER"
    return None


def choose_target(rtype, col, row, crystals, mining_nodes):
    pos = (col, row)
    if rtype == 3 and mining_nodes:
        return min(mining_nodes, key=lambda p: distance(pos, p))
    if crystals:
        return max(crystals, key=lambda p: crystals[p] - 3 * distance(pos, p) + p[1])
    if rtype in (1, 3) and mining_nodes:
        return min(mining_nodes, key=lambda p: distance(pos, p))
    return col, row + 8


def choose_move(obs, config, col, row, target, occupied, reserved, enemies):
    planned = bfs_first_move(obs, config, col, row, target, occupied, reserved, enemies)
    if planned:
        return planned

    options = []
    current_wall = wall_at(obs, config, col, row)
    for move, dc, dr, bit in DIRS:
        if current_wall & bit:
            continue
        ncol, nrow = col + dc, row + dr
        if not (0 <= ncol < config.width):
            continue
        if not (obs.southBound <= nrow <= obs.northBound):
            continue

        dest = (ncol, nrow)
        score = -distance(dest, target)
        if move == "NORTH":
            score += 3
        if nrow <= obs.southBound + 1:
            score -= 25
        if dest in occupied or dest in reserved:
            score -= 100
        if dest in enemies:
            score -= 20
        options.append((score, move))

    if not options:
        return "IDLE"
    options.sort(reverse=True)
    best_score = options[0][0]
    best = [move for score, move in options if score == best_score]
    return choice(best)


def bfs_first_move(obs, config, col, row, target, occupied, reserved, enemies):
    start = (col, row)
    if start == target:
        return None

    queue = deque([(start, None)])
    seen = {start}
    best = None
    best_dist = distance(start, target)

    while queue and len(seen) < 160:
        (ccol, crow), first = queue.popleft()
        current_dist = distance((ccol, crow), target)
        if current_dist < best_dist:
            best_dist = current_dist
            best = first
        if (ccol, crow) == target:
            return first

        current_wall = wall_at(obs, config, ccol, crow)
        for move, dc, dr, bit in DIRS:
            if current_wall & bit:
                continue
            ncol, nrow = ccol + dc, crow + dr
            nxt = (ncol, nrow)
            if nxt in seen:
                continue
            if not (0 <= ncol < config.width):
                continue
            if not (obs.southBound <= nrow <= obs.northBound):
                continue
            if nrow <= obs.southBound + 1:
                continue
            if nxt in enemies:
                continue
            if nxt != target and (nxt in occupied or nxt in reserved):
                continue
            seen.add(nxt)
            queue.append((nxt, first or move))

    return best


def safe_jump(obs, config, col, row, reserved, enemies):
    choices = []
    for move, dc, dr, _ in DIRS:
        ncol, nrow = col + 2 * dc, row + 2 * dr
        if not (0 <= ncol < config.width):
            continue
        if not (obs.southBound <= nrow <= obs.northBound):
            continue

        landing_wall = wall_at(obs, config, ncol, nrow)
        dest = (ncol, nrow)
        score = 0
        if move == "NORTH":
            score += 50
        elif move in ("EAST", "WEST"):
            score += 5
        else:
            score -= 80
        score += 4 * (nrow - obs.southBound)
        if landing_wall == 15:
            score -= 200
        if landing_wall & NORTH:
            score -= 20
        if dest in reserved:
            score -= 100
        if dest in enemies:
            score -= 40
        choices.append((score, move))

    if not choices:
        return None
    choices.sort(reverse=True)
    if choices[0][0] < -50:
        return None
    return "JUMP_" + choices[0][1]


def factory_move(obs, config, col, row, occupied, reserved, enemies):
    options = []
    current_wall = wall_at(obs, config, col, row)
    for move, dc, dr, bit in DIRS:
        if move == "SOUTH":
            continue
        if current_wall & bit:
            continue
        ncol, nrow = col + dc, row + dr
        if not (0 <= ncol < config.width):
            continue
        if not (obs.southBound <= nrow <= obs.northBound):
            continue
        dest = (ncol, nrow)
        score = 5 * (nrow - obs.southBound)
        if move == "NORTH":
            score += 30
        if nrow <= obs.southBound + 2:
            score -= 50
        if dest in occupied or dest in reserved:
            score -= 100
        if dest in enemies:
            score -= 40
        options.append((score, move))

    if not options:
        return "IDLE"
    options.sort(reverse=True)
    return options[0][1]


def factory_escape(obs, config, col, row, enemies):
    current_wall = wall_at(obs, config, col, row)
    urgent = []
    for move, dc, dr, bit in DIRS:
        if move == "SOUTH":
            continue
        if current_wall & bit:
            continue
        ncol, nrow = col + dc, row + dr
        if not (0 <= ncol < config.width):
            continue
        if not (obs.southBound <= nrow <= obs.northBound):
            continue
        score = 10 * (nrow - obs.southBound)
        if move == "NORTH":
            score += 100
        if (ncol, nrow) in enemies:
            score -= 40
        urgent.append((score, move))
    if not urgent:
        return "IDLE"
    urgent.sort(reverse=True)
    return urgent[0][1]


def agent(obs, config):
    actions = {}
    my_units = {
        uid: data for uid, data in obs.robots.items()
        if data[4] == obs.player
    }
    enemies = {
        (data[1], data[2]) for data in obs.robots.values()
        if data[4] != obs.player
    }
    occupied = {(data[1], data[2]): uid for uid, data in my_units.items()}
    reserved = set()
    crystals = parse_points(obs.crystals)
    mining_nodes = parse_points(obs.miningNodes)

    factories = []
    mobiles = []
    for uid, data in my_units.items():
        if data[0] == 0:
            factories.append((uid, data))
        else:
            mobiles.append((uid, data))

    mobiles.sort(key=lambda item: (-item[1][2], item[1][0], item[0]))

    for uid, data in mobiles:
        rtype, col, row, energy = data[0], data[1], data[2], data[3]
        if energy <= 1:
            actions[uid] = "IDLE"
            reserved.add((col, row))
            continue

        if rtype == 3 and (col, row) in mining_nodes and energy >= get_cfg(config, "transformCost", 100) + 5:
            actions[uid] = "TRANSFORM"
            reserved.add((col, row))
            continue

        current_wall = wall_at(obs, config, col, row)
        if rtype == 2 and (current_wall & NORTH) and energy >= get_cfg(config, "wallRemoveCost", 100) + 120:
            actions[uid] = "REMOVE_NORTH"
            reserved.add((col, row))
            continue

        target = choose_target(rtype, col, row, crystals, mining_nodes)
        move = choose_move(obs, config, col, row, target, occupied, reserved, enemies)
        actions[uid] = move
        reserved.add(destination(col, row, move))

    for uid, data in factories:
        col, row, energy = data[1], data[2], data[3]
        jump_cd = data[6] if len(data) > 6 else 0
        build_cd = data[7] if len(data) > 7 else 0
        current_wall = wall_at(obs, config, col, row)
        north_cell = (col, row + 1)
        counts = unit_counts(my_units)

        if row <= obs.southBound + 1 and jump_cd == 0:
            actions[uid] = safe_jump(obs, config, col, row, reserved, enemies) or factory_escape(obs, config, col, row, enemies)
        elif row <= obs.southBound + 1:
            actions[uid] = factory_escape(obs, config, col, row, enemies)
        elif row <= obs.southBound + 3 and jump_cd == 0:
            actions[uid] = safe_jump(obs, config, col, row, reserved, enemies) or factory_move(obs, config, col, row, occupied, reserved, enemies)
        elif north_cell in occupied or north_cell in reserved:
            actions[uid] = "IDLE"
        elif build_cd == 0 and not (current_wall & NORTH):
            build = choose_build(config, energy, counts, len(crystals), len(mining_nodes))
            actions[uid] = build if build else factory_move(obs, config, col, row, occupied, reserved, enemies)
        elif current_wall & NORTH and jump_cd == 0:
            actions[uid] = safe_jump(obs, config, col, row, reserved, enemies) or "IDLE"
        else:
            actions[uid] = factory_move(obs, config, col, row, occupied, reserved, enemies)

    return actions
