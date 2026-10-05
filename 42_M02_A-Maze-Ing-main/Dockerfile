FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TERM=xterm-256color \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY Makefile dev-requirements.txt config.txt ./

# Keep the environment outside /app so the Compose mount cannot hide it.
# The existing Makefile asks for confirmation when installing dependencies.
RUN python -m venv /opt/venv \
    && printf 'y\n' | make install VENV_DIR=/opt/venv \
    && python -m pip check \
    && python -c "import pydantic, rich, mypy, flake8, build"

COPY . .

ENTRYPOINT ["python", "a_maze_ing.py"]
CMD ["config.txt"]
