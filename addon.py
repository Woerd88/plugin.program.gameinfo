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
    elif parser.description == "Nintendo Entertainment System":
        info = FillNintendoNES(parser)
    elif parser.description == "Super Nintendo Entertainment System":
        info = FillNintendoSNES(parser)
    elif parser.description == "Nintendo Family Computer Disk System":
        info = FillNintendoFDS(parser)
    elif parser.description == "Nintendo Gameboy":
        info = FillNintendoGameboy(parser)
    elif parser.description == "Nintendo Gameboy Advance":
        info = FillNintendoGameboyAdvance(parser)
    elif parser.description == "Nintendo 64":
        info = FillNintendo64(parser)
    elif parser.description == "Nintendo Virtual Boy":
        info = FillNintendoVirtualBoy(parser)
    elif parser.description == "Neo Geo Pocket":
        info = FillNeoGeoPocket(parser)
    elif parser.description == "WonderSwan":
        info = FillWonderSwan(parser)
    elif parser.description == "Sega Master System":
        info = FillSegaMasterSystem(parser)
    elif parser.description == "Sega MegaDrive / Genesis / 32X":
        info = FillSegaMegaDriveGenesis32X(parser)
    elif parser.description == "3DO CD-ROM file system":
        info = FillPanasonic_3DO(parser)
    elif parser.description == "Phillips CD-I file system":
        info = FillPhillipsCDI(parser)
    elif parser.description == "PC-FX":
        info = FillNecPCFX(parser)
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
    # Sega Genesis CD, same header location as Sega Genesis rom, but with ISO9660
    #use parser.sector_header_size?
    data = parser.stream.readBytes( (0x110) * 8, 160)
    print "parser headersize %s" % parser.sector_header_size
    if data.startswith("SEGA GENESIS"):
        return FillSegaGenesisCD(data)

    #Sega Saturn CD header is located at first system area
    data = parser.stream.readBytes( 0x00, 112)
    if data.startswith("SEGA SEGASATURN"):
        return FillSegaSaturnCD(data)

    #check for PlayStation Files
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

def FillPanasonic_3DO(parser):
    #3DO CD-ROM file system
    info = GameInfo()
    info.game_system = "Panasonic 3DO CD-ROM"
    return info

def FillPhillipsCDI(parser):
    #Phillips CD-I file system
    info = GameInfo()
    info.game_system = "Phillips CD-I"
    info.game_serial = parser["volume[0]/vol_set_id"].value
    return info

def FillNecPCFX(parser):
    #PC-FX
    info = GameInfo()
    info.game_system = "NEC PC-FX"
    info.game_serial = parser["header/title"].value
    return info

def FillNintendoFDS(parser):
    #Nintendo Family Computer Disk System
    info = GameInfo()
    info.game_system = "Nintendo Family Computer Disk System"
    info.game_serial = parser["header/game_title"].value
    return info

def FillNintendoNES(parser):
    #Nintendo Entertainment System
    info = GameInfo()
    info.game_system = "Nintendo Entertainment System"
    return info

def FillNintendoSNES(parser):
    #Super Nintendo Entertainment System
    info = GameInfo()
    info.game_system = "Super Nintendo Entertainment System"
    info.game_serial = parser["snes_header/game_title"].value
    return info

def FillNintendoGameboy(parser):
    #Nintendo Gameboy
    info = GameInfo()
    info.game_system = "Nintendo Gameboy"
    info.game_serial = parser["header/game_title"].value
    return info

def FillNintendoGameboyAdvance(parser):
    #Nintendo Gameboy Advance
    info = GameInfo()
    info.game_system = "Nintendo Gameboy Advance"
    info.game_serial = parser["header/game_title"].value
    return info

def FillNintendoDS(parser):
    #Nintendo DS
    info = GameInfo()
    info.game_system = "Nintendo DS"
    info.game_title = parser["header/game_title"].value
    info.game_maker = parser["header/maker_code"].value
    return info

def FillNintendo64(parser):
    #Nintendo 64
    info = GameInfo()
    info.game_system = "Nintendo 64"
    info.game_serial = parser["header/game_title"].value
    return info

def FillNintendoVirtualBoy(parser):
    #Nintendo Virtual Boy
    info = GameInfo()
    info.game_system = "Nintendo Virtual Boy"
    info.game_serial = parser["header/game_title"].value
    return info

def FillNeoGeoPocket(parser):
    #Neo Geo Pocket
    info = GameInfo()
    info.game_system = "Neo Geo Pocket"
    info.game_serial = parser["header/game_title"].value
    return info

def FillWonderSwan(parser):
    #WonderSwan
    info = GameInfo()
    if parser["header/min_system"].value == 0:
        info.game_system = "WonderSwan"
    else:
        info.game_system = "WonderSwan Color"
    return info

def FillSegaMasterSystem(parser):
    #"Sega Master System"
    info = GameInfo()
    info.game_system = "Sega Master System / GameGear"
    info.game_serial = str(parser["header/product_code"].value)
    return info

def FillSegaMegaDriveGenesis32X(parser):
    #"Sega MegaDrive / Genesis / 32X"
    info = GameInfo()
    try:
        info.game_system = parser["header/console_name"].value
        info.game_title = parser["header/international_name"].value
        info.game_serial = parser["header/serial"].value
    except Exception, e:
        info.game_serial = "SMD ROM"
    return info

def FillSegaGenesisCD(data):
    info = GameInfo()
    info.game_system = "Sega Genesis CD"
    info.game_title = data[32:80] #48 bytes
    info.game_serial = data[131:139] #8 bytes
    return info

def FillSegaSaturnCD(data):
    info = GameInfo()
    info.game_system = "Sega Saturn"
    info.game_serial = data[32:42] #10 bytes
    info.game_title = data[96:] #16 bytes
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