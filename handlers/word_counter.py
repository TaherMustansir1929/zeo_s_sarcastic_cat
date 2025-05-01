import os
import sqlite3
import re

from my_prompts.word_count_prompts import word_count_reaction

# Define database path relative to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "word_count.db")

# Ensure the db directory exists
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Define target phrases globally or load from config
TARGET_PHRASES = ["low taper fade", "nigga", "massive"]

def _sanitize_phrase_for_table_name(phrase):
    """Sanitizes a phrase to be used as a valid SQLite table name."""
    # Replace spaces and non-alphanumeric characters with underscores
    s = re.sub(r'\W+', '_', phrase)
    # Ensure it doesn't start with a number
    if s and s[0].isdigit():
        s = '_' + s
    # SQLite table names are case-insensitive, convert to lower for consistency
    return s.lower()

def initialize_db():
    """Initializes the database and creates a table for each target phrase."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for phrase in TARGET_PHRASES:
        table_name = _sanitize_phrase_for_table_name(phrase)
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                count INTEGER
            )
        ''')
    conn.commit()
    conn.close()

# Initialize the database on script load
initialize_db()

async def word_counter_handler(bot, message):
    if message.author == bot.user:
        return

    user_id = str(message.author.id)
    username = str(message.author)
    matched_phrase = None
    table_name = None

    for target_phrase in TARGET_PHRASES:
        if target_phrase in message.content.lower():
            matched_phrase = target_phrase
            table_name = _sanitize_phrase_for_table_name(matched_phrase)
            break # Process only the first matched phrase

    if matched_phrase and table_name:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check current count in the specific table
        cursor.execute(f"SELECT count FROM {table_name} WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        current_count = 0
        if result:
            current_count = result[0]

        # Update count
        new_count = current_count + 1
        cursor.execute(f'''
            INSERT INTO {table_name} (user_id, username, count)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET count = excluded.count, username = excluded.username
        ''', (user_id, username, new_count))

        conn.commit()
        conn.close()

        # Send message in channel with updated count
        reaction_response = word_count_reaction(matched_phrase, new_count, message.author)
        response = f"{message.author.mention} said `{matched_phrase}` {new_count} times! \n{reaction_response}"
        await message.channel.send(response)

        return # Exit after handling the first match

# Remove old CSV handling logic (commented out or deleted)
#    # Create word_count directory if it doesn't exist
#    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#    word_count_dir = os.path.join(BASE_DIR, "word_count")
#    if not os.path.exists(word_count_dir):
#        os.makedirs(word_count_dir)
#
#    for target_phrase in target_phrases:
#        if target_phrase in message.content.lower():
#            matched = True
#            file_path = f"{target_phrase.replace(' ', '_')}.csv"
#            csv_file = os.path.join(word_count_dir, file_path)
#            # Read existing data
#            data = {}
#            try:
#                with open(csv_file, mode="r", newline='', encoding="utf-8") as f:
#                    reader = csv.reader(f)
#                    for row in reader:
#                        if len(row) == 2:
#                            data[row[0]] = int(row[1])
#            except FileNotFoundError:
#                pass
#            # Update count
#            if username in data:
#                data[username] += 1
#            else:
#                data[username] = 1
#            # Write back
#            with open(csv_file, mode="w", newline='', encoding="utf-8") as f:
#                writer = csv.writer(f)
#                for user, count in data.items():
#                    writer.writerow([user, count])
#            # Send message in channel with updated count
#            response = word_count_reaction(target_phrase, data[username], message.author)
#            response = f"{message.author.mention} said `{target_phrase}` {data[username]} times! \n{response}"
#            await message.channel.send(response)
#
#            if matched:
#                return