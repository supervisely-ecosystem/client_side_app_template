try:
    import supervisely
except ImportError:
    import sys

    import sly_sdk as supervisely

    sys.modules["supervisely"] = supervisely

from sly_sdk.webpy import WebPyApplication

from src.gui import layout

app = WebPyApplication(layout)


@app.event(app.Event.figure_geometry_saved)
def on_figure_geometry_saved(data):
    print("Figure geometry saved:", data)
