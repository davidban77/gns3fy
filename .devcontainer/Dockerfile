# Inspired from:
# https://github.com/nornir-automation/nornir/blob/develop/Dockerfile
# https://github.com/microsoft/vscode-dev-containers/tree/master/containers/python-3-miniconda
# FROM continuumio/miniconda3
FROM circleci/python:3.7

WORKDIR /gns3fy
USER circleci:circleci
# ENV PATH="/root/.poetry/bin:$PATH" \
#     PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     DEBIAN_FRONTEND=noninteractive

# RUN apt-get update \
#     && apt-get install -yq curl git openssh-client less iproute2 procps iproute2 lsb-release make \
#     && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python \
#     && poetry config virtualenvs.create false \
#     && apt-get autoremove -y \
#     && apt-get clean -y \
#     && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install --no-interaction
