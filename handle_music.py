#!/usr/bin/env python3
"""
Script handling all music requests. This file can only handle '.mp3' files as
other files do not allow for id3 tag writing.
Please note that this script requires the 'mutagen' and 'discogs_client'
modules to run.

    Usage:
        python3 handle_music.py <options>

    options:
        help       Prints this help message.
        art         Get artwork for mp3 files.
        id3         Rewrite id3 tags for mp3 files using the filename.
        copy        Copies mp3 files to destination.
        move        Moves mp3 files to destination.
        all         Perform id3, art and copy (in that order).
        uploads     Find files having a modification date ulterior to
                    one specified. The files can then be copied to a folder or
                    simply listed.

        set_source <path>   Sets default source path for commands.
        set_dest <path>     Sets default destination path for commands.

                    If no <path> is provided, help messages are printed.


        clear       Clear all data stored in debugging log file.
        log_info    Retrieve information about debug logging.
        log_off     Turn off debug logging.
        log_on      Turn on debug logging.
        settings    Prints the settings.

        <option>_help
                Prints more detailed help messages for each options: art, id3,
                copy, move, uploads.

Created by Jakob Beckmann on 22/07/2017.
"""

import re
import os
import shutil
import webbrowser
import sys
import json

# Import for personal tools such a docstring trimming and progress bars.
try:
    import resources.per_tools as pt
except ImportError:
    import per_tools as pt
# Import shared data and functions
try:
    import resources.actions as actn
except ImportError:
    import actions as actn
try:
    import resources.shared_data as sd
except ImportError:
    import shared_data as sd


sd.CONFIG_PATH = os.path.expanduser("resources/handle_music.json")



# Create debug logger and logger liked to terminal
terminal = pt.Logger()
debugger = pt.Logger(filename="handle_music.log", timestamp=True)
debugger.write("----------", prefix="---------- ")
debugger.set_default_prefix("[+]")
sd.debugger = debugger
sd.terminal = terminal

try:
    with open(sd.CONFIG_PATH, 'r') as fh:
        settings = json.load(fh)
except FileNotFoundError:
    debugger.write("Failed to load configuration file.", prefix="[-]")
    debugger.write("Exiting: 0", prefix="[-]")
    terminal.write("Please ensure the existence of the config.json file " +
                   "in resources directory.\nTerminating ...")
    sys.exit(1)

sd.settings = settings
debugger.write("Successfully loaded settings.")

if not settings["logging"]:
    debugger.write("Debug logger is getting disabled.")
    debugger.disable()

# Set up regular expression compilations
sd.and_ = re.compile(settings["and_tags"], re.IGNORECASE)
sd.feat = re.compile(settings["feature_tags"], re.IGNORECASE)
sd.feat2 = re.compile(settings["feature2_tags"], re.IGNORECASE)
sd.invalid = re.compile(settings["invalid_tags"], re.IGNORECASE)


# Get command line arguments
args = sys.argv

# If none specified or "help" print help
if len(args) == 1 or args[1] == "help":
    debugger.write("help called.")
    print(pt.trim_docstring(sys.modules[__name__].__doc__))

