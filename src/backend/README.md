# Backend Services for the project

## Introduction

### Data Router

Critical component of the project to connect with zookeeper and route the data to the correct node.

### Framework

- [FastAPI](https://fastapi.tiangolo.com/): FastAPI is a modern, fast (high-performance), web framework for building
  APIs with Python 3.7+ based on standard Python type hints.
- [Pydantic](https://pydantic-docs.helpmanual.io/): Data validation and settings management using python type
  annotations.
- [Poetry](https://python-poetry.org/): Python dependency management and packaging made easy.
- [Docker](https://www.docker.com/): Docker is a set of platform as a service products that use OS-level virtualization
  to deliver software in packages called containers.

## Local Development

### Prerequisites

#### Poetry

1. Install poetry using the following command:

```bash
brew install poetry
```

2. Install the dependencies using the following command:

```bash
poetry install
```

3. Set up the virtual environment (python interpreter) in pycharm.

#### FastAPI

1. Add the app confiruation by selecting the dropdown in the top dropdown and selecting the `app` configuration.
2. Add a new configuration by clicking the `+` button and selecting `FastAPI`.0
3. Set the application file to point to the *server.py* file.
4. Click `OK` to save the configuration.
5. Run the application using the `Run` (green play button) button.

## Deployment

Deployment is done using docker and Makefile. The following commands are available:

- `make build_data_router`: Build the data router image.
- `make run_data_router`: Run the data router container in a detached mode.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
