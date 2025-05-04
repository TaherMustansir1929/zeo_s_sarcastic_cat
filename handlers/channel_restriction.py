import os
from dotenv import load_dotenv

load_dotenv()

# Channel where bot commands are allowed
# Set this to the ID of the channel where you want commands to be allowed
# If set to 0, commands will be allowed in all channels
# To get a channel ID, right-click on a channel in Discord and select "Copy ID"
# (Developer Mode must be enabled in Discord settings)
COMMANDS_CHANNEL_ID = int(os.getenv("COMMANDS_CHANNEL_ID", "0"))  # Default to 0 if not set

async def channel_restriction_handler(bot, message):
    # Channel restriction feature: Check if the message is a command and if it's in the allowed channel
    if message.content.startswith(bot.command_prefix):
        # If COMMANDS_CHANNEL_ID is 0, allow commands in all channels (for backward compatibility)
        # Otherwise, check if the command is being used in the designated channel
        if COMMANDS_CHANNEL_ID != 0 and message.channel.id != COMMANDS_CHANNEL_ID:
            # If the message is a command but not in the allowed channel, inform the user
            allowed_channel = message.guild.get_channel(COMMANDS_CHANNEL_ID)
            if allowed_channel:
                # Send a message directing the user to the correct channel
                await message.channel.send(
                    f"{message.author.mention}, commands can only be used in {allowed_channel.mention}!")
            return  # Don't process the command

    # Process commands only if they're in the allowed channel or if no channel restriction is set
    await bot.process_commands(message)