#!/usr/bin/env python3
"""
Module containing function declarations to be imported into handle_music.py.

Created by Jakob Beckmann on 22/07/2017.
"""


import re
import os
import shutil
import webbrowser
import time
import sys
import json

# Import for personal tools such a docstring trimming and progress bars.
try:
    import resources.per_tools as pt
except ImportError:
    import per_tools as pt
try:
    import resources.shared_data as sd
except ImportError:
    import shared_data as sd

# Imports for artwork API
import discogs_client as dc
from discogs_client.exceptions import HTTPError

# Imports for writting id3 tags
from mutagen.easyid3 import EasyID3
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.id3 import APIC, ID3, error



###############################################################################


def get_artwork(files=None):
    '''
    Get artwork for a file list.

    Note that this action might require you to authorise the program to access
    the discogs client when used for the first time. In this case, your default
    web browser will automatically be launched.
    Please be aware that your potentially sensitive authorisation data will be
    stored in 'config.json' which is not encrypted.

    Args:
        (list)files:    (optional) File list to be processed.

    Returns:
        List of processed files.
    '''

    # Set up loggers and settings
    terminal = sd.terminal
    debugger = sd.debugger
    settings = sd.settings


    # AUTHENTICATION
    if settings["access_token"] is None or settings["access_secret"] is None:
        debugger.write("Requesting manual authentication from discogs.")
        ds = dc.Client(settings["user_agent"])
        ds.set_consumer_key(settings["consumer_key"],
                            settings["consumer_secret"])
        token, secret, url = ds.get_authorize_url()

        # Open webbrowser to verify authorisation
        webbrowser.open_new(url)

        oauth_verifier = input('Verification code: ')
        try:
            access_token, access_secret = ds.get_access_token(oauth_verifier)
        except HTTPError:
            terminal.write("Unable to authenticate.\nTerminating ...")
            debugger.write("Verification failed with discogs client.",
                           prefix="[-]")
            debugger.write("Exiting: 1", prefix="[-]")
            sys.exit(1)

        debugger.write("Authorisation code verified, saving tokens to memory.")

        settings["access_token"] = access_token
        settings["access_secret"] = access_secret

        try:
            with open(sd.CONFIG_PATH, 'w') as fh:
                json.dump(settings, fh, indent=4)
        except FileNotFoundError:
            terminal.write("Please ensure the existence of the " +
                           "config.json file in resources directory.")
            debugger.write("Error opening configuration file.", prefix="[-]")
            debugger.write("Could not store authentication settings.",
                           prefix="[-]")

        debugger.write("Tokens to saved to memory.")

    else:
        debugger.write("Authenticating with discogs from memory.")
        try:
            ds = dc.Client(settings["user_agent"],
                           consumer_key=settings["consumer_key"],
                           consumer_secret=settings["consumer_secret"],
                           token=settings["access_token"],
                           secret=settings["access_secret"])
        except:
            terminal.write("Unable to authenticate with discogs. Clearing" +
                           "access tokens. Please try again.")
            debugger.write("Verification failed with discogs client.",
                           prefix="[-]")
            debugger.write("Clearing access tokens ...", prefix="[-]")

            settings["access_token"] = None
            settings["access_secret"] = None

            try:
                with open(sd.CONFIG_PATH, 'w') as fh:
                    json.dump(settings, fh, indent=4)
            except FileNotFoundError:
                terminal.write("Please ensure the existence of the " +
                               "config.json file in resources directory.")
                debugger.write("Error opening configuration file.",
                               prefix="[-]")
                debugger.write("Could not store authentication settings.",
                               prefix="[-]")

            debugger.write("Access tokens cleared.", prefix="[-]")
            debugger.write("Exiting: 1", prefix="[-]")
            sys.exit(1)

        debugger.write("Sucessfully authenticated.")

    # AUTHENTICATION END

    # Request source directory
    if files is None:
        terminal.write("Default source directory: {}".format(
                settings["source"]))
        source = input("Please enter source or leave empty for default:\n")
        if not source:
            source = settings["source"]
        while not os.path.exists(source):
            source = input("Directory does not exist, please try again:\n")
            if not source:
                source = settings["source"]

        rec_depth = input("Please specify a recursion depth (leave blank for" +
                      " infinite): ")
        while rec_depth and int(rec_depth) <= 0:
            rec_depth = input("Invalid entry, please try again: ")

        if not rec_depth:
            rec_depth = None
        else:
            rec_depth = int(rec_depth)

        files = pt.find_files(source, "*.mp3", depth=rec_depth)
        sd.source = source
    else:
        source = sd.source

    debugger.write("Source: {}.".format(source))
    debugger.write("{} files found.".format(len(files)))

    # Setting up progress bar
    terminal.write("{} files found.".format(len(files)))
    terminal.write("Preparing for file image writing ...")
    pg = pt.ProgressBar(len(files))
    pg.print()

    for file in files:
        tmp_file = MP3(file, ID3=ID3)

        # Try add missing tags
        try:
            tmp_file.add_tags()
        except error:
            pass

        # Get artist name from id3 tags
        tag_list = EasyID3(file)
        artist = str(tag_list["artist"][0])
        artist = re.split(sd.and_, artist)[0].strip()
        artist = re.split(sd.feat, artist)[0].strip()

        results = ds.search(artist, type="artist")

        try:
            try:
                image = results[0].images[0]['uri']
                type_ = image.split('.')[-1]
                content, resp = ds._fetcher.fetch(None, 'GET', image,
                            headers={'User-agent': ds.user_agent})
            except:
                image = results[1].images[0]['uri']
                type_ = image.split('.')[-1]
                content, resp = ds._fetcher.fetch(None, 'GET', image,
                            headers={'User-agent': ds.user_agent})
            tmp_file.tags.add(
                APIC(
                    encoding=3,
                    mime='image/' + type_,
                    type=0,
                    desc=u'Cover',
                    data=content
                )
            )
            tmp_file.save()

        except:
            pass

        pg.inc_and_print()

    terminal.write("Process complete.")
    debugger.write("get_artwork completed with {} files.".format(
            len(files)))

    return files


