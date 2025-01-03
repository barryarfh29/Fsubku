import asyncio
import contextlib
import html
import inspect
import io
import os
import shlex
import sys
from typing import TYPE_CHECKING, Any, Dict

import hydrogram
from hydrogram import Client, filters
from hydrogram.helpers import ikb
from meval import meval

import main
from fstg.base import database
from fstg.filters import filter_owner
from fstg.helpers import button, cache
from fstg.utils import config, convert_seconds, paste_content

if TYPE_CHECKING:
    from hydrogram.types import CallbackQuery, Message

    from fstg.base import Bot

TASKS: Dict[str, Any] = {}


@Client.on_callback_query(filter_owner & filters.regex(r"cmd_(eval|shell|abort)"))
async def evaluate_handler_query(
    client: "Bot", callback_query: "CallbackQuery"
) -> None:
    command = callback_query.data.split("_")[1]

    chat_id = callback_query.message.chat.id
    message = await client.get_messages(
        chat_id, callback_query.message.reply_to_message.id
    )
    reply_message = await client.get_messages(chat_id, callback_query.message.id)

    if command == "eval":
        _id_ = f"{chat_id} - {message.id}"
        task = asyncio.create_task(async_evaluate_func(client, message, reply_message))
        TASKS[_id_] = task
        try:
            await task
        except asyncio.CancelledError:
            await reply_message.edit_text(
                "<blockquote><b>Process Cancelled!</b></blockquote>",
                reply_markup=ikb(button.Eval),
            )
        finally:
            if _id_ in TASKS:
                del TASKS[_id_]
    elif command == "shell":
        await exec_bash_func(client, message, reply_message)
    elif command == "abort":
        cancel_task(task_id=f"{chat_id} - {message.id}")


@Client.on_message(filter_owner & filters.command("e"))
async def evaluate_handler(client: "Bot", message: "Message") -> None:
    if len(message.command) == 1:
        await message.reply_text(
            "<blockquote><b>No Code!</b></blockquote>",
            quote=True,
            reply_markup=ikb(button.Eval),
        )
        return

    reply_message = await message.reply_text(
        "...", quote=True, reply_markup=ikb(button.Abort)
    )

    _id_ = f"{message.chat.id} - {message.id}"
    task = asyncio.create_task(async_evaluate_func(client, message, reply_message))
    TASKS[_id_] = task
    try:
        await task
    except asyncio.CancelledError:
        await reply_message.edit_text(
            "<blockquote><b>Process Cancelled!</b></blockquote>",
            reply_markup=ikb(button.Eval),
        )
    finally:
        if _id_ in TASKS:
            del TASKS[_id_]


@Client.on_message(filter_owner & filters.command("sh"))
async def shell_handler(client: "Bot", message: "Message") -> None:
    if len(message.command) == 1:
        await message.reply_text(
            "<blockquote><b>No Code!</b></blockquote>",
            quote=True,
            reply_markup=ikb(button.Shell),
        )
        return

    reply_message = await message.reply_text("...", quote=True)
    await exec_bash_func(client, message, reply_message)


async def async_evaluate_func(
    client: "Bot", message: "Message", reply_message: "Message"
) -> None:
    await reply_message.edit_text(
        "<blockquote><b>Executing...</b></blockquote>", reply_markup=ikb(button.Abort)
    )

    if len(message.text.split()) == 1:
        await reply_message.edit_text(
            "<blockquote><b>No Code!</b></blockquote>", reply_markup=ikb(button.Eval)
        )
        return

    eval_vars = {
        "asyncio": asyncio,
        "os": os,
        "src": inspect.getsource,
        "sys": sys,
        "config": config,
        "cache": cache,
        "db": database,
        "main": main,
        "hydrogram": hydrogram,
        "enums": hydrogram.enums,
        "errors": hydrogram.errors,
        "helpers": hydrogram.helpers,
        "raw": hydrogram.raw,
        "types": hydrogram.types,
        "c": client,
        "m": message,
        "r": message.reply_to_message,
        "u": (message.reply_to_message or message).from_user,
        "ikb": ikb,
    }

    eval_code = message.text.split(maxsplit=1)[1]

    start_time = client.loop.time()

    file = io.StringIO()
    with contextlib.redirect_stdout(file):
        try:
            meval_out = await meval(eval_code, globals(), **eval_vars)
            print_out = file.getvalue().strip() or str(meval_out) or "None"
        except Exception as exception:
            print_out = repr(exception)

    elapsed_time = client.loop.time() - start_time
    converted_time = convert_seconds(elapsed_time)

    final_output = (
        f"<pre>{html.escape(print_out)}</pre>\n"
        f"<pre language='Elapsed Time'>{converted_time}</pre>"
    )
    eval_buttons = button.Eval.copy()
    if len(final_output) > 4096:
        paste_url = await paste_content(str(print_out))
        eval_buttons.insert(0, [("Output", f"{paste_url}", "url")])

        caption = f"<pre language='Elapsed Time'>{converted_time}</pre>"
        await reply_message.edit_text(
            caption, reply_markup=ikb(eval_buttons), disable_web_page_preview=True
        )
    else:
        await reply_message.edit_text(final_output, reply_markup=ikb(eval_buttons))


async def exec_bash_func(
    client: "Bot", message: "Message", reply_message: "Message"
) -> None:
    await reply_message.edit_text("<blockquote><b>Executing...</b></blockquote>")

    if len(message.text.split()) == 1:
        await reply_message.edit_text(
            "<blockquote><b>No Code!</b></blockquote>", reply_markup=ikb(button.Shell)
        )
        return

    shell_code = message.text.split(maxsplit=1)[1]
    shlex.split(shell_code)

    init_time = client.loop.time()

    sub_process_sh = await asyncio.create_subprocess_shell(
        shell_code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await sub_process_sh.communicate()
    bash_print_out = (stdout + stderr).decode().strip()

    converted_time = convert_seconds(client.loop.time() - init_time)

    final_output = f"<pre>{bash_print_out}</pre>\n<pre language='Elapsed Time'>{converted_time}</pre>"
    bash_buttons = button.Shell.copy()
    if len(final_output) > 4096:
        paste_url = await paste_content(str(bash_print_out))
        bash_buttons.insert(0, [("Output", f"{paste_url}", "url")])

        caption = f"<pre language='Elapsed Time'>{converted_time}</pre>"
        await reply_message.edit_text(
            caption, reply_markup=ikb(bash_buttons), disable_web_page_preview=True
        )
    else:
        await reply_message.edit_text(final_output, reply_markup=ikb(bash_buttons))


def cancel_task(task_id: str) -> None:
    task = TASKS.get(task_id, None)
    if task and not task.done():
        return task.cancel()
