import discord

import MathCookie
import Send
import dataService.data_service as dt_srv
import CoolGameFunc as cgf
from data.guild_show import GuildPretty
from data.member_show import MemberPretty

HelpCmd = ('help', 'cmd', 'command', 'commands')
QuitCmd = ('endgame', 'terminate', 'quit', 'exit', 'end')
perform_action = ('slap', 'kick', 'spank', 'kill', 'punch', 'lewd', 'kiss')


def turn_on(member: discord.member):
    return dt_srv.cool_game_turn_on(member.guild.id, member.id)


def turn_off(member: discord.member):
    return dt_srv.cool_game_turn_off(member.guild.id, member.id)


async def cool_game_io(message_meta: discord.message, command: str):
    if command in QuitCmd:
        if not turn_off(message_meta.author):
            await Send.empty_terminate_error(message_meta)
        else:
            await Send.terminate_successful(message_meta)

    elif command == 'init':
        if not turn_on(message_meta.author):
            await Send.parallel_init_error(message_meta)
        else:
            await Send.init_successful(message_meta)

    else:
        await Send.embed_help_cool_game(message_meta.channel)


async def cool_game_input_process(message_meta: discord.message):
    if not dt_srv.player_playing(message_meta.author.guild.id, message_meta.author.id):
        return

    if len(message_meta.content) != 4:
        await Send.wrong_input(message_meta)
        return

    if cgf.repeat_found(message_meta.content):
        await Send.repeat_input(message_meta)
        return

    data = dt_srv.get_random(message_meta.author.guild.id, message_meta.author.id)

    partial_result = cgf.check_log(message_meta.content, data[0])

    done = partial_result[1] == 4
    await Send.publish_result(message_meta, partial_result, data[1]-1)

    if data[1]-1 == 0 and not done:
        await Send.ran_out_of_tries(message_meta, data[0])

    dt_srv.update_member_cool_game_list(message_meta.author.guild.id, message_meta.author.id, done)


def get_stats_guild(guild_id: int) -> GuildPretty:
    return dt_srv.get_guild_data(guild_id)


async def show_stats_guild(author: discord.member, guild: discord.guild, channel: discord.channel):
    await Send.present_guild_data(author, get_stats_guild(guild.id), guild, channel)


def get_stats_member(m_id: int, guild_id: int) -> MemberPretty:
    return dt_srv.get_member_data(m_id, guild_id)


async def show_stats_member(author: discord.member, mentions: discord.mentions, channel: discord.channel):
    if not mentions:
        mention = author
    else:
        mention = mentions[0]
    await Send.present_member_data(author, mention.name, get_stats_member(mention.id, mention.guild.id),
                                   mention.joined_at, channel)


async def message_event_handling(message_meta: discord.message):
    if MathCookie.check_integer(message_meta.content, False):
        await cool_game_input_process(message_meta)

    message_as_list = message_meta.content.replace('`', '').replace('|', '').split()

    if not message_as_list:
        return

    prefix_acceptable = dt_srv.find_prefix_by_guild_id(message_meta.guild.id)

    if message_as_list[0] not in prefix_acceptable:
        await Send.try_formatted_interpreter(message_meta)

    if message_meta.content.lower() in ('uwu', 'owo'):
        await Send.uwu(message_meta.channel)

    # if message_meta.content.lower() == 'get members status':
    #     await Send.online_members(message_meta.guild.members, message_meta.channel)

    if message_as_list[0] in prefix_acceptable:
        message_as_list.remove(message_as_list[0])

        if not message_as_list:
            await Send.cookie_quote(message_meta.channel)
            return

        command = message_as_list[0].lower()

        if command in HelpCmd:
            await Send.embed_help(message_meta.channel)

        elif command == 'purge':
            message_as_list.remove(message_as_list[0])
            if not message_as_list or not MathCookie.check_integer(message_as_list[0], False):
                await Send.error_purge(message_meta.channel)
            else:
                await Send.purge(message_meta, int(message_as_list[0]))

        elif command == 'math':
            message_as_list.remove(message_as_list[0])
            answer = MathCookie.math_cookie(message_as_list)
            if (not answer) and answer != 0:
                await Send.incorrect_expression(message_meta)
            else:
                await Send.correct_expression(answer, message_meta)

        elif command == 'coolgame':
            message_as_list.remove(message_as_list[0])
            await cool_game_io(message_meta, message_as_list[0].lower())

        elif command == 'matrixify':
            message_as_list.remove(message_as_list[0])
            await Send.handle_matrixify(message_as_list, message_meta.channel)

        elif command in QuitCmd:
            if turn_off(message_meta.author):
                await Send.terminate_successful(message_meta)

        elif command in ('simp', 'simprate', 'gay', 'gayrate'):
            await Send.fun_command(message_meta, command)

        elif command in ('stats', 'stat', 'server', 'info', 'leaderboard'):
            await show_stats_guild(message_meta.author, message_meta.guild, message_meta.channel)
            #  <---Guild Info----->

        elif command in ('mystats', 'mystat', 'myinfo', 'profile'):
            await show_stats_member(message_meta.author,
                                    message_meta.mentions, message_meta.channel)
            # <----Member Info----->
        elif command in ('pfp', 'dp', 'av', 'avatar'):
            mentions = message_meta.mentions
            if mentions:
                to_be_presented = mentions[0]
            else:
                to_be_presented = message_meta.author
            await Send.profile_picture(to_be_presented, message_meta.author, message_meta.channel)

        elif command in perform_action:
            await Send.perform_action_embed(message_meta.author, message_meta.mentions, message_meta.channel, command)

        elif command in ('emojis', 'emotes'):
            # message_as_list.remove(message_as_list[0])
            # if not message_as_list:               
            await Send.emoji_cheat_sheet(message_meta.author, 0, message_meta)
            # elif message_as_list[0] == '-a':
            #     message_as_list.remove(message_as_list[0])
            #     if not message_as_list:
            #         await Send.emoji_cheat_sheet(message_meta.author, 0, message_meta, None)
            #     elif message_as_list[0].lower() in ('false', '0', 'no', 'f', 'n'):
            #         await Send.emoji_cheat_sheet(message_meta.author, 0, message_meta, False)

        elif command in ('sendback', 'sendbackembed'):
            message_as_list.remove(message_as_list[0])
            if command == 'sendbackembed':
                await Send.send_back_embed(message_meta.channel, message_as_list)
            else:
                await Send.send_back(message_meta.channel, message_as_list)

        else:
            await Send.cookie_quote(message_meta.channel)

    elif message_meta.content in QuitCmd:
        if turn_off(message_meta.author):
            await Send.terminate_successful(message_meta)


async def reaction_event_handling(reaction):
    if reaction.emoji == '➡':
        await Send.emoji_cheat_sheet(None, 1, reaction.message)
    elif reaction.emoji == '⬅':
        await Send.emoji_cheat_sheet(None, -1, reaction.message)
