import json

MAP_FILE = "ExpertPlusStandard.dat.bak"
OUTPUT = "ExpertPlusStandard.dat"
HALF_JUMP_DURATION = 2.01
NJS = 24
JD = 35.08

MULTIPLIER_FASTER_WALL_NJS = 8
MULTIPLIER_HYPER_WALL_NJS = 16
MULTIPLIER_HYPER_WALL_DURATION = 0.1

KEY_CUSTOM_DATA = "_customData"
KEY_LINE_INDEX = "_lineIndex"
KEY_TIME = "_time"
KEY_WALL_WIDTH = "_width"
KEY_WALL_TYPE = "_type"
KEY_WALL_DURATION = "_duration"
KEY_CUSTOM_POSITION = "_position"
KEY_CUSTOM_SCALE = "_scale"
KEY_CUSTOM_INTERACTABLE = "_interactable"
KEY_CUSTOM_NJS = "_noteJumpMovementSpeed"

with open(MAP_FILE) as map_file:
    map_dict = json.load(map_file)

print(map_dict.keys())

events = map_dict["_events"]
notes = map_dict["_notes"]
walls = map_dict["_obstacles"]


def asserts(a, b, s=""):
    if a != b:
        raise AssertionError(f"{s} - Got {a} and {b}")


def convert_line_index(index: int) -> (bool, float):
    if -1000 < index < 1000:
        return 0 <= index <= 3, index

    if index < 0:
        index += 1000
    if index > 0:
        index -= 1000

    return False, index / 1000


def convert_wall_width(width: int) -> (bool, float):
    if width < 1000:
        return width <= 4, width

    return False, (width - 1000) / 1000


def convert_wall_type(t: int) -> (bool, float, float):
    """Returns (isBaseGame, WallStartLayer, WallHeight)"""
    assert t >= 0
    if t == 1 or t == 0:
        return True, t, (3 - t)

    assert t >= 1000

    if 1000 <= t <= 4000:
        height = t * 3 / 1000 - 3
        return False, 0, height

    t -= 4001
    height = t // 1000
    layer = t % 1000

    height = height * 3 / 1000
    layer = layer / 250

    return False, layer, height


def get_custom_data(obj, key):
    if KEY_CUSTOM_DATA not in obj:
        return None
    custom_data = obj[KEY_CUSTOM_DATA]
    if key not in custom_data:
        return None
    return custom_data[key]


def set_custom_data(obj, key, value):
    if KEY_CUSTOM_DATA not in obj:
        obj[KEY_CUSTOM_DATA] = dict()
    obj[KEY_CUSTOM_DATA][key] = value


def convert_wall(wall):
    li = wall[KEY_LINE_INDEX]
    wid = wall[KEY_WALL_WIDTH]
    t = wall[KEY_WALL_TYPE]
    is1, line_index = convert_line_index(li)
    is2, width = convert_wall_width(wid)
    is3, layer, height = convert_wall_type(t)
    is_base_game = is1 and is2 and is3
    if is_base_game:
        return
    x = line_index - 2
    y = layer

    _position = get_custom_data(wall, KEY_CUSTOM_POSITION)
    if _position is None:
        set_custom_data(wall, KEY_CUSTOM_POSITION, [x, y])
    # else:  # the existing NE position looks more correct than ME
    #     # check existing
    #     if abs(x - _position[0]) > 0.01 or abs(y - _position[1]) > 0.01:
    #         # print([x, y], _position)
    #         # set_custom_data(wall, KEY_CUSTOM_POSITION, [x, y])
    #         if (x != 0 and _position[0] == 0) or (y != 0 and _position[1] == 0):
    #             print([x, y], _position)

    _scale = get_custom_data(wall, KEY_CUSTOM_SCALE)
    if _scale is None:
        set_custom_data(wall, KEY_CUSTOM_SCALE, [width, height])
    # else:  # the existing NE scale (all squares?) looks more correct than ME
    #     # check existing
    #     # if len(_scale) != 2:  # looks like all the scale have only width and height, no length
    #     #     print(_scale)
    #     if abs(_scale[0] - width) > 0.01 or abs(_scale[1] - height) > 0.01:
    #         # print([width, height], _scale)
    #         if (width != 0 and _scale[0] == 0) or (height != 0 and _scale[1] == 0):  # check 0 scales
    #             print([width, height], _scale)

    # if _scale is None and _position is None:
    #     print(wall)

    wall[KEY_WALL_WIDTH] = 1
    wall[KEY_WALL_TYPE] = 0
    wall[KEY_LINE_INDEX] = 0

    duration = wall[KEY_WALL_DURATION]
    is_fake = duration < 0 or wid < 0

    if is_fake:
        set_custom_data(wall, KEY_CUSTOM_INTERACTABLE, False)

    if duration < 0:
        wall[KEY_WALL_DURATION] = abs(duration)
        wall[KEY_TIME] = wall[KEY_TIME] - HALF_JUMP_DURATION

        if abs(duration) < HALF_JUMP_DURATION:
            njs = NJS * MULTIPLIER_HYPER_WALL_NJS
        else:
            njs = NJS * MULTIPLIER_FASTER_WALL_NJS
        set_custom_data(wall, KEY_CUSTOM_NJS, njs)

        scale = get_custom_data(wall, KEY_CUSTOM_SCALE)
        if len(scale) == 2:
            set_custom_data(wall, KEY_CUSTOM_SCALE, [scale[0], scale[1], JD])


def convert_walls():
    # walls.sort(key=lambda w: w["_time"])
    for wall in walls:
        convert_wall(wall)


def things():
    for event in events:
        if KEY_CUSTOM_DATA in event:
            print(event)

    for note in notes:
        if KEY_CUSTOM_DATA in note:
            print(note)

    for wall in walls:
        if KEY_CUSTOM_DATA in wall:
            print(wall)


def tests():
    asserts(convert_line_index(0), (True, 0))
    asserts(convert_line_index(4), (False, 4))
    asserts(convert_line_index(1000), (False, 0))
    asserts(convert_line_index(-1000), (False, 0))
    asserts(convert_line_index(2000), (False, 1))
    asserts(convert_line_index(-2000), (False, -1))
    asserts(convert_line_index(2324), (False, 1.324))
    asserts(convert_line_index(-2864), (False, -1.864))
    asserts(convert_wall_type(0), (True, 0, 3))
    asserts(convert_wall_type(1), (True, 1, 2))
    asserts(convert_wall_type(1000), (False, 0, 0))
    asserts(convert_wall_type(2000), (False, 0, 3))
    asserts(convert_wall_type(1500), (False, 0, 1.5))

    asserts(convert_wall_type(4001), (False, 0, 0))
    asserts(convert_wall_type(1004001), (False, 0, 3))
    asserts(convert_wall_type(504001), (False, 0, 1.5))
    asserts(convert_wall_type(504251), (False, 1, 1.5))
    asserts(convert_wall_type(504501), (False, 2, 1.5))
    asserts(convert_wall_type(504751), (False, 3, 1.5))


if __name__ == '__main__':
    pass
    # things()
    tests()

    convert_walls()
    with open(OUTPUT, 'w') as out_file:
        json.dump(map_dict, out_file)
