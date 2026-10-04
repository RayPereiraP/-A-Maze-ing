FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TERM=xterm-256color

WORKDIR /app

COPY . /app
RUN if [ -f requirements.txt ]; then python -m pip install --no-cache-dir -r requirements.txt; fi

COPY docker/run-maze.sh /usr/local/bin/run-maze

ENTRYPOINT ["sh", "/usr/local/bin/run-maze"]
CMD ["config.txt"]
