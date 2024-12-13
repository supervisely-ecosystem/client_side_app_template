from supervisely.app.widgets import Text, Container, Button, Select
from sly import WebPyApplication


# Layout code
text = Text("Hello, World!")
select = Select(items=["Option 1", "Option 2", "Option 3"])
button = Button("Click me!")
layout = Container(widgets=[text, select, button])


app = WebPyApplication()


@app.add_handler(select.value_changed)
def on_select_change(value):
    print("Select value changed:", value)


@app.add_handler(button.click)
def on_button_click():
    print("Button clicked!")


if __name__ == "__main__":
    app.render(layout=layout, dir="src")


@app.run_function
def main(*args, **kwargs):
    print("Hello, World!")
    print("Args:", args)
    print("Kwargs:", kwargs)


app.run  # or app # PyOdide will execute run this function and return the result


# How to trigger callbacks from widgets interactions?
# 1. redefine post in the SlyApp.js (bad)
# 2. on calling WebPyApplication.render() replace post requests or @click / @change events with custom events (code generation, not preferred)
# 3. add webpy handling in all the widgets (a lot of work and maintenance)
# 4. ?

# Problems:
# 1. How to access layout widgets? For example in the main function we want to get the value of some widget
# 2. widgets callbacks?
