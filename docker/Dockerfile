FROM python:3.8

WORKDIR /command_invoker

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install vim -y && apt-get clean

COPY ./aws ./aws
COPY ./azure ./azure
COPY ./scripts ./scripts

ENTRYPOINT ["/bin/bash"]
