#!/usr/bin/env python3

import argparse
import base64
import contextlib
import dataclasses
import datetime
import json
import logging
import mimetypes
import os
from os import makedirs, path, scandir
import shutil
import sys
import textwrap
import typing
from uuid import uuid4 as _uuid4

from memoorje.crypto import EncryptionV1

logger = logging.getLogger(__name__)
encryption = EncryptionV1()


def uuid4():
    return str(_uuid4())


def parse_datetime_or_now(date: typing.Optional[str], default: typing.Optional[datetime.datetime] = None):
    if default is None:
        default = datetime.datetime.now()
    try:
        return datetime.datetime.fromisoformat(date)
    except TypeError:
        return default
    except ValueError:
        logger.error("Invalid time format: %s", date)
        return default


@dataclasses.dataclass()
class Capsule:
    id: str
    name: str
    root_dir: str
    created_on: datetime.datetime
    updated_on: datetime.datetime
    description: typing.Optional[str] = None

    def contents(self):
        yield from find_capsule_contents(self.root_dir)


@dataclasses.dataclass()
class CapsuleContentMetadata:
    path: str
    mime_type: str
    created_on: datetime.datetime
    updated_on: datetime.datetime

    def as_dict(self):
        return {
            "path": self.path,
            "mimeType": self.mime_type,
            "createdOn": self.created_on.isoformat(),
            "updatedOn": self.updated_on.isoformat(),
        }

    def encrypt(self, password: str):
        data = serialize(self.as_dict())
        return encryption.encrypt(password, data)


@dataclasses.dataclass()
class CapsuleContent:
    id: str
    meta: CapsuleContentMetadata
    data: bytes


def find_capsule_contents(directory: str, root_dir: typing.Optional[str] = None) -> typing.Iterator[CapsuleContent]:
    if root_dir is None:
        root_dir = directory

    for item in os.scandir(directory):
        if item.is_file():
            if item.name == "_meta.json":
                continue
            now = datetime.datetime.now()
            metadata = CapsuleContentMetadata(
                item.path.removeprefix(f"{root_dir}/"),
                mimetypes.guess_type(item.name)[0],
                now,
                now,
            )
            with open(item.path, "rb") as capsule_data_file:
                yield CapsuleContent(
                    uuid4(),
                    metadata,
                    capsule_data_file.read(),
                )
        elif item.is_dir():
            yield from find_capsule_contents(item.path, root_dir)


def find_capsules(directory: str) -> typing.Iterator[Capsule]:
    for item in scandir(directory):
        if not item.is_dir():
            continue
        try:
            with open(path.join(item.path, "_meta.json")) as metafile:
                meta = json.load(metafile)
        except FileNotFoundError:
            meta = {}
        except json.JSONDecodeError:
            logger.error(f"Invalid meta file for capsule '{item.name}'")
            meta = {}
        created_on = parse_datetime_or_now(meta.get("createdOn", None))
        yield Capsule(
            uuid4(),
            item.name,
            root_dir=item.path,
            created_on=created_on,
            updated_on=parse_datetime_or_now(meta.get("updatedOn", None), created_on),
            description=meta.get("description", None),
        )


def _get_args():
    parser = argparse.ArgumentParser(
        path.basename(sys.argv[0]),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Exports a directory tree as a static capsule API tree. \n"
            "The directory from which to generate the tree should look like this: \n\n"
            "  a capsule/\n"
            "    a file.jpg\n"
            "    another file.md\n"
            "    a subdirectory/\n"
            "      a file in a subdirectory.txt\n"
            "  another capsule/\n"
            "    some file.mp3\n\n"
            "Each capsule may contain a _meta.json file with an optional description and \n"
            "createdOn and updatedOn datetimes formatted as ISO strings."
        ),
    )
    parser.add_argument(
        "--export-path",
        default="http://localhost:8080",
        help="The path to use as prefix for HTTP urls.",
    )
    parser.add_argument("--export-dir", default=None, help="The directory to export to.")
    parser.add_argument(
        "--password",
        required=True,
        help="The password to use for encryption.",
    )
    parser.add_argument("root_dir", help="The root dir from which a capsule API tree should be generated.")
    return parser.parse_args()


@contextlib.contextmanager
def gen_index(directory: str, filename: str = "index.json"):
    with open(path.join(directory, filename), "wb") as index_file:
        index_file.write(b'{\n    "results": [\n')

        class Writer:
            def __init__(self):
                self.is_first_write = True

            def write(self, data: bytes):
                if not self.is_first_write:
                    index_file.write(b",\n")
                else:
                    self.is_first_write = False
                index_file.write(textwrap.indent(data.decode(), prefix=" " * 8).encode())

        yield Writer()
        index_file.write(b"\n    ]\n}")


def serialize(obj):
    return json.dumps(obj, ensure_ascii=False, indent=4).encode()


def export(root_dir: str, password: str, export_path: str, export_dir: typing.Optional[str] = None):
    export_dir = export_dir or f"{root_dir}.export"
    capsule_dir = path.join(export_dir, "capsules")
    capsule_contents_dir = path.join(export_dir, "capsule-contents")

    try:
        shutil.rmtree(export_dir)
    except FileNotFoundError:
        pass
    makedirs(capsule_dir, exist_ok=True)
    makedirs(capsule_contents_dir, exist_ok=True)

    with gen_index(capsule_dir) as capsule_index, gen_index(capsule_contents_dir) as all_capsule_contents_index:
        for capsule in find_capsules(root_dir):
            capsule_api_object = {
                "id": capsule.id,
                "name": capsule.name,
                "description": capsule.description,
                "createdOn": capsule.created_on.isoformat(),
                "updatedOn": capsule.updated_on.isoformat(),
            }
            serialized_capsule = serialize(capsule_api_object)
            capsule_index.write(serialized_capsule)
            with open(path.join(capsule_dir, f"{capsule.id}.json"), "wb") as capsule_file:
                capsule_file.write(serialized_capsule)

            with gen_index(capsule_contents_dir, f"capsule-{capsule.id}-contents.json") as capsule_contents_index:
                for capsule_content in capsule.contents():
                    data_bin_name = f"{capsule_content.id}-data.bin"
                    capsule_content_api_object = {
                        "id": capsule_content.id,
                        "metadata": base64.b64encode(capsule_content.meta.encrypt(password)).decode(),
                        "data": path.join(export_path, "capsule-contents", data_bin_name),
                    }
                    with open(path.join(capsule_contents_dir, data_bin_name), "wb") as data_bin:
                        data_bin.write(encryption.encrypt(password, capsule_content.data))
                    serialized_capsule_content = serialize(capsule_content_api_object)
                    all_capsule_contents_index.write(serialized_capsule_content)
                    capsule_contents_index.write(serialized_capsule_content)
                    with open(path.join(capsule_contents_dir, f"{capsule_content.id}.json"), "wb") as cap_content_file:
                        cap_content_file.write(serialized_capsule_content)


def _main(args):
    export(args.root_dir, args.password, args.export_path, args.export_dir)


if __name__ == "__main__":
    _main(_get_args())
