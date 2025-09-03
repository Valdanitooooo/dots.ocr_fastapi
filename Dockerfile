FROM python:3.13-slim AS builder

RUN pip install uv

WORKDIR /app

COPY requirements.txt /app/

RUN uv venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN uv pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
RUN chown appuser:appuser /app

COPY --from=builder /app/venv /app/venv
RUN chown -R appuser:appuser /app/venv

ENV PATH="/app/venv/bin:$PATH"

USER appuser

COPY --chown=appuser:appuser . /app/

EXPOSE 8491

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8491"]