###############################################################################
###############################################################################

def id3_correct(files=None):
    """
    Corrent id3 tags of songs based on the filename. It assumes the files are names after the following convention:
    artist_name - song_name.mp3

    Args:
        (list)files:    (optional) File list to be processed.

    Returns:
        List of processed files.
    """
    # Set up return value
    result = []

    # Set up loggers and settings
    terminal = sd.terminal
    debugger = sd.debugger
    settings = sd.settings

    # Request source directory
    if files is None:
        terminal.write("Default source directory: {}".format(
                settings["source"]))
        source = input("Please enter source or leave empty for default:\n")
        if not source:
            source = settings["source"]
        while not os.path.exists(source):
            source = input("Directory does not exist, please try again:\n")
            if not source:
                source = settings["source"]


        rec_depth = input("Please specify a recursion depth (leave blank for" +
                      " infinite): ")
        while rec_depth and int(rec_depth) <= 0:
            rec_depth = input("Invalid entry, please try again: ")

        if not rec_depth:
            rec_depth = None
        else:
            rec_depth = int(rec_depth)

        files = pt.find_files(source, "*.mp3", depth=rec_depth)
        sd.source = source
    else:
        source = sd.source

    debugger.write("Source: {}.".format(source))
    debugger.write("{} files found.".format(len(files)))

    # Initialise list of tags.
    tag_list = {}

    # Try to create an _invalid directory in source directory.
    try:
        os.mkdir(os.path.join(source, '_invalid'))
    except:
        debugger.write("_invalid directory already exists.")

    # Set up progress bar
    terminal.write("Preparing for id3 writing ...")
    pg = pt.ProgressBar(len(files))
    pg.print()

    for file in files:
        # Change file name and replace feat flag with 'ft.'
        head, basename = os.path.split(file)
        basename = re.sub(sd.feat, ' ft. ', basename)
        basename = re.sub(sd.feat2, '(ft. ', basename)
        tmp_file = os.path.join(head, basename)

        os.rename(file, tmp_file)
        file = tmp_file


        tags = re.split(' - ', basename)
        if re.search(sd.invalid, basename) or len(tags) != 2:
            os.rename(file, os.path.join(source, "_invalid", basename))
            pg.inc_and_print()
            continue
        else:
            tag_list[file] = EasyID3(file)

            # Process artist name
            artist_name = tags[0].strip()
            tag_list[file]['artist'] = artist_name

            # Process song title
            title_name = tags[1][:-4].strip()
            tag_list[file]['title'] = title_name
            tag_list[file].save()

            result.append(file)

        pg.inc_and_print()

    terminal.write("Process complete.")
    debugger.write("id3_correct completed with {} files.".format(
            len(result)))

    return result

