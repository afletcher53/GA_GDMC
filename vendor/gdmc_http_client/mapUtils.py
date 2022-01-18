# ! /usr/bin/python3
"""### Provides tools for maps and heightmaps

Heavily edited version from the Github
This module contains functions to:
* Calculate a heightmap ideal for building
* Visualise numpy arrays
"""
__all__ = ["calc_good_heightmap"]
# __version__

import cv2
import matplotlib.pyplot as plt
import numpy as np
from vendor.gdmc_http_client.interfaceUtils import setBlock


def visualize(*arrays, title=None, autonormalize=True):
    """**Visualizes one or multiple numpy arrays.**

    Args:
        title (str, optional): display title. Defaults to None.
        autonormalize (bool, optional): Normalizes the array to be between 0 (black) and 255 (white). Defaults to True.
    """
    for array in arrays:
        if autonormalize:
            array = (normalize(array) * 255).astype(np.uint8)

        plt.figure()
        if title:
            plt.title(title)
        plt_image = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        imgplot = plt.imshow(plt_image)
    plt.show()


def normalize(array):
    """**Normalizes the array to contain values from 0 to 1.**"""
    return (array - array.min()) / (array.max() - array.min())


def paint_fence(worldSlice, heightmap):
    """Paints a fence around the search area"""
    area = worldSlice.rect
    for x in range(area[0], area[0] + area[2]):
        z = area[1]
        y = heightAt(x, z, heightmap=heightmap, area=area)
        setBlock(x, y - 1, z, "red_wool")
        setBlock(x, y, z, "oak_fence")

    for z in range(area[1], area[1] + area[3]):
        x = area[0]
        y = heightAt(x, z, heightmap=heightmap, area=area)
        setBlock(x, y - 1, z, "red_wool")
        setBlock(x, y, z, "oak_fence")
    for x in range(area[0], area[0] + area[2]):
        z = area[1] + area[3] - 1
        y = heightAt(x, z, heightmap=heightmap, area=area)
        setBlock(x, y - 1, z, "red_wool")
        setBlock(x, y, z, "oak_fence")
    for z in range(area[1], area[1] + area[3]):
        x = area[0] + area[2] - 1
        y = heightAt(x, z, heightmap=heightmap, area=area)
        setBlock(x, y - 1, z, "red_wool")
        setBlock(x, y, z, "oak_fence")


def heightAt(x, z, heightmap, area):
    """Access height using local coordinates."""
    # Warning:
    # Heightmap coordinates are not equal to world coordinates!
    return heightmap[(x - area[0], z - area[1])]
