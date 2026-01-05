#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import click

from commoncode.cliutils import PluggableCommandLineOption
from textcode.gibberish import Gibberish

@click.command(name='scancode-train-gibberish-model')
@click.help_option('-h', '--help')
def train_gibberish_model(*args, **kwargs,):
    """Train model used by textcode.Gibberish to detect gibberish"""
    click.echo('Training gibberish detector model...')
    gibberish_detector = Gibberish()
    gibberish_detector.train()


if __name__ == '__main__':
    train_gibberish_model()
