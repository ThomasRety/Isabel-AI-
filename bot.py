import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from random import randint, choice
import sqlite3
import re

Client = discord.Client()
bot_prefix = ""
client = commands.Bot(command_prefix=bot_prefix)


VERSION = "1.1.4"
CHANGELOG = ""
dbPath = "./save/database.db"

help_msg = """ Voici une aide des commandes disponibles!\n
- $cool \n
- !commands : liste les commandes personnalisées \n
- !add : ajoute une commande personnalisée (uniquement admin) \n
- !music : donne une musique parmi celles ajoutées \n
- !youtube link : ajoute le link aux musiques déjà existantes (uniquement admin) \n
- !ping / !pong : permet de jouer au ping pong (uniquement dans #salle-de-sport \n
- !de : permet de jouer aux dés. Voir !helpdice pour plus d'informations\n
- !helpdice : permet d'afficher l'aide pour les dés.\n
- !sumdice nb_dice [floor]: fait la somme de NB_DICE de type des NB_DICE et renvoie des informations.\n
- !version : renvoie la version de l'IA.\n
- !changelog : renvoie le changelog de la dernière version\n
- !curses [add] : Ajoute add aux mots interdits si spécifiés, sinon liste les mots interdits. [add] nécéssite d'être administrateur."""

help_dice = """ Voici l'aide des dés:\n
- !de\n
- !de [chiffre]\n
- !de [floor] [nombre des]\n
- !de [floor 1] [cible] [floor 2]\n
- !de [floor 1] [cible] [floor 2] [critical fail] [critical succes]\n"""

def getChangelog(CHANGELOG):
    with open('./changelog.log', 'r') as f:
        for line in f:
            CHANGELOG += line
    return (CHANGELOG)

CHANGELOG = getChangelog(CHANGELOG)

def getOldVersion():
    global VERSION
    old = ""
    try:
        with open('./.old', 'r') as f:
            old = f.readline()
        return old
    except Exception as E:
        try:
            with open('./.old', 'a') as f:
                f.write(VERSION)
            return VERSION
        except Exception as E:
            print(E)
            import sys
            sys.exit(-1)

def getCommands(idServer):
    a = dict()
    f = "SELECT command, response FROM personnalisedCommands WHERE idServer='{}'".format(idServer)
    rows = executeCommand(f)
    if rows is False:
        pass
    else:
        try:
            for r in rows:
                a[r[0]] = r[1]
        except Exception as E:
            pass
    return a


def save_command(idServer, command, response):
    f = "INSERT INTO personnalisedCommands(idServer, command, response) VALUES('{}', '{}', '{}')".format(idServer, command, response)
    executeCommand(f)
    
def getMusics(idServer):
    f = "SELECT link FROM musicsLink WHERE idServer = '{}'".format(idServer)
    row = executeCommand(f)
    a = list()
    if (row is not False):
        for truc in row:
            for musics in truc:
                a.append(musics)
    return (a)


def modifKarma(message, howMuch):
    idServer = message.server.id
    idPlayer = message.author.id
    f = "SELECT karma FROM karma WHERE idServer = '{}' and idPlayer = '{}'".format(idServer, idPlayer)
    row = executeCommand(f)
    if row is False:
        return
    try:
        if len(row) == 0:
            f = "INSERT INTO karma(idServer, idPlayer, karma) VALUES('{}', '{}', {})".format(idServer, idPlayer, str(howMuch))
            executeCommand(f)
            return
    except Exception as E:
        pass
    try:
        karma = row[0][0]
        f = "UPDATE karma SET karma = {} WHERE idPlayer = '{}' and idServer = '{}'".format(str(karma+howMuch), idPlayer, idServer)
        executeCommand(f)
    except Exception as E:
        print ("mdofiKarma UPDATE", E)
    return


def getIdPlayer(name):
    if name.isdigit():
        return name
    #dans ce cas là c'est le Name du gars
    f = "SELECT idPlayer FROM player WHERE name = '{}'".format(name)
    row = executeCommand(f)
    if row is False or len(row) == 0:
        return False
    try:
        return (row[0][0])
    except:
        return False


