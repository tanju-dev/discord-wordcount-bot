import os
import re

import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")


@bot.command()
async def count(ctx, *, begriffe):
    # Begriffe durch Kommas trennen
    suchbegriffe = [
        begriff.strip().lower()
        for begriff in begriffe.split(",")
        if begriff.strip()
    ]

    if not suchbegriffe:
        await ctx.send("Bitte gib mindestens ein Wort an.")
        return

    # Für jedes Suchwort nur die ersten 3 Buchstaben verwenden
    suchanfänge = []

    for wort in suchbegriffe:
        # Bei Wörtern mit weniger als 3 Buchstaben das komplette Wort nehmen
        anfang = wort[:3]

        if anfang not in suchanfänge:
            suchanfänge.append(anfang)

    # Nutzer -> Anzahl
    user_counts = {}

    # Alle Textkanäle des Servers durchsuchen
    for channel in ctx.guild.text_channels:
        try:
            async for message in channel.history(limit=None):

                # Bots ignorieren
                if message.author.bot:
                    continue

                text = message.content.lower()

                anzahl = 0

                # Jeden gesuchten Anfang prüfen
                for anfang in suchanfänge:

                    # Wort muss mit dem Anfang beginnen
                    pattern = r"(?<!\w)" + re.escape(anfang) + r"\w*"

                    anzahl += len(re.findall(pattern, text))

                if anzahl > 0:
                    user_id = message.author.id

                    if user_id not in user_counts:
                        user_counts[user_id] = {
                            "name": message.author.display_name,
                            "count": 0
                        }

                    user_counts[user_id]["count"] += anzahl

        except discord.Forbidden:
            # Kanal kann nicht gelesen werden
            continue

    if not user_counts:
        await ctx.send(
            f"Keine passenden Wörter gefunden: "
            f"{', '.join(suchbegriffe)}"
        )
        return

    # Nach Anzahl sortieren
    ranking = sorted(
        user_counts.values(),
        key=lambda x: x["count"],
        reverse=True
    )

    # Tierlist erstellen
    text = "**🏆 Wort-Tierlist**\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for position, user in enumerate(ranking[:20], start=1):

        if position <= 3:
            prefix = medals[position - 1]
        else:
            prefix = f"**{position}.**"

        text += f"{prefix} {user['name']} — **{user['count']}**\n"

    text += (
        f"\nGesuchte Wörter: `{', '.join(suchbegriffe)}`"
        f"\nGeprüfte Anfänge: `{', '.join(suchanfänge)}`"
    )

    await ctx.send(text)


bot.run(TOKEN)