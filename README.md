# handle_music

## Description
Script handling all personal music requests. It uses the `mutagen` module to set id3 tags and the `discogs_client` in order to retrieve album art.

This program is mostly of use to people using a music program different to iTunes as it provides functionality to organise your music. On top of that, for songs downloaded from sources not providing cover art and proper id3 tagging, this script allows to simultaneously provide artwork, id3 tagging and organisation.

The recommended use of the script is to set the default source to your download folder and the default destination to your music folder. Then, when having downloaded music, simply run `python3 handle_music.py all` to organise the music automatically for you. Note that this copies the files to your music folder hence leaving a version of the downloaded files in the download folder.

Please note that album cover art is given exclusively by the artist name. Hence every song by one artist gets the same cover art. The reason behind this reasoning is that unofficial remixes of songs (which are hence not listed on discogs) can still receive cover art.

## Setup
This program makes use of the `config.json` file to store program settings. In order to use this program properly, please register the application on discogs and substitute the `consumer_key` and `consumer_secret` keys in the configuration file.

Note that in a future version, the setup might be programmed into a `setup` command, but as this has no use for the author, it has little priority.


## Usage
`python3 handle_music.py <option>`

Please note that options cannot be directly linked by providing several in a row.

### Command options:
| Options   | Description                                                     |
|-----------|-----------------------------------------------------------------|
|`help`     | Prints this help message.                                       |
|`art`      | Get artwork for mp3 files.                                      |
|`id3`      | Rewrite id3 tags for mp3 files using the filename.              |
|`copy`     | Copies mp3 files to destination.                                |
|`move`     | Moves mp3 files to destination.                                 |
|`all`      | Perform id3, art and copy (in that order).                      |
|`uploads`  | Find files having a modification date ulterior to one specified. The files can then be copied to a folder or simply listed.|

### Settings options:
If no `<path>` is provided, help messages are printed.

| Options            | Description                                            |
|--------------------|--------------------------------------------------------|
|`set_source <path>` | Sets default source path for commands.                 |
|`set_dest <path>`   | Sets default destination path for commands.            |

### Logger commands:
| Options     | Description                                                   |
|-------------|---------------------------------------------------------------|
|`clear`      | Clear all data stored in debugging log file.                  |
|`log_info`   | Retrieve information about debug logging.                     |
|`log_off`    | Turn off debug logging.                                       |
|`log_on`     | Turn on debug logging.                                        |
|`settings`   | Prints the settings.                                          |

### Getting help:
Use `<option>_help` to print more detailed help messages for each option: art, id3, copy, move, uploads.

