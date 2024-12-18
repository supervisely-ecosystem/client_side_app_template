try:
    import supervisely
except ImportError:
    import sys
    import sly_sdk as supervisely

    sys.modules["supervisely"] = supervisely

from supervisely.app.widgets import Text, Container, Button, Select


text: Text = globals().get("text", Text("Hello, World!", widget_id="widget_1"))
select: Select = globals().get(
    "select",
    Select(
        items=[Select.Item("Option 1"), Select.Item("Option 2"), Select.Item("Option 3")],
        widget_id="widget_2",
    ),
)
button = globals().get("button", Button("Click me!", widget_id="widget_3"))
layout = globals().get("layout", Container(widgets=[text, select, button], widget_id="widget_4"))


@select.value_changed
def on_select_change(value):
    print("Select value changed:", value)


@button.click
def on_button_click():
    print("Button clicked!")
    text.text = str(select.get_value())
