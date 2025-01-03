try:
    import supervisely
except ImportError:
    import sys

    import sly_sdk as supervisely

    sys.modules["supervisely"] = supervisely

from sly_sdk.webpy import WebPyApplication

from src.gui import layout

app = WebPyApplication(layout)
