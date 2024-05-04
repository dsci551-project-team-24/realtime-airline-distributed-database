# Realtime Airline Distributed Database
# Backend Services for the project

Google Drive Link: https://drive.google.com/drive/folders/1Zsa3HSqT73Afcusk2-X5UMuPpRCtSVYL?usp=sharing
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

```bash

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

#### Zookeeper setup

We need to setup the localhost ZNode so the router image can run and bring up the clients.

1. Under the dev directory
2. Run the following command to add the znode

```bash
python3 add_local.py
```

#### FastAPI

1. Add the app configuration by selecting the dropdown in the top dropdown and selecting the `app` configuration.
2. Add a new configuration by clicking the `+` button and selecting `FastAPI`.0
3. Set the application file to point to the *server.py* file.'
4. Ensure you have MySQL running on your local machine
5. Under environment variables, add the following environment variables:

```bash
MYSQL_USER=root
MYSQL_PASSWORD=<your_db_password>
```

6. Click `OK` to save the configuration.
7. Run the application using the `Run` (green play button) button.

## Deployment

Deployment is done using docker and Makefile. The following commands are available:

- Go to the infra directory and run the following command to build the docker image:

```bash
make router_image
```

To run the entire infra with the backend services, run the following command:

```bash
make deploy
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
