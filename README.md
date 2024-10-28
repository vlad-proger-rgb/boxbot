# BoxBot

Telegram Bot game where players collect random rewards from boxes and compete on a global leaderboard. This is my first-ever Telegram bot project. It is also the first time I have used SQL database.

## Technologies

- Python
- SQLite
- pyTelegramBotAPI

## Bot Features

- Can be added to groups

- Collect random rewards from boxes:
  - Choose one out of four boxes

- Daily rewards:
  - Random number from 5 to 25, divisible by 5

- Leaderboard:
  - Global Player leaderboard
  - Global Group leaderboard
  - Group leaderboard

- Statistics:
  - Games played
  - Daily rewards collected

- Information about the user

- Admin panel
  - Mailing: send messages to all users or groups in the database
  - Execute SQL queries directly from the bot. The keyword required, such as `SELECT`

## Note

The source code uploaded as it is - no changes, no refactoring, no optimizations. There's a lot of strange and redundant code, but it works. The only change is moving the API key and the user ID into the `.env` file.
