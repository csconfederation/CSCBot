import discord

from discord.ext import commands
from cogs.utils import checks

class BulkRoleManager:
    """Used to manage roles role for large numbers of members"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def getAllWithRole(self, ctx, role : discord.Role, getNickname = False):
        """Prints out a list of members with the specific role"""
        count = 0
        messages = []
        message = ""
        await self.bot.say("Players with {0} role:\n".format(role.name))
        for member in ctx.message.server.members:
            if role in member.roles:
                if getNickname:
                    message += "{0.nick}: {0.name}#{0.discriminator}\n".format(member)
                else:
                    message += "{0.name}#{0.discriminator}\n".format(member)
                if len(message) > 1900:
                    messages.append(message)
                    message = ""
                count += 1
        if count == 0:
            await self.bot.say("Nobody has the {0} role".format(role.name))
        else:
            if message is not "":
                messages.append(message)
            for msg in messages:
                await self.bot.say("{0}{1}{0}".format("```", msg))
            await self.bot.say(":white_check_mark: {0} player(s) have the {1} role".format(count, role.name))

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def removeRoleFromAll(self, ctx, role : discord.Role):
        """Removes the role from every member who has it in the server"""
        empty = True
        for member in ctx.message.server.members:
            if role in member.roles:
                await self.bot.remove_roles(member, role)
                empty = False
        if empty:
            await self.bot.say(":x: Nobody has the {0} role".format(role.mention))
        else:
            await self.bot.say(":white_check_mark: {0} role removed from everyone in the server".format(role.name))


    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def addRole(self, ctx, role : discord.Role, *userList):
        """Adds the role to every member that can be found from the userList"""
        empty = True
        added = 0
        had = 0
        notFound = 0
        message = ""
        for user in userList:
            try:
                member = commands.MemberConverter(ctx, user).convert()
                if member in ctx.message.server.members:
                    if role not in member.roles:
                        await self.bot.add_roles(member, role)
                        added += 1
                    else:
                        had += 1
                    empty = False
            except:
                if notFound == 0:
                    message += "Couldn't find:\n"
                message += "{0}\n".format(user)
                notFound += 1
        if empty:
            message += ":x: Nobody was given the role {0}".format(role.mention)
        else:
           message += ":white_check_mark: {0} role given to everyone that was found from list".format(role.mention)
        if notFound > 0:
            message += ". {0} user(s) were not found".format(notFound)
        if had > 0:
            message += ". {0} user(s) already had the role".format(had)
        if added > 0:
            message += ". {0} user(s) had the role added to them".format(added)
        await self.bot.say(message)

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def makeDE(self, ctx, *userList):
        """Adds the Draft Eligible and League roles, removes Spectator role, and adds the DE prefix to every member that can be found from the userList"""
        empty = True
        added = 0
        had = 0
        notFound = 0
        deRole = None
        leagueRole = None
        spectatorRole = None
        message = ""
        for role in ctx.message.server.roles:
            if role.name == "Draft Eligible":
                deRole = role
            elif role.name == "League":
                leagueRole = role
            elif role.name == "Spectator":
                spectatorRole = role
            if leagueRole and deRole and spectatorRole:
                break

        if deRole is None or leagueRole is None or spectatorRole is None:
            await self.bot.say("Couldn't find either the Draft Eligible, League, or Spectator role in the server")
            return

        for user in userList:
            try:
                member = commands.MemberConverter(ctx, user).convert()
                if member in ctx.message.server.members:
                    if leagueRole not in member.roles:
                        await self.bot.add_roles(member, deRole, leagueRole)
                        added += 1
                        await self.bot.change_nickname(member, "{0} | {1}".format("DE", self.get_player_nickname(member)))
                        await self.bot.remove_roles(member, spectatorRole)
                    else:
                        message += "Already in League: {0}\n".format(user.mention)
                        had += 1
                    empty = False
            except:
                message += "Couldn't find: {0}\n".format(user)
                notFound += 1
        if empty:
            message += ":x: Nobody was given the Draft Eligible role"
        else:
           message += ":white_check_mark: Draft Eligible role given to everyone that was found from list"
        if notFound > 0:
            message += ". {0} user(s) were not found".format(notFound)
        if had > 0:
            message += ". {0} user(s) already had the role".format(had)
        if added > 0:
            message += ". {0} user(s) had the role added to them".format(added)
        await self.bot.say(message)
    
    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def getId(self, ctx, *userList):
        notFound = []
        for user in userList:
            try:
                member = commands.MemberConverter(ctx, user).convert()
                if member in ctx.message.server.members:
                    nickname = self.get_player_nickname(member)
                    await self.bot.say("{1}:{0.name}#{0.discriminator}:{0.id}".format(member, nickname))
            except:
                notFound.append(user)
        if len(notFound) > 0:
            await self.bot.say(":x: Couldn't find:")
            for user in notFound:
                await self.bot.say(user)

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def giveRoleToAllWithRole(self, ctx, currentRole : discord.Role, roleToGive : discord.Role):
        """Gives the roleToGive to every member who already has the currentRole"""
        count = 0
        hadRoleCount = 0
        countGiven = 0
        for member in ctx.message.server.members:
            if currentRole in member.roles:
                count += 1
                if roleToGive in member.roles:
                    hadRoleCount += 1
                else:
                    await self.bot.add_roles(member, roleToGive)
                    countGiven += 1
        if count == 0:
            message = ":x: Nobody has the {0} role".format(currentRole.name)
        else:
            message = ":white_check_mark: {0} user(s) had the {1} role".format(count, currentRole.name)
            if hadRoleCount > 0:
                message += ". {0} user(s) already had the {1} role".format(hadRoleCount, roleToGive.name)
            if countGiven > 0:
                message += ". {0} user(s) had the {1} role added to them".format(countGiven, roleToGive.name)
        await self.bot.say(message)

    def get_player_nickname(self, user : discord.Member):
        if user.nick is not None:
            array = user.nick.split(' | ', 1)
            if len(array) == 2:
                currentNickname = array[1].strip()
            else:
                currentNickname = array[0]
            return currentNickname
        return user.name
       

def setup(bot):
    bot.add_cog(BulkRoleManager(bot))