def modifKarma2(name, idServer, howMuch):
    idPlayer = getIdPlayer(name)
    if idPlayer is False:
        return
    f = "SELECT karma FROM karma WHERE idServer = '{}' and idPlayer = '{}'".format(idServer, idPlayer)
    row = executeCommand(f)
    if row is False:
        return
    try:
        if len(row) == 0:
            f = "INSERT INTO karma(idServer, idPlayer, karma) VALUES('{}', '{}', {})".format(idServer, idPlayer, str(howMuch))
            executeCommand(f)
            return
    except Exception as E:
        pass
    try:
        karma = row[0][0]
        f = "UPDATE karma SET karma = {} WHERE idPlayer = '{}' and idServer = '{}'".format(str(karma+howMuch), idPlayer, idServer)
        executeCommand(f)
    except Exception as E:
        print ("mdofiKarma UPDATE", E)
    return

def getScoreboardKarma(message):
    idServer = message.server.id
    f = "SELECT karma, idPlayer FROM karma WHERE idServer = '{}' ORDER BY karma DESC".format(idServer)
    row = executeCommand(f)
    a = ""
    try:
        if row is False:
            return ("Aucun joueur n'as encore de Karma sur ce serveur!")
        if len(row) == 0:
            return ("Aucun joueur n'as encore de Karma sur ce serveur!")
        print (row)
        for truc in row:
            b = "SELECT name FROM player WHERE idPlayer = '{}'".format(truc[1])
            c = getData(b)
            if c is not False:
                a += c + ' : ' + str(truc[0]) + '\n'
        print ("getScoreboardKarma message = ", a)
    except Exception as E:
        print ("getScoreboard :", E)
    return (a)
    
def getKarma(message):
    idServer = message.server.id
    idPlayer = message.author.id
    f = "SELECT karma FROM karma WHERE idServer = '{}' and idPlayer = '{}'".format(idServer, idPlayer)
    row = executeCommand(f)
    try:
        if row is False:
            return ("Erreur")
        if len(row) == 0:
            return ("Vous n'avez pas de karma!")
        return ("Votre karma est : " + str(row[0][0]))
    except Exception as E:
        print ("getKarma Exception : ", E)
    return ("")

def save_musics(link, idServer, name=None):
    f = "INSERT INTO musicsLink(idServer, link, name) VALUES('{}, '{}', '{}')".format(idServer, link, name)
    executeCommand(f)

def getCurses(idServer):
    f = "SELECT curseWord FROM cursesWords WHERE idServer = '{}'".format(idServer)
    row = executeCommand(f)
    if (row == False):
        return (list())
    a = list()
    try:
        for truc in row:
            for curses in truc:
                a.append(curses)
    except Exception as E:
        return (list())
    return (a)

def save_curses(message, word):
    f = "INSERT INTO cursesWords(idServer, curseWord) VALUES ('{}', '{}')".format(message.server.id, word)
    executeCommand(f)
    
def getWords(message):
    return re.compile('\w+').findall(message)

def safeData(text):
    a = ""
    b = re.compile("[^']").findall(text)
    for letter in b:
        a += letter
    return a

def proba(x, max=100):
    y = randint(0, max)
    return (x == y)

def auth_author(message):
    serverId = message.server.id
    f = "SELECT idPeople from adminsIA where idServer = '{}'".format(serverId)
    row = executeCommand(f)
    if (row == False):
        return (False)
    try:
        for peoples in row:
            if (message.author.id in peoples):
                return (True)
        return (False)
    except Exception as E:
        print(E)

def is_link_youtube(link):
    link = safeData(link)
    return (link.startswith("https://youtube.com") or link.startswith("https://www.youtube.com"))

def is_channel_banned(message):
    serverId = message.server.id
    f = "SELECT idChannel FROM bannedChannels where idServer = '{}'".format(serverId)
    row = executeCommand(f)
    if (row == False):
        return (True)
    try:
        for ids in row:
            if (message.channel.id in ids):
                return (True)
        return (False)
    except Exception as E:
        print(E)
    return (True)

