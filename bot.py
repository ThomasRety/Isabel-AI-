import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from random import randint, choice

Client = discord.Client()
bot_prefix = ""
client = commands.Bot(command_prefix=bot_prefix)

help_msg = """ Voici une aide des commandes disponibles!\n
- $cool \n
- !commands : liste les commandes personnalisées \n
- !add : ajoute une commande personnalisée (uniquement admin) \n
- !music : donne une musique parmi celles ajoutées \n
- !youtube link : ajoute le link aux musiques déjà existantes (uniquement admin) \n
- !ping / !pong : permet de jouer au ping pong (uniquement dans #salle-de-sport \n
- !de : permet de jouer aux dés. Voir !helpdice pour plus d'informations\n
- !helpdice : permet d'afficher l'aide pour les dés.\n
- !sumdice nb_dice : fait la somme de NB_DICE de type des NB_DICE et renvoie des informations."""

help_dice = """ Voici l'aide des dés:\n
- !de\n
- !de [chiffre]\n
- !de [floor] [nombre des]\n
- !de [floor 1] [cible] [floor 2]\n
- !de [floor 1] [cible] [floor 2] [critical fail] [critical succes]\n"""

def open_commands():
    fd = open('./save/commands.txt', 'r')
    liste_command = {}
    for line in fd:
        try:
            liste = line.split('|')
            liste_command[liste[0]] = liste[1]
        except:
            pass
    fd.close()
    return (liste_command)

liste_command = open_commands()

def save_command(content):
    fd = open('./save/commands.txt', 'a')
    fd.write(content + '\n')
    fd.close()

def open_music():
    fd = open('./save/musics.txt', 'r')
    list_music = list()
    for line in fd:
        list_music.append(line)
    fd.close()
    return (list_music)

list_music = open_music()

def save_musics(content):
    fd = open('./save/musics.txt', 'a')
    fd.write(content + '\n')
    fd.close()

def open_curse():
    fd = open('./save/curses.txt', 'r')
    list_curses = list()
    for line in fd:
        list_curses.append(line)
    fd.close()
    return (list_curses)

list_curses = open_curse()

def save_curses(content):
    fd = open('./save/curses.txt', 'a')
    fd.write(content + '\n')
    fd.close()

def proba(x, max=100):
    y = randint(0, max)
    return (x == y)

def auth_author(message):
     return (message.author.id == "193824642304180224" or message.author.id == "150342658911502336")

def is_link_youtube(link):
    return (link.startswith("https://youtube.com") or link.startswith("https://www.youtube.com"))

def is_channel_banned(id):
    global list_banned
    for ia in list_banned:
        if(ia.startswith(id)):
            return True
    return False

def save_banned_channel(id):
    fd = open('./save/banned.txt', 'a')
    fd.write(id + "\n")
    fd.close()

def open_banned():
    fd = open('./save/banned.txt', 'r')
    list_banned = list()
    for line in fd:
        list_banned.append(line)
    fd.close()
    return (list_banned)

list_banned = open_banned()

@client.event
async def on_ready():
    print("Isabel Online")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    print("======================================")
   
@client.command(pass_context=True)
async def Isabel(ctx):
    await client.say("/tts Oui, C'est moi")

@client.command(pass_context=True)
async def liste_client(ctx):
    for server in client.servers:
        for member in server.members:
           await client.say("{} est présent.".format(member.name))


@client.event
async def on_member_join(member):
    print("member has joined")
    for server in client.servers:
        for channel in server.channels:
            if (channel.name == "dev"):
                channel1 = channel
            elif (channel.name == "annonces"):
                channel2 = channel
        for role in server.roles:
            if role.name == "Padawan":
                defaut_role = role
        break
    await client.send_message(channel1, "Welcome {}. You joined the server at {}".format(member.name, str(member.joined_at)))
    client.add_roles(member, defaut_role)
#    await client.send_message(channel2, "Welcome {}. You joined the server at {}".format(member.nick, str(member.joined_at)))

IA = "Isabel [IA]#6016"

