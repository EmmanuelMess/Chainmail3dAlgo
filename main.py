import random
from dataclasses import dataclass
from typing import Callable

delta_movement = 0.02


@dataclass
class Vector3(object):
    x: float
    y: float
    z: float

    def __hash__(self):
        return ((self.x * 43 + self.y) * 43 + self.z) * 43


@dataclass
class Vector3i(object):
    x: int
    y: int
    z: int

    def __hash__(self):
        return ((self.x * 43 + self.y) * 43 + self.z) * 43


@dataclass
class SponsoredDeformation(object):
    sponsor_index: Vector3i
    to_deform_index: Vector3i


@dataclass
class Link(object):
    pos: Vector3
    color: list


@dataclass
class Info(object):
    neighbours: Callable[[int, Vector3i], Vector3i]
    size: Vector3i
    links: dict
    axis: list # neighbours of each link
    min_dif: Vector3
    max_dif: Vector3


def allin(end: Vector3i) -> list:
    return [Vector3i(x, y, z) for y in range(end.y) for x in range(end.x) for z in range(end.z)]


def loaddata(size: Vector3i, links: dict, min_dif: Vector3, max_dif: Vector3) -> Info:
    RIGHT, LEFT, TOP, BOTTOM = 0, 1, 2, 3

    def get_neighbours(axis: int, index: Vector3i):
        # ordered right left top bottom as in the paper
        if axis == RIGHT and index.x + 1 in range(size.x):
            return Vector3i(index.x + 1, index.y, index.z)
        if axis == LEFT and index.x - 1 in range(size.x):
            return Vector3i(index.x - 1, index.y, index.z)
        if axis == TOP and index.y - 1 in range(size.y):
            return Vector3i(index.x, index.y - 1, index.z)
        if axis == BOTTOM and index.y + 1 in range(size.y):
            return Vector3i(index.x, index.y + 1, index.z)
        return None

    return Info(get_neighbours, size, links, [RIGHT, LEFT, TOP, BOTTOM], min_dif, max_dif)


def check_and_correct(chain: Info, sponsor_index: Vector3i, to_correct_index: Vector3i) -> bool:
    was_moved = False
    sponsor = chain.links[sponsor_index]
    neighbour = chain.links[to_correct_index].pos
    dist = Vector3(abs(neighbour.x - sponsor.pos.x), abs(neighbour.y - sponsor.pos.y), abs(neighbour.z - sponsor.pos.z))
    while (dist.x != 0 and dist.x < chain.min_dif.x or dist.x > chain.max_dif.x) \
            or (dist.y != 0 and dist.y < chain.min_dif.y or dist.y > chain.max_dif.y) \
            or (dist.z != 0 and dist.z < chain.min_dif.z or dist.z > chain.max_dif.z):
        if dist.x < chain.min_dif.x and dist.x != 0:
            was_moved = True
            neighbour.x += (neighbour.x - sponsor.pos.x)/dist.x * delta_movement
        if dist.y < chain.min_dif.y and dist.y != 0:
            was_moved = True
            neighbour.y += (neighbour.y - sponsor.pos.y) / dist.y * delta_movement
        if dist.z < chain.min_dif.z and dist.z != 0:
            was_moved = True
            neighbour.z += (neighbour.z - sponsor.pos.z) / dist.z * delta_movement

        if dist.x > chain.max_dif.x:
            was_moved = True
            neighbour.x -= (neighbour.x - sponsor.pos.x)/dist.x * delta_movement
        if dist.y > chain.max_dif.y:
            was_moved = True
            neighbour.y -= (neighbour.y - sponsor.pos.y) / dist.y * delta_movement
        if dist.z > chain.max_dif.z:
            was_moved = True
            neighbour.z -= (neighbour.z - sponsor.pos.z) / dist.z * delta_movement

        dist = Vector3(abs(neighbour.x - sponsor.pos.x), abs(neighbour.y - sponsor.pos.y), abs(neighbour.z - sponsor.pos.z))

    return was_moved


def deform(chain: Info, deformation: Vector3, deformed_index: Vector3i):
    get_neighbour = chain.neighbours
    deformed: Link = chain.links[deformed_index]

    deformed.pos.x += deformation.x
    deformed.pos.y += deformation.y

    deformation_set: set = set()
    to_check_lists = {i: [] for i in chain.axis}

    for i in chain.axis:
        neighbour = get_neighbour(i, deformed_index)
        if neighbour is not None:
            to_check_lists[i].append(SponsoredDeformation(deformed_index, neighbour))

    for i in chain.axis:
        while len(to_check_lists[i]) > 0:
            sponsored_deformation = to_check_lists[i].pop(0)
            sponsor_index = sponsored_deformation.sponsor_index
            to_modif_index = sponsored_deformation.to_deform_index

            if check_and_correct(chain, sponsor_index, to_modif_index):
                deformation_set.add(to_modif_index)

                for j in chain.axis:
                    next_index = get_neighbour(j, to_modif_index)

                    if next_index is not None:
                        if not next_index in deformation_set:
                            to_check_lists[j] += [SponsoredDeformation(to_modif_index, next_index)]


def show(chain: Info):
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(15, 15))
    ax = fig.add_subplot(111)

    x = [link.pos.x for link in chain.links.values()]
    y = [link.pos.y for link in chain.links.values()]
    colors = [link.color for link in chain.links.values()]

    ax.scatter(x, y, c=colors, marker='o', s=200)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.invert_yaxis()
    plt.show(block=True)


def main():
    size = Vector3i(9, 9, 1)
    links = {vec: Link(Vector3(vec.x, vec.y, vec.z), [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)])
             for vec in allin(size)}
    min_dif = Vector3(0.2, 0.2, 0.2)
    max_dif = Vector3(1, 1, 1)
    chain = loaddata(size, links, min_dif, max_dif)

    show(chain)
    deformation = Vector3(0.75, -1.75, 0)
    deformed_index = Vector3i(1, 1, 0)
    deform(chain, deformation, deformed_index)

    show(chain)


if __name__ == '__main__':
    main()