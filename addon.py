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
    info.game_title = ""
    info.game_system = "Unknown"
    info.game_maker = ""
    info.game_serial = ""

    if parser.description == "Nintendo DS game file":
        info = FillNintendoDS(parser)
    elif parser.description == "ISO 9660 file system":
        info = checkISO9660file(parser)
    else:
        info.game_system = parser.description

    result =  "System:" + "\t" + info.game_system + "\n"
    result += "Title:" + "\t" + info.game_title + "\n"
    result += "Maker:" + "\t" + info.game_maker + "\n"
    result += "Serial:" + "\t" + info.game_serial + "\n"

    return result

def checkISO9660file(parser):

    #first check the system areas for
    # Sega Dreamcast
    # Sega Saturn CD

    #
    return checkPlaystation(parser)

def checkPlaystation(parser):

    #loop over all file to check for:
    #SYSTEM.CNF = PS1 and PS2 images
    #PARAM.SFO  = PSP and PS3 images

    info = GameInfo()

    i = 0
    while True:

        try:
            objectname = "directory_records[%d]" % i
            entry = parser[objectname]

            file_name = entry["file_identifier"].value

            #Check PS1 / PS2
            if file_name.startswith("SYSTEM.CNF"):

                location = entry["extent_lpath"].value
                size = entry["extent_size_l"].value
                #Size should be exact 69 bytes?
                data = parser.stream.readBytes((location * parser.sector_size + parser.sector_header_size) * 8, size)
                #PS1 == BOOT = cdrom:\SLUS_009.22;1
                if data.startswith("BOOT = cdrom:"):
                    info.game_serial = data[14:25]
                    info.game_system = "Playstaion 1"
                    break

                #PS2 == BOOT2 = cdrom0:\SLES_534.94;1
                if data.startswith("BOOT2 = cdrom0:"):
                    info.game_serial = data[16:27]
                    info.game_system = "Playstaion 2"
                    break

            i += 1
        except Exception, e:
            break

    return info

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