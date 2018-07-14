import discord
import asyncio
import pickle

valid_helper_roles = {  
                        "Art History": ["ap art history", "art history"],
                        "Biology": ["biology", "ap bio", "ap biology", "bio"],
                        "Calculus": ["calculus", "ap calc", "calc ab", "calc bc", "calc"],
                        "Capstone": ["capstone", "ap capstone"],
                        "Chemistry": ["chem", "chemistry", "ap chem", "ap chemsitry"],
                        "Chinese": ["ap chinese", "chinese"],
                        "Comp. Government": ["comparative government", "comp gov", "comp. gov"],
                        "Computer Science Principles": ["ap computer science principles", "ap csp", "csp", "computer principles", "computer science principles"],
                        "Computer Science": ["ap computer science a", "ap csa", "computer science a"],
                        "Environmental Science": ["apes", "environmental science", "ap es", "ap e.s"],
                        "European History": ["ap euro", "euro", "ap european history", "european history"],
                        "French": ["ap french", "french"],
                        "German": ["ap german", "german"],
                        "Home Economics": ["ap home economics", "ap home ec", "home ec", "home economics"],
                        "Human Geography": ["human geo", "geography", "geo", "ap geo", "human geography"],
                        "Italian": ["ap italian", "italian"],
                        "Japanese": ["ap japanese", "japanese"],
                        "Language Arts": ["ap language", "ap lang", "lang"],
                        "Latin": ["ap latin", "latin"],
                        "Literature": ["lit", "literature", "ap lit", "ap literature"],
                        "Macroeconomics": ["ap macro", "macro", "ap macroeconomics", "macroeconomics"],
                        "Microeconomics": ["ap micro", "micro", "ap microeconomics", "microeconomics"],
                        "Music Theory": ["ap music theory", "music", "music theory", "ap music"],
                        "Psychology": ["psych", "ap psych", "ap psychology"],
                        "Physics 1": ["ap physics 1", "physics 1"],
                        "Physics 2": ["ap physics 2", "physics 2"],
                        "Physics C Mech": ["ap physics mech", "physics mech"],
                        "Physics C E/M": ["ap physics e/m", "ap physics e&m", "physics e/m", "physics e&m"],
                        "Research": ["ap research", "research"],
                        "Seminar": ["ap seminar", "seminar"],
                        "Spanish Langauge": ["ap spanish language", "spanish language", "spanish culture"],
                        "Spanish Literature": ["ap spanish literature", "spanish literature", "spanish lit"],
                        "Studio Art": ["ap studio art", "studio art"],
                        "Statistics": ["ap statistics", "ap stats", "stats", "ap statistics"],
                        "U.S Government": ["ap gov", "u.s government", "us gov", "gov"],
                        "U.S History": ["apush", "united states", "us history", "u.s history", "ap u.s histroy"],
                        "World History": ["apwh", "ap world history", "world history", "world", "ap wh"]
                        }

TIMEOUT_TIME = 15

# jjam912's code
# Set up the help message
help = """To ping helpers, use ```!ping <helper name>```
Be careful when using this command! It will ping all helpers of that role, and you will not be able to ping again for """ + str(TIMEOUT_TIME) + """ seconds.\n\nTo check how much longer until you can ping a helper use ```!notify time```\nTo request to receive a reminder when you can once again ping a helper use ```!notify remind```\n\nAliases for each role are as follows: ```
"""

for subject in valid_helper_roles.keys():
    help += "\n* {0}: {1}\n".format(subject, ", ".join(valid_helper_roles[subject]))

help += "\n```"

help += "\n\n*Below are mod-only commands*:\n\nTo completely blacklist a user from pinging helpers use: ```!blacklist <user's mention>```\nTo unblacklist a user from pinging helpers use: ```!unblacklist <user's mention>```"

TOKEN = ''

client = discord.Client()

# ACT Inc.'s Code

def convertCommonNameToProperName(s):
    for item in valid_helper_roles:
        if s in valid_helper_roles[item]:
            return item + " Helper"
    return ""

def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def readBlacklist(obj, filename):
    with open(filename, 'rb') as input:
        blu = pickle.load(input)
        return blu

blacklisted_users = []
try:
    blacklisted_users = readBlacklist('d', 'blacklist.pkl')
except (OSError, IOError) as e:
    save_object(blacklisted_users, 'blacklist.pkl')

users_on_timeout = {}
messages_to_delete = {}

async def updateTimer():
    while True:
        await asyncio.sleep(1)
        names_to_remove = []
        for item in users_on_timeout:
            users_on_timeout[item][0] = users_on_timeout[item][0] - 1
            if (users_on_timeout[item][0] <= 0):
                names_to_remove.append(item)
        for item in names_to_remove:
            if (users_on_timeout[item][1]):
                await client.send_message(item, "This is your reminder that you are now allowed to ping helpers.")
            del users_on_timeout[item]

