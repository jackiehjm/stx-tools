# Copyright (c) 2021 Wind River Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging

from stx import command  # pylint: disable=E0611
from stx import stx_configparser  # pylint: disable=E0611
from stx import stx_control  # pylint: disable=E0611
from stx import stx_repomgr  # pylint: disable=E0611
from stx import utils  # pylint: disable=E0611

logger = logging.getLogger('STX')
utils.set_logger(logger)


class STXMainException(Exception):
    pass


class CommandLine:
    '''Handles parsing the commandline parameters for stx tool'''

    def __init__(self):
        command.check_prjdir_env()
        self.handleconfig = stx_configparser.HandleConfigTask()
        self.handlecontrol = stx_control.HandleControlTask()
        self.parser = self.parseCommandLine()

    def parseCommandLine(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=False,
            description='STX Build Tool',
            epilog='''Tips:
Use %(prog)s --help to get help for all of parameters\n\n''')

        subparsers = parser.add_subparsers(title='Builtin Commands:',
                                           help='sub-command for stx\n\n')

        control_subparser = subparsers.add_parser('control',
                                                  help='Execute the control \
task.\t\teg: [start|enter|stop|status|upgrade]')
        control_subparser.add_argument('ctl_task',
                                       help='[ start|stop|enter|status|upgrade\
                                       ]: Create or Stop or Enter or List or \
                                       Upgrade the stx-builder/obs/lat/pulp \
                                       containers.\n\n')
        control_subparser.add_argument('--dockername',
                                       help='[ builder|pkgbuilder|repomgr|lat \
                                       ], the four dockers you can enter, if \
                                       there is no this argument for enter \
                                       task, default enter the stx-builder \
                                       container\n\n', required=False)
        control_subparser.set_defaults(handle=self.handlecontrol.handleControl)

        config_subparser = subparsers.add_parser('config',
                                                 help='Change stx config \
settings.\t\teg: [ --show|--get|--add|--unset|--remove-section ]')
        config_subparser.add_argument('--show',
                                      help='Show all the content of the config\
                                      file\n\n', action='store_true')
        config_subparser.add_argument('--add',
                                      help='Add the setting section.key and \
                                      value into the config file.\n\n',
                                      nargs=2, required=False)
        config_subparser.add_argument('--get',
                                      help='Get the value of the section.key \
                                      from the config file.\n\n', nargs=1,
                                      required=False)
        config_subparser.add_argument('--unset',
                                      help='Remove value of the section.key \
                                      from the config file.\n\n', nargs=1,
                                      required=False)
        config_subparser.add_argument('--removesection',
                                      help='Remove the section from the \
                                      config file.\n\n', nargs=1,
                                      required=False)
        config_subparser.set_defaults(handle=self.handleconfig.handleConfig)

        repo_subparser = subparsers.add_parser('repomgr',
                                               help='Manage source|binary \
packages.\t\teg: [ list|download|sync|mirror|clean|remove_repo|upload_pkg|\
delete_pkg ]')
        repo_subparser.add_argument('repomgr_task',
                                    help='[ list|download|sync|mirror|clean|\
                                    remove_repo|upload_pkg|delete_pkg ]: \
                                    Execute the management task.\n\n')
        repo_subparser.set_defaults(handle=stx_repomgr.handleRepomgr)

        parser.add_argument('-d', '--debug',
                            help='Enable debug output\n\n',
                            action='store_const', const=logging.DEBUG,
                            dest='loglevel', default=logging.INFO)

        parser.add_argument('-h', '--help',
                            help='Show this help message and exit\n\n',
                            action='help')

        parser.add_argument('-q', '--quiet',
                            help='Hide all output except error messages\n\n',
                            action='store_const', const=logging.ERROR,
                            dest='loglevel')

        parser.add_argument('-v', '--version',
                            help='Stx build tools version\n\n',
                            action='version', version='%(prog)s 1.0.0')
        return parser

    def parseArgs(self):
        args = self.parser.parse_args()
        logger.setLevel(args.loglevel)
        return args


def stx_main():
    command_line = CommandLine()
    args = command_line.parseArgs()

    if hasattr(args, 'handle'):
        args.handle(args)
    else:
        command_line.parser.print_help()

    return 0
