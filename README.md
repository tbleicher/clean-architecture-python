### Installation

In the _repo root folder_ ('clean-arch-docker') run

```
$ docker-compose up -d --build
```

This will build and start the Docker image. You can test that it's running with `curl`:

```
$ curl http://localhost:4000/healthcheck
```

### Testing

First start the container, then use a Docker command to run Pytest within the container:

```
$ docker-compose up -d
$ docker-compose exec web python -m pytest
```

### Development

The `src` folder is mapped volume in the Docker container and the startup command runs `uvicorn` with the `--reload` option so a change to the source files will restart the server automatically.

However, Python dependencies are installed only in the container and not accessible by your editor. Your editor may depend on these to enable things like Intellisense. You can create a virtual environment in the `src` folder just for the editor:

```
$ cd src
$ python3.9 -m venv ./venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
```

If you use VS Code you can also use a [Remote Python Development](https://devblogs.microsoft.com/python/remote-python-development-in-visual-studio-code/).
