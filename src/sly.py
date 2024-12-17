import json
from pathlib import Path
import shutil


# SDK code
class WebPyApplication:
    def __init__(self):
        self._run_f = None
        self._widgets_n = 0
        self.is_inited = False

    def __init_state(self):
        from js import slyApp

        self._slyApp = slyApp
        app = slyApp.app
        app = getattr(app, "$children")[0]  # <- based on template
        self._state = app.state
        self._data = app.data
        self._context = app.context  # ??
        self._store = slyApp.store  # <- Labeling tool store (image, classes, objects, etc)

        self.is_inited = True

    # Labeling tool data access
    def get_current_image(self):
        cur_img = getattr(self._store.state.videos.all, str(self._context.imageId))
        img_src = cur_img.sources[0]
        img_cvs = img_src.imageData
        return img_cvs

    @property
    def state(self):
        from supervisely.app.content import StateJson

        if not self.is_inited:
            self.__init_state()
        StateJson().update(self._state)
        return StateJson()

    @property
    def data(self):
        from supervisely.app.content import DataJson

        if not self.is_inited:
            self.__init_state()
        DataJson().update(self._data)
        return DataJson()

    @classmethod
    def render(cls, layout, dir=""):
        import supervisely as sly
        from supervisely.app.content import DataJson, StateJson

        app = sly.Application(layout=layout)
        index = app.render({"__webpy_script__": True})
        # @change="post('/{{{widget.widget_id}}}/value_changed')" -> @change="runPythonScript('/{{{widget.widget_id}}}/value_changed')"
        index = index.replace("post('/", "runPythonScript('/")

        dir = Path(dir)
        with open(dir / "index.html", "w") as f:
            f.write(index)

        json.dump(StateJson(), open(dir / "state.json", "w"))
        json.dump(DataJson(), open(dir / "data.json", "w"))

        shutil.copy("sly.py", dir / "sly.py")
        shutil.copy("gui.py", dir / "gui.py")
        shutil.copy("main.py", dir / "main.py")

    def _get_handler(self, *args, **kwargs):
        if len(args) != 1:
            return None
        if not isinstance(args[0], str):
            return None
        handlers = kwargs.get("widgets_handlers", {})
        if args[0] in handlers:
            return handlers[args[0]]
        return None

    def run(self, *args, **kwargs):
        import gui
        from supervisely.app.fastapi import _MainServer
        from fastapi.routing import APIRoute

        # self.state
        # self.data  # to init StateJson and DataJson

        server = _MainServer().get_server()
        handlers = {}
        for route in server.router.routes:
            if isinstance(route, APIRoute):
                handlers[route.path] = route.endpoint

        handler = self._get_handler(*args, widgets_handlers=handlers, **kwargs)
        if handler is not None:
            return handler()
        if self._run_f is None:
            raise NotImplementedError("Run function is not defined")
        return self._run_f(*args, **kwargs)

    def run_function(self, f):
        self._run_f = f
        return f
