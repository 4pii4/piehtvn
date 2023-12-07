FROM docker.io/library/python:3-bookworm

LABEL authors="stdpi <github.com/huwutao>"

RUN useradd -ms /bin/bash pyr
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=pyr . .

CMD [ "python", "./backend.py" ]