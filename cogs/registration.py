import discord
from discord.ext import commands
import hashlib
import sqlite3
import aiohttp
import time
import ssl
import asyncio

class RegisterSettingsView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
        
    def change_settings(self, enabled: bool):
        try:
            conn = sqlite3.connect("db/settings.sqlite")
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='register_settings'")
            if not cursor.fetchone():
                cursor.execute("CREATE TABLE register_settings (enabled BOOLEAN)")
                cursor.execute("INSERT INTO register_settings VALUES (?)", (enabled,))
            else:
                cursor.execute("UPDATE register_settings SET enabled = ? WHERE rowid = 1", (enabled,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating register settings: {e}")

    @discord.ui.button(label="Enable", emoji="✅", style=discord.ButtonStyle.success, custom_id="enable_register", row=0)
    async def enable_register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.change_settings(True)
            await interaction.response.send_message("✅ Registration has been enabled.", ephemeral=True)
        except Exception:
            await interaction.response.send_message("❌ An error occurred while enabling registration.", ephemeral=True)
            
    @discord.ui.button(label="Disable", emoji="❌", style=discord.ButtonStyle.danger, custom_id="disable_register", row=0)
    async def disable_register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            self.change_settings(False)
            await interaction.response.send_message("❌ Registration has been disabled.", ephemeral=True)
        except Exception:
            await interaction.response.send_message("❌ An error occurred while disabling registration.", ephemeral=True)

class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.conn_alliance = sqlite3.connect("db/alliance.sqlite")
        self.c_alliance = self.conn_alliance.cursor()
        
        self.conn_users = sqlite3.connect("db/users.sqlite")
        self.c_users = self.conn_users.cursor()

        # Persistent aiohttp session
        self.session = aiohttp.ClientSession()
    
    async def cog_unload(self):
        self.conn_alliance.close()
        self.conn_users.close()
        await self.session.close()

    async def show_settings_menu(self, interaction: discord.Interaction):
        if not self.is_global_admin(interaction.user.id):
            await interaction.response.send_message(
                "❌ You do not have permission to access this command.",
                ephemeral=True
            )
            return
        
        view = RegisterSettingsView(self)
        await interaction.response.send_message(
            "Choose an option to enable or disable the registration system:",
            view=view,
            ephemeral=True
        )
        
    def is_global_admin(self, user_id: int) -> bool:
        with sqlite3.connect("db/setting
