#!/bin/python3

import time
import subprocess, random, json, re, math, io
from http.client import HTTPConnection
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from telethon.tl.types import InputMediaPoll, PollAnswer
from telethon import functions
from telethon import functions, types

from telethon import events
import os
from telethon.sync import TelegramClient

from c3 import C3

proxy = None
try:
    connection = HTTPConnection("telegram.org", port=80, timeout=1)
    connection.request("HEAD", "/")
except:
    proxy =("socks5", '127.0.0.1', 2080)

import pathlib
dir = pathlib.Path(__file__).parent.resolve()
creds_file = open(os.path.join(dir,"credentials.json"))
creds = json.load(creds_file)
db = open(os.path.join(dir,"todo-chats"))
chats = [int(line) for line in db.read().splitlines()]
db.close()
def head(async_iterator): return async_iterator.__anext__()
async def should_answer(event, client) -> bool:
    if event.chat_id not in chats:
        return False
    try:
        sender = await client.get_entity(event.from_id)
        if sender.bot:
            return False
    except:
        pass
    return True

def main():
    with TelegramClient( os.path.join(dir,creds["name"]), creds["api_id"], creds["api_hash"], proxy=proxy) as client: 
        print("> c3 be runnin")
        print(chats)
        last_message = {}
        with open(os.path.join(dir, "pinned-messages"), 'r') as pinned_file:
                try:
                    pinned_messages_ids = json.load(pinned_file)
                except:
                    pinned_messages_ids = {}
        print(pinned_messages_ids)

        @client.on(events.NewMessage(func=lambda e: head(await should_answer(e, client) for _ in '_')))
        async def groups_handler(event):
            message = event.message
            chat_id = event.chat_id
            chat_id_str = str(chat_id)
            try:
                first_space = message.text.index(' ')
                cmd = message.text[:first_space]
                rest = message.text[first_space+1:]
            except ValueError:
                cmd = message.text
                rest = ""
            async def pin_last():
                try:
                    message = await client.get_messages('TelethonSnippets', ids=pinned_messages_ids[chat_id_str])
                    print(message)
                    await message.unpin()
                    pinned_messages_ids[chat_id_str] = None
                    print(pinned_messages_ids[chat_id_str])
                except:
                    print("error!")
                    pass
                print("last:", last_message[chat_id_str])
                await last_message[chat_id_str].pin()
                pinned_messages_ids[chat_id_str] = last_message[chat_id_str].id
                
                with open(os.path.join(dir, "pinned-messages"), 'w') as pinned_file:
                    json.dump(pinned_messages_ids, pinned_file)


            c3 = C3(chat_id, rest)
            def print_help():
                return "\n".join([key for key in handlers])
                    
            handlers = {
                "c3-add": c3.append,
                "c3-print": c3.print,
                "c3-printd": c3.print_done,
                "c3-search": c3.search,
                "c3-do": c3.set_done,
                "c3-del": c3.delete,
                "c3-prio": c3.set_priority,
                "c3-edit": c3.edit_message,
                "c3-help": print_help,
            }

            async_handlers = {
                "c3-pin": pin_last,
                }

            try:
                output = handlers[cmd]()
                await client.delete_messages(event.chat_id, [event.message.id])
                try:
                    await client.edit_message(chat_id, pinned_messages_ids[chat_id_str], output)
                except Exception as e:
                    if type(e) != MessageNotModifiedError:
                        print("KeyError occured: ", e)
                        last_message[chat_id_str] = await client.send_message(chat_id,output)
            except KeyError:
                try:
                    output = await async_handlers[cmd]()
                    await client.delete_messages(event.chat_id, [event.message.id])
                except KeyError:
                    pass

        def init(chat_id):
            if chat_id not in chats:
                db = open(os.path.join(dir,"todo-chats"), 'a')
                db.write(f"{chat_id}\n")
                chats.append(chat_id)
                db.close()
        def deinit(chat_id):
            chats.remove(chat_id)
            db = open(os.path.join(dir,"todo-chats"), 'w')
            db.writelines([f"{chat}\n" for chat in chats])
            db.close()

        handlers = { "c3-deinit": deinit, "c3-init": init }
        @client.on(events.NewMessage(from_users="me"))
        async def my_handler(event):
            try:
                handlers[event.message.text](event.chat_id)
                await client.delete_messages(event.chat_id, [event.message.id])
            except:
                pass


        client.run_until_disconnected()

if __name__ == "__main__":
    main()
