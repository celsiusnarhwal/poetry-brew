from pathlib import Path

import requests
from cleo.io.inputs.option import Option
from poetry.console.application import Application
from poetry.console.commands.command import Command
from poetry.plugins import ApplicationPlugin
from poetry.poetry import Poetry
from pydantic import BaseModel
from tomlkit import TOMLDocument

from templates import FORMULA_TEMPLATE


class PluginConfig(BaseModel):
    dependencies: list[str] = []

    def __init__(self, poetry: Poetry):
        def get_config(config: dict | TOMLDocument) -> dict:
            return {k.replace("-", "_"): v for k, v in
                    config.get("tool", {}).get("brew", {}).get("config", {}).items()}

        _config = get_config(poetry.file.read())

        super().__init__(**_config)


def get_package_info(package: str, version: str):
    response = requests.get(f"https://pypi.org/pypi/{package}/{version}/json")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Couldn't get package info for {package} {version}.")


def generate(cmd: Command, output: Path, include: list, exclude: list, only: list):
    plugin_config = PluginConfig(cmd.poetry)

    pyproject = cmd.poetry.file.read()
    lockfile = cmd.poetry.locker.lock_data
    tool_poetry = pyproject["tool"]["poetry"]
    resources = []

    root_pkg = {
        "name": tool_poetry["name"],
        "version": tool_poetry["version"],
        "description": tool_poetry.get("description") or "",
        "homepage": tool_poetry.get("homepage") or "",
    }

    root_pkg_info = get_package_info(root_pkg["name"], root_pkg["version"])

    dist_info = next(filter(lambda x: x["packagetype"] == "sdist", root_pkg_info["urls"]))

    root_pkg["url"] = dist_info["url"]
    root_pkg["checksum"] = dist_info["digests"]["sha256"]

    group_names = *tool_poetry.get("group", {}).keys(),

    match {*include, *exclude, *only}.difference(["main", *group_names]):
        case invalid_groups if invalid_groups:
            cmd.line_error(f"Invalid group(s): {', '.join(invalid_groups)}", style="error")
            return 1

    groups = only or set(group_names).intersection(include or group_names).union(["main"]).difference(exclude)

    for dependency in lockfile["package"]:
        if dependency["category"] in groups:
            pkg = {
                "name": dependency["name"],
            }

            pkg_info = get_package_info(pkg["name"], dependency["version"])

            dist_info = next(filter(lambda url: url["packagetype"] == "sdist", pkg_info["urls"]))

            pkg["url"] = dist_info["url"]
            pkg["checksum"] = dist_info["digests"]["sha256"]

            resources.append(pkg)

    formula = FORMULA_TEMPLATE.render(package=root_pkg, resources=resources, dependencies=plugin_config.dependencies)

    output.mkdir(parents=True, exist_ok=True)
    (output / f"{root_pkg['name']}.rb").write_text(formula)


class PoetryBrewCommand(Command):
    name = "brew"
    description = "Generate a Homebrew formula for the current project."
    options = [
        Option("--with", description="The optional dependency groups to include in the formula.", flag=False,
               is_list=True),
        Option("--without", description="The dependency groups to exclude from the formula. Supersedes --with.",
               flag=False, is_list=True),
        Option("--only",
               description="The only dependency groups to include in the formula. Overrides --with and --without.",
               flag=False,
               is_list=True),
        Option("--output",
               description="The directory to write the formula to. It and any intermediate directories will be "
                           "created as necessary. Defaults to the current working directory.",
               flag=False),
    ]

    def handle(self) -> int:
        output = Path(self.option("output") or Path.cwd())

        generate(
            self,
            output=output,
            include=self.option("with"),
            exclude=self.option("without"),
            only=self.option("only"),
        )


class PoetryBrewPlugin(ApplicationPlugin):
    def activate(self, application: Application) -> None:
        application.command_loader.register_factory("brew", self.brew_command_factory)

    @staticmethod
    def brew_command_factory():
        return PoetryBrewCommand()
