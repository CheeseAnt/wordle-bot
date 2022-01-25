## How to build
``docker build -t cheeseant/wordle:<tag> .``

## How to run
It is recommended to use a volume mount with the ``wordle_bot_flat_file`` env to persist the file outside the docker container. 

### Environment variables
- wordle_bot_token : The token for the discord bot
- wordle_bot_channel : The channel the Wordle bot will listen to (default: wordle)
- wordle_bot_flat_file : The storage file for the wordle bot. (default: wordle.db)

### Start command
`
docker run --env wordle_bot_token=<token>
  --env wordle_bot_flat_file=/app/storage/wordle.db
  -v "$(pwd)"/wordle:/app/storage/
  --name wordle
  cheeseant/wordle:<tag>
`
