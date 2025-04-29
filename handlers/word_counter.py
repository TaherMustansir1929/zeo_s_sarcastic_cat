import os
import csv

from my_prompts.word_count_prompts import word_count_reaction

async def word_counter_handler(bot, message):
    if message.author == bot.user:
        return

    target_phrases = ["low taper fade", "nigga", "massive"]
    username = str(message.author)
    matched = False

    # Create word_count directory if it doesn't exist
    word_count_dir = 'word_counts'
    if not os.path.exists(word_count_dir):
        os.makedirs(word_count_dir)

    for target_phrase in target_phrases:
        if target_phrase in message.content.lower():
            matched = True
            file_path = f"{target_phrase.replace(' ', '_')}.csv"
            csv_file = os.path.join(word_count_dir, file_path)
            # Read existing data
            data = {}
            try:
                with open(csv_file, mode="r", newline='', encoding="utf-8") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) == 2:
                            data[row[0]] = int(row[1])
            except FileNotFoundError:
                pass
            # Update count
            if username in data:
                data[username] += 1
            else:
                data[username] = 1
            # Write back
            with open(csv_file, mode="w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                for user, count in data.items():
                    writer.writerow([user, count])
            # Send message in channel with updated count
            response = word_count_reaction(target_phrase, data[username], message.author)
            response = f"{message.author.mention} said `{target_phrase}` {data[username]} times! \n{response}"
            await message.channel.send(response)

            if matched:
                return