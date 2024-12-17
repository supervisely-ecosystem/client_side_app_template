from sly import WebPyApplication

if __name__ == "__main__":
    import gui

    WebPyApplication.render(layout=gui.layout, dir="src")
