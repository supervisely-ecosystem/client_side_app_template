from datetime import datetime
import cv2
import numpy as np
from sly_sdk.webpy import WebPyApplication
from sly_sdk.sly_logger import logger

from src.gui import layout, dilation_strength, need_processing


app = WebPyApplication(layout)

# Creating geometry version dictionary to avoid recursion.
last_geometry_version = {}


def process(mask: np.ndarray) -> np.ndarray:
    """Processing the mask.

    :param mask: Mask to process.
    :type mask: np.ndarray
    :return: Processed mask.
    :rtype: np.ndarray
    """
    # Reading the strength of the dilation operation from the UI
    # and applying it to the mask.
    dilation = cv2.dilate(mask.astype(np.uint8), None, iterations=dilation_strength.get_value())

    # Returning a new mask.
    return dilation


@app.event(app.Event.figure_geometry_saved)
def on_figure_geometry_saved(data):
    logger.info("Left mouse button released after drawing mask with brush")
    if not need_processing.is_on():
        # Checking if the processing is turned on in the UI.
        return

    # Get figure
    figure_id = data["figureId"]
    figure = app.get_figure_by_id(figure_id)

    # app.update_figure_geometry will trigger the same event, so we need to avoid infinite recursion.
    current_geom_version = figure.geometry_version
    last_geom_version = last_geometry_version.get(figure_id, None)
    last_geometry_version[figure_id] = current_geom_version + 2
    if last_geom_version is not None and last_geom_version >= current_geom_version:
        return

    # Get mask from the figure
    figure_geometry = figure.geometry
    mask = figure_geometry["data"]

    # Processing the mask. You need to implement your own logic in the process function.
    new_mask = process(mask)

    # Update the mask in the figure
    app.update_figure_geometry(figure, new_mask)
