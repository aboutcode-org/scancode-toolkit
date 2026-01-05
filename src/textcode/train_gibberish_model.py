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
@click.option(
    '--big',
    type=click.Path(exists=True, readable=True, dir_okay=False, resolve_path=True, path_type=str),
    default=None,
    help='Text file containing main training corpus for the gibberish detector',
    cls=PluggableCommandLineOption,
)
@click.option(
    '--good',
    type=click.Path(exists=True, readable=True, dir_okay=False, resolve_path=True, path_type=str),
    default=None,
    help='Text file containing text considered to be not gibberish (good)',
    cls=PluggableCommandLineOption,
)
@click.option(
    '--bad',
    type=click.Path(exists=True, readable=True, dir_okay=False, resolve_path=True, path_type=str),
    default=None,
    help='Text file containing text considered to be gibberish (bad)',
    cls=PluggableCommandLineOption,
)
@click.help_option('-h', '--help')
def train_gibberish_model(big, good, bad, *args, **kwargs,):
    """Train model used by textcode.Gibberish to detect gibberish"""
    gibberish_detector_train_args = {}
    if big:
        gibberish_detector_train_args["bigfile"] = big
    if good:
        gibberish_detector_train_args["goodfile"] = good
    if bad:
        gibberish_detector_train_args["badfile"] = bad

    click.echo('Training gibberish detector model...')
    gibberish_detector = Gibberish()
    gibberish_detector.train(
        **gibberish_detector_train_args
    )


if __name__ == '__main__':
    train_gibberish_model()
