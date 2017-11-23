import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from random import randint, choice
import sqlite3
import re
import logging

Client = discord.Client()
bot_prefix = ""
client = commands.Bot(command_prefix=bot_prefix)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

VERSION = "1.3.0 Major Update!"
CHANGELOG = ""
dbPath = "./save/database.db"

help_msg = """ Voici une aide des commandes disponibles!\n
- $cool \n
- !commands : liste les commandes personnalisées \n
- !add command|response [|option=Value]: ajoute une commande personnalisée (uniquement admin) \n
- !music : donne une musique parmi celles ajoutées \n
- !youtube link : ajoute le link aux musiques déjà existantes (uniquement admin) \n
- !ping / !pong : permet de jouer au ping pong (uniquement dans #salle-de-sport \n
- !de : permet de jouer aux dés. Voir !helpdice pour plus d'informations\n
- !helpdice : permet d'afficher l'aide pour les dés.\n
- !sumdice nb_dice [floor]: fait la somme de NB_DICE de type des NB_DICE et renvoie des informations.\n
- !version : renvoie la version de l'IA.\n
- !changelog : renvoie le changelog de la dernière version\n
- !curses [add] : Ajoute add aux mots interdits si spécifiés, sinon liste les mots interdits. [add] nécéssite d'être administrateur.\n
- !setAuthorized PingPong|Music|Secret|Commands : authorise le channel à jouer l'option spécifié\n
- !unAuthorized PingPong|Music|Secret|Commands : enlève l'autorisation de ce channel à jouer l'option spécifié
- !setDefaultChannel [idChannel] : spécifie le channel comme étant un channel par défaut\n
- !unsetDefaultChannel [idChannel] : enlève le channel spécifié des channels par défauts"""

help_dice = """ Voici l'aide des dés:\n
- !de\n
- !de [chiffre]\n
- !de [floor] [nombre des]\n
- !de [floor 1] [cible] [floor 2]\n
- !de [floor 1] [cible] [floor 2] [critical fail] [critical succes]\n"""

def proba(x, max=100):
    y = randint(0, max)
    return (x == y)

############################################################################################################################################
########################################################### DB PART ########################################################################
############################################################################################################################################

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
   
############################################################################################################################################
########################################################### GET DATA #######################################################################
############################################################################################################################################

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
    
def getWords(message):
    return re.compile('\w+').findall(message)

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

def safeData(text):
    a = ""
    b = re.compile("[^']").findall(text)
    for letter in b:
        a += letter
    return a
    
def getMusics(idServer):
    f = "SELECT link FROM musicsLink WHERE idServer = '{}'".format(idServer)
    row = executeCommand(f)
    a = list()
    if (row is not False):
        for truc in row:
            for musics in truc:
                a.append(musics)
    return (a)

def getData(request):
    row = executeCommand(request)
    if row == False:
        return (False)
    try:
        return (row[0][0])
    except:
        return (False)

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

def getCommands(message, authorizationLevel):
    idServer = message.server.id
    content = safeData(message.content.lower())
    f = "SELECT response FROM personnalisedCommands WHERE idServer='{}' AND command = '{}' AND needLevel <= {}".format(idServer, content, str(authorizationLevel))
    rows = executeCommand(f)
    if rows is False or len(rows) == 0:
        return False
    else:
        try:
            row = rows[0][0]
        except Exception as E:
            pass
    if authorizationLevel >= 3:
        return row
    f = getAuthorization("authorizationCommands", message.channel.id, message.channel.id)
    if f is False:
        return row
    return False

def getListCommands(idServer, authorizationLevel):
    a = dict()
    f = "SELECT command, response FROM personnalisedCommands WHERE idServer= '{}' AND needLevel <= {}".format(idServer, str(authorizationLevel))
    rows = executeCommand(f)
    if rows is False or len(rows) == 0:
        return False
    try:
        for row in rows:
            a[row[0]] = row[1]
    except Exception as E:
        return False
    return a

def getChangelog(CHANGELOG):
    with open('./changelog.log', 'r') as f:
        for line in f:
            CHANGELOG += line
    return (CHANGELOG)

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

def getQuestion(message, defaultMessage='needAuthorization', defaultValue=0):
    try:
        question = message.split('|')
        command = question[0]
        response = question[1]
        option = defaultMessage
        value = defaultValue
        try:
            options = question[2]
            options = options.split('=')
            if options[0] is not "":
                option = options[0]
            value = options[1]
        except Exception as E:
            pass
        finally:
            return command, response, option, value
    except Exception as E:
        print ("Problème : ", E)
    return False, False, False, False

