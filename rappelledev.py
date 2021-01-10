#!/bin/env python3
import argparse
import subprocess
import os
import json
import enum
import logging


# Logging
logging.basicConfig(level=logging.INFO)


# Globals
DB_NAME = "rappelle-be"
TEST_DB_NAME = "rappelle-be-test"
POSTGRES_USER = "theuser"
CONFIG_DIR = os.path.expanduser("~/.config/rappelledev")
CONFIG_FILE = f"{CONFIG_DIR}/config.json"
DOCKER_COMPOSE_OVERRIDE_FILE = f"{CONFIG_DIR}/docker-compose.override.yaml"


# Helpers
def read_json_file(f):
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'rb') as f:
            return json.load(f)


class Env(enum.Enum):
    prod = 'prod'
    dev = 'dev'


class Runner():
    """ A configurable runner for commands """

    def __init__(self, cwd, docker_compose_cmd, env):
        self.cwd = cwd
        self.env = env
        self.docker_compose_cmd = docker_compose_cmd
        self.logger = logging.getLogger("Runner")

    def run(self, args, cwd=None, check=True):
        cwd = cwd or self.cwd
        self.logger.info(f"Running {args} in {cwd}")
        return subprocess.run(args, cwd=cwd, check=check)

    def run_docker_compose(self, args, **kwargs):
        cwd = self.cwd + "/docker-compose"
        prefix_args = self.docker_compose_cmd
        prefix_args += ["-f", "docker-compose.yaml"]
        if self.env == Env.prod.value:
            prefix_args += ["-f", "docker-compose.prod.yaml"]
        if self.env == Env.dev.value:
            prefix_args += ["-f", "docker-compose.dev.yaml"]
        if os.path.isfile(DOCKER_COMPOSE_OVERRIDE_FILE):
            prefix_args += ["-f", DOCKER_COMPOSE_OVERRIDE_FILE]
        return self.run([*prefix_args, *args], **kwargs, cwd=cwd)

    def check_output(self, args, cwd=None):
        cwd = cwd or self.cwd
        self.logger.info(f"Capturing {args} in {cwd}")
        return subprocess.check_output(args, cwd=cwd)


class Command():
    """ A superclass for all commands """

    def __init__(self, runner):
        self._runner = runner

    @classmethod
    def get_name(self):
        raise NotImplementedError()

    @classmethod
    def configure_parser(cls, parser):
        raise NotImplementedError()

    def __call__(self, args):
        raise NotImplementedError()


# Commands
class RunPostgresCmd(Command):

    @classmethod
    def get_name(self):
        return "run-postgres"

    @classmethod
    def configure_parser(cls, parser):
        parser.add_argument(
            "args",
            nargs="+",
            help="Arguments passed to docker-compose up"
        )

    def __call__(self, args):
        self._runner.run_docker_compose(
            [
                "up",
                "--force-recreate",
                *(args.args or []),
                "postgres"
            ]
        )


class RunRappelleBeCmd(Command):

    @classmethod
    def get_name(self):
        return "run-rappelle-be"

    @classmethod
    def configure_parser(cls, parser):
        pass

    def __call__(self, args):
        self._runner.run_docker_compose(
            [
                "up",
                "--force-recreate",
                "--build",
                "rappelle-be"
            ]
        )


class RunRappelleWebCmd(Command):

    @classmethod
    def get_name(self):
        return "run-rappelle-web"

    @classmethod
    def configure_parser(cls, parser):
        pass

    def __call__(self, args):
        self._runner.run_docker_compose(["up", "--force-recreate", "--build", "rappelle-web"])


class RunReverseProxyCmd(Command):

    @classmethod
    def get_name(self):
        return "run-revproxy"

    @classmethod
    def configure_parser(cls, parser):
        pass

    def __call__(self, args):
        self._runner.run_docker_compose(
            [
                "up",
                "--force-recreate",
                "--build",
                "--no-deps",
                "revproxy"
            ]
        )


class DockerComposeCmd(Command):
    """ Runs a docker-compose command in the right context """

    @classmethod
    def get_name(self):
        return "docker-compose"

    @classmethod
    def configure_parser(cls, parser):
        parser.add_argument("args", nargs='+', help="Command to run")

    def __call__(self, args):
        self._runner.run_docker_compose(args.args)


class RunHostRevproxyCmd(Command):
    """ Runs a reversr proxy at the host network """

    @classmethod
    def get_name(self):
        return "run-host-revproxy"

    @classmethod
    def configure_parser(cls, parser):
        pass

    def __call__(self, args):
        self._runner.run_docker_compose(["build", "local-revproxy"])
        self._runner.run_docker_compose(["run", "local-revproxy"])


# ArgumentParser
# Arg parsing
parser = argparse.ArgumentParser(description="Development tools for rappelle")
parser.add_argument(
    "-D",
    "--directory",
    help="the directory with the github repo root"
)
parser.add_argument(
    "--docker-compose-cmd",
    help="json array with comand to use for docker compose"
)
parser.add_argument(
    "-e",
    "--env",
    help="Environment. One of dev or prod.",
    choices=list((x.value for x in Env))
)

subparsers = parser.add_subparsers()

for cmd_cls in Command.__subclasses__():
    name = cmd_cls.get_name()
    doc = cmd_cls.__doc__
    sub_parser = subparsers.add_parser(name, help=doc)
    sub_parser.set_defaults(cmd_cls=cmd_cls)
    cmd_cls.configure_parser(sub_parser)


def main():
    args = parser.parse_args()
    config = read_json_file(CONFIG_FILE) or {}
    env = args.env or config.get("env") or Env.prod.value
    assert env in (x.value for x in Env), f"Invalid env \"{env}\""
    docker_compose_cmd = (
        args.docker_compose_cmd
        or config.get("docker-compose-cmd", None)
        or ["/bin/env", "docker-compose"]
    )
    directory = args.directory or config.get("directory") or os.path.expanduser("~/rappelledev")
    logging.info("Starting with env=%s directory=%s docker_compose_cmd=%s", env, directory, docker_compose_cmd)
    runner = Runner(cwd=directory, docker_compose_cmd=docker_compose_cmd, env=env)
    args.cmd_cls(runner)(args)


if __name__ == "__main__":
    main()
