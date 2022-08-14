import random
from math import ceil
from typing import Dict, List


def random_hex_color() -> str:
    """
    Returns random color in HEX format 
    """
    return '#'+''.join(random.sample('0123456789ABCDEF',6))


def combine_hex_colors(colors_to_weights: Dict[str, float]) -> str:
    """
    params:
        colors_to_weights: Dictionary with colors in HEX format as keys and
        their proportions in final color as values
    returns:
        HEX combination of all colors from colors_to_weights
    """
    d_items = sorted(colors_to_weights.items())
    tot_weight = sum(colors_to_weights.values())
    red = int(sum([int(k[1:3], 16) * v for k, v in d_items]) / tot_weight)
    green = int(sum([int(k[3:5], 16) * v for k, v in d_items]) / tot_weight)
    blue = int(sum([int(k[5:7], 16) * v for k, v in d_items]) / tot_weight)
    zpad = lambda x: x if len(x) == 2 else '0' + x

    res = zpad(hex(red)[2:]) + zpad(hex(green)[2:]) + zpad(hex(blue)[2:])
    return f'#{res}'


def interpotate_between_colors(colors: List[str], points: int) -> List[str]:
    """
    params:
        colors: List of colors in HEX format to interpolate between
        points: number of points to generate
    returns:
        List of HEX colors with length "points" 
    """
    points_for_color = ceil(points / (len(colors) - 1))
    result = []
    color_number = 0
    color_weight = 0
    for _ in range(points):
        color_weight += 1

        color_proportion = color_weight * (1.0 / points_for_color)
        color = combine_hex_colors({
            colors[color_number]: 1.0 - color_proportion,
            colors[color_number+1]: color_proportion
        })
        result.append(color)
        if color_proportion >= 1:
            color_weight = 0
            color_number += 1 

    return result
