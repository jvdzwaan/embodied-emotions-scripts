FROM python:2

COPY requirements.txt /code/embodied-emotions-scripts/requirements.txt
WORKDIR /code/embodied-emotions-scripts
RUN pip install -r requirements.txt

CMD jupyter-notebook --ip 0.0.0.0 --port 8888 --allow-root --no-browser