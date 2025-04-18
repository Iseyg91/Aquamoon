import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import random
import asyncio
import time
import datetime
import re
import subprocess
import sys
import traceback
from keep_alive import keep_alive
from discord.ui import Button, View
from datetime import datetime
from discord.ui import View, Select
from discord.ext import tasks
from collections import defaultdict
from collections import deque
import pymongo
from pymongo import MongoClient
import psutil
import platform

token = os.environ['AQUAMOON']
intents = discord.Intents.all()
start_time = time.time()
bot = commands.Bot(command_prefix="!!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ Le bot {bot.user} est maintenant connecté ! (ID: {bot.user.id})")

    # Initialisation de l'uptime du bot
    bot.uptime = time.time()
    
    # Récupération du nombre de serveurs et d'utilisateurs
    guild_count = len(bot.guilds)
    member_count = sum(guild.member_count for guild in bot.guilds)
    
    # Affichage des statistiques du bot dans la console
    print(f"\n📊 **Statistiques du bot :**")
    print(f"➡️ **Serveurs** : {guild_count}")
    print(f"➡️ **Utilisateurs** : {member_count}")
    
    # Liste des activités dynamiques
    activity_types = [
        discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} Membres"),
        discord.Activity(type=discord.ActivityType.streaming, name=f"{guild_count} Serveurs"),
        discord.Activity(type=discord.ActivityType.streaming, name="Aquamoon"),
    ]
    
    # Sélection d'une activité au hasard
    activity = random.choice(activity_types)
    
    # Choix d'un statut aléatoire
    status_types = [discord.Status.online, discord.Status.idle, discord.Status.dnd]
    status = random.choice(status_types)
    
    # Mise à jour du statut et de l'activité
    await bot.change_presence(activity=activity, status=status)
    
    print(f"\n🎉 **{bot.user}** est maintenant connecté et affiche ses statistiques dynamiques avec succès !")

    # Afficher les commandes chargées
    print("📌 Commandes disponibles 😊")
    for command in bot.commands:
        print(f"- {command.name}")

    try:
        # Synchroniser les commandes avec Discord
        synced = await bot.tree.sync()  # Synchronisation des commandes slash
        print(f"✅ Commandes slash synchronisées : {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")

    # Jongler entre différentes activités et statuts
    while True:
        for activity in activity_types:
            for status in status_types:
                await bot.change_presence(status=status, activity=activity)
                await asyncio.sleep(10)  # Attente de 10 secondes avant de changer l'activité et le statut
    for guild in bot.guilds:
        GUILD_SETTINGS[guild.id] = load_guild_settings(guild.id)

# Gestion des erreurs globales pour toutes les commandes
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Une erreur s'est produite : {event}")
    embed = discord.Embed(
        title="❗ Erreur inattendue",
        description="Une erreur s'est produite lors de l'exécution de la commande. Veuillez réessayer plus tard.",
        color=discord.Color.red()
    )
    await args[0].response.send_message(embed=embed)
#-------------------------------------------------------- Owner:

BOT_OWNER_IDS = [792755123587645461, 555060734539726862]

# Vérification si l'utilisateur est l'owner du bot
def is_owner(ctx):
    return ctx.author.id in BOT_OWNER_IDS

@bot.command()
async def shutdown(ctx):
    if is_owner(ctx):
        embed = discord.Embed(
            title="Arrêt du Bot",
            description="Le bot va maintenant se fermer. Tous les services seront arrêtés.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Cette action est irréversible.")
        await ctx.send(embed=embed)
        await bot.close()
    else:
        await ctx.send("Seul l'owner peut arrêter le bot.")