###############################################################################
###############################################################################

def file_copy(files=None):
    """
    Copies files to destination directory. Note that this creates
    subdirectories in the destination according to artist names. Hence a file
    by artist <artist_name> will be copied into a folder named <artist_name>
    within the destination directory,

    Args:
        (list)files:    (optional) File list to be processed.

    Returns:
        List of processed files.
    """

    # Set up loggers and settings
    terminal = sd.terminal
    debugger = sd.debugger
    settings = sd.settings

    # Request source directory
    if files is None:
        terminal.write("Default source directory: {}".format(
                settings["source"]))
        source = input("Please enter source or leave empty for default:\n")
        if not source:
            source = settings["source"]
        while not os.path.exists(source):
            source = input("Directory does not exist, please try again:\n")
            if not source:
                source = settings["source"]


        rec_depth = input("Please specify a recursion depth (leave blank for" +
                      " infinite): ")
        while rec_depth and int(rec_depth) <= 0:
            rec_depth = input("Invalid entry, please try again: ")

        if not rec_depth:
            rec_depth = None
        else:
            rec_depth = int(rec_depth)

        files = pt.find_files(source, "*.mp3", depth=rec_depth)
        sd.source = source
    else:
        source = sd.source

    # Request destination directory
    terminal.write("Default destination directory: {}".format(
            settings["destination"]))
    destination = input("Please enter destination or leave empty for " +
                        "default:\n")
    if not destination:
        destination = settings["destination"]

    while not os.path.exists(destination):
        destination = input("Directory does not exist, please try again:\n")
        if not destination:
            destination = settings["destination"]

    debugger.write("Source: {}.".format(source))
    debugger.write("Destination: {}.".format(destination))
    debugger.write("{} files found.".format(len(files)))

    pg = pt.ProgressBar(len(files))
    pg.print()

    for file in files:
        # Get artist name from id3 tags
        tag_list = EasyID3(file)
        artist = str(tag_list["artist"][0])

        try:
            os.mkdir(os.path.join(destination, artist))
        except FileExistsError:
            debugger.write("Folder '{}' already exists.".format(artist))

        basename = os.path.basename(file)
        try:
            shutil.copy2(file, os.path.join(destination, artist, basename))
        except:
            debugger.write("Error copying file {}".format(file), prefix="[-]")

        pg.inc_and_print()

    terminal.write("Process complete.")
    debugger.write("file_copy completed with {} files.".format(
            len(files)))

    return files


###############################################################################
###############################################################################

