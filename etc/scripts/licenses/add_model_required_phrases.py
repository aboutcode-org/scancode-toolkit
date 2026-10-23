#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#


def main():
    try:
        from scancode_required_phrases.model_cli import add_model_required_phrases
    except ModuleNotFoundError as error:
        if error.name not in {
            "scancode_required_phrases",
            "scancode_required_phrases.model_cli",
        }:
            raise
        raise SystemExit(
            "The scancode-required-phrases model command is required. "
            "Install or update the package with its inference extra."
        ) from None

    add_model_required_phrases()


if __name__ == "__main__":
    main()
