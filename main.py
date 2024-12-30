import pygame
import numpy as np

from enum import Enum
from colorsys import hsv_to_rgb
from itertools import cycle

Point = tuple[int, int]

class SurfaceState(Enum):
    Draw = 0
    Flags = 1
    Groups = 2

    def next(self):
        states = cycle(list(SurfaceState))
        while self != next(states):
            pass
        return next(states)

def generate_group_colors(num_colors: int, saturation: float = 0.5, value: float =1.0) -> list[str]:
    hex_colors = []
    hsv_colors = [[float(x / num_colors), saturation, value] for x in range(num_colors)]

    for hsv in hsv_colors:
        hsv = [int(x * 255) for x in hsv_to_rgb(*hsv)]
        hex_colors.append(f"#{hsv[0]:02x}{hsv[1]:02x}{hsv[2]:02x}")
    return hex_colors

def distance(left: Point, right: Point) -> float:
    return np.sqrt((left[0] - right[0]) ** 2 + (left[1] - right[1]) ** 2)

def dbscan(points: list[Point], min_pts: int, eps: float) -> (list[str], list[int]):
    flag_colors = ["red" for _ in range(len(points))]

    for i, point1 in enumerate(points):
        number_pts = 0

        for point2 in points:
            if point1 != point2 and distance(point1, point2) < eps:
                number_pts += 1

        if number_pts >= min_pts:
            flag_colors[i] = "green"

    for i, point1 in enumerate(points):
        if flag_colors[i] != "green":
            for j, point2 in enumerate(points):
                if flag_colors[j] == "green" and point1 != point2 and distance(point1, point2) < eps:
                    flag_colors[i] = "yellow"
                    break

    groups = [0 for _ in range(len(points))]

    group = 0
    for i, point1 in enumerate(points):
        if flag_colors[i] == "green" and groups[i] == 0:
            group += 1
            group_neighbors(point1, points, groups, flag_colors, eps, group)

    return flag_colors, groups


def group_neighbors(point1: Point, points: list[Point], groups: list[int], flags: list[str], eps: float, group: int) -> None:
    for i, point2 in enumerate(points):
        if groups[i] == 0 and distance(point1, point2) < eps:
            groups[i] = group
            if flags[i] != "yellow":
                group_neighbors(point2, points, groups, flags, eps, group)

if __name__ == '__main__':
    surface_size = (800, 600)
    radius = 10

    min_pts = 3
    eps = 60

    points: list[Point] = []
    running = True
    surface_state = SurfaceState.Draw

    pygame.init()
    surface = pygame.display.set_mode(surface_size)
    surface.fill("white")
    pygame.display.update()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if surface_state == SurfaceState.Draw:
                    point = event.pos
                    points.append(point)

                    pygame.draw.circle(surface, color='black', center=point, radius=radius)
                    pygame.display.update()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    surface_state = surface_state.next()
                    flag_colors, groups = dbscan(points, min_pts, eps)
                    colors: list[str] = []
                    if surface_state == SurfaceState.Flags:
                        colors = flag_colors
                    elif surface_state == SurfaceState.Groups:
                        group_colors = generate_group_colors(len(groups))
                        colors = [group_colors[group] for group in groups]
                    else:
                        colors = ['black' for _ in range(len(points))]
                    for i, point in enumerate(points):
                        pygame.draw.circle(surface, color=colors[i], center=point, radius=radius)
                    pygame.display.update()
            elif event.type == pygame.QUIT:
                running = False