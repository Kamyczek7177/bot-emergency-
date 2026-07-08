import discord
from discord import app_commands
from discord.ui import View, Button
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

ADMIN_ROLE_ID = 1523944059171766343

warns = {}  # <--- DODANE - do przechowywania warnów

# ================== PRZYCISK ZAMYKANIA TICKETU ==================
class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij Ticket", emoji="🔒", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🔒 Ticket zostanie zamknięty za 5 sekund...", ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()


class TicketButton(Button):
    def __init__(self, label: str, emoji: str):
        super().__init__(label=label, emoji=emoji, style=discord.ButtonStyle.primary)
    
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        ticket_type = self.label

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
        }

        admin_role = guild.get_role(ADMIN_ROLE_ID)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        category = discord.utils.get(guild.categories, name="TICKETY") or await guild.create_category("TICKETY")

        channel = await guild.create_text_channel(
            f"{ticket_type.lower()}-{member.name}",
            overwrites=overwrites,
            category=category
        )

        embed = discord.Embed(
            title=f"🎟️ Ticket: {ticket_type}",
            description=f"Witaj {member.mention}!\nOpisz swoją sprawę.",
            color=0x5865F2
        )
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Ticket utworzony: {channel.mention}", ephemeral=True)


class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketButton("Sklep", "🛒"))
        self.add_item(TicketButton("Pomoc", "🔧"))
        self.add_item(TicketButton("Współpraca", "🤝"))
        self.add_item(TicketButton("Zarząd", "👑"))
        self.add_item(TicketButton("Skargi", "📝"))
        self.add_item(TicketButton("Rekrutacja", "📋"))


# ================== KOMENDY ==================

@tree.command(name="setup", description="Ustaw panel ticketów")
@app_commands.default_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ System Ticketów - Emergency Community",
        description="Wybierz rodzaj zgłoszenia:",
        color=0x5865F2
    )
    await interaction.response.send_message(embed=embed, view=TicketPanel())


@tree.command(name="regulamin", description="Wysyła regulamin serwera")
@app_commands.default_permissions(administrator=True)
async def regulamin(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 Regulamin Serwera - Emergency Community",
        description="**Witaj na serwerze!** Zapoznaj się z zasadami poniżej.",
        color=0x5865F2
    )

    embed.add_field(
        name="🔒 Ogólne Zasady",
        value=(
            "1. Szanuj wszystkich członków serwera — brak wyzwisk, obrażania, dyskryminacji.\n"
            "2. Zabraniamy treści NSFW, rasistowskich, politycznych oraz niezgodnych z prawem.\n"
            "3. Nie spamuj, nie flooduj i nie reklamuj innych serwerów bez zgody administracji.\n"
            "4. Nick musi być czytelny — bez wulgaryzmów i prowokacyjnych treści.\n"
            "5. Zakazane jest omijanie banów, timeoutów oraz posiadanie multikont."
        ),
        inline=False
    )

    embed.add_field(
        name="💬 Kanały i Komunikacja",
        value=(
            "2.1. Używaj kanałów zgodnie z ich przeznaczeniem.\n"
            "2.2. Zachowaj kulturę wypowiedzi — nie prowokuj i nie wszczynaj kłótni.\n"
            "2.3. Nie nadużywaj emoji, caps locka, botów ani komend poza wyznaczonymi miejscami.\n"
            "2.4. Nie udostępniaj linków bez zgody administracji."
        ),
        inline=False
    )

    embed.add_field(
        name="🛒 Strefa Zakupów / Wymian",
        value=(
            "3.1. Ogłoszenia handlowe publikuj **tylko** w wyznaczonych kanałach.\n"
            "3.2. Administracja nie ponosi odpowiedzialności za transakcje między użytkownikami.\n"
            "3.3. Oszustwa skutkują natychmiastowym banem.\n"
            "**3.4. Zwrotów nie przyjmujemy.**"
        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ Rangi i Administracja",
        value=(
            "4.1. Decyzje administracji są ostateczne.\n"
            "4.2. Nadużywanie zgłoszeń lub próby manipulacji będą karane.\n"
            "4.3. Administratorzy mają prawo modyfikować regulamin bez wcześniejszego uprzedzenia."
        ),
        inline=False
    )

    embed.add_field(
        name="✅ Informacja Końcowa",
        value=(
            "**Wejście na serwer oznacza akceptację regulaminu.**\n"
            "Niezastosowanie się do zasad grozi ostrzeżeniem, timeoutem lub banem."
        ),
        inline=False
    )

    embed.set_footer(text="Emergency Community • Obowiązuje od 8 lipca 2026")
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Regulamin został wysłany!", ephemeral=True)


@tree.command(name="say", description="Wysyła ładny embed (tytuł + opis)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    tytul="Tytuł wiadomości",
    opis="Główna treść wiadomości"
)
async def say(interaction: discord.Interaction, tytul: str, opis: str):
    embed = discord.Embed(
        title=tytul,
        description=opis,
        color=0x5865F2
    )
    
    embed.set_footer(text="Emergency Community")
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Wiadomość wysłana pomyślnie!", ephemeral=True)


@tree.command(name="close", description="Zamyka ticket")
async def close(interaction: discord.Interaction):
    if not any(word in interaction.channel.name for word in ["sklep","pomoc","wspolpraca","zarzad","skargi","rekrutacja"]):
        return await interaction.response.send_message("❌ To nie jest ticket!", ephemeral=True)
    await interaction.response.send_message("🔒 Zamykam za 5s...")
    await asyncio.sleep(5)
    await interaction.channel.delete()


# ================== WERYFIKACJA W ODDZIELNYM KANALE ==================

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zweryfikuj się", emoji="✅", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(1359421485235568670)
        
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Zostałeś zweryfikowany!\nMiłej zabawy na serwerze Emergency Community!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Błąd: Nie znaleziono roli.", ephemeral=True)


@tree.command(name="setup-verify", description="Ustawia wiadomość weryfikacyjną w kanale")
@app_commands.default_permissions(administrator=True)
async def setup_verify(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔐 Weryfikacja",
        description="**Aby uzyskać pełny dostęp do serwera, kliknij przycisk poniżej.**",
        color=0x5865F2
    )
    
    embed.add_field(
        name="Co zyskujesz po weryfikacji?",
        value="• Dostęp do wszystkich kanałów\n• Możliwość pisania na czacie\n• Udział w patrolach i eventach",
        inline=False
    )

    view = VerifyView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Wiadomość weryfikacyjna została ustawiona!", ephemeral=True)


# Automatyczne powitanie
@client.event
async def on_member_join(member):
    welcome_channel = client.get_channel(1523783146498428988)
    
    if welcome_channel is None:
        return

    embed = discord.Embed(
        title="EMERGENCY COMMUNITY × WITAMY",
        description=f"Witaj **{member.mention}**, na serwerze **Emergency Community**!\n"
                    f"Zapoznaj się z naszym regulaminem i ciesz się wspólną grą.",
        color=0x00b0ff
    )

    embed.set_image(url="https://i.imgur.com/ESRgjFc.png")
    embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
    embed.set_footer(text=f"© 2026 Emergency Community | Lobby • {discord.utils.format_dt(discord.utils.utcnow(), 'd')}")

    await welcome_channel.send(embed=embed)


# ================== KOMENDY MODERACYJNE ==================

@tree.command(name="ban", description="Banuje użytkownika")
@app_commands.default_permissions(ban_members=True)
@app_commands.describe(
    user="Użytkownik do zbanowania",
    reason="Powód bana",
    days="Liczba dni (pozostaw puste dla perma bana)"
)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str, days: int = None):
    if user.top_role >= interaction.user.top_role:
        return await interaction.response.send_message("❌ Nie możesz zbanować osoby z wyższą rangą.", ephemeral=True)

    try:
        if days:
            await user.ban(reason=reason, delete_message_days=days)
            await interaction.response.send_message(f"✅ **{user}** został zbanowany na **{days} dni**.\nPowód: {reason}", ephemeral=False)
        else:
            await user.ban(reason=reason)
            await interaction.response.send_message(f"✅ **{user}** został zbanowany **permamentnie**.\nPowód: {reason}", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"❌ Nie udało się zbanować: {e}", ephemeral=True)


