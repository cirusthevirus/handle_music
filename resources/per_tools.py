#!/usr/bin/env python3
"""
Tools module containing basic utilities for personal python scripts.

Created by Jakob Beckmann on 22/07/2017 (updated on 22/07/2017).
"""

import os
import time
from glob import glob

class ProgressBar:
    """
    Object that when printed to the terminal window prints a progress bar.

    Available methods:
        - __init__(total, prefix='', suffix='', decimals=1, length=50,
                   fill='█')
        - print()
        - increment()
        - inc_and_print()
    """
    def __init__(self, total, prefix='', suffix='', decimals=1, length=50,
        fill='█'):
        """
        Creates a ProgressBar object.

        Args:
            (int)total:     (required) Total iterations.
            (str)prefix:    (default: '') Prefix string.
            (str)suffix:    (default: '') Suffix string
            (int)decimals:  (default: 1) Percentage precision parameter.
            (int)length     (default: 50) Character length of bar.
            (str)fill:      (default: '█') Bar fill character.
        """
        self._iteration = 0
        self._total = total
        self._prefix = prefix
        self._suffix = suffix
        self._decimals = decimals
        self._length = length
        self._fill = fill

    def print(self):
        """
        Prints the progress bar. Note that the cursor is moved back to
        the beginning of the line to overwrite the progress bar next time it is
        printed.
        """
        percent = ("{0:." + str(self._decimals) + "f}").format(100 *
            (self._iteration / float(self._total)))
        filled_length = int(self._length * self._iteration // self._total)
        bar = self._fill * filled_length + '-' * (self._length - filled_length)
        print('\r%s |%s| %s%% %s' % (self._prefix, bar, percent, self._suffix),
              end = '\r')

        # Print New Line on Complete
        if self._iteration >= self._total:
            print()

    def increment(self):
        """
        Increments the iteration.
        """
        self._iteration += 1

    def inc_and_print(self):
        """
        Increments the iteration and prints the progress bar to the screen.
        """
        self.increment()
        self.print()


###############################################################################
###############################################################################

def find_files(source, pattern, depth=None):
    """
    Find files with extensions and a recusive depth of 'depth' in source.

    Args:
        (str)source:    (required) Source directory.
        (str)pattern:   (required) Pattern to search files (e.g. '*.txt').
        (int)depth:     (default: Infinite) Recursive depth of search.

    Returns:
        List of the files found.
    """
    result = []

    if depth is None:
        result = [file for tuple_ in os.walk(source) for file in\
                  glob(os.path.join(tuple_[0], pattern))]
    else:
        for depth_level in range(0, depth):
            result += glob(os.path.join(source, '/*' * depth_level, pattern),
                           recursive = False)

    return result

###############################################################################
###############################################################################

def trim_docstring(docstr):
    """
    Trims a python docstring so that indentation is corrected.

    Args:
        (str)docstr:    (required) Docstring to be formatted.

    Returns:
        String of the formatted docstring.
    """
    if not docstr:
        return ''

    # Remove indent.
    lines = docstr.expandtabs().splitlines()
    indent = 80
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    trimmed = [lines[0].strip()]
    if indent < 80:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())

    # Remove leading and trailing blank lines.
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    return '\n'.join(trimmed)


###############################################################################
###############################################################################

class Logger:
    """
    Logger class to easily write messages to logfile or standard output.
    """
    def __init__(self, filename=None, timestamp=False):
        """
        Initialise the logger.

        Args:
            (str)filename:  (default: None) Log filename. If None, printing
                            to standard output.
            (bool)
                timestamp:  (default: False) Sets if messages are timestamped.
        """
        self._filepath = os.path.expanduser("~/Library/Logs/")
        self._filename = filename
        self._timestamp = timestamp
        self._enabled = True
        self._prefix = ""

        # Create directory if not existing and printing to actual file.
        if self._filename is not None and not os.path.exists(self._filepath):
            os.makedirs(self._filepath)

    def enable(self):
        """
        Enable the logger allowing it to log messages.
        """
        self._enabled = True

    def disable(self):
        """
        Disable the logger prohibiting it from logging messages.
        """
        self._enabled = False

    def set_default_prefix(self, prefix):
        """
        Sets a default prefix for the logger.

        Args:
            (str)prefix:    (required) Prefix to be set to default.
        """
        self._prefix = prefix


    def set_path_to_file(self, path):
        """
        Sets the path to where the log file should be stored. By default, this
        is initialised to ~/Library/Logs.

        Args:
            (str)path:      (required) Path to desired log file directory.
        """
        self._filepath = os.path.expanduser(path)
        self._filepath = os.path.join(self._filepath, self._filename)


    def write(self, text, prefix=None, time_=None, end="\n", timestamp=None):
        """
        Writes to the log file.

        Args:
            (str)text:      (required) Text to write.
            (str)prefix:    (default: None) Prefix to appear at the very
                            beginning of the log message. This is only
                            necessary to use when using timestamps as the
                            prefix appear before the timestamp. If None,
                            internally set default is used ("").
            (struct_time)
                time_:       (default: None) Time to use for timestamp. If
                            None, current time is used.
            (str)end:       (default: "\n") String to add at the very end of
                            the log message. Mostly used when no newline is
                            preferred.
            (bool)
                timestamp:  (default: None) Whether to use a timestamp in
                            log message. If None, the logger default is used
                            that is set when the logger is initialised.
        """
        if not self._enabled:
            return

        if timestamp is None:
            timestamp = self._timestamp

        if timestamp:
            if time_ is None:
                time_ = time.localtime()
            timestamp_str = time.strftime("[%d/%m/%y - %H:%M:%S] ", time_)
        else:
            timestamp_str = ""

        if prefix is None:
            prefix = self._prefix

        if self._filename is None:
            print(prefix + timestamp_str + text, end=end)
        else:
            with open(os.path.join(self._filepath, self._filename), 'a') as fh:
                fh.write(prefix + timestamp_str + text + end)

    def clear(self):
        """
        Deletes the log file associated with this logger.
        """
        if self._filename is not None:
            os.remove(os.path.join(self._filepath, self._filename))

    def get_info(self):
        """
        Retrieves information about the logger.

        Returns:
            Dictionary with keys:
                filename
                filepath
                timestamp
        """
        return {"filename": self._filename,
                "filepath": self._filepath,
                "timestamp": self._timestamp,
                "enabled": self._enabled
                }


