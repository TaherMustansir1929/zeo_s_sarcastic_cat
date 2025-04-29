# Discord Bot

A Discord bot with various commands including AI-powered responses, word counting, and more.

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with the following variables:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   COMMANDS_CHANNEL_ID=123456789012345678  # Optional: Replace with your channel ID
   ```

   If `COMMANDS_CHANNEL_ID` is not set or is set to `0`, commands will be allowed in all channels.

   See the [Channel Restriction](#channel-restriction) section below for detailed instructions on how to find your channel ID.

4. Run the bot:
   ```
   python main.py
   ```

## Features

### Channel Restriction

The bot can be configured to only respond to commands in a specific channel. To enable this:

1. Enable Developer Mode in Discord:
   - Open Discord
   - Go to User Settings (gear icon near your username)
   - Select "Advanced" in the left sidebar
   - Toggle on "Developer Mode"

2. Find the ID of the channel where you want commands to be allowed:
   - Right-click on the channel in Discord
   - Select "Copy ID" from the context menu
   - The channel ID is now copied to your clipboard (it's a long number like 123456789012345678)

3. Add the channel ID to your `.env` file:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   COMMANDS_CHANNEL_ID=123456789012345678  # Replace with your actual channel ID
   ```

4. Restart the bot

When users try to use commands in other channels, they will be informed that commands can only be used in the designated channel.

#### Troubleshooting

- If commands work in all channels despite setting COMMANDS_CHANNEL_ID, make sure:
  - You've entered the correct channel ID
  - The .env file is in the same directory as main.py
  - You've restarted the bot after making changes
  - The channel ID is a number without quotes

- If you want to disable channel restriction and allow commands in all channels:
  - Set `COMMANDS_CHANNEL_ID=0` in your .env file
  - Or remove the COMMANDS_CHANNEL_ID line entirely from your .env file

### Available Commands

- `!ask [message]` - Ask the AI a question
- `!rizz` - Generate a pickup line
- `!rate [pickup line]` - Rate a pickup line
- `!ai [message]` - Talk to the AI
- `!help_me` - Display a list of available commands
- `!ping` - Check the bot's latency
- And more...

## Word Counter

The bot automatically counts how many times users say certain phrases and responds with a custom message.