@tree.command(name="warn", description="Daje ostrzeżenie (auto ban po 3)")
@app_commands.default_permissions(kick_members=True)
@app_commands.describe(user="Użytkownik", reason="Powód")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    if user.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        return await interaction.response.send_message("❌ Nie możesz ostrzec tej osoby.", ephemeral=True)

    user_id = user.id
    warns[user_id] = warns.get(user_id, 0) + 1
    level = warns[user_id]

    log_channel = client.get_channel(1523783146498428988)  # ← ZMIEŃ na ID kanału logów

    embed = discord.Embed(
        title=f"⚠️ Ostrzeżenie {level}/3",
        description=f"**{user.mention}** otrzymał ostrzeżenie.",
        color=0xff0000 if level == 3 else 0xffaa00
    )
    embed.add_field(name="Powód", value=reason, inline=False)
    embed.add_field(name="Wydane przez", value=interaction.user.mention, inline=True)
    embed.set_footer(text=f"ID: {user.id}")

    if log_channel:
        await log_channel.send(embed=embed)

    await interaction.response.send_message(f"✅ Nadano ostrzeżenie **{level}/3** dla {user.mention}", ephemeral=True)

    if level >= 3:
        try:
            await user.ban(reason=f"Auto-ban po 3 ostrzeżeniach | Ostatni powód: {reason}")
            ban_embed = discord.Embed(title="🚫 Auto-Ban", description=f"**{user}** został zbanowany automatycznie (3/3 warnów).", color=0x000000)
            ban_embed.add_field(name="Ostatni powód", value=reason, inline=False)
            if log_channel:
                await log_channel.send(embed=ban_embed)
        except:
            pass


@client.event
async def on_ready():
    print(f"✅ Bot zalogowany jako {client.user}")
    
    try:
        guild = discord.Object(id=1359413588074303528)
        await tree.sync(guild=guild)
        print("✅ Komendy zsynchronizowane na serwerze!")
        
        await tree.sync()
        print("✅ Komendy globalne zsynchronizowane!")
    except Exception as e:
        print(f"Błąd synchronizacji: {e}")



client.run(os.getenv("MTQyODM2NDkxNTk0ODY1MDU4Nw.GoJXwV.AP1i7NRCh5TWuOZ5At46TyIonepY9GqeOoUZBc"))

