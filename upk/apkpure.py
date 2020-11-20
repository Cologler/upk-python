# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from urllib.parse import quote, urlsplit
from logging import Logger

from bs4 import BeautifulSoup
import progressbar
import requests

BASE_URL = "https://apkpure.com"

class ApkPure:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    def _get_soup(self, url: str):
        r = requests.get(url, timeout=30)
        return BeautifulSoup(r.content, features='html.parser')

    def _get_direct_download_url(self, dlpage_url: str):
        self._logger.debug(f'download page url: {dlpage_url}')
        soup = self._get_soup(dlpage_url)
        download_link = soup.select_one('#download_link')
        if download_link:
            download_url = download_link['href']
            return download_url

    def _get_variants(self, variant_url: str):
        self._logger.debug(f'variants page url: {variant_url}')
        variants = []
        soup = self._get_soup(variant_url)
        for row in soup.select('div.table-row'):
            if 'table-head' not in row['class']:
                cols = list(row.select('.table-cell'))
                variants.append(dict(
                    arch=cols[1].text,
                    url=BASE_URL+cols[4].select_one('a')['href']
                ))
        return variants

    def _get_latest_version_info(self, versions_url: str):
        self._logger.debug(f'versions page url: {versions_url}')
        soup = self._get_soup(versions_url)
        for item in soup.select('.ver-wrap li a'):
            file_type = item.select_one('.ver-item-t').text.lower() # apk or xapk
            if file_type not in  ('apk', 'xapk'):
                self._logger.warning(f'unknown file type: {file_type}.')
            if file_type == 'apk':
                version = item.select_one('.ver-item-n').text
                assert version[0] == 'V'
                version = version[1:]

                apk_page_url = BASE_URL + item['href']
                scope = urlsplit(apk_page_url).path.split('/')[3]
                if scope == 'variant':
                    variants = self._get_variants(apk_page_url)
                    variant = ([v for v in variants if v['arch'] == 'armeabi-v7a']+[None])[0]
                    assert variant, variants
                    download_page_url = variant['url']
                elif scope == 'download':
                    download_page_url = apk_page_url
                else:
                    self._logger.warning(f'unknown sub path: {scope}')
                    continue

                download_url = self._get_direct_download_url(download_page_url)
                return dict(
                    version=version,
                    download_url=download_url
                )

    def find_latest_package_info(self, name: str):
        url = f'{BASE_URL}/search?q={quote(name)}'
        soup = self._get_soup(url)
        a = soup.select_one('p.search-title a')
        if not a:
            self._logger.debug(f'no search result.')
            return None
        if not a['href'].endswith(name):
            self._logger.debug(f'no package match {name}')
            return None

        versions_url = BASE_URL + a['href'] + '/versions'
        return self._get_latest_version_info(versions_url)
