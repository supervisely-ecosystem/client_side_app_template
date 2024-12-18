import sys

from sly_sdk.sly import WebPyApplication
import sly_sdk as supervisely

sys.modules["supervisely"] = supervisely


app = WebPyApplication()


@app.run_function
def main(*args, **kwargs):
    print("Hello, World!")
    print("Args:", args)
    print("Kwargs:", kwargs)


if __name__ == "__main__":
    app.run(*sys.argv[1:])

app.run
