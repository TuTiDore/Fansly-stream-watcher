FROM ubuntu:latest

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir streamlink && \
    pip install --no-cache-dir cloudscraper

RUN mkdir media

ARG USER=TuTiDore
ARG REPO=Streamlink-Plugin-Fansly
ARG BRANCH=main
ADD https://api.github.com/repos/$USER/$REPO/git/refs/heads/$BRANCH ./version.json
RUN git clone -b $BRANCH https://github.com/$USER/$REPO.git /root/fansly-plugin

RUN mkdir -p /root/.local/share/streamlink/plugins/
RUN cp /root/fansly-plugin/fansly.py /root/.local/share/streamlink/plugins/fansly.py

COPY runner.py /app/runner.py

ENTRYPOINT ["python3", "-u", "runner.py"]