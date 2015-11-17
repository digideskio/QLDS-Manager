from command.default import ManagerDefaultController
from cement.core.controller import expose
from util.config import Configuration
from util.filesystem import FSCheck
from urllib.request import urlretrieve
from subprocess import call
import os
import stat
import tarfile


class DownloadController(ManagerDefaultController):
    steamcmd_url = 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz'
    steamcmd_archive = '/steamcmd.tar.gz'
    ql_appid = 349090

    class Meta:
        label = 'download'
        description = 'Allows to download/update SteamCMD and QL Dedicated Server files'

    @expose(hide=True)
    def default(self):
        self.app.args.parse_args(['--help'])

    @expose(help='Downloads and installs SteamCMD')
    def steamcmd(self):
        config = Configuration()

        steamcmd_dir = os.path.expanduser(config.get('dir', 'steamcmd'))
        steamcmd_dir_fs = FSCheck(steamcmd_dir, 'SteamCMD dir')

        #check if steamcmd dir exists
        if steamcmd_dir_fs.exists(error=False):
            print('% exists. Remove it or change SteamCMD location in settings' % steamcmd_dir)
            exit(21)

        os.makedirs(steamcmd_dir)

        steamcmd_dir_fs.access('w') #check for write access in dir

        print('Downloading SteamCMD archive')
        urlretrieve(self.steamcmd_url, steamcmd_dir + self.steamcmd_archive)

        print('Extracting SteamCMD atchive to %s' % steamcmd_dir)
        archive = tarfile.open(steamcmd_dir + self.steamcmd_archive)
        archive.extractall(steamcmd_dir)

        steamcmd_stat = os.stat(steamcmd_dir + '/steamcmd.sh')
        os.chmod(steamcmd_dir + '/steamcmd.sh', steamcmd_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        print('SteamCMD installed in %s' % steamcmd_dir)
        print('Remember that you need "lib32stdc++6" installed in your system')

    @expose(help='Downloads and updates QL Dedicated Server files')
    def ql(self):
        config = Configuration()

        steamcmd = os.path.expanduser(config.get('dir', 'steamcmd') + '/steamcmd.sh')

        steamcmd_fs = FSCheck(steamcmd, 'SteamCMD')

        steamcmd_fs.exists()
        steamcmd_fs.access('x')

        print('Downloading QL Dedicated Server files using SteamCMD...')

        call([
            steamcmd,
            '+login', 'anonymous',
            '+force_install_dir', os.path.expanduser(config.get('dir', 'ql')),
            '+app_update', str(self.ql_appid),
            '+quit'
        ])