def save_banned_channel(message, id):
    serverId = message.server.id
    f = "INSERT INTO bannedChannels(idServer, idChannel) VALUES ('{}', '{}')".format(serverId, id)
    executeCommand(f)
    

##### DB PART

def executeCommand(f):
    global dbPath
    conn = sqlite3.connect(dbPath)
    c = conn.cursor()
    try:
        c.execute(f)
    except sqlite3.OperationalError as E:
        print("Requete plante", f)
        print(E)
        return (False)
    row = c.fetchall()
    conn.commit()
    conn.close()
    return (row)

def getData(request):
    row = executeCommand(request)
    if row == False:
        return (False)
    try:
        return (row[0][0])
    except:
        return (False)

def insertPlayer(message):
    idPlayer = message.author.id
    name = message.author.name
    name = safeData(name)
    f = "SELECT name FROM player where idPlayer = '{}'".format(idPlayer)
    row = executeCommand(f)
    try:
        if row is False:
            return
        if len(row) == 0:
            f = "INSERT INTO player(idPlayer, name) VALUES('{}', '{}')".format(idPlayer, name)
            executeCommand(f)
        else:
            f = "UPDATE player SET name = '{}' WHERE idPlayer = '{}'".format(name, idPlayer)
            executeCommand(f)
    except Exception as E:
        print ("Insert Player Exception : ", E)

