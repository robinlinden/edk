#!/usr/bin/env python3

import argparse
import os
import pathlib
import subprocess
import yaml


def _path_from_env(variable, default):
    value = os.environ.get(variable)
    if value:
        return pathlib.Path(value)
    return default


HOME = pathlib.Path(os.path.expandvars("$HOME"))
XDG_CONFIG_HOME = _path_from_env("XDG_CONFIG_HOME", HOME / ".config")


class Sdks:
    def __init__(self, local=None, user=None):
        self.local = local or list()
        self.user = user or list()

    def __str__(self):
        s = "Local:\n" + "\n".join(map(lambda p: "  " + p.name[:-5], self.local)) + "\n"
        s += "User:\n" + "\n".join(map(lambda p: "  " + p.name[:-5], self.user))
        return s

    def all(self):
        return self.local + self.user


def _get_sdk_files():
    local_sdk_dir = pathlib.Path.cwd() / ".edk"
    user_sdk_dir = XDG_CONFIG_HOME / "edk"
    return Sdks(list(local_sdk_dir.glob("*.yaml")), list(user_sdk_dir.glob("*.yaml")))


def _get_sdk_file(sdk_name):
    sdks = _get_sdk_files()
    for sdk in sdks.all():
        if sdk.name[:-5] == sdk_name:
            return sdk
    return None


def do_list(_):
    sdks = _get_sdk_files()
    print("Available SDKs:")
    print(sdks)


def _require_sdk(name):
    sdk = _get_sdk_file(name)
    if sdk is None:
        print(f"SDK {name} not found.")
        exit(1)
    return sdk


def do_show(args):
    sdk = _require_sdk(args.sdk)
    sdk_data = sdk.read_text()
    print(sdk_data)


class CMakeCommand:
    def __init__(self):
        self.env = dict()
        self.build_dir = None
        self.generator = None
        self.arguments = dict()

    def __str__(self):
        s = str()
        if self.env:
            s += " ".join("{}={}".format(*i) for i in self.env.items())
            s += " "
        s += "cmake "
        s += "-S ."
        if self.build_dir:
            s += f" -B {self.build_dir}"
        if self.generator:
            s += f" -G\"{self.generator}\""
        if len(self.arguments) > 0:
            s += " "
            s += " ".join("-D{}={}".format(*i) for i in self.arguments.items())
        return s


def _make_cmake_command(data):
    cmake = CMakeCommand()

    cmake.env = data["env"]

    if not data["cmake"]:
        return cmake

    data = data["cmake"]
    cmake.build_dir = data["build_dir"]
    cmake.generator = data["generator"]
    cmake.arguments = data["args"]
    return cmake


def do_cmake(args):
    sdk = _require_sdk(args.sdk)
    with open(sdk) as f:
        data = yaml.load(f, Loader=yaml.Loader)
    cmake_command = _make_cmake_command(data)
    print(f"Running `{cmake_command}`", flush=True)

    env = {
        **os.environ,
        **cmake_command.env
    }
    cmake_command.env = None
    exit(subprocess.run(str(cmake_command), env=env).returncode)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=do_list)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("sdk")
    show_parser.set_defaults(func=do_show)

    show_parser = subparsers.add_parser("cmake")
    show_parser.add_argument("sdk")
    show_parser.set_defaults(func=do_cmake)

    parsed = parser.parse_args()
    parsed.func(parsed)