############################################################################################################################################
########################################################### AUTHORIZATION ##################################################################
############################################################################################################################################

def getAuthorizationLevel(message):
    serverId = message.server.id
    f = "SELECT authorizationLevel FROM player WHERE idServer = '{}' AND idPlayer = '{}'".format(serverId, idPlayer)
    row = executeCommand(f)
    if (row == False) or len(row) == 0:
        return (False)
    try:
        return (row[0][0])
    except Exception as E:
        print(E)

def is_link_youtube(link):
    link = safeData(link)
    return (link.startswith("https://youtube.com") or link.startswith("https://www.youtube.com"))

def is_channel_banned(message):
    serverId = message.server.id
    f = "SELECT idChannel FROM bannedChannels WHERE idServer = '{}'".format(serverId)
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


def isAuthorizedChannelSpecified(mode, idServer):
    f = "SELECT * FROM {} WHERE idServer = '{}'".format(mode, isServer)
    row = executeCommand(f)
    if row is False or len(row) == 0:
        return (False)
    return (True)

def getAuthorization(mode, idServer, idChannel):
    f = "SELECT * FROM {} WHERE idServer = '{}' AND idChannel = '{}'".format(mode, idServer, idChannel)
    row = executeCommand(f)
    if row is False or len(row) == 0:
        return (False)
    return (True)

def getAuthorizationSecret(idServer, idChannel):
    f = "SELECT * FROM authorizationSecret WHERE idServer = '{}' AND idChannel = '{}' LIMIT 1".format(idServer, idChannel)
    row = executeCommand(f)
    if row is False or len(row) == 0:
        return (False)
    try:
        return row[0][0]
    except Exception as E:
        return False


def getDefaultChannel(idServer):
    f = "SELECT idChannel FROM defaultChannel WHERE idServer = '{}'".format(idServer)
    rows = executeCommand(f)
    if rows is False or len(rows) == 0:
        return False
    try:
        a = list()
        for row in rows:
            a.append(row[0])
        return (a)
    except Exception as E:
        print("getDefaultChannel", E)
        return False
        
def setAuthorization(mode, idServer, idChannel):
    f = "INSERT INTO {}(idServer, idChannel) VALUES('{}', '{}')".format(mode, idServer, idChannel)
    executeCommand(f)

    
def deleteAuthorization(mode, idServer, idChannel):
    f = "DELETE FROM {} WHERE idServer = '{}' AND idChannel = '{}'".format(mode, idServer, idChannel)
    executeCommand(f)


def setAuthorizationLevel(idServer, idPlayer, authorizalionLevel):
    f = "UPDATE player SET authorizationLevel = {} WHERE idPlayer = '{}' AND idServer = '{}'".format(str(authorizationLevel), idPlayer, idServer)
    executeCommand(f)

############################################################################################################################################
########################################################### SAVE DATA ######################################################################
############################################################################################################################################


def save_musics(link, idServer, name=None):
    f = "INSERT INTO musicsLink(idServer, link, name) VALUES('{}, '{}', '{}')".format(idServer, link, name)
    executeCommand(f)

def save_banned_channel(message, id):
    serverId = message.server.id
    f = "INSERT INTO bannedChannels(idServer, idChannel) VALUES ('{}', '{}')".format(serverId, id)
    executeCommand(f)


def saveDefaultChannel(message, id):
    serverId = message.server.id
    f = "INSERT INTO defaultChannel(idServer, idChannel) VALUES('{}', '{}')".format(serverId, id)
    executeCommand(f)

def save_curses(message, word):
    f = "INSERT INTO cursesWords(idServer, curseWord) VALUES ('{}', '{}')".format(message.server.id, word)
    executeCommand(f)

def save_command(idServer, content, defaultMessage='needLevel', defaultValue=1):
    command, response, option, value = getQuestion(content, defaultMessage=defaultMessage, defaultValue=defaultValue)
    f = "SELECT * FROM personnalisedCommands WHERE idServer = '{}' AND command = '{}'".format(idServer, command)
    row = executeCommand(f)
    if len(row) != 0:
        return ("La commande existe déjà")
    if command is False:
        return ("REQUETE PLANTE")
    f = "INSERT INTO personnalisedCommands(idServer, command, response, {}) VALUES('{}', '{}', '{}', '{}')".format(option, idServer, command, response, str(value))
    row = executeCommand(f)
    if row is False:
        return ("Erreur, l'option n'existe pas")
    return ("La commande a été ajoutée avec succès")


############################################################################################################################################
########################################################### KARMA FUNCTIONS#################################################################
############################################################################################################################################

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

############################################################################################################################################
########################################################### LAUNCH IA ######################################################################
############################################################################################################################################

