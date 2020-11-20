# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import *
import os
import sys
import traceback
import zipfile
import xml.etree.ElementTree as et
import logging

from .androidManifestDecompress import read
from .apkpure import ApkPure
from .utils import download

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
root_logger = logging.getLogger('upk')

def collect_pkgs(d: str):
    'collect all packages from the directory'
    pkgs = {}
    for name in os.listdir(d):
        if name.lower().endswith('.apk'):
            path = os.path.join(d, name)
            with zipfile.ZipFile(path) as z:
                with z.open('AndroidManifest.xml') as am:
                    try:
                        a = read(am)
                    except:
                        root_logger.getChild(repr(name)).error(f'unable decode manifest, skiped.')
                    else:
                        xml = et.fromstring(a)
                        pkgs.setdefault(xml.get('package'), []).append(xml.get('versionName'))
    return pkgs

def update_apks(d: str):
    pkgs = collect_pkgs(d)
    # todo: sort
    for pkg in pkgs:
        logger = root_logger.getChild(repr(pkg))
        provider = ApkPure(logger)
        local_versions = set(pkgs[pkg])
        pkginfo = provider.find_latest_package_info(pkg)
        if not pkginfo:
            logger.info('unable find packages, skiped.')
            continue
        if not pkginfo['download_url']:
            logger.info('unable find download url, skiped.')
            continue
        latest_version = pkginfo['version']
        logger.debug(f'local version: {local_versions}, latest version: {latest_version}')
        if latest_version not in local_versions:
            logger.info(f'found new version, begin download...')
            download(pkginfo['download_url'], d, logger=logger)
        else:
            logger.info('current is latest version, nothing to do.')

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        args = argv[1:]

        root_logger.setLevel(level=logging.INFO)
        if '--debug' in args:
            args.remove('--debug')
            root_logger.setLevel(level=logging.DEBUG)

        if args:
            update_apks(args[0])

    except Exception: # pylint: disable=W0703
        traceback.print_exc()
        if sys.stderr.isatty(): input('wait for read...')

if __name__ == '__main__':
    main()