@client.event
async def on_message(message):
    if (message.author.id == "359784743518339082"):
        return
    lock = 0
    global liste_command
    global list_music
    global help_msg
    global list_curses
    global list_banned
    global help_dice

    if (message.content.lower().startswith("!helpdice")):
        await client.send_message(message.channel, help_dice)
        return

    if message.content.lower() == "!help":
        await client.send_message(message.channel, help_msg)
        return

    if (message.content.lower().startswith("!sumdice")):
        nb_arg = message.content.lower().split(' ')
        nb_result = []
        n = 0
        try:
            nb_dice = int(nb_arg[1])
            if (nb_dice <= 0):
                await client.send_message(message.channel, "Usage: !sumdice nb_dice")
                return
            
            while (n < nb_dice):
                nb_result.append(randint(0, nb_dice))
                n = n + 1
            maxi = max(nb_result)
            mini = min(nb_result)
            sumd = sum(nb_result)
            moy = sumd / nb_dice
            result = "Nombre de dés: {}\nSomme: {}\nMoyenne: {}\nMinimum: {}\nMaximum: {}".format(str(nb_dice), str(sumd), str(moy), str(mini), str(maxi))
            await client.send_message(message.channel, result)

        except Exception as E:
            print(message.content)
            print(E)
            print('------------------------')
        return

    if (message.content.lower().startswith("!de")):
        nb_arg = message.content.lower().split(' ')
        if len(nb_arg) == 1:
            chiffre = randint(0,100)
            await client.send_message(message.channel, "Résultat: "+ str(chiffre))
            return
        
        elif (len(nb_arg) == 2):
            try:
                chiffre = randint(0, int(nb_arg[1]))
                await client.send_message(message.channel, "Résultat: " + str(chiffre))
            except Exception as E:
                print(E)
                await client.send_message(message.channel, "Usage: !de [chiffre]")
            return
        
        elif (len(nb_arg) == 3):
            try:
                nb_des = int(nb_arg[2])
                floor = int(nb_arg[1])
                result = "Resultat: "
                n = 0
                if nb_des <= 1:
                    await client.send_message(message.channel, "Erreur! Le nombre de dés doit être positif")
                    return
                while n != nb_des:
                    chiffre = randint(0, floor)
                    result = result + str(chiffre) + ' '
                    n = n + 1
                await client.send_message(message.channel, result)
            except Exception as E:
                print(E)
                await client.send_message(message.channel, "Usage: !de [floor] [nombre des]")
            return

        elif (len(nb_arg) == 4):
            try:
                floor_1 = int(nb_arg[1])
                floor_2 = int(nb_arg[3])
                target = int(nb_arg[2])
                if target < floor_1 or floor_1 >= floor_2:
                    print("Target = " + str(target) + " floor_1 = " + str(floor_1) + " floor_2 = " + str(floor_2) + " target < floor_1 : " + str(target < floor_1) + " floor 1 >= floor2: " + str(floor_1 >= floor_2))
                    await client.send_message(message.channel, "Usage: !de [floor 1] [cible] [floor 2]")
                    return
                chiffre = randint(floor_1, floor_2)
                if (chiffre == target):
                    await client.send_message(message.channel, "Réussite critique! Résultat = " + str(chiffre))
                    return
                elif (chiffre < target and (chiffre > (floor_1 + ((floor_2 - floor_1) * 0.1)))):
                    await client.send_message(message.channel, "Echec! Résultat = " + str(chiffre))
                elif (chiffre > target and (chiffre < (floor_2 + ((floor_2 - floor_1) * 0.1)))):
                    await client.send_message(message.channel, "Reussite! Résultat = " + str(chiffre))
                elif (chiffre < target and (chiffre < (floor_1 + ((floor_2 - floor_1) * 0.1)))):
                    await client.send_message(message.channel, "Echec critique! Résultat = " + str(chiffre))
                elif (chiffre > target and (chiffre > (floor_2 + ((floor_2 - floor_1) * 0.1)))):
                    await client.send_message(message.channel, "Réussite critique! Résultat = " + str(chiffre))
            except Exception as E:
                print(E)
                await client.send_message(message.channel, "Usage: !de [floor 1] [cible] [floor 2]")
            return

        elif (len(nb_arg) == 6):
            try:
                floor_1 = int(nb_arg[1])
                floor_2 = int(nb_arg[3])
                target = int(nb_arg[2])
                critical_fail = int(nb_arg[4])
                critique_succes = int(nb_arg[5])

                if critical_fail < floor_1 or critical_fail > critique_succes:
                    await client.send_message(message.channel, "Usage: !de [floor 1] [cible] [floor 2] [critical fail] [critical succes]")
                    return
                if critique_succes > floor_2:
                    await client.send_message(message.channel, "Usage: !de [floor 1] [cible] [floor 2] [critical fail] [critical succes]")
                    return                    
                if target < floor_1 or floor_2 <= floor_1:
                    await client.send_message(message.channel, "Usage: !de [floor 1] [cible] [floor 2] [critical fail] [critical succes]")
                    return
                
                chiffre = randint(floor_1, floor_2)
                if (chiffre == target):
                    await client.send_message(message.channel, "Réussite critique! Résultat = " + str(chiffre))
                    return
                elif (chiffre < target and (chiffre > critical_fail)):
                    await client.send_message(message.channel, "Echec! Résultat = " + str(chiffre))
                elif (chiffre > target and (chiffre < critique_succes )):
                    await client.send_message(message.channel, "Reussite! Résultat = " + str(chiffre))
                elif (chiffre < target and (chiffre < critical_fail)):
                    await client.send_message(message.channel, "Echec critique! Résultat = " + str(chiffre))
                elif (chiffre > target and (chiffre > critique_succes)):
                    await client.send_message(message.channel, "Réussite critique! Résultat = " + str(chiffre))
            except Exception as E:
                print(E)
                await client.send_message(message.channel, "Usage: !de [floor 1] [cible] [floor 2] [critical fail] [critical succes]")
                return
            return
        
    if (is_channel_banned(message.channel.id)):
        print(message.channel.name)
        return

    if message.content.lower() == "!banisabel" and auth_author(message):
        print(len(message.content.lower()))
        if len(message.content.lower()) > len("!banisabel"):
            save_banned_channel(message.content.lower()[len("!banisabel"):])
        else:
            save_banned_channel(message.channel.id)
        list_banned = open_banned()
        return
    
    if message.content.lower().startswith("!curses") and auth_author(message):
        if len(message.content) >= 8:
            message.content = message.content[8:]
            save_curses(message.content)
            list_curses = open_curse()
        else:
            s = "Voici la liste des mots interdits: " + "\n"
            for key in list_curses:
                s = s + key 
            print(s)
            await client.send_message(message.channel, s)
        return
    
    if message.content.startswith('!add') and auth_author(message):
        print(message.content[5:])
        try:
            content = message.content[5:]
            save_command(content)
            liste_command = open_commands()
        except:
            client.send_message(message.channel, "Essayez !add question|reponses")
        return

    if message.content.lower().startswith('!youtube') and auth_author(message):
        print(message.content[9:])
        message.content = message.content[9:]
        if not is_link_youtube(message.content):
            await client.send_message(message.channel, "Ceci n'est pas un lien youtube")
            return
        print("Le lien est bien de youtube")
        save_musics(message.content)
        list_music = open_music()

    if message.content.lower().startswith("!music") and (message.channel.id == "360516429813907479" or message.channel.id == "360874716472279053" or message.channel.id == "360128517591138324"):
        try:
            music = choice(list_music)
            await client.send_message(message.channel, "Voici une musique: " + music)
        except Exception as E:
            await client.send_message(message.channel, "Erreur: il n'y a aucune musique d'ajoutée")
            print("Exception = " + E)
            print(list_music)

    if message.content.startswith("$secret") and (message.author.id == "193824642304180224" or message.author.id == "150342658911502336" or message.author.id == "339290266169114626"):
        liste_member = ''
        liste_channel = ''
        for server in client.servers:
            for member in server.members:
                liste_member = liste_member + '\n' + member.name + ' ' + member.id
            for channel in server.channels:
                if channel.name == "dev":
                    channel1 = channel
                liste_channel = liste_channel + '\n' + channel.id + ' ' + channel.name
        await client.send_message(channel1, "Secret = " + message.channel.id)
        print(message.channel.id)
        await client.send_message(channel1, liste_member)
        await client.send_message(channel1, liste_channel)
        print(liste_member)
        print(liste_channel)
    if message.content.startswith("$secret") and not (message.author.id == "193824642304180224" or message.author.id == "150342658911502336" or message.author.id == "339290266169114626"):
        await client.send_message(message.channel, "Vous n'avez pas la permission d'effecter cette commande")
    if message.content.startswith('$cool') and message.author.name == "Tristan Starkl El Destructor":
        await client.send_message(message.channel, 'Qui est cool? Tape Tristan ici')

        def check(msg):
            return (msg.content.startswith('Tristan'))

        message = await client.wait_for_message(author=message.author, check=check)
        await client.send_message(message.channel, '{} est cool en effet'.format("Tristan"))

    if message.content.startswith('$cool') and message.author.name == "Ael's":
        await client.send_message(message.channel, 'Qui est cool? Tape Ael\'s ici')

        def check(msg):
            return (msg.content.startswith("Ael's"))

        message = await client.wait_for_message(author=message.author, check=check)
        await client.send_message(message.channel, '{} est cool en effet'.format("Ael's"))
        
    if message.content.startswith('$cool') and (message.author.name != "Ael's" and message.author.name != "Tristan Starkl El Destructor"):
        await client.send_message(message.channel, 'Qui est cool? SPOILER...PAS TOI')

    if message.content.startswith("!invitation"):
        for server in client.servers:
            for channel in server.channels:
                if channel == message.channel:
                    invites = client.create_invite(server, max_age=30, max_uses=1)
                    
