import json
from pathlib import Path

import supervisely as sly


# SDK code
class WebPyApplication:
    def __init__(self):
        # webpy imports
        from js import slyApp

        self._slyApp = slyApp
        app = slyApp.app
        app = getattr(app, "$children")[0]  # <- based on template
        self._state = app.state
        self._data = app.data
        self._handlers = {}  # <- widget_id: handler
        # self._context = app.context # ??
        # self._store = slyApp.store # ?? <- Labeling tool store (image, classes, objects, etc)

        self._run_f = None
        self._widgets_n = 0

    def generate_widget_id(self):
        self._widgets_n += 1
        return "widget_" + str(self._widgets_n)

    def add_handler(self, widget_handler):
        def inner(f):
            # This is a decorator, needed to add handler in the widget template
            decorated_f = widget_handler(f)

            widget: sly.app.widgets.Widget = widget_handler.__self__
            widget.widget_id = self.generate_widget_id()

            def wrapper(*args, **kwargs):
                return decorated_f(*args, **kwargs)

            return wrapper

        return inner

    def _replace_handlers_in_template(self, template: str):
        # @change="post('/{{{widget.widget_id}}}/value_changed')" -> @change="runPythonScript('/{{{widget.widget_id}}}/value_changed')"
        template = template.replace("post('/", "runPythonScript('/")
        return template

    def _register_handlers(self, app: sly.Application):
        server = app.get_server()
        for route in server.router.routes:
            self._handlers[route.endpoint] = route.handler

    def render(self, layout, dir=""):
        from supervisely.app.content import DataJson, StateJson

        app = sly.Application(layout=layout)
        index = app.render({"__webpy_script__": True})
        index = self._replace_handlers_in_template(index)  # ???

        dir = Path(dir)
        with open(dir / "index.html", "w") as f:
            f.write(index)

        json.dump(StateJson(), open(dir / "state.json", "w"))
        json.dump(DataJson(), open(dir / "data.json", "w"))

    def _get_callback(self, *args, **kwargs):
        if len(args) != 1:
            return None
        if not isinstance(args[0], str):
            return None
        if args[0] in self._handlers:
            return self._handlers[args[0]]
        return None

    def run(self, *args, **kwargs):
        callback = self._get_callback(*args, **kwargs)
        if callback is not None:
            return callback()
        if self._run_f is None:
            raise NotImplementedError("Run function is not defined")
        return self._run_f(*args, **kwargs)

    def run_function(self):
        def wrapper(f):
            self._run_f = f
            return f

        return wrapper
