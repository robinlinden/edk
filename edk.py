#!/usr/bin/env python3

import argparse
import pathlib


def _get_sdk_files():
    local_sdk_dir = pathlib.Path.cwd() / ".edk"
    local_sdks = list(local_sdk_dir.glob("*.yaml"))
    return local_sdks


def _get_sdk_file(sdk_name):
    sdks = _get_sdk_files()
    for sdk in sdks:
        if sdk.name.strip(".yaml") == sdk_name:
            return sdk
    return None


def do_list(_):
    sdks = _get_sdk_files()
    print("Available SDKs:")
    for sdk in sdks:
        print(sdk.name.strip(".yaml"))


def do_show(args):
    sdk = _get_sdk_file(args.sdk)
    if sdk is None:
        print(f"SDK {args.sdk} not found.")
        exit(1)
    sdk_data = sdk.read_text()
    print(sdk_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=do_list)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("sdk")
    show_parser.set_defaults(func=do_show)

    parsed = parser.parse_args()
    parsed.func(parsed)
