FROM python:3.8
RUN useradd -ms /bin/bash user
USER user
WORKDIR /home/user
COPY requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt
EXPOSE 8050
ENTRYPOINT [ "python3", "dash_graphs.py"]