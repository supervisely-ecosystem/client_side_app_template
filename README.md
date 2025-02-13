# Web Python Applications
You can create a python application that will be running in the Supervisely Labeling tool in the browser. This allows you to have direct access to the objects of the tool such as images and annotations and to create event handlers for the tool.


## How to develop:
Your application should have a file with a `WebPyApplication` object named `app`.
Every application repository should have a sly_sdk module from this repository. This module is required for the application to work. It is temporary and will be removed in the future as we will update Supervisely SDK.

`WebPyApplication` object should be miported from sly_sdk.webpy
Widgets should be imported from `supervisely.app.widgets` but all of them should be available in the `sly_sdk.app.widgets` module as well.
We will add more widgets in the future.


### GUI:
To create a GUI for the application, you need to pass a `layout` argument to the `WebPyApplication` constructor. The layout should be a `Widget` object.
Not all Supervisely widgets are supported yet.


### config.json
In config.json you need to set the following variables:
- `gui_folder_path`: Path from where the GUI will be served. You can enter any non-conflicting path.
- `src_dir`: Path to the directory where the source code is located. All the modules that are imported in the main file should be in this directory.
- `main_script`: Path to the main script file. This file should be in the `src_dir` directory or in a subdirectory of it. This file should contain a variable `app` that is `WebPyApplication` object.

example:
```json
{
    "gui_folder_path": "app",
    "src_dir": "src",
    "main_script": "src/main.py"
}
```

### Events:

You can subscribe to events in the Labeling tool. To do this, you need to create a function and decorate it with the `@app.event` decorator. The function should expect a single argument, which will be the data sent by the event.

Available events can be found in the `app.Event` class

example:
```python
@app.event(app.Event.figure_geometry_saved)
def on_figure_geometry_saved(data):
    print("Figure geometry saved:", data)
```
