import xbmcaddon
import xbmcgui
import hachoir_core

from hachoir_core.field import FieldError
from hachoir_core.i18n import getTerminalCharset
from hachoir_core.error import HACHOIR_ERRORS, error
from hachoir_core.stream import InputStreamError, StringInputStream
from hachoir_parser import createParser, HachoirParserList, ValidateError
from hachoir_core.compatibility import all

#Globals
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')

class GameInfo():
    def __init__(self):
        self.game_title = ""
        self.game_system = ""
        self.game_maker = ""
        self.game_serial = ""

def checkFile(filename):
    sys.stdout.write(addonname + ":Checking File: " + filename)
    sys.stdout.flush()
    try:
        parser = createParser(filename)
    except InputStreamError, err:
        return ("streamerror")
    if not parser:
        return ("unable to create parser")
    else:
        return checkParser(parser)

def checkParser(parser):

    info = GameInfo()

    if parser.description == "Nintendo DS game file":
        info = FillNintendoDS(parser)
    else:
        info.game_system = parser.description

    result =  "System:" + "\t" + info.game_system + "\n"
    result += "Title:" + "\t" + info.game_title + "\n"
    result += "Maker:" + "\t" + info.game_maker + "\n"
    result += "Serial:" + "\t" + info.game_serial + "\n"

    return result

def printFile(parser):

    for field in parser:
        print("%s -> (%s / %s) len %d  %s=%s" % (field.path, field.address, field.absolute_address,  field.size, field.name, field.display))
        if field.is_field_set: printFile(field)

def FillNintendoDS(parser):

    info = GameInfo()
    info.game_system = "Nintendo DS"
    info.game_title = parser["header/game_title"].value
    info.game_maker = parser["header/maker_code"].value
    return info

def main():

    #Show a welcome screen
    #xbmcgui.Dialog().ok(addonname, "Starting Game Info Addon!", "", "")

    #Ask the user to select a game file
    game_filename = xbmcgui.Dialog().browseSingle(1, addonname + ": Select Game File", 'files', '', False, False, '')

    if game_filename == "":
        sys.exit(1)

    #try to guess and parse the file
    game_info = checkFile(game_filename)

    #Present the data to the user
    xbmcgui.Dialog().ok(addonname, game_info, "", "")

    #we are done here
    sys.exit(1)

if __name__ == "__main__":
    main()