def insertPlayer(message):
    idPlayer = message.author.id
    name = message.author.name
    name = safeData(name)
    idServer = message.server.id
    f = "SELECT name FROM player where idPlayer = '{}' AND idServer = '{}'".format(idPlayer, idServer)
    row = executeCommand(f)
    try:
        if row is False:
            return
        if len(row) == 0:
            f = "INSERT INTO player(idPlayer, name, idServer) VALUES('{}', '{}')".format(idPlayer, name)
            executeCommand(f)
        else:
            f = "UPDATE player SET name = '{}' WHERE idPlayer = '{}' AND idServer = '{}'".format(name, idPlayer, idServer)
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

CHANGELOG = getChangelog(CHANGELOG)

@client.event
async def on_member_join(member):
    print("member has joined")
    idServer = member.server.id
    listIdChannel = getDefaultChannel(idServer)
    if listIdChannel == False:
        return
    for server in client.servers:
        if server.id == idServer:
            for idChannel in listIdChannel:
                for channel in server.channels:
                    if idChannel == channel.id:
                        await client.send_message(channel, "Welcome {}. You joined the server at {}".format(member.name, str(member.joined_at)))
    

IA = "Isabel [IA]#6016"

############################################################################################################################################
########################################################### IA #############################################################################
############################################################################################################################################

