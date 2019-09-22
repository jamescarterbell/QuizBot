# James Bell QuizBot
import random
import asyncio
import aiohttp
import json
import discord
import requests
from requests import session
from http import cookies, cookiejar
from discord import Reaction, Game, Emoji, User, channel, member, Message, Embed
from discord.ext.commands import Bot
from praw import models as reddit
from random import shuffle

BOT_PREFIX = ("QQ ", "Qq ", "qQ ", "qq ")
# Get at discordapp.com/developers/applications/me
TOKEN = ""

s = session()
s.cookies["key"] = TOKEN

client = Bot(command_prefix=BOT_PREFIX)

number_to_text = ["{}\N{COMBINING ENCLOSING KEYCAP}".format(
    num) for num in range(0, 10)]

on_reactions = list()


@client.listen(name="on_reaction_add")
async def on_reaction_add(reaction, user):
    for f in on_reactions:
        await f(reaction, user)


@client.command(pass_context=True,
                name="Question",
                description='Place question and answers within quotes.\nAutomatically removes spoiler tag, use spoiler tags within answer quotes to hide options.',
                aliases=["question", "Quiz", "quiz"])
async def Question(context, question: str, answers: str, ping_right: bool = False, time: int = 60, points: int = 10):
    message = context.message
    await message.delete()

    answers = answers.replace("||", "").split("|")
    shuffle(answers)

    if len(answers) < 2:
        await message.channel.send('You need to give more than one answer!')
        return

    if len(answers) > 9:
        await message.channel.send('You need to give less than 9 answers!')
        return

    right_answer = 0

    embed = Embed(title="Question Time!",
                  description="Answer {}'s question to score {} points!".format(
                      context.author.mention,
                      points),
                  color=0x0005ff)
    embed.set_thumbnail(
        url="https://vignette.wikia.nocookie.net/undertale/images/5/58/Mettaton.gif/revision/latest/scale-to-width-down/226?cb=20151111052226")

    embed.add_field(name="You have:",
                    value="{} seconds left!".format(time))

    embed.add_field(name="Question:", value=question, inline=False)

    for num, word in enumerate(answers):
        if word[0] == "*":
            right_answer = num
            word = word.replace("*", "")
        embed.add_field(
            name="Choice " + number_to_text[num+1], value=word, inline=False)
    new_message = await message.channel.send(embed=embed)

    past_reactions = {}

    async def react_checker(reaction, user):
        if user.bot:
            return
        if reaction.message.id != new_message.id:
            return
        if user in past_reactions:
            if past_reactions[user].emoji != reaction.emoji:
                await past_reactions[user].remove(user)
        past_reactions[user] = reaction

    this_react_checker = react_checker
    on_reactions.append(this_react_checker)

    for i in range(0, len(answers)):
        await new_message.add_reaction(number_to_text[i+1])

    while time > 0:
        time -= 5
        embed.set_field_at(0, name="You have:",
                           value="{} seconds left!".format(time), inline=True)
        await asyncio.sleep(5)
        await new_message.edit(embed=embed)
    embed.clear_fields()
    embed.add_field(name="Question:", value=question)
    embed.add_field(name="Your Time is Up! The Answer was:",
                    value=number_to_text[right_answer + 1] + " " + answers[right_answer].replace("*", ""), inline=False)

    await new_message.clear_reactions()

    right_users = list()
    right_user_string = ""

    for num, user in enumerate(past_reactions):
        if not user.bot:
            if past_reactions[user].emoji == number_to_text[right_answer + 1]:
                result = s.get(
                    "http://localhost:8000/{}/{}/{}".format(
                        user.name, user.display_name, points))
                if not result == "SUCC":
                    continue
                if ping_right:
                    right_users.append(user)
                    right_user_string += user.mention + "\n"

    if ping_right:
        if len(right_users) > 0:
            embed.add_field(name="Congratulations to:",
                            value=right_user_string)

    await new_message.edit(embed=embed)

    on_reactions.remove(this_react_checker)


@client.command(pass_context=True,
                name="Get Score",
                description='Get the socre for given users',
                aliases=["score", "Score", "scores", "Scores"])
async def Score(context):
    message = "```\n"
    for member in context.message.mentions:
        result = s.get(
            "http://localhost:8000/{}?nick={}".format(
                member.name, member.display_name))
        if not result.text == "ERR":
            message += result.text + "\n"
    message += "```"
    await context.message.channel.send(message)


@client.command(pass_context=True,
                name="Survey",
                description='Ask a question with no right answer and see how people respond.\nPlace question and answers within quotes.\nAutomatically removes spoiler tag, use spoiler tags within answer quotes to hide options.',
                aliases=["survey", "Vote", "vote"])
async def Survey(context, question: str, answers: str, time: int = 60):
    message = context.message
    await message.delete()

    answers = answers.replace("||", "").split("|")
    shuffle(answers)

    if len(answers) < 2:
        await message.channel.send('You need to give more than one answer!')
        return

    if len(answers) > 9:
        await message.channel.send('You need to give less than 9 answers!')
        return

    embed = Embed(title="Survey Time!",
                  description="Please answer {}'s question!".format(
                      context.author.mention),
                  color=0xff1111)
    embed.set_thumbnail(
        url="https://vignette.wikia.nocookie.net/undertale/images/5/58/Mettaton.gif/revision/latest/scale-to-width-down/226?cb=20151111052226")

    embed.add_field(name="You have:",
                    value="{} seconds left!".format(time))

    embed.add_field(name="Survey:", value=question, inline=False)

    for num, word in enumerate(answers):
        embed.add_field(
            name="Choice " + number_to_text[num+1], value=word, inline=False)
    new_message = await message.channel.send(embed=embed)

    past_reactions = {}
    reaction_emoji = list()

    async def react_checker(reaction, user):
        if user.bot:
            reaction_emoji.append(reaction.emoji)
            return
        if reaction.message.id != new_message.id:
            return
        if user in past_reactions:
            if past_reactions[user].emoji != reaction.emoji:
                await past_reactions[user].remove(user)
        past_reactions[user] = reaction

    this_react_checker = react_checker
    on_reactions.append(this_react_checker)

    for i in range(0, len(answers)):
        await new_message.add_reaction(number_to_text[i+1])

    while time > 0:
        time -= 5
        embed.set_field_at(0, name="You have:",
                           value="{} seconds left!".format(time), inline=True)
        await asyncio.sleep(5)
        await new_message.edit(embed=embed)
    embed.clear_fields()
    embed.add_field(name="Survey Results For:", value=question, inline=False)

    survey_results = {}
    total_answers = 0

    for emoji in reaction_emoji:
        survey_results[emoji] = 0

    for num, user in enumerate(past_reactions):
        if not user.bot:
            if past_reactions[user].emoji in survey_results:
                survey_results[past_reactions[user].emoji] += 1
            else:
                survey_results[past_reactions[user].emoji] = 1
            total_answers += 1

    for num, result in enumerate(survey_results):
        survey_results[result] /= total_answers
        embed.add_field(name="{}% voted for:".format(survey_results[result] * 100),
                        value=result + " " + answers[num],
                        inline=False)

    await new_message.clear_reactions()
    await new_message.edit(embed=embed)

    on_reactions.remove(this_react_checker)


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(TOKEN)