@client.event
async def on_ready():
    global VERSION
    print("Isabel Online")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    print("VERSION: {}".format(VERSION))
    old = getOldVersion()
    if VERSION != old:
        for servers in client.servers:
            await client.send_message(servers, "Isabel est maintenant en version: " + VERSION)
    print("======================================")


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
    #l'IA ne parse pas ses propres messages
    if (message.author.id == "359784743518339082"):
        return
    lock = 0
    global CHANGELOG
    global VERSION
    global help_msg
    global help_dice


    insertPlayer(message)
    modifKarma(message, 0)
    if (message.content.lower() == "!changelog"):
        await client.send_message(message.channel, CHANGELOG)
        return

    if (message.content.lower() == "!version"):
        await client.send_message(message.channel, "La version actuelle est: {}".format(VERSION), tts=True)
        return
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
            floor = 6 if (len(nb_arg) == 2) else int(nb_arg[2])
            nb_dice = int(nb_arg[1])
            if (nb_dice <= 0):
                await client.send_message(message.channel, "Usage: !sumdice nb_dice")
                return
            
            while (n < nb_dice):
                nb_result.append(randint(0, floor))
                n = n + 1
            maxi = max(nb_result)
            mini = min(nb_result)
            sumd = sum(nb_result)
            moy = sumd / nb_dice
            result = "Nombre de dés: {}\nSomme: {}\nMoyenne: {}\nMinimum: {}\nMaximum: {}".format(str(nb_dice), str(sumd), str(moy), str(mini), str(maxi))
            await client.send_message(message.channel, result)
            a = ''
            for result in nb_result:
                a = a + str(result) + ' '
            await client.send_message(message.channel, 'Résultat des dés: {}'.format(a))
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
                    await client.send_message(message.channel, "Réussite! Résultat = " + str(chiffre))
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
        
    if (is_channel_banned(message)):
        print(message.channel.name)
        return

    if message.content.lower() == "!banisabel" and auth_author(message):
        print(len(message.content.lower()))
        if len(message.content.lower()) > len("!banisabel"):
            save_banned_channel(message, message.content.lower()[len("!banisabel"):])
        else:
            save_banned_channel(message, message.channel.id)
        return
    
    if message.content.lower().startswith("!curses") and  len(message.content) >= 8 and auth_author(message):
        message.content = message.content[8:]
        save_curses(message, message.content)

    elif message.content.lower().startswith("!curses"):
        s = "Voici la liste des mots interdits: " + "\n"
        list_curses = getCurses(message.server.id)
        for key in list_curses:
            s = s + key 
            await client.send_message(message.channel, s)
        return
    
    if message.content.startswith('!add') and auth_author(message):
        print(message.content[5:])
        try:
            content = message.content[5:]
            content = content.split('|')
            try:
                command = content[0]
                response = content[1]
            except Exception as E:
                raise
            save_command(message.server.id, command, response)
        except:
            client.send_message(message.channel, "Essayez !add question|reponses")
        return

    if message.content.lower().startswith('!youtube') and auth_author(message):
        print(message.content[9:])
        message.content = message.content[9:]
        if not is_link_youtube(message.content):
            await client.send_message(message.channel, "Ceci n'est pas un lien youtube")
            return
        message.content = message.content.split(' ')
        if len(message.content) == 2:
            save_musics(message.content[0], message.server.id, message.content[1])
        else:
            save_musics(message.content[0], message.server.id)

    if message.content.lower().startswith("!music") and (message.channel.id == "360516429813907479" or message.channel.id == "360874716472279053" or message.channel.id == "360128517591138324"):
        listeMusic = getMusics(message.server.id)
        if len(listeMusic) > 0:
            await client.send_message(message.channel, "Voici une musique: " + music)
            music = choice(listeMusic)
            await client.send_message(message.channel, str(music))
        else:
            await client.send_message(message.channel, "Erreur: il n'y a aucune musique d'ajoutée")

    if message.content.startswith("$secret") and (auth_author(message)):
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
    if message.content.startswith("$secret") and not auth_author(message):
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

    if message.content.lower().startswith("!karma"):
        if len(message.content.lower()) > (len("!karma") + 1):
            await client.send_message(message.channel, getScoreboardKarma(message))
        else:
            await client.send_message(message.channel, str(getKarma(message)))
            
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
                modifKarma(message, -1)
            else:
                modifKarma(message, +1)
                await client.send_message(message.channel, "GG à toi aussi")
        elif proba(1, randint(1, 25)):
            await client.send_message(message.channel, "Arf, j'ai raté")
            def check(msg):
                return (msg.content.lower().startswith("gg"))

            message = await client.wait_for_message(check=check)
            await client.send_message(message.channel, "Bien Joué à toi aussi")

    if (message.content.lower().startswith("!modifkarma") and auth_author(message)):
        try:
            message.content = message.content.lower().split(' ')
        except:
            return
        if len(message.content) == 3:
            name = safeData(message.content[1])
            try:
                howMuch = int(message.content[2])
            except:
                return
            idServer = message.server.id
            modifKarma2(name, idServer, howMuch)
        elif len(message.content) == 2:
            try:
                howMuch = int(message.content[2])
            except:
                return
            modifKarma(message, howMuch)
        elif len(message.content) == 1:
            return
        else:
            try:
                howMuch = int(message.content[-1])
            except:
                return
            idServer = message.server.id
            name = message.content[1:-1]
            for N in name:
                modifKarma2(N, idServer, howMuch)
            
    if message.content.lower() == "!commands":
        s = ''
        liste_command = getCommands(message.server.id)
        if len(liste_command) == 0:
            await client.send_message(message.channel, "Il y a aucune commande personnalisé pour l'instant.")
        for keys in liste_command:
            s = s + 'Commande : ' + keys + ' Réponse: ' + liste_command[keys] + '\n'
        await client.send_message(message.channel, s)

    a = getCurses(message.server.id)
    b = getWords(message.content.lower())
    for curse in a:
        for word in b:
            if word.lower() == curse.lower():
                await client.send_message(message.channel, "Ne prononcez pas ce mot!")
                modifKarma(message, -1)

    a = getCommands(message.server.id)
    b = a.get(message.content.lower())
    if b is not None:
        await client.send_message(message.channel, b)
    


        

client.run("MzU5Nzg0NzQzNTE4MzM5MDgy.DKPrxA.xxcA9zwf9f2G1FYe7snbW1zmFEk")