elif len(args) == 2:
    #######################################################################
    # HELP COMMANDS
    if args[1] == "art_help":
        debugger.write("{} called.".format(args[1]))
        print(pt.trim_docstring(actn.get_artwork.__doc__))

    elif args[1] == "id3_help":
        debugger.write("{} called.".format(args[1]))
        print(pt.trim_docstring(actn.id3_correct.__doc__))

    elif args[1] == "copy_help":
        debugger.write("{} called.".format(args[1]))
        print(pt.trim_docstring(actn.file_copy.__doc__))

    elif args[1] == "move_help":
        debugger.write("{} called.".format(args[1]))
        print(pt.trim_docstring(actn.file_move.__doc__))

    elif args[1] == "uploads_help":
        debugger.write("{} called.".format(args[1]))
        print(pt.trim_docstring(actn.find_uploads.__doc__))

    #######################################################################
    # MUSIC COMMANDS
    elif args[1] == "art":
        debugger.write("{} called.".format(args[1]))
        actn.get_artwork()

    elif args[1] == "id3":
        debugger.write("{} called.".format(args[1]))
        actn.id3_correct()

    elif args[1] == "copy":
        debugger.write("{} called.".format(args[1]))
        actn.file_copy()

    elif args[1] == "move":
        debugger.write("{} called.".format(args[1]))
        actn.file_move()

    elif args[1] == "all":
        debugger.write("{} called.".format(args[1]))
        debugger.write("id3 internally called.")
        files = actn.id3_correct()
        debugger.write("art internally called.")
        files = actn.get_artwork(files)
        debugger.write("copy internally called.")
        files = actn.file_copy(files)

    elif args[1] == "uploads":
        debugger.write("{} called.".format(args[1]))
        actn.find_uploads()

    #######################################################################
    # CHANGE DEFAULT SETTINGS HELP MESSAGES
    elif args[1] == "set_source":
        debugger.write("{} help called.".format(args[1]))
        print(pt.trim_docstring(sd.set_source_docstring))

    elif args[1] == "set_dest":
        debugger.write("{} help called.".format(args[1]))
        print(pt.trim_docstring(sd.set_dest_docstring))


    #######################################################################
    # LOGFILE OPTIONS
    elif args[1] == "clear":
        debugger.clear()
        info = debugger.get_info()
        terminal.write("Log file deleted: {}{}".format(info["filepath"],
                                                       info["filename"]))
        sys.exit(0)

    elif args[1] == "log_info":
        debugger.write("{} called.".format(args[1]))
        info = debugger.get_info()
        terminal.write("Log file information:")
        for key, value in info.items():
            terminal.write("{:<20}{}".format(key, value))

    elif args[1] == "log_off":
        debugger.write("{} called.".format(args[1]))
        settings["logging"] = False
        try:
            with open(sd.CONFIG_PATH, 'w') as fh:
                json.dump(settings, fh, indent=4)
        except FileNotFoundError:
            terminal.write("Please ensure the existence of the " +
                            "config.json file in resources directory.")
            debugger.write("Error opening configuration file.",
                           prefix="[-]")
        terminal.write("Logger turned off.")

    elif args[1] == "log_on":
        debugger.enable()
        debugger.write("{} called.".format(args[1]))
        settings["logging"] = True
        try:
            with open(sd.CONFIG_PATH, 'w') as fh:
                json.dump(settings, fh, indent=4)
        except FileNotFoundError:
            terminal.write("Please ensure the existence of the " +
                            "config.json file in resources directory.")
            debugger.write("Error opening configuration file.",
                           prefix="[-]")
        terminal.write("Logger turned on.")

    elif args[1] == "settings":
        debugger.write("{} called.".format(args[1]))
        terminal.write("{:-^40}".format("General information"))
        for key, value in settings.items():
            terminal.write("{:<20}{}".format(key, value))
        # Print logger info
        info = debugger.get_info()
        terminal.write("{:-^40}".format("Log file information"))
        for key, value in info.items():
            terminal.write("{:<20}{}".format(key, value))

    else:
        debugger.write("Called with unknown option.")
        print("Unknown option: {}.\n".format(args[1]))
        print(pt.trim_docstring(sys.modules[__name__].__doc__))

###############################################################################

elif len(args) == 3:
    ###########################################################################
    # CHANGE DEFAULT SETTINGS
    if args[1] == "set_source":
        debugger.write("{} called with path: {}".format(args[1], args[2]))
        path = os.path.expanduser(args[2])
        path = os.path.abspath(path)
        settings["source"] = path
        try:
            with open(sd.CONFIG_PATH, 'w') as fh:
                json.dump(settings, fh, indent=4)
        except FileNotFoundError:
            terminal.write("Please ensure the existence of the " +
                            "config.json file in resources directory.")
            debugger.write("Error opening configuration file.",
                           prefix="[-]")
        terminal.write("Default source set to: {}".format(path))
        debugger.write("Default source set to: {}".format(path))

    elif args[1] == "set_dest":
        debugger.write("{} called with path: {}".format(args[1], args[2]))
        path = os.path.expanduser(args[2])
        path = os.path.abspath(path)
        settings["destination"] = path
        try:
            with open(sd.CONFIG_PATH, 'w') as fh:
                json.dump(settings, fh, indent=4)
        except FileNotFoundError:
            terminal.write("Please ensure the existence of the " +
                            "config.json file in resources directory.")
            debugger.write("Error opening configuration file.",
                           prefix="[-]")
        terminal.write("Default destination set to: {}".format(path))
        debugger.write("Default destination set to: {}".format(path))

###############################################################################

else:
    debugger.write("Called incorrectly")
    print("Incorrect usage.\n")
    print(pt.trim_docstring(sys.modules[__name__].__doc__))

debugger.write("Exiting: 0")
