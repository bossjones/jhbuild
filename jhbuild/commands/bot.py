# jhbuild - a build script for GNOME 1.x and 2.x
# Copyright (C) 2001-2006  James Henstridge
# Copyright (C) 2008 Frederic Peters
#
#   bot.py: buildbot slave commands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os
import sys
import urllib
from optparse import make_option
import socket
import __builtin__

import jhbuild.moduleset
import jhbuild.frontends
from jhbuild.commands import Command, register_command
from jhbuild.commands.base import cmd_build
from jhbuild.config import addpath
from jhbuild.errors import UsageError, FatalError, CommandError

try:
    import buildbot
except ImportError:
    buildbot = None

class cmd_bot(Command):
    doc = _('Control buildbot slave')

    name = 'bot'
    usage_args = '[ options ... ]'

    def __init__(self):
        Command.__init__(self, [
            make_option('--setup',
                        action='store_true', dest='setup', default=False,
                        help=_('create a new instance')),
            make_option('--start',
                        action='store_true', dest='start', default=False,
                        help=_('start an instance')),
            make_option('--stop',
                        action='store_true', dest='stop', default=False,
                        help=_('stop an instance')),
            make_option('--log',
                        action='store_true', dest='log', default=False,
                        help=_('watch the log of a running instance')),
            make_option('--step',
                        action='store_true', dest='step', default=False,
                        help=_('exec a buildbot step (internal use)')),
            make_option('--start-server',
                        action='store_true', dest='start_server', default=False,
                        help=_('start a buildbot server')),
            ])

    def run(self, config, options, args):
        if options.setup:
            return self.setup(config)

        global buildbot
        if buildbot is None:
            import site
            pythonversion = 'python' + str(sys.version_info[0]) + '.' + str(sys.version_info[1])
            pythonpath = os.path.join(config.prefix, 'lib', pythonversion, 'site-packages')
            site.addsitedir(pythonpath)
            if config.use_lib64:
                pythonpath = os.path.join(config.prefix, 'lib64', pythonversion, 'site-packages')
                site.addsitedir(pythonpath)
            try:
                import buildbot
            except ImportError:
                raise FatalError(_('buildbot and twisted not found, run jhbuild bot --setup'))

        # make jhbuild config file accessible to buildbot files
        # (master.cfg , steps.py, etc.)
        __builtin__.__dict__['jhbuild_config'] = config

        if options.start:
            return self.start(config)
        if options.step:
            os.environ['JHBUILDRC'] = config.filename
            os.environ['LC_ALL'] = 'C'
            os.environ['LANGUAGE'] = 'C'
            os.environ['LANG'] = 'C'
            __builtin__.__dict__['_'] = lambda x: x
            config.interact = False
            config.nonetwork = True
            if args[0] == 'update':
                command = 'updateone'
                config.nonetwork = False
            elif args[0] == 'build':
                command = 'buildone'
                config.alwaysautogen = True
            elif args[0] == 'check':
                command = 'buildone'
                config.nobuild = True
                config.makecheck = True
                config.forcecheck = True
                config.build_policy = 'all'
            else:
                command = args[0]
            os.environ['TERM'] = 'dumb'
            rc = jhbuild.commands.run(command, config, args[1:])
            sys.exit(rc)
        if options.start_server:
            return self.start_server(config)


    def setup(self, config):
        module_set = jhbuild.moduleset.load(config, 'buildbot')
        module_list = module_set.get_module_list('all', config.skip)
        build = jhbuild.frontends.get_buildscript(config, module_list)
        return build.build()
    
    def start(self, config):
        from twisted.application import service
        application = service.Application('buildslave')
        if ':' in config.jhbuildbot_master:
            master_host, master_port = config.jhbuildbot_master.split(':')
            master_port = int(master_port)
        else:
            master_host, master_port = config.jhbuildbot_master, 9070

        slave_name = config.jhbuildbot_slavename or socket.gethostname()

        keepalive = 600
        usepty = 0
        umask = None
        basedir = os.path.join(config.checkoutroot, 'jhbuildbot')
        if not os.path.exists(os.path.join(basedir, 'builddir')):
            os.makedirs(os.path.join(basedir, 'builddir'))
        os.chdir(basedir)

        from buildbot.slave.bot import BuildSlave
        s = BuildSlave(master_host, master_port,
                slave_name, config.jhbuildbot_password, basedir,
                keepalive, usepty, umask=umask)
        s.setServiceParent(application)


        from twisted.scripts._twistd_unix import UnixApplicationRunner, ServerOptions

        options = ServerOptions()
        options.parseOptions(['--no_save', '--nodaemon'])

        class JhBuildbotApplicationRunner(UnixApplicationRunner):
            application = None

            def createOrGetApplication(self):
                return self.application

        JhBuildbotApplicationRunner.application = application
        JhBuildbotApplicationRunner(options).run()

    def start_server(self, config):

        from twisted.scripts._twistd_unix import UnixApplicationRunner, ServerOptions

        options = ServerOptions()
        options.parseOptions(['--no_save', '--nodaemon'])

        class JhBuildbotApplicationRunner(UnixApplicationRunner):
            application = None

            def createOrGetApplication(self):
                return self.application

        from twisted.application import service
        from buildbot.master import BuildMaster
        application = service.Application('buildmaster')

        basedir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '../../buildbot/')
        os.chdir(basedir)
        if not os.path.exists(os.path.join(basedir, 'builddir')):
            os.makedirs(os.path.join(basedir, 'builddir'))
        master_cfg_path = os.path.join(basedir, 'master.cfg')

        BuildMaster(basedir, master_cfg_path).setServiceParent(application)

        JhBuildbotApplicationRunner.application = application
        JhBuildbotApplicationRunner(options).run()


register_command(cmd_bot)
