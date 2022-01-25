FROM python:3.10-slim as builder

ENV wordle_bot_channel=wordle

WORKDIR app

COPY . .

# Install all packages & test
RUN pip3 install -r requirements.txt \
    && pip3 install -r test-requirements.txt \
    && python -m pytest tests/

FROM python:3.10-slim as runner

ENV wordle_bot_token=""
ENV wordle_bot_channel=wordle
ENV wordle_bot_flat_file="/app/wordle.db"

WORKDIR app

# Copy runtime-files only
COPY --from=builder /app/wordle wordle
COPY --from=builder /app/requirements.txt requirements.txt

# Install runtime packages
RUN pip3 install -r requirements.txt

ENV PYTHONPATH /app

CMD ["python", "/app/wordle/wordle_bot.py"]