async def removeMessages():
     while True:
        await asyncio.sleep(1)
        messages_to_remove = []
        #print (messages_to_delete)
        for item in messages_to_delete:
            messages_to_delete[item] = messages_to_delete[item] - 1
            if (messages_to_delete[item] <= 0):
                messages_to_remove.append(item)
        for item in messages_to_remove:
            await client.delete_message(item)
            del messages_to_delete[item]

@client.event
async def on_message(message):
    global messages_to_delete
    if message.author == client.user:
        return
    if message.content.startswith("!help"):
        await client.send_message(message.author, help)
        #await client.delete_message(message)
        messages_to_delete[message] = 3
    elif message.content.startswith('!notify'):
        messages_to_delete[message] = 3
        arg = " ".join(message.content.split(" ")[1:len(message.content.split(" "))]).lower()
        if (arg == "time"):
            if (message.author in users_on_timeout):
               await client.send_message(message.author, "You will be able to ping for a helper in " + str(users_on_timeout[message.author][0]) + " seconds.")
            else:
                await client.send_message(message.author, "You are currently allowed to ping helpers.")
        elif (arg == "remind"):
            if (message.author in users_on_timeout):
                if (users_on_timeout[message.author][1]):
                    await client.send_message(message.author, "You will no longer be receiving a reminder for when you can ping a helper.")
                else:
                    await client.send_message(message.author, "You will receive a reminder once you are allowed to ping a helper.")
                users_on_timeout[message.author][1] = not users_on_timeout[message.author][1]
            else:
                await client.send_message(message.author, "You are currently allowed to ping helpers.")
    elif message.content.startswith('!ping'):
        if (not message.author.mention in blacklisted_users):
            common_helper_role = " ".join(message.content.split(" ")[1:len(message.content.split(" "))]).lower()
            helper_role = convertCommonNameToProperName(common_helper_role)
            if (message.author in users_on_timeout):
                msg = await client.send_message(message.channel, message.author.mention + " Sorry, but you cannot ping a helper for " + str(users_on_timeout[message.author][0]) + " seconds.")
                messages_to_delete[msg] = 5
            else:   
                if (helper_role != ""):
                    role = discord.utils.get(message.server.roles, name=helper_role)
                    await client.edit_role(message.server, role, mentionable=True)
                    await client.send_message(message.channel, "Pinging " + role.mention + " for help.")
                    await client.edit_role(message.server, role, mentionable=False)
                    users_on_timeout[message.author] = [TIMEOUT_TIME, False]
                else:
                    await client.send_message(message.channel, message.author.mention + " Sorry, but there is no helper role \"" + common_helper_role + "\".")
        else:
            msg = await client.send_message(message.channel, message.author.mention + " Sorry, but you are blacklisted from pinging helpers.")
            messages_to_delete[message] = 5
            messages_to_delete[msg] = 5
    # Mod Only Commands
    if message.content.startswith('!blacklist'):
        role_names = [role.name for role in message.author.roles]
        #if "Mod" in role_names:
        if message.author.server_permissions.manage_server:
            user_name = message.content.split(" ")[1].lower()
            reason = " ".join(message.content.split(" ")[2:len(message.content.split(" "))]).lower()
            if (user_name.startswith("<@")):
                if (user_name not in blacklisted_users):
                    blacklisted_users.append(user_name)
                    msg = await client.send_message(message.channel, message.author.mention + (" %s is now blacklisted from pinging helpers. The reason given was: \n" % user_name) + reason)
                else:
                    msg = await client.send_message(message.channel, message.author.mention + " %s is already blacklisted from pinging helpers." % user_name)
                    messages_to_delete[msg] = 5
        else:
            msg = await client.send_message(message.channel, message.author.mention + " Sorry, but that command is mods only.")
            messages_to_delete[msg] = 5
    elif message.content.startswith('!unblacklist'):
        role_names = [role.name for role in message.author.roles]
        #if "Mod" in role_names:
        if message.author.server_permissions.manage_server:
            user_name = " ".join(message.content.split(" ")[1:len(message.content.split(" "))]).lower()
            if (user_name.startswith("<@")):
                if (user_name not in blacklisted_users):
                    msg = await client.send_message(message.channel, message.author.mention + " %s is alrady not blacklisted from pinging helpers." % user_name)
                    messages_to_delete[msg] = 5
                else:
                    blacklisted_users.remove(user_name)
                    msg = await client.send_message(message.channel, message.author.mention + " %s is no longer blacklisted from pinging helpers." % user_name)
        else:
            msg = await client.send_message(message.channel, message.author.mention + " Sorry, but that command is mods only.")
            messages_to_delete[msg] = 5

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name='By ACT Inc and jjam912'))
    client.loop.create_task(updateTimer())
    client.loop.create_task(removeMessages())

client.run(TOKEN)
save_object(blacklisted_users, "blacklist.pkl")
print ("Created 'blacklist.pkl'.")