#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import re
import codecs
import argparse
import os
import logging
import subprocess
__author__ = 'luckytianyiyan@gmail.com'
__version__ = '0.1.0'

STRING_FILE = 'Localizable.strings'

# Colors
BLUE = '\033[1;94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
HIGH_LIGHT = '\033[1;97m'
ENDC = '\033[0m'

# Format
STEP_FORMAT = BLUE + '==>' + HIGH_LIGHT + '{}' + ENDC


class Strings(object):
    def __init__(self, target_dir, encoding='utf_16_le'):
        self.__dir = target_dir
        self.encoding = encoding
        self.filename = os.path.join(target_dir if target_dir else '', STRING_FILE)
        self.__reference = {}

    def generate(self, files):
        self.__generate_reference()
        script = 'genstrings'
        for filename in files:
            script += ' %s' % filename
        self.__run_script('%s -o %s' % (script, self.__dir))
        self.__translate()

    @staticmethod
    def __run_script(script, display_output=True):
        if display_output:
            logging.info('%s' % script)
            logging.info('---')
        process = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ''
        while process.poll() is None:
            line = process.stdout.readline()
            if line:
                output += line
                if display_output:
                    logging.info(line.strip())
        if display_output:
            logging.info('process finished with %s\n' % ('success' if
                                                         process.returncode == 0 or process.returncode is None else
                                                         ('exit code %r' % process.returncode)))

        return process.returncode, output

    def __generate_reference(self):
        self.__reference = {}
        if os.path.exists(self.filename):
            f = codecs.open(self.filename, "r", encoding=self.encoding)
            for line in f:
                match = re.match(r'"(?P<key>.*?)" = "(?P<value>.*?)";', line)
                if match is not None:
                    key = match.group('key')
                    value = match.group('value')
                    self.__reference[key] = value
            f.close()
        logging.info(STEP_FORMAT.format(' Generated Reference'))
        logging.info('count: %r' % len(self.__reference))

    def __translate(self):
        sum = 0
        translated = {}
        f = codecs.open(self.filename, "r", encoding=self.encoding)
        lines = f.readlines()
        for (index, line) in enumerate(lines):
            match = re.match(r'"(?P<key>.*?)" = "(?P<value>.*?)";', line)
            if match is not None:
                key = match.group('key')
                result = self.__reference.get(key, None)

                if result is not None:
                    value = match.group('value')
                    if self.__reference[key] != value:
                        line = '"%s" = "%s";\n' % (key, result)
                        lines[index] = line
                        sum += 1
                        translated[key] = result
        f.close()

        f = codecs.open(self.filename, "w+", encoding=self.encoding)
        f.writelines(lines)
        f.flush()
        f.close()

        logging.info(STEP_FORMAT.format(' Translated Strings'))
        logging.info('count: %r' % sum)
        logging.info('')
        for k in translated.keys():
            logging.debug('%s => %s' % (k, translated[k]))


def arg_parser():
    description = r"""
  _______     _____ _        _
 |__   __|   / ____| |      (_)
    | |_   _| (___ | |_ _ __ _ _ __   __ _ ___
    | | | | |\___ \| __| '__| | '_ \ / _` / __|
    | | |_| |____) | |_| |  | | | | | (_| \__ \
    |_|\__, |_____/ \__|_|  |_|_| |_|\__, |___/
        __/ |                         __/ |
       |___/                         |___/
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=description)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('files', metavar='file', nargs='+', help='source file .[mc]')
    parser.add_argument('-o', '--output', dest='dir', help='place output files in \'dir\'')

    return parser


def main():
    parser = arg_parser()
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG, format='%(message)s', )

    for filename in args.files:
        if not os.path.exists(filename):
            parser.error('%s not exists' % filename)
        if os.path.isdir(filename):
            parser.error('%s is a directory' % filename)

    strings = Strings(args.dir)

    strings.generate(args.files)

    # logging.debug('\nsource strings count: %r\n' % len(source))

if __name__ == '__main__':
    main()