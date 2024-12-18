import enum
from fastapi import FastAPI


def get_or_create_event_loop():
    """
    Get the current event loop or create a new one if it doesn't exist.
    Works for different Python versions and contexts.

    :return: Event loop
    :rtype: asyncio.AbstractEventLoop
    """
    import asyncio

    try:
        # Preferred method for asynchronous context (Python 3.7+)
        return asyncio.get_running_loop()
    except RuntimeError:
        # If the loop is not running, get the current one or create a new one (Python 3.8 and 3.9)
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            # For Python 3.10+ or if the call occurs outside of an active loop context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        local = kwargs.pop("__local__", False)
        if local is False:
            if cls not in cls._instances:
                cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            return cls._instances[cls]
        else:
            return super(Singleton, cls).__call__(*args, **kwargs)


class Field(str, enum.Enum):
    STATE = "state"
    DATA = "data"
    CONTEXT = "context"


class _PatchableJson(dict):
    def __init__(self, field: Field, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._field = field
        self._linked_obj = None

    def raise_for_key(self, key: str):
        if key in self:
            raise KeyError(f"Key {key} already exists in {self._field}")

    def __update(self, js_obj):
        self.update(js_obj.to_py())

    def link(self, js_obj):
        self._linked_obj = js_obj
        self.__update(js_obj)

    def send_changes(self):
        if self._linked_obj is None:
            return
        from pyodide.ffi import to_js

        for key, value in to_js(self):
            self._linked_obj[key] = value


class StateJson(_PatchableJson, metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        super().__init__(Field.STATE, *args, **kwargs)


class DataJson(_PatchableJson, metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        super().__init__(Field.DATA, *args, **kwargs)


class MainServer(metaclass=Singleton):
    def __init__(self):
        self._server = FastAPI()

    def get_server(self) -> FastAPI:
        return self._server


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

        StateJson().link(self._state)
        DataJson().link(self._data)

        self.is_inited = True

    # Labeling tool data access
    def get_current_image(self):
        cur_img = getattr(self._store.state.videos.all, str(self._context.imageId))
        img_src = cur_img.sources[0]
        img_cvs = img_src.imageData
        return img_cvs

    @property
    def state(self):
        if not self.is_inited:
            self.__init_state()
        StateJson().update(self._state)
        return StateJson()

    @property
    def data(self):
        if not self.is_inited:
            self.__init_state()
        DataJson().update(self._data)
        return DataJson()

    @classmethod
    def render(cls, layout, dir=""):
        import json
        import os
        from pathlib import Path
        import shutil
        import supervisely as sly
        from supervisely.app.content import DataJson, StateJson
        from fastapi.staticfiles import StaticFiles
        from fastapi.routing import Mount

        app = sly.Application(layout=layout)
        index = app.render({"__webpy_script__": True})
        # @change="post('/{{{widget.widget_id}}}/value_changed')" -> @change="runPythonScript('/{{{widget.widget_id}}}/value_changed')"
        index = index.replace("post('/", "runPythonScript('/")

        dir = Path(dir)
        with open(dir / "index.html", "w") as f:
            f.write(index)

        json.dump(StateJson(), open(dir / "state.json", "w"))
        json.dump(DataJson(), open(dir / "data.json", "w"))

        shutil.copy("gui.py", dir / "gui.py")
        shutil.copy("main.py", dir / "main.py")

        shutil.copytree("sly_sdk", dir / "sly_sdk", dirs_exist_ok=True)

        server = app.get_server()
        for route in server.routes:
            if route.path == "/sly":
                route: Mount
                for route in route.routes:
                    if route.path == "/css" and isinstance(route.app, StaticFiles):
                        source_dir = route.app.directory
                        for root, _, files in os.walk(source_dir):
                            rel_path = Path(root).relative_to(source_dir)
                            for file in files:
                                if file.endswith(("css", "js", "html")):
                                    sly.fs.copy_file(
                                        Path(root, file), dir / Path("sly/css", rel_path, file)
                                    )

    def _get_handler(self, *args, **kwargs):
        if len(args) != 1:
            return None
        if not isinstance(args[0], str):
            return None
        handlers = kwargs.get("widgets_handlers", {})
        if args[0] in handlers:
            return handlers[args[0]]
        return None

    def _run_handler(self, f, *args, **kwargs):
        import inspect

        if inspect.iscoroutinefunction(f):
            loop = get_or_create_event_loop()
            return loop.run_until_complete(f(*args, **kwargs))
        return f(*args, **kwargs)

    def run(self, *args, **kwargs):
        import gui
        from fastapi.routing import APIRoute

        self.state
        self.data  # to init StateJson and DataJson

        server = MainServer().get_server()
        handlers = {}
        for route in server.router.routes:
            if isinstance(route, APIRoute):
                handlers[route.path] = route.endpoint

        handler = self._get_handler(*args, widgets_handlers=handlers, **kwargs)
        if handler is not None:
            return self._run_handler(handler)
        if self._run_f is None:
            raise NotImplementedError("Run function is not defined")
        return self._run_f(*args, **kwargs)

    def run_function(self, f):
        self._run_f = f
        return f