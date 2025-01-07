from supervisely.app.widgets import Container, Slider, Switch, Field
from supervisely.sly_logger import logger


# Creating widget to turn on/off the processing of labels.
need_processing = Switch(switched=True, widget_id="need_processing_widget")
processing_field = Field(
    title="Process masks",
    description="If turned on, then the mask will be processed after every change on left mouse release after drawing",
    content=need_processing,
    widget_id="processing_field_widget",
)

# Creating widget to set the strength of the processing.
dilation_strength = Slider(value=10, min=1, max=50, step=1, widget_id="dilation_strength_widget")
dilation_strength_field = Field(
    title="Dilation",
    description="Select the strength of the dilation operation",
    content=dilation_strength,
    widget_id="dilation_strength_field_widget",
)

layout = Container(widgets=[processing_field, dilation_strength_field], widget_id="layout_widget")


@need_processing.value_changed
def processing_switched(is_switched):
    logger.debug(f"Processing is now {is_switched}")


@dilation_strength.value_changed
def strength_changed(value):
    logger.debug(f"Strength is now {value}")
