from sly_sdk.sly import WebPyApplication


app = WebPyApplication()


@app.run_function
def main(*args, **kwargs):
    print("Hello, World!")
    print("Args:", args)
    print("Kwargs:", kwargs)


app.run
