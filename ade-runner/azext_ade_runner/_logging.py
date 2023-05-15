# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=logging-fstring-interpolation

import os

from knack.log import get_logger as knack_get_logger

from ._constants import ACTION_NAME, IN_RUNNER, STORAGE_DIR


def get_logger(name: str):
    '''Get the logger for the extension'''
    _logger = knack_get_logger(name)

    # this must only happen in the builder, otherwise
    # the log file could be created on users machines
    if IN_RUNNER and STORAGE_DIR.is_dir():
        import logging
        log_file = STORAGE_DIR / 'runner.log'
        formatter = logging.Formatter('{asctime} [{name:^28}] {levelname:<8}: {message}',
                                      datefmt='%m/%d/%Y %I:%M:%S %p', style='{',)
        fh = logging.FileHandler(log_file)
        fh.setLevel(level=_logger.level)
        fh.setFormatter(formatter)
        _logger.addHandler(fh)

    return _logger


log = get_logger(__name__)

log.info('##################################')
log.info('Azure Depoyment Environment Runner')
log.info('##################################')
log.info('')
log.info(f'IN_RUNNER: {IN_RUNNER}')
log.info('')
log.info(f'Running action: {ACTION_NAME}')
log.info('')
log.info('ENVIRONMENT VARIABLES:')
log.info('======================')
for key, value in os.environ.items():
    log.info(f'{key}: {value}')
log.info('======================')
log.info('')
