from sly import WebPyApplication
import gui


app = WebPyApplication()


@app.run_function
def main(*args, **kwargs):
    print("Hello, World!")
    print("Args:", args)
    print("Kwargs:", kwargs)


if __name__ == "__main__":
    import sys

    app.run(*sys.argv[1:])

app.run
