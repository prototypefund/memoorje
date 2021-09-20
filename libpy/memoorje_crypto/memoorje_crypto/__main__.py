#!/usr/bin/env python3

import argparse
import sys

from memoorje_crypto import formats


def _parse_args():
    parser = argparse.ArgumentParser(prog="memoorje.crypto")
    subparsers = parser.add_subparsers()

    def add_encryption_args(parser: argparse.ArgumentParser):
        parser.add_argument(
            "--encryption-format",
            default=formats.EncryptionV1.__name__,
            choices={formats.EncryptionV1.__name__},
            help="The encryption format to use.",
        )
        parser.add_argument(
            "--input",
            type=argparse.FileType("rb"),
            default=None if sys.stdin.isatty() else sys.stdin.buffer,
        )
        parser.add_argument(
            "--output",
            type=argparse.FileType("wb"),
            default=None if sys.stdout.isatty() else sys.stdout.buffer,
        )
        parser.add_argument(
            "--password",
            required=True,
            help="The password to use for encryption/decryption.",
        )

    encrypt = subparsers.add_parser("encrypt", help="encrypt data")
    add_encryption_args(encrypt)
    encrypt.set_defaults(method="encrypt")
    decrypt = subparsers.add_parser("decrypt", help="decrypt data")
    add_encryption_args(decrypt)
    decrypt.set_defaults(method="decrypt")
    return parser.parse_args()


def _main(args):
    if args.input is None:
        print(
            "Please define an input file via --input or use stdin.",
            file=sys.stderr,
        )
        sys.exit(1)
    if args.output is None:
        print(
            "Refusing to write binary data to stdout. " "Please specify a file or redirect output.",
            file=sys.stderr,
        )
        sys.exit(1)
    encryption = getattr(formats, args.encryption_format)()
    processor = getattr(encryption, args.method)
    data = processor(args.password, args.input.read())
    args.output.write(data)


if __name__ == "__main__":
    _main(_parse_args())
