import asyncio, websockets, sys, click, time, os
from prompt_toolkit import print_formatted_text, HTML
from websockets.exceptions import ConnectionClosedError


USERS = {}
sepr = chr(969696)


def obtntime():
    timestmp = time.localtime()
    timehour = str(timestmp.tm_hour)
    timemint = str(timestmp.tm_min)
    timesecs = str(timestmp.tm_sec)
    if int(timehour) < 10:  timehour = "0" + timehour
    if int(timemint) < 10:  timemint = "0" + timemint
    if int(timesecs) < 10:  timesecs = "0" + timesecs
    return timehour + ":" + timemint + ":" + timesecs


def getallus(chatroom):
    userlist = []
    for indx in USERS:
        if chatroom == USERS[indx][1]:
            userlist.append(USERS[indx][0])
    return userlist


async def notify_mesej(message):
    if USERS: await asyncio.wait([user.send(message) for user in USERS])


def wrap_text(message, max_width, indent=24):
    wrapped_message = str()
    indent_text = str()
    message_width = len(message)
    width = max_width - indent

    for i in range(indent):
        indent_text += ' '

    for i in range(0, message_width, width):
        if i > 0:
            wrapped_message += indent_text
        wrapped_message += message[i : i + width]
        if i < message_width - width:
            wrapped_message += '\n'

    return wrapped_message


async def chatroom(websocket, path):
    if not websocket in USERS:
        USERS[websocket] = ""
    try:
        async for mesgjson in websocket:
            if sepr in mesgjson and websocket in USERS:
                if USERS[websocket] == "":
                    USERS[websocket] = [mesgjson.split(sepr)[0], mesgjson.split(sepr)[1]]
                    print_formatted_text(HTML("[" + obtntime() + "] " + "<b>USERJOINED</b> > <green>" + mesgjson.split(sepr)[0] + "@" + mesgjson.split(sepr)[1] + "</green>"))
                    await notify_mesej("SNCTRYZERO" + sepr + "USERJOINED" + sepr + mesgjson.split(sepr)[0] + sepr + mesgjson.split(sepr)[1] + sepr + str(getallus(mesgjson.split(sepr)[1])))
            else:
                terminal_columns = os.get_terminal_size()[0]
                print_formatted_text(HTML("[" + obtntime() + "] " + "<b>SNCTRYZERO</b> > " + wrap_text(str(mesgjson), terminal_columns)))
                await notify_mesej(mesgjson)
    except ConnectionClosedError as EXPT:
        print_formatted_text(HTML("[" + obtntime() + "] " + "<b>USEREXITED</b> > <red>" + USERS[websocket][0] + "@" + USERS[websocket][1] + "</red>"))
        userlist = getallus(USERS[websocket][1])
        userlist.remove(USERS[websocket][0])
        leftmesg = "SNCTRYZERO" + sepr + "USEREXITED" + sepr + USERS[websocket][0] + sepr + USERS[websocket][1] + sepr + str(userlist)
        USERS.pop(websocket)
        await notify_mesej(leftmesg)


def servenow(netpdata="127.0.0.1", chatport="9696"):
    try:
        start_server = websockets.serve(chatroom, netpdata, int(chatport))
        asyncio.get_event_loop().run_until_complete(start_server)
        print_formatted_text(HTML("[" + obtntime() + "] " + "<b>SNCTRYZERO</b> > <green>SNCTRYZERO was started up on 'ws://" + str(netpdata) + ":" + str(chatport) + "/'</green>"))
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("")
        print_formatted_text(HTML("[" + obtntime() + "] " + "<b>SNCTRYZERO</b> > <red><b>SNCTRYZERO was shut down</b></red>"))
        sys.exit()


@click.command()
@click.option("-c", "--chatport", "chatport", help="Set the port value for the server [0-65536]", required=True)
@click.option("-6", "--ipprotv6", "netprotc", flag_value="ipprotv6", help="Start the server on an IPv6 address", required=True)
@click.option("-4", "--ipprotv4", "netprotc", flag_value="ipprotv4", help="Start the server on an IPv4 address", required=True)
@click.version_option(version="04092020", prog_name="SNCTRYZERO Server by t0xic0der")
def mainfunc(chatport, netprotc):
    try:
        os.system("clear")
        print_formatted_text(HTML("[" + obtntime() + "] " + "<b>SNCTRYZERO</b> > <green><b>Starting SNCTRYZERO v04092020...</b></green>"))
        netpdata = ""
        if netprotc == "ipprotv6":
            print_formatted_text(HTML("[" + obtntime() + "] " + "<b>SNCTRYZERO</b> > <green>IP version : 6</green>"))
            netpdata = "::"
        elif netprotc == "ipprotv4":
            print_formatted_text(HTML("[" + obtntime() + "] " + "<b>SNCTRYZERO</b> > <green>IP version : 4</green>"))
            netpdata = "0.0.0.0"
        servenow(netpdata, chatport)
    except OSError:
        print_formatted_text(HTML("[" + obtntime() + "] " + "<b>SNCTRYZERO</b> > <red><b>The server could not be started up</b></red>"))


if __name__ == "__main__":
    mainfunc()
