from supervisely.app.widgets import Text, Container, Button, Select

text = Text("Hello, World!", widget_id="widget_1")
select = Select(
    items=[Select.Item("Option 1"), Select.Item("Option 2"), Select.Item("Option 3")],
    widget_id="widget_2",
)
button = Button("Click me!", widget_id="widget_3")
layout = Container(widgets=[text, select, button], widget_id="widget_4")


@select.value_changed
def on_select_change(value):
    print("Select value changed:", value)


@button.click
def on_button_click():
    print("Button clicked!")