@bot.command()
async def restart(ctx):
    if is_owner(ctx):
        embed = discord.Embed(
            title="Redémarrage du Bot",
            description="Le bot va redémarrer maintenant...",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        os.execv(sys.executable, ['python'] + sys.argv)  # Redémarre le bot
    else:
        await ctx.send("Seul l'owner peut redémarrer le bot.")

@bot.command()
async def getbotinfo(ctx):
    """Affiche les statistiques détaillées du bot avec un embed amélioré visuellement."""
    try:
        start_time = time.time()
        
        # Calcul de l'uptime du bot
        uptime_seconds = int(time.time() - bot.uptime)
        uptime_days, remainder = divmod(uptime_seconds, 86400)
        uptime_hours, remainder = divmod(remainder, 3600)
        uptime_minutes, uptime_seconds = divmod(remainder, 60)

        # Récupération des statistiques
        total_servers = len(bot.guilds)
        total_users = sum(g.member_count for g in bot.guilds if g.member_count)
        total_text_channels = sum(len(g.text_channels) for g in bot.guilds)
        total_voice_channels = sum(len(g.voice_channels) for g in bot.guilds)
        latency = round(bot.latency * 1000, 2)  # Latence en ms
        total_commands = len(bot.commands)

        # Création d'une barre de progression plus détaillée pour la latence
        latency_bar = "🟩" * min(10, int(10 - (latency / 30))) + "🟥" * max(0, int(latency / 30))

        # Création de l'embed
        embed = discord.Embed(
            title="✨ **Informations du Bot**",
            description=f"📌 **Nom :** `{bot.user.name}`\n"
                        f"🆔 **ID :** `{bot.user.id}`\n"
                        f"🛠️ **Développé par :** `Iseyg`\n"
                        f"🔄 **Version :** `1.1.5`",
            color=discord.Color.blurple(),  # Dégradé bleu-violet pour une touche dynamique
            timestamp=datetime.utcnow()
        )

        # Ajout de l'avatar et de la bannière si disponible
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        if bot.user.banner:
            embed.set_image(url=bot.user.banner.url)

        embed.set_footer(text=f"Requête faite par {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        # 📊 Statistiques générales
        embed.add_field(
            name="📊 **Statistiques générales**",
            value=(
                f"📌 **Serveurs :** `{total_servers:,}`\n"
                f"👥 **Utilisateurs :** `{total_users:,}`\n"
                f"💬 **Salons textuels :** `{total_text_channels:,}`\n"
                f"🔊 **Salons vocaux :** `{total_voice_channels:,}`\n"
                f"📜 **Commandes :** `{total_commands:,}`\n"
            ),
            inline=False
        )

        # 🔄 Uptime
        embed.add_field(
            name="⏳ **Uptime**",
            value=f"🕰️ `{uptime_days}j {uptime_hours}h {uptime_minutes}m {uptime_seconds}s`",
            inline=True
        )

        # 📡 Latence
        embed.add_field(
            name="📡 **Latence**",
            value=f"⏳ `{latency} ms`\n{latency_bar}",
            inline=True
        )

        # 🌐 Hébergement (modifiable selon ton setup)
        embed.add_field(
            name="🌐 **Hébergement**",
            value="🖥️ `Render + Uptime Robot`",  # Change ça si nécessaire
            inline=False
        )

        # 📍 Informations supplémentaires
        embed.add_field(
            name="📍 **Informations supplémentaires**",
            value="💡 **Technologies utilisées :** `Python, discord.py`\n"
                  "⚙️ **Bibliothèques :** `discord.py, asyncio, etc.`",
            inline=False
        )

        # Ajout d'un bouton d'invitation
        view = discord.ui.View()
        invite_button = discord.ui.Button(
            label="📩 Inviter le Bot du développeur",
            style=discord.ButtonStyle.link,
            url="https://discord.com/oauth2/authorize?client_id=1356693934012891176&permissions=8&integration_type=0&scope=bot"
        )
        view.add_item(invite_button)

        await ctx.send(embed=embed, view=view)

        end_time = time.time()
        print(f"Commande `getbotinfo` exécutée en {round((end_time - start_time) * 1000, 2)}ms")

    except Exception as e:
        print(f"Erreur dans la commande `getbotinfo` : {e}")

#--------------------------------------------------------- Mot Sensible:
# Liste des mots sensibles
sensitive_words = [
    # Insultes et injures
    "connard", "crétin", "idiot", "imbécile", "salopard", "enfoiré", "méchant", "abruti", "débile", "bouffon",
    "clown", "baltringue", "fils de pute", "gros con", "sale type", "ordure", "merdeux", "guignol", "vaurien",
    "tocard", "branleur", "crasseux", "charognard", "raté", "bâtard", "déchet", "parasite",

    # Discrimination et discours haineux
    "raciste", "sexiste", "homophobe", "antisémite", "xénophobe", "transphobe", "islamophobe", "misogyne", 
    "misandre", "discriminatoire", "suprémaciste", "extrémiste", "fasciste", "nazi", "néonazi", "dictateur",

    # Violence et criminalité
    "viol", "tuer", "assassin", "attaque", "agression", "meurtre", "génocide", "exécution", "kidnapping",
    "prise d'otage", "armes", "fusillade", "terrorisme", "attentat", "jihad", "bombardement", "suicidaire",
    "décapitation", "immolation", "torture", "lynchage", "massacre", "pillage", "extermination",

    # Crimes sexuels et exploitation
    "pédocriminel", "abus", "sexe", "pornographie", "nu", "masturbation", "prostitution", "pédophilie", 
    "inceste", "exhibition", "fétichisme", "harcèlement", "traite humaine", "esclavage sexuel", "viol collectif",

    # Drogues et substances illicites
    "drogue", "cocaïne", "héroïne", "crack", "LSD", "ecstasy", "méthamphétamine", "opium", "cannabis", "alcool", 
    "ivresse", "overdose", "trafic de drogue", "toxicomanie", "drogue de synthèse", "GHB", "fentanyl",

    # Cybercriminalité et piratage
    "hack", "pirater", "voler des données", "phishing", "ddos", "raid", "flood", "spam", "crasher", "exploiter",
    "ransomware", "trojan", "virus informatique", "keylogger", "backdoor", "brute force", "scam", 
    "usurpation d'identité", "darknet", "marché noir", "cheval de Troie", "spyware", "hameçonnage",

    # Fraude et corruption
    "fraude", "extorsion", "chantage", "blanchiment d'argent", "corruption", "pot-de-vin", "abus de pouvoir", 
    "détournement de fonds", "évasion fiscale", "fraude fiscale", "marché noir", "contrefaçon",

    # Manipulation et désinformation
    "dictature", "oppression", "propagande", "fake news", "manipulation", "endoctrinement", "secte", 
    "lavage de cerveau", "désinformation",

    # Groupes criminels et troubles sociaux
    "violence policière", "brutalité", "crime organisé", "mafia", "cartel", "milice", "mercenaire", "guérilla",
    "insurrection", "émeute", "rébellion", "coup d'état", "anarchie", "terroriste", "séparatiste"
]

ADMIN_ID = 555060734539726862  # ID de l'admin modifié

# Dictionnaire pour suivre les messages d'un utilisateur pour l'anti-spam
user_messages = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore les messages du bot

    # 🔹 Détection des mots sensibles
    for word in sensitive_words:
        if re.search(rf"\b{re.escape(word)}\b", message.content, re.IGNORECASE):
            print(f"🚨 Mot sensible détecté dans le message de {message.author}: {word}")
            asyncio.create_task(send_alert_to_admin(message, word))
            break  # On arrête la boucle dès qu'un mot interdit est trouvé

    # 🔹 Réponse à la mention du bot
    if bot.user.mentioned_in(message) and message.content.strip().startswith(f"<@{bot.user.id}>"):
        embed = discord.Embed(
            title="👋 Besoin d’aide ?",
            description=(f"Salut {message.author.mention} ! Moi, c’est **{bot.user.name}**, ton assistant sur ce serveur. 🤖\n\n"
                         "🔹 **Pour voir toutes mes commandes :** Appuie sur le bouton ci-dessous ou tape `+aide`\n"
                         "🔹 **Une question ? Un souci ?** Contacte le staff !\n\n"
                         "✨ **Profite bien du serveur et amuse-toi !**"),
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(text="Réponse automatique • Disponible 24/7", icon_url=bot.user.avatar.url)
        
        view = View()
        button = Button(label="📜 Voir les commandes", style=discord.ButtonStyle.primary, custom_id="help_button")

        async def button_callback(interaction: discord.Interaction):
            ctx = await bot.get_context(interaction.message)
            await ctx.invoke(bot.get_command("aide"))
            await interaction.response.send_message("Voici la liste des commandes !", ephemeral=True)

        button.callback = button_callback
        view.add_item(button)

        await message.channel.send(embed=embed, view=view)
        return  # Retourne pour éviter de faire le reste du traitement si c'est une mention

    # 🔹 Traite les commandes en préfixe après tout le reste
    await bot.process_commands(message)

async def send_alert_to_admin(message, detected_word):
    """Envoie une alerte privée à l'admin en cas de mot interdit détecté."""
    try:
        admin = await bot.fetch_user(ADMIN_ID)
        embed = discord.Embed(
            title="🚨 Alerte : Mot sensible détecté !",
            description=f"Un message contenant un mot interdit a été détecté sur le serveur **{message.guild.name}**.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="📍 Salon", value=f"{message.channel.mention}", inline=True)
        embed.add_field(name="👤 Auteur", value=f"{message.author.mention} (`{message.author.id}`)", inline=True)
        embed.add_field(name="💬 Message", value=f"```{message.content}```", inline=False)
        embed.add_field(name="⚠️ Mot détecté", value=f"`{detected_word}`", inline=True)
        if message.guild:
            embed.add_field(name="🔗 Lien vers le message", value=f"[Clique ici]({message.jump_url})", inline=False)
        embed.set_footer(text="Système de détection automatique", icon_url=bot.user.avatar.url)
        await admin.send(embed=embed)
    except Exception as e:
        print(f"⚠️ Erreur lors de l'envoi de l'alerte : {e}")
#---------------------------------------------------- Bienvenue
WELCOME_CHANNEL_ID = 1358170527847419936
TARGET_GUILD_ID = 1355912711329943762

@bot.event
async def on_member_join(member):
    # Vérifie si l'utilisateur rejoint le bon serveur
    if member.guild.id != TARGET_GUILD_ID:
        return

    # Envoi du message de bienvenue
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        # Mention de l'ID avant l'embed
        await channel.send("<@555060734539726862>")

        embed = discord.Embed(
            title="<a:fete:1172810362261880873> **Bienvenue sur le serveur Aquamoon !** <a:fete:1172810362261880873>",
            description=(
                "<a:paintpalette:1172810412341587970> **Aquamoon** : L'univers créatif où la magie de l'imaginaire prend vie ! 🌙✨\n\n"
                "🎨✨ **Aquamoon** ✨🎨\n\n"
                "#Communautaire #Créatif #Divertissement\n\n"
                "🚀 **Boost & Avantages** → #Nitro\n"
                "🎬 **Animés & Streaming** → #Crunchyroll\n"
                "🖌️ **Création & Design** → #Éditeur #Graphiste\n"
                "🤝 **Échange & Partage** → #Communautaire\n\n"
            ),
            color=discord.Color.blue()
        )
        embed.set_image(url="https://github.com/Iseyg91/Aquamoon/blob/main/12-topaz.png?raw=true")

        await channel.send(f"{member.mention}", embed=embed)



#---------------------------------------------------------------- Moderation

# Gestion des erreurs pour les commandes
AUTHORIZED_USER_ID = 792755123587645461

# 🎨 Fonction pour créer un embed formaté
def create_embed(title, description, color, ctx, member=None, action=None, reason=None, duration=None):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=ctx.message.created_at)
    embed.set_footer(text=f"Action effectuée par {ctx.author.name}", icon_url=ctx.author.avatar.url)
    
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)

    if member:
        embed.add_field(name="👤 Membre sanctionné", value=member.mention, inline=True)
    if action:
        embed.add_field(name="⚖️ Sanction", value=action, inline=True)
    if reason:
        embed.add_field(name="📜 Raison", value=reason, inline=False)
    if duration:
        embed.add_field(name="⏳ Durée", value=duration, inline=True)

    return embed

# 🎯 Vérification des permissions et hiérarchie
def has_permission(ctx, perm):
    return ctx.author.id == AUTHORIZED_USER_ID or getattr(ctx.author.guild_permissions, perm, False)

def is_higher_or_equal(ctx, member):
    return member.top_role >= ctx.author.top_role

# 📩 Envoi d'un log
async def send_log(ctx, member, action, reason, duration=None):
    guild_id = ctx.guild.id
    settings = GUILD_SETTINGS.get(guild_id, {})
    log_channel_id = settings.get("sanctions_channel")

    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            embed = create_embed("🚨 Sanction appliquée", f"{member.mention} a été sanctionné.", discord.Color.red(), ctx, member, action, reason, duration)
            await log_channel.send(embed=embed)

# 📩 Envoi d'un message privé à l'utilisateur sanctionné
async def send_dm(member, action, reason, duration=None):
    try:
        embed = create_embed("🚨 Vous avez reçu une sanction", "Consultez les détails ci-dessous.", discord.Color.red(), member, member, action, reason, duration)
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f"Impossible d'envoyer un DM à {member.display_name}.")

@bot.command()
async def ban(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à bannir.")

    if ctx.author == member:
        return await ctx.send("🚫 Vous ne pouvez pas vous bannir vous-même.")
    if is_higher_or_equal(ctx, member):
        return await ctx.send("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.")
    if has_permission(ctx, "ban_members"):
        await member.ban(reason=reason)
        embed = create_embed("🔨 Ban", f"{member.mention} a été banni.", discord.Color.red(), ctx, member, "Ban", reason)
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Ban", reason)
        await send_dm(member, "Ban", reason)


@bot.command()
async def unban(ctx, user_id: int = None):
    if user_id is None:
        return await ctx.send("❌ Il manque un argument : vous devez spécifier l'ID d'un utilisateur à débannir.")

    if has_permission(ctx, "ban_members"):
        try:
            user = await bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            embed = create_embed("🔓 Unban", f"{user.mention} a été débanni.", discord.Color.green(), ctx, user, "Unban", "Réintégration")
            await ctx.send(embed=embed)
            await send_log(ctx, user, "Unban", "Réintégration")
            await send_dm(user, "Unban", "Réintégration")
        except discord.NotFound:
            return await ctx.send("❌ Aucun utilisateur trouvé avec cet ID.")
        except discord.Forbidden:
            return await ctx.send("❌ Je n'ai pas les permissions nécessaires pour débannir cet utilisateur.")


@bot.command()
async def kick(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à expulser.")

    if ctx.author == member:
        return await ctx.send("🚫 Vous ne pouvez pas vous expulser vous-même.")
    if is_higher_or_equal(ctx, member):
        return await ctx.send("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.")
    if has_permission(ctx, "kick_members"):
        await member.kick(reason=reason)
        embed = create_embed("👢 Kick", f"{member.mention} a été expulsé.", discord.Color.orange(), ctx, member, "Kick", reason)
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Kick", reason)
        await send_dm(member, "Kick", reason)

@bot.command()
async def mute(ctx, member: discord.Member = None, duration_with_unit: str = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à mute.")
    
    if duration_with_unit is None:
        return await ctx.send("❌ Il manque un argument : vous devez préciser une durée (ex: `10m`, `1h`, `2j`).")

    if ctx.author == member:
        return await ctx.send("🚫 Vous ne pouvez pas vous mute vous-même.")
    if is_higher_or_equal(ctx, member):
        return await ctx.send("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.")
    if not has_permission(ctx, "moderate_members"):
        return await ctx.send("❌ Vous n'avez pas la permission de mute des membres.")
    
    # Vérification si le membre est déjà en timeout
    if member.timed_out:
        return await ctx.send(f"❌ {member.mention} est déjà en timeout.")
    
    # Traitement de la durée
    time_units = {"m": "minutes", "h": "heures", "j": "jours"}
    try:
        duration = int(duration_with_unit[:-1])
        unit = duration_with_unit[-1].lower()
        if unit not in time_units:
            raise ValueError
    except ValueError:
        return await ctx.send("❌ Format invalide ! Utilisez un nombre suivi de `m` (minutes), `h` (heures) ou `j` (jours).")

    # Calcul de la durée
    time_deltas = {"m": timedelta(minutes=duration), "h": timedelta(hours=duration), "j": timedelta(days=duration)}
    duration_time = time_deltas[unit]

    try:
        # Tente de mettre le membre en timeout
        await member.timeout(duration_time, reason=reason)
        duration_str = f"{duration} {time_units[unit]}"
        
        # Embeds et réponses
        embed = create_embed("⏳ Mute", f"{member.mention} a été muté pour {duration_str}.", discord.Color.blue(), ctx, member, "Mute", reason, duration_str)
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Mute", reason, duration_str)
        await send_dm(member, "Mute", reason, duration_str)
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de mute ce membre. Vérifiez les permissions du bot.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Une erreur s'est produite lors de l'application du mute : {e}")
    except Exception as e:
        await ctx.send(f"❌ Une erreur inattendue s'est produite : {str(e)}")


@bot.command()
async def unmute(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à démuter.")

    if has_permission(ctx, "moderate_members"):
        await member.timeout(None)
        embed = create_embed("🔊 Unmute", f"{member.mention} a été démuté.", discord.Color.green(), ctx, member, "Unmute", "Fin du mute")
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Unmute", "Fin du mute")
        await send_dm(member, "Unmute", "Fin du mute")

# Fonction de vérification des permissions
async def check_permissions(ctx):
    # Vérifier si l'utilisateur a la permission "Manage Messages"
    return ctx.author.guild_permissions.manage_messages or ctx.author.id == 1166334752186433567

# Fonction pour vérifier si le membre est immunisé
async def is_immune(member):
    # Exemple de logique d'immunité (peut être ajustée)
    # Vérifie si le membre a un rôle spécifique ou une permission
    return any(role.name == "Immunité" for role in member.roles)

# Fonction pour envoyer un message de log
async def send_log(ctx, member, action, reason):
    log_channel = discord.utils.get(ctx.guild.text_channels, name="logs")  # Remplacer par le salon de log approprié
    if log_channel:
        embed = discord.Embed(
            title="Avertissement",
            description=f"**Membre :** {member.mention}\n**Action :** {action}\n**Raison :** {reason}",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Avertissement donné par {ctx.author}", icon_url=ctx.author.avatar.url)
        await log_channel.send(embed=embed)

# Fonction pour envoyer un message en DM au membre
async def send_dm(member, action, reason):
    try:
        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=f"**Action :** {action}\n**Raison :** {reason}",
            color=discord.Color.red()
        )
        embed.set_footer(text="N'oublie pas de respecter les règles !")
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f"Impossible d'envoyer un message privé à {member.name}")

# Commande de warning
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    try:
        if await check_permissions(ctx) and not await is_immune(member):
            # Envoi du message de confirmation
            embed = discord.Embed(
                title="⚠️ Avertissement donné",
                description=f"{member.mention} a reçu un avertissement pour la raison suivante :\n**{reason}**",
                color=discord.Color.orange()
            )
            embed.set_footer(text=f"Avertissement donné par {ctx.author}", icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)

            # Envoi du log et du message privé
            await send_log(ctx, member, "Warn", reason)
            await send_dm(member, "Warn", reason)
    except Exception as e:
        # Capturer l'exception et afficher le détail dans la console
        print(f"Erreur dans la commande warn: {e}")
        await ctx.send(f"Une erreur s'est produite lors de l'exécution de la commande.")

#------------------------------------------------------- Gestion:

@bot.command()
async def clear(ctx, amount: int = None):
    # Vérifie si l'utilisateur a la permission de gérer les messages ou s'il est l'ID autorisé
    if ctx.author.id == 792755123587645461 or ctx.author.guild_permissions.manage_messages:
        if amount is None:
            await ctx.send("Merci de préciser un chiffre entre 2 et 100.")
            return
        if amount < 2 or amount > 100:
            await ctx.send("Veuillez spécifier un nombre entre 2 et 100.")
            return

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f'{len(deleted)} messages supprimés.', delete_after=5)
    else:
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")

# Configuration des emojis personnalisables
EMOJIS = {
    "members": "👥",
    "crown": "👑",  # Emoji couronne
    "voice": "🎤",
    "boosts": "🚀"
}

@bot.command()
async def addrole(ctx, user: discord.Member = None, role: discord.Role = None):
    """Ajoute un rôle à un utilisateur."""
    # Vérifie si l'utilisateur a la permission de gérer les rôles
    if ctx.author.id != 792755123587645461 and not ctx.author.guild_permissions.manage_roles:
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
        return

    # Vérifier si les arguments sont bien fournis
    if user is None or role is None:
        await ctx.send("Erreur : veuillez suivre ce format : +addrole @user @rôle")
        return

    try:
        # Ajouter le rôle à l'utilisateur
        await user.add_roles(role)
        await ctx.send(f"{user.mention} a maintenant le rôle {role.name} !")
    except discord.Forbidden:
        await ctx.send("Je n'ai pas les permissions nécessaires pour attribuer ce rôle.")
    except discord.HTTPException as e:
        await ctx.send(f"Une erreur est survenue : {e}")
    
@bot.command()
async def delrole(ctx, user: discord.Member = None, role: discord.Role = None):
    """Retire un rôle à un utilisateur."""
    # Vérifie si l'utilisateur a la permission de gérer les rôles
    if ctx.author.id != 792755123587645461 and not ctx.author.guild_permissions.manage_roles:
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
        return

    # Vérifier si les arguments sont bien fournis
    if user is None or role is None:
        await ctx.send("Erreur : veuillez suivre ce format : +delrole @user @rôle")
        return

    try:
        # Retirer le rôle à l'utilisateur
        await user.remove_roles(role)
        await ctx.send(f"{user.mention} n'a plus le rôle {role.name} !")
    except discord.Forbidden:
        await ctx.send("Je n'ai pas les permissions nécessaires pour retirer ce rôle.")
    except discord.HTTPException as e:
        await ctx.send(f"Une erreur est survenue : {e}")

@bot.command()
async def vc(ctx):
    print("Commande 'vc' appelée.")

    try:
        guild = ctx.guild
        print(f"Guild récupérée: {guild.name} (ID: {guild.id})")

        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        voice_members = sum(len(voice_channel.members) for voice_channel in guild.voice_channels)
        boosts = guild.premium_subscription_count or 0
        owner_member = guild.owner
        server_invite = "https://discord.gg/X4dZAt3BME"
        verification_level = guild.verification_level.name
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        server_created_at = guild.created_at.strftime('%d %B %Y')

        embed = discord.Embed(title=f"📊 Statistiques de {guild.name}", color=discord.Color.purple())

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👥 Membres", value=f"**{total_members}**", inline=True)
        embed.add_field(name="🟢 Membres en ligne", value=f"**{online_members}**", inline=True)
        embed.add_field(name="🎙️ En vocal", value=f"**{voice_members}**", inline=True)
        embed.add_field(name="💎 Boosts", value=f"**{boosts}**", inline=True)

        embed.add_field(name="👑 Propriétaire", value=f"<@{owner_member.id}>", inline=True)
        embed.add_field(name="🔒 Niveau de vérification", value=f"**{verification_level}**", inline=True)
        embed.add_field(name="📝 Canaux textuels", value=f"**{text_channels}**", inline=True)
        embed.add_field(name="🔊 Canaux vocaux", value=f"**{voice_channels}**", inline=True)
        embed.add_field(name="📅 Créé le", value=f"**{server_created_at}**", inline=False)
        embed.add_field(name="🔗 Lien du serveur", value=f"[{guild.name}]({server_invite})", inline=False)

        embed.set_footer(text="📈 Statistiques mises à jour en temps réel | ♥️ by Iseyg")

        await ctx.send(embed=embed)
        print("Embed envoyé avec succès.")

    except Exception as e:
        print(f"Erreur lors de l'exécution de la commande 'vc': {e}")
        await ctx.send("Une erreur est survenue lors de l'exécution de la commande.")
        return  # Empêche l'exécution du reste du code après une erreur

@bot.command()
async def nuke(ctx):
    # Vérifie si l'utilisateur a la permission Administrateur
    if ctx.author.id != 792755123587645461 and not ctx.author.guild_permissions.administrator:
        await ctx.send("Tu n'as pas les permissions nécessaires pour exécuter cette commande.")
        return

    # Vérifie que la commande a été lancée dans un salon texte
    if isinstance(ctx.channel, discord.TextChannel):
        # Récupère le salon actuel
        channel = ctx.channel

        # Sauvegarde les informations du salon
        overwrites = channel.overwrites
        channel_name = channel.name
        category = channel.category
        position = channel.position

        # Récupère l'ID du salon pour le recréer
        guild = channel.guild

        try:
            # Supprime le salon actuel
            await channel.delete()

            # Crée un nouveau salon avec les mêmes permissions, catégorie et position
            new_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=category
            )

            # Réajuste la position du salon
            await new_channel.edit(position=position)

            # Envoie un message dans le nouveau salon pour confirmer la recréation
            await new_channel.send(
                f"💥 {ctx.author.mention} a **nuké** ce salon. Il a été recréé avec succès."
            )
        except Exception as e:
            await ctx.send(f"Une erreur est survenue lors de la recréation du salon : {e}")
    else:
        await ctx.send("Cette commande doit être utilisée dans un salon texte.")
    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)


#--------------------------------------------------------- Giveaway:
giveaways = {}  # Stocke les participants

class GiveawayView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.prize = " !!Giveaway !!"
        self.duration = 60  # En secondes
        self.duration_text = "60 secondes"
        self.emoji = "🎉"
        self.winners = 1
        self.channel = ctx.channel
        self.message = None  # Pour stocker l'embed message

    async def update_embed(self):
        """ Met à jour l'embed avec les nouvelles informations. """
        embed = discord.Embed(
            title="🎉 **Création d'un Giveaway**",
            description=f"🎁 **Gain:** {self.prize}\n"
                        f"⏳ **Durée:** {self.duration_text}\n"
                        f"🏆 **Gagnants:** {self.winners}\n"
                        f"📍 **Salon:** {self.channel.mention}",
            color=discord.Color.gold()  # Utilisation d'une couleur bleue sympathique
        )
        embed.set_footer(text="Choisissez les options dans le menu déroulant ci-dessous.")
        embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(9).png?raw=true")  # Logo ou icône du giveaway

        if self.message:
            await self.message.edit(embed=embed, view=self)

    async def parse_duration(self, text):
        """ Convertit un texte en secondes et retourne un affichage formaté. """
        duration_seconds = 0
        match = re.findall(r"(\d+)\s*(s|sec|m|min|h|hr|heure|d|jour|jours)", text, re.IGNORECASE)

        if not match:
            return None, None

        duration_text = []
        for value, unit in match:
            value = int(value)
            if unit in ["s", "sec"]:
                duration_seconds += value
                duration_text.append(f"{value} seconde{'s' if value > 1 else ''}")
            elif unit in ["m", "min"]:
                duration_seconds += value * 60
                duration_text.append(f"{value} minute{'s' if value > 1 else ''}")
            elif unit in ["h", "hr", "heure"]:
                duration_seconds += value * 3600
                duration_text.append(f"{value} heure{'s' if value > 1 else ''}")
            elif unit in ["d", "jour", "jours"]:
                duration_seconds += value * 86400
                duration_text.append(f"{value} jour{'s' if value > 1 else ''}")

        return duration_seconds, " ".join(duration_text)

    async def wait_for_response(self, interaction, prompt, parse_func=None):
        """ Attend une réponse utilisateur avec une conversion de type si nécessaire. """
        await interaction.response.send_message(prompt, ephemeral=True)
        try:
            msg = await bot.wait_for("message", check=lambda m: m.author == interaction.user, timeout=30)
            return await parse_func(msg.content) if parse_func else msg.content
        except asyncio.TimeoutError:
            await interaction.followup.send("⏳ Temps écoulé. Réessayez.", ephemeral=True)
            return None

    @discord.ui.select(
        placeholder="Choisir un paramètre",
        options=[
            discord.SelectOption(label="🎁 Modifier le gain", value="edit_prize"),
            discord.SelectOption(label="⏳ Modifier la durée", value="edit_duration"),
            discord.SelectOption(label="🏆 Modifier le nombre de gagnants", value="edit_winners"),
            discord.SelectOption(label="💬 Modifier le salon", value="edit_channel"),
            discord.SelectOption(label="🚀 Envoyer le giveaway", value="send_giveaway"),
        ]
    )
    async def select_action(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]

        if value == "edit_prize":
            response = await self.wait_for_response(interaction, "Quel est le gain du giveaway ?", str)
            if response:
                self.prize = response
                await self.update_embed()
        elif value == "edit_duration":
            response = await self.wait_for_response(interaction, 
                "Durée du giveaway ? (ex: 10min, 2h, 1jour)", self.parse_duration)
            if response and response[0] > 0:
                self.duration, self.duration_text = response
                await self.update_embed()
        elif value == "edit_winners":
            response = await self.wait_for_response(interaction, "Combien de gagnants ?", lambda x: int(x))
            if response and response > 0:
                self.winners = response
                await self.update_embed()
        elif value == "edit_channel":
            await interaction.response.send_message("Mentionne le salon du giveaway.", ephemeral=True)
            msg = await bot.wait_for("message", check=lambda m: m.author == interaction.user, timeout=30)
            if msg.channel_mentions:
                self.channel = msg.channel_mentions[0]
                await self.update_embed()
            else:
                await interaction.followup.send("Aucun salon mentionné.", ephemeral=True)
        elif value == "send_giveaway":
            embed = discord.Embed(
                title="🎉 Giveaway !",
                description=f"🎁 **Gain:** {self.prize}\n"
                            f"⏳ **Durée:** {self.duration_text}\n"
                            f"🏆 **Gagnants:** {self.winners}\n"
                            f"📍 **Salon:** {self.channel.mention}\n\n"
                            f"Réagis avec {self.emoji} pour participer !",
                color=discord.Color.gold()  # Utilisation d'une couleur de succès pour l'envoi
            )
            embed.set_footer(text="Bonne chance à tous les participants ! 🎉")
            embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(8).png?raw=true")  # Logo ou icône du giveaway

            message = await self.channel.send(embed=embed)
            await message.add_reaction(self.emoji)

            giveaways[message.id] = {
                "prize": self.prize,
                "winners": self.winners,
                "emoji": self.emoji,
                "participants": []
            }

            await interaction.response.send_message(f"🎉 Giveaway envoyé dans {self.channel.mention} !", ephemeral=True)

            await asyncio.sleep(self.duration)
            await self.end_giveaway(message)

    async def end_giveaway(self, message):
        data = giveaways.get(message.id)
        if not data:
            return

        participants = data["participants"]
        if len(participants) < 1:
            await message.channel.send("🚫 Pas assez de participants, giveaway annulé.")
            return

        winners = random.sample(participants, min(data["winners"], len(participants)))
        winners_mentions = ", ".join(winner.mention for winner in winners)

        embed = discord.Embed(
            title="🏆 Giveaway Terminé !",
            description=f"🎁 **Gain:** {data['prize']}\n"
                        f"🏆 **Gagnants:** {winners_mentions}\n\n"
                        f"Merci d'avoir participé !",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Merci à tous ! 🎉")
        embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(7).png?raw=true")  # Icône ou logo de fin de giveaway

        await message.channel.send(embed=embed)
        del giveaways[message.id]

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message_id = reaction.message.id
    if message_id in giveaways and str(reaction.emoji) == giveaways[message_id]["emoji"]:
        if user not in giveaways[message_id]["participants"]:
            giveaways[message_id]["participants"].append(user)
            print(f"{user} a rejoint le giveaway !")  # Message de débogage
        else:
            print(f"{user} est déjà un participant.")  # Message de débogage


@bot.command()
@commands.has_permissions(administrator=True)  # Restriction aux admins
async def gcreate(ctx):
    await ctx.send("Quel est le nom du giveaway ?")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=60)
        prize_name = msg.content  # Le nom du giveaway que l'utilisateur a entré
    except asyncio.TimeoutError:
        await ctx.send("⏳ Temps écoulé pour spécifier le nom du giveaway.")
        return

    view = GiveawayView(ctx)
    view.prize = prize_name  # Met à jour le nom du prize avec celui donné par l'utilisateur

    embed = discord.Embed(
        title="🎉 **Création d'un Giveaway**",
        description=f"Utilise le menu déroulant ci-dessous pour configurer ton giveaway.\n\n"
                    f"🎁 **Gain:** {prize_name}\n"
                    "⏳ **Durée:** 60 secondes\n"
                    "🏆 **Gagnants:** 1\n"
                    f"📍 **Salon:** {ctx.channel.mention}",
        color=discord.Color.gold()
    )
    embed.set_footer(text="Choisis les options dans le menu déroulant ci-dessous.")
    embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(6).png?raw=true")

    view.message = await ctx.send(embed=embed, view=view)

fast_giveaways = {}  # Stocke les participants et les informations pour les fast giveaways

class FastGiveawayView(discord.ui.View):
    def __init__(self, ctx, prize_name):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.prize = prize_name  # Utilisation du nom personnalisé pour le giveaway
        self.duration = 60  # En secondes
        self.duration_text = "60 secondes"
        self.emoji = "🎉"
        self.winners = 1
        self.channel = ctx.channel
        self.message = None  # Pour stocker l'embed message

    async def update_embed(self):
        """ Met à jour l'embed avec les nouvelles informations. """
        embed = discord.Embed(
            title="🎉 **Création d'un Fast Giveaway**",
            description=f"🎁 **Gain:** {self.prize}\n"
                        f"⏳ **Durée:** {self.duration_text}\n"
                        f"🏆 **Gagnants:** {self.winners}\n"
                        f"📍 **Salon:** {self.channel.mention}",
            color=discord.Color.gold()  # Utilisation d'une couleur bleue sympathique
        )
        embed.set_footer(text="Choisissez les options dans le menu déroulant ci-dessous.")
        embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(9).png?raw=true")  # Logo ou icône du giveaway

        if self.message:
            await self.message.edit(embed=embed, view=self)

    async def parse_duration(self, text):
        """ Convertit un texte en secondes et retourne un affichage formaté. """
        duration_seconds = 0
        match = re.findall(r"(\d+)\s*(s|sec|m|min|h|hr|heure|d|jour|jours)", text, re.IGNORECASE)

        if not match:
            return None, None

        duration_text = []
        for value, unit in match:
            value = int(value)
            if unit in ["s", "sec"]:
                duration_seconds += value
                duration_text.append(f"{value} seconde{'s' if value > 1 else ''}")
            elif unit in ["m", "min"]:
                duration_seconds += value * 60
                duration_text.append(f"{value} minute{'s' if value > 1 else ''}")
            elif unit in ["h", "hr", "heure"]:
                duration_seconds += value * 3600
                duration_text.append(f"{value} heure{'s' if value > 1 else ''}")
            elif unit in ["d", "jour", "jours"]:
                duration_seconds += value * 86400
                duration_text.append(f"{value} jour{'s' if value > 1 else ''}")

        return duration_seconds, " ".join(duration_text)

    async def wait_for_response(self, interaction, prompt, parse_func=None):
        """ Attend une réponse utilisateur avec une conversion de type si nécessaire. """
        await interaction.response.send_message(prompt, ephemeral=True)
        try:
            msg = await bot.wait_for("message", check=lambda m: m.author == interaction.user, timeout=30)
            return await parse_func(msg.content) if parse_func else msg.content
        except asyncio.TimeoutError:
            await interaction.followup.send("⏳ Temps écoulé. Réessayez.", ephemeral=True)
            return None

    @discord.ui.select(
        placeholder="Choisir un paramètre",
        options=[
            discord.SelectOption(label="⏳ Modifier la durée", value="edit_duration"),
            discord.SelectOption(label="🏆 Modifier le nombre de gagnants", value="edit_winners"),
            discord.SelectOption(label="💬 Modifier le salon", value="edit_channel"),
            discord.SelectOption(label="🚀 Envoyer le giveaway", value="send_giveaway"),
        ]
    )
    async def select_action(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]

        if value == "edit_duration":
            response = await self.wait_for_response(interaction, 
                "Durée du giveaway ? (ex: 10min, 2h, 1jour)", self.parse_duration)
            if response and response[0] > 0:
                self.duration, self.duration_text = response
                await self.update_embed()
        elif value == "edit_winners":
            response = await self.wait_for_response(interaction, "Combien de gagnants ?", lambda x: int(x))
            if response and response > 0:
                self.winners = response
                await self.update_embed()
        elif value == "edit_channel":
            await interaction.response.send_message("Mentionne le salon du giveaway.", ephemeral=True)
            msg = await bot.wait_for("message", check=lambda m: m.author == interaction.user, timeout=30)
            if msg.channel_mentions:
                self.channel = msg.channel_mentions[0]
                await self.update_embed()
            else:
                await interaction.followup.send("Aucun salon mentionné.", ephemeral=True)
        elif value == "send_giveaway":
            embed = discord.Embed(
                title="🎉 Fast Giveaway !",
                description=f"🎁 **Gain:** {self.prize}\n"
                            f"⏳ **Durée:** {self.duration_text}\n"
                            f"🏆 **Gagnants:** {self.winners}\n"
                            f"📍 **Salon:** {self.channel.mention}\n\n"
                            f"Réagis avec {self.emoji} pour participer !",
                color=discord.Color.gold()  # Utilisation d'une couleur de succès pour l'envoi
            )
            embed.set_footer(text="Bonne chance à tous les participants ! 🎉")
            embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(8).png?raw=true")  # Logo ou icône du giveaway

            message = await self.channel.send(embed=embed)
            await message.add_reaction(self.emoji)

            fast_giveaways[message.id] = {
                "prize": self.prize,
                "winners": self.winners,
                "emoji": self.emoji,
                "participants": [],
                "start_time": None,  # Pas encore démarré
            }

            await interaction.response.send_message(f"🎉 Giveaway envoyé dans {self.channel.mention} !", ephemeral=True)

            await asyncio.sleep(self.duration)
            await self.end_fast_giveaway(message)

    async def end_fast_giveaway(self, message):
        data = fast_giveaways.get(message.id)
        if not data:
            return

        participants = data["participants"]
        if len(participants) < 1:
            await message.channel.send("🚫 Pas assez de participants, giveaway annulé.")
            return

        winners = random.sample(participants, min(data["winners"], len(participants)))
        winners_mentions = ", ".join(winner.mention for winner in winners)

        # Envoi du message privé au gagnant et ajout de la réaction pour la vérification du temps de réponse
        winner = winners[0]  # Exemple pour un seul gagnant
        winner_dm = await winner.create_dm()
        dm_message = await winner_dm.send(f"Félicitations, {winner.mention}! Tu as gagné {data['prize']}! Réagis avec {self.emoji} pour valider ta victoire.")

        # Envoi du message privé et lancement du minuteur au moment de l'envoi
        fast_giveaways[message.id]["start_time"] = asyncio.get_event_loop().time()  # Démarre le minuteur ici

        # Attente de la réaction et calcul du temps
        await dm_message.add_reaction(self.emoji)
        def check(reaction, user):
            return user == winner and str(reaction.emoji) == self.emoji

        try:
            reaction, _ = await bot.wait_for('reaction_add', check=check, timeout=60)
            reaction_time = asyncio.get_event_loop().time() - fast_giveaways[message.id]["start_time"]  # Temps depuis l'envoi du message privé
            reaction_time_seconds = round(reaction_time, 2)
            await message.channel.send(f"Le gagnant {winner.mention} a réagi en {reaction_time_seconds} secondes.")
        except asyncio.TimeoutError:
            await winner_dm.send("Le temps est écoulé, tu n'as pas réagi à temps.")
            await message.channel.send(f"Le gagnant {winner.mention} n'a pas réagi à temps.")
        
        embed = discord.Embed(
            title="🏆 Fast Giveaway Terminé !",
            description=f"🎁 **Gain:** {data['prize']}\n"
                        f"🏆 **Gagnants:** {winners_mentions}\n\n"
                        f"Merci d'avoir participé !",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Merci à tous ! 🎉")
        embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(7).png?raw=true")  # Icône ou logo de fin de giveaway

        await message.channel.send(embed=embed)
        del fast_giveaways[message.id]

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message_id = reaction.message.id
    if message_id in fast_giveaways:
        giveaway = fast_giveaways[message_id]
        if str(reaction.emoji) == giveaway["emoji"]:
            if user not in giveaway["participants"]:
                giveaway["participants"].append(user)

@bot.command()
@commands.has_permissions(administrator=True)
async def fastgw(ctx):
    # Demander le nom du fast giveaway
    await ctx.send("Quel est le nom du fast giveaway ?")
    prize_name = await bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=30)
    
    # Créer une vue de giveaway avec le nom donné
    view = FastGiveawayView(ctx, prize_name.content)
    
    embed = discord.Embed(
        title="🎉 **Création d'un Fast Giveaway**",
        description=f"Utilise le menu déroulant ci-dessous pour configurer ton fast giveaway.\n\n"
                    f"🎁 **Gain:** {prize_name.content}\n"
                    f"⏳ **Durée:** 60 secondes\n"
                    f"🏆 **Gagnants:** 1\n"
                    f"📍 **Salon:** {ctx.channel.mention}",
        color=discord.Color.gold()
    )
    embed.set_footer(text="Choisis les options dans le menu déroulant ci-dessous.")
    embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(6).png?raw=true")

    view.message = await ctx.send(embed=embed, view=view)

# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
