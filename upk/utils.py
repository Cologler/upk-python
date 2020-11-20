# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import os
import logging

import progressbar
import requests
import atomicwrites

def download(url: str, path: str, logger: logging.Logger):
    r = requests.get(url=url, stream=True)
    if os.path.isdir(path):
        cd = r.headers['Content-Disposition']
        fn = cd.removeprefix('attachment; filename=').removeprefix('"').removesuffix('"')
        path = os.path.join(path, fn)
    else:
        fn = os.path.basename(path)

    logger.info(f'save to "{fn}".')

    bar = progressbar.ProgressBar(
        redirect_stdout=True,
        redirect_stderr=True,
        widgets=[
            progressbar.Percentage(),
            progressbar.Bar(),
            ' (',
            progressbar.AdaptiveTransferSpeed(),
            ' ',
            progressbar.ETA(),
            ') ',
        ])

    with atomicwrites.atomic_write(path, mode='wb') as f:
        total_length = int(r.headers.get('content-length'))
        bar.start(total_length)
        readsofar = 0
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                readsofar += len(chunk)
                bar.update(readsofar)
                f.write(chunk)
                f.flush()
        bar.finish()
