# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import TypedDict, Optional
from logging import Logger
import zipfile
import xml.etree.ElementTree as et

from .androidManifestDecompress import read

class _PackageInfo(TypedDict):
    package: Optional[str]
    version: Optional[str]

def read_package_info(path: str, logger: Logger) -> Optional[_PackageInfo]:
    'read package info from *.apk file.'

    with zipfile.ZipFile(path) as z:
        with z.open('AndroidManifest.xml') as am:
            try:
                a = read(am)
            except:
                logger.warning(f'unable decode manifest, skiped.')
            else:
                xml = et.fromstring(a)
                return dict(
                    package=xml.get('package'),
                    version=xml.get('versionName')
                )