@client.event
async def on_message(message):
    #l'IA ne parse pas ses propres messages
    authorizationLevel = getAuthorizationLevel(message)
    if authorizationLevel is False or authorizationLevel == 0:
        return

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

    if message.content.lower() == "!banisabel" and authorizationLevel >= 3:
        print(len(message.content.lower()))
        if len(message.content.lower()) > len("!banisabel"):
            save_banned_channel(message, message.content.lower()[len("!banisabel"):])
        else:
            save_banned_channel(message, message.channel.id)
        return
    
    if message.content.lower().startswith("!curses") and  len(message.content) >= 8 and authorizationLevel >= 3:
        message.content = message.content[8:]
        save_curses(message, message.content)

    elif message.content.lower().startswith("!curses"):
        s = "Voici la liste des mots interdits: " + "\n"
        list_curses = getCurses(message.server.id)
        for key in list_curses:
            s = s + key 
            await client.send_message(message.channel, s)
        return
    
    if message.content.startswith('!add') and authorizationLevel == 4:
        print(message.content[5:])
        try:
            content = message.content[5:]
            await client.send_message(channel, save_command(message, content))
        except:
            client.send_message(message.channel, "Essayez !add question|reponses")
        return

    if message.content.lower().startswith('!youtube') and authorizationLevel >= 2:
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

    if message.content.lower().startswith("!music") and ((isAuthorizedChannelSpecified("authorizationMusic", message.server.id) == True and
                                                          getAuthorization("authorizationMusic", message.server.id, message.channel.id))
                                                         or (authorizationLevel >= 3) or (isAuthorizedChannelSpecified("authorizationMusic", message.server.id) == False)):
        listeMusic = getMusics(message.server.id)
        if len(listeMusic) > 0:
            await client.send_message(message.channel, "Voici une musique: " + music)
            music = choice(listeMusic)
            await client.send_message(message.channel, str(music))
        else:
            await client.send_message(message.channel, "Erreur: il n'y a aucune musique d'ajoutée")

    if message.content.startswith("$secret") and authorizationLevel == 4:
        liste_member = ''
        liste_channel = ''
        channel1 = getAuthorizationSecret(message.server.id)
        if channel1 == False:
            channel1 = message.channel
        for server in client.servers:
            if server.id == message.server.id:
                for member in server.members:
                    liste_member = liste_member + '\n' + member.name + ' ' + member.id
                for channel in server.channels:
                    liste_channel = liste_channel + '\n' + channel.id + ' ' + channel.name
        await client.send_message(channel1, "Secret = " + message.channel.id)
        print(message.channel.id)
        await client.send_message(channel1, liste_member)
        await client.send_message(channel1, liste_channel)
        print(liste_member)
        print(liste_channel)
        return
    if message.content.startswith("$secret") and authorizationLevel < 4:
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

    if (message.content.lower().startswith("!pong") or message.content.lower().startswith("!ping"))and ((isAuthorizedChannelSpecified("authorizationPingPong", message.server.id) == False) or ((isAuthorizedChannelSpecified("authorizationPingPong", message.server.id) == True) and getAuthorization("authorizationPingPong", message.server.id, message.channel.id) == True) or (authorizationLevel >= 3)):
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

    if (message.content.lower().startswith("!modifkarma") and authorizationLevel == 4):
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

    if message.content.lower().startswith('!setauthorized') and authorizationLevel == 4:
        option = message.content.lower()
        option = option[len("!setAuthorized "):]
        option = safeData(option)
        if option == "pingpong":
            setAuthorization("authorizationPingPong", message.server.id, message.channel.id)
        elif option == "music":
            setAuthorization("authorizationMusic", message.server.id, message.channel.id)
        elif option == "commands":
            setAuthorization("authorizationCommands", message.server.id, message.channel.id)
        elif option == "secret":
            setAuthorization("authorizationSecret", message.server.id, message.channel.id)
        else:
            await client.send_message(message.channel, "Erreur, l'option spécifiée n'existe pas!")
        return

    if message.content.lower().startswith("!setDefaultChannel".lower()) and authorizationLevel == 4:
        option = message.content.lower()
        option = option[len("!setDefaultChannel "):]
        if option == '':
            setAuthorization("defaultChannel", message.server.id, message.channel.id)
            await client.send_message(message.channel, "C'est maintenant le channel par défaut")
        else:
            option = safeData(option)
            setAuthorization('defaultChannel', message.server.id, option)
            await client.send_message(message.channel, "Le channel {} est maintenant considéré comme le channel par défault pour Isabel".format(str(option)))
        return

    if message.content.lower().startswith("!unsetDefaultChannel".lower()) and authorizationLevel == 4:
        option = message.content.lower()
        option = option[len("!unsetDefaultChannel "):]
        if option == '':
            deleteAuthorization("defaultChannel", message.server.id, message.channel.id)
            await client.send_message(message.channel, "Ce channel n'est plus un channel par défaut")
        else:
            option = safeData(option)
            deleteAuthorization('defaultChannel', message.server.id, option)
            await client.send_message(message.channel, "Le channel {} n'est plus un channel par défaut pour Isabel".format(str(option)))
        return

    if message.content.lower().startswith("!setDefaultChangelog".lower()) and authorizationLevel == 4:
        option = message.content.lower()
        option = option[len("!setDefaultChangelog "):]
        if option == '':
            setAuthorization("defaultChangelog", message.server.id, message.channel.id)
            await client.send_message(message.channel, "Ce channel n'est plus un channel par défaut pour le changelog")
        else:
            option = safeData(option)
            setAuthorization('defaultChangelog', message.server.id, option)
            await client.send_message(message.channel, "Le channel {} n'est plus un channel par défaut pour le changelog".format(str(option)))
        return
    
    if message.content.lower().startswith("!unsetDefaultChangelog".lower()) and authorizationLevel == 4:
        option = message.content.lower()
        option = option[len("!unsetDefaultChangelog "):]
        if option == '':
            deleteAuthorization("defaultChangelog", message.server.id, message.channel.id)
            await client.send_message(message.channel, "Ce channel n'est plus un channel par défaut pour le changelog")
        else:
            option = safeData(option)
            deleteAuthorization('defaultChangelog', message.server.id, option)
            await client.send_message(message.channel, "Le channel {} n'est plus un channel par défaut pour le changelog".format(str(option)))
        return

    if message.content.lower().startswith("!unauthorized") and authorizationLevel == 4:
        option = message.content.lower()
        option = option[len("!unAuthorized "):]
        if option == "pingpong":
            deleteAuthorization("authorizationPingPong", message.server.id, message.channel.id)
        elif option == "music":
            deleteAuthorization("authorizationMusic", message.server.id, message.channel.id)
        elif option == "commands":
            deleteAuthorization("authorizationCommands", message.server.id, message.channel.id)
        elif option == "secret":
            deleteAuthorization("authorizationSecret", message.server.id, message.channel.id)
        else:
            await client.send_message(message.channel, "Erreur, l'option spécifiée n'existe pas!")
        return
    
    if message.content.lower() == "!commands":
        s = ''
        liste_command = getListCommands(message.server.id, authorizationLevel)
        if liste_command is False or len(liste_command) == 0:
            await client.send_message(message.channel, "Il y a aucune commande personnalisé pour l'instant.")
            return
        
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

    if ((isAuthorizedChannelSpecified("authorizationCommands", message.server.id) == False) or ((isAuthorizedChannelSpecified("authorizationCommands", message.server.id) == True) and getAuthorization("authorizationCommands") == True) or authorizationLevel >= 3): 
        a = getCommands(message)
        if a is not False:
            await client.send_message(message.channel, a)
    


if __name__ == '__main__':
    import sys
    try:
        TOKEN = sys.argv[1]
    except:
        print('USAGE: python3 bot.py TOKENBOT')
        sys.exit(1)
    client.run(TOKEN)