def file_move(files=None):
    """
    Moves files to destination directory. Note that this creates
    subdirectories in the destination according to artist names. Hence a file
    by artist <artist_name> will be moved into a folder named <artist_name>
    within the destination directory,

    Args:
        (list)files:    (optional) File list to be processed.

    Returns:
        List of processed files.
    """
    # Set up loggers and settings
    terminal = sd.terminal
    debugger = sd.debugger
    settings = sd.settings

    # Request source directory
    if files is None:
        terminal.write("Default source directory: {}".format(
                settings["source"]))
        source = input("Please enter source or leave empty for default:\n")
        if not source:
            source = settings["source"]
        while not os.path.exists(source):
            source = input("Directory does not exist, please try again:\n")
            if not source:
                source = settings["source"]


        rec_depth = input("Please specify a recursion depth (leave blank for" +
                      " infinite): ")
        while rec_depth and int(rec_depth) <= 0:
            rec_depth = input("Invalid entry, please try again: ")

        if not rec_depth:
            rec_depth = None
        else:
            rec_depth = int(rec_depth)

        files = pt.find_files(source, "*.mp3", depth=rec_depth)
        sd.source = source
    else:
        source = sd.source

    # Request destination directory
    terminal.write("Default destination directory: {}".format(
            settings["destination"]))
    destination = input("Please enter destination or leave empty for " +
                        "default:\n")
    if not destination:
        destination = settings["destination"]

    while not os.path.exists(destination):
        destination = input("Directory does not exist, please try again:\n")
        if not destination:
            destination = settings["destination"]

    debugger.write("Source: {}.".format(source))
    debugger.write("Destination: {}.".format(destination))
    debugger.write("{} files found.".format(len(files)))

    pg = pt.ProgressBar(len(files))
    pg.print()

    for file in files:
        # Get artist name from id3 tags
        tag_list = EasyID3(file)
        artist = str(tag_list["artist"][0])

        try:
            os.mkdir(os.path.join(destination, artist))
        except FileExistsError:
            debugger.write("Folder '{}' already exists.".format(artist))

        basename = os.path.basename(file)
        try:
            shutil.move(file, os.path.join(destination, artist, basename))
        except:
            debugger.write("Error copying file {}".format(file), prefix="[-]")

        pg.inc_and_print()

    terminal.write("Process complete.")
    debugger.write("file_copy completed with {} files.".format(
            len(files)))

    return files


###############################################################################
###############################################################################

def find_uploads():
    """
    Requests user input for a date and source directory, then filters the
    songs having been modified after said date. This command either prints to
    the terminal or copies files to a destination directory.
    Note that the default DESTINATION directory in the settings is used as
    default source for the file filtering.

    Returns:
        List of processed files.
    """
    # Set up loggers and settings
    terminal = sd.terminal
    debugger = sd.debugger
    settings = sd.settings

    # Request source directory
    terminal.write("Default source directory: {}".format(
            settings["destination"]))
    source = input("Please enter source or leave empty for " +
                        "default:\n")
    if not source:
        source = settings["destination"]

    while not os.path.exists(source):
        source = input("Directory does not exist, please try again:\n")
        if not source:
            source = settings["destination"]

    debugger.write("Source: {}.".format(source))

    # Get timestamp
    _input = input("Please enter a timestamp (dd/mm/yy) to filter music by: ")
    _input = _input.strip()
    debugger.write("Date entered: {}".format(_input))
    ts = time.strptime(_input, "%d/%m/%y")

    # Get all files in source directory
    _files = pt.find_files(source, "*.mp3")

    # Filter out files that have been modified after specified date
    files = [file for file in _files if \
             time.gmtime(os.path.getmtime(file)) > ts]

    debugger.write("{} files found.".format(len(files)))
    terminal.write("{} files found.".format(len(files)))

    print_to_ter = input("Copy files instead of printing to termianl? [y/n]: ")
    if print_to_ter == "y":
        print_to_ter = False
    else:
        print_to_ter = True

    debugger.write("Print to terminal: {}".format(print_to_ter))

    if not print_to_ter:
        destination = input("Please provide a destination directory:\n")
        while not os.path.exists(destination):
            destination = input("Directory doesn't exist, please try again:\n")

        debugger.write("Destination: {}".format(destination))
        terminal.write("Preparing to copy files ...")
        pg = pt.ProgressBar(len(files))
        pg.print()

        for file in files:
            # Get artist name from id3 tags
            tag_list = EasyID3(file)
            artist = str(tag_list["artist"][0])

            try:
                os.mkdir(os.path.join(destination, artist))
            except FileExistsError:
                debugger.write("Folder '{}' already exists.".format(artist))

            basename = os.path.basename(file)
            try:
                shutil.copy2(file, os.path.join(destination, artist, basename))
            except:
                debugger.write("Error copying file {}".format(file),
                               prefix="[-]")

            pg.inc_and_print()

        terminal.write("Process complete.")
        debugger.write("find_uploads completed with {} files.".format(
                len(files)))

        return files
    else:
        terminal.write("In source: {}".format(source))
        for file in files:
            terminal.write(os.path.basename(file), prefix="  - ")

        debugger.write("find_uploads completed with {} files.".format(
                len(files)))

        return files













