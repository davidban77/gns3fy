# Inspired from:
# https://github.com/nornir-automation/nornir/blob/develop/Dockerfile
# https://github.com/microsoft/vscode-dev-containers/tree/master/containers/python-3-miniconda
# FROM continuumio/miniconda3
FROM circleci/python:3.7

WORKDIR /gns3fy
USER circleci:circleci

COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv && uv sync
