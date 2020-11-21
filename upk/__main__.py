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
from .apk import read_package_info

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
root_logger = logging.getLogger('upk')

def collect_packages(path: str):
    'collect all packages from the directory'
    pkgs = {}

    def index_apk(apk_path: str, apk_name: str):
        logger = root_logger.getChild(repr(apk_name))
        pkginfo = read_package_info(apk_path, logger)
        if pkginfo:
            pkgs.setdefault(pkginfo['package'], []).append(pkginfo['version'])

    if os.path.isdir(path):
        for name in os.listdir(path):
            if name.lower().endswith('.apk'):
                index_apk(os.path.join(path, name), name)

    elif os.path.isfile(path):
        name = os.path.basename(path)
        if name.lower().endswith('.apk'):
            index_apk(path, name)
        else:
            root_logger.error(f'{name} is not a apk file.')

    else:
        root_logger.error(f'{path} is not a apk file or a directory.')

    return pkgs

def update_packages(path: str):
    if os.path.isfile(path):
        dlto = os.path.dirname(path)
    else:
        dlto = path

    for pkg, pkg_v in collect_packages(path).items():
        logger = root_logger.getChild(repr(pkg))
        provider = ApkPure(logger)
        local_versions = set(pkg_v)
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
            download(pkginfo['download_url'], dlto, logger=logger)
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
            update_packages(args[0])

    except: # pylint: disable=W0703
        traceback.print_exc()

if __name__ == '__main__':
    main()
