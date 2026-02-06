FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV UV_COMPILE_BYTECODE=1

WORKDIR /app
ADD . /app

CMD ["uv", "run", "main.py"]