#                    await client.send_message(message.channel, next(invite).url)
                    break

    if message.content.lower().startswith("bonjour isabel"):
        await client.send_message(message.channel, 'Bonjour ' + message.author.name + ' !')
        lock = 1
    if message.content.lower().startswith("bonjour") and message.author.id != "359784743518339082" and lock == 0:
        await client.send_message(message.channel, 'Bonjour!')
    if message.content.lower().startswith("au revoir isabel") and lock == 0:
        await client.send_message(message.channel, 'Au revoir ' + message.author.name + ' !')
        lock = 1
    if message.content.lower().startswith("au revoir") and message.author.id != "359784743518339082" and lock == 0:
        await client.send_message(message.channel, 'Au revoir!')
    if message.content.lower().startswith("bonsoir isabel") and lock == 0:
        await client.send_message(message.channel, 'Bonsoir ' + message.author.name + ' !')
        lock = 1
    if message.content.lower().startswith("bonsoir") and message.author.id != "359784743518339082" and lock == 0:
        await client.send_message(message.channel, 'Bonsoir')

    #PING PONG GAME

    if (message.content.lower().startswith("!pong") or message.content.lower().startswith("!ping")) and (message.channel.id == "360516429813907479" or message.channel.id == "360128517591138324"):
        await client.send_message(message.channel, 'Ping!' if message.content.lower().startswith("!pong") else "Pong!")
        if (proba(1, 6)):
            await client.send_message(message.channel, "J'ai gagné")
            def check(msg):
                return (msg.content.lower().startswith("gg") or msg.content.lower().startswith("conasse"))

            message = await client.wait_for_message(check=check)
            if message.content.lower().startswith("conasse"):
                karma = -1
            else:
                karma = 1
                await client.send_message(message.channel, "GG à toi aussi")
            print(karma)
        elif proba(1, randint(1, 25)):
            await client.send_message(message.channel, "Arf, j'ai raté")
            def check(msg):
                return (msg.content.lower().startswith("gg"))

            message = await client.wait_for_message(check=check)
            await client.send_message(message.channel, "Bien Joué à toi aussi")

    if message.content.lower() == "!commands":
        s = ''
        if len(liste_command) == 0:
            await client.send_message(message.channel, "Il y a aucune commande personnalisé pour l'instant.")
        for keys in liste_command:
            s = s + 'Commande : ' + keys + ' Réponse: ' + liste_command[keys] + '\n'
        await client.send_message(message.channel, s)

    for keys in list_curses:
        if keys.lower() == (message.content.lower() + '\n'):
            await client.send_message(message.channel, "Ne pronnoncez pas ce mot!")

    
    for keys in liste_command:
        if keys.lower() == message.content.lower():
            await client.send_message(message.channel, liste_command[keys])
            break

        
@client.event
async def on_typing(channel, user, when):
    if (is_channel_banned(channel.id)):
        return
    if user.id == "150342658911502336" and proba(1, 33):
        print('Aels le grand réfléchit')
        await client.send_message(channel, 'AELS LE GRAND REFLECHIT')
    elif user.id == "193824642304180224" and proba(1, 40):
        print('Tristan parle')
        await client.send_message(channel, 'SHUT UP TRISTAN PARLE')
    elif user.id == "230278412365725696" and proba(1, 30) and message.channel.id != "360516429813907479":
        print('Kebab parle')
        await client.send_message(channel, 'FUYEZ KEBAB PARLE')
  #  elif user.id == "337971676027289600" and proba(1, 2) and channel.id != "339208165482692608":
   #     await client.send_message(channel, "Ecoutez moi, car l'autre Isabel ne répand que mensonges...")

client.run("MzU5Nzg0NzQzNTE4MzM5MDgy.DKPrxA.xxcA9zwf9f2G1FYe7snbW1zmFEk")
