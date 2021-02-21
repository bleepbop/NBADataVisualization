FROM python:3.9-slim-buster
WORKDIR /usr/nbaMachineLearning
COPY requirements.txt .
COPY /src .
RUN pip3 install -r requirements.txt
CMD [ "python", "dash_graphs.py"]