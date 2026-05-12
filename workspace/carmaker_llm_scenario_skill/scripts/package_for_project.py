#!/usr/bin/env python3
"""Package generated CarMaker files under a project-local subfolder."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def rewrite_testrun_paths(
    source: Path,
    destination: Path,
    road_name: str,
    template_names: list[str],
    subdir: str,
) -> list[str]:
    text = source.read_text(encoding="utf-8", errors="replace")
    changes: list[str] = []

    old_road = f"Road.FName = {road_name}"
    new_road = f"Road.FName = {subdir}/{road_name}"
    if old_road in text:
        text = text.replace(old_road, new_road, 1)
        changes.append(f"{old_road} -> {new_road}")

    for template_name in template_names:
        old_template = f"Template.FName = {template_name}"
        new_template = f"Template.FName = {subdir}/{template_name}"
        if old_template in text:
            text = text.replace(old_template, new_template)
            changes.append(f"{old_template} -> {new_template}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return changes


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def verify_package(package_root: Path, scenario: str, road_name: str, template_names: list[str], subdir: str) -> list[str]:
    errors: list[str] = []
    testrun = package_root / "Data" / "TestRun" / subdir / scenario
    road = package_root / "Data" / "Road" / subdir / road_name

    if not testrun.is_file():
        errors.append(f"missing packaged TestRun: {testrun}")
    if not road.is_file():
        errors.append(f"missing packaged Road: {road}")
    for template_name in template_names:
        template = package_root / "Data" / "Traffic" / "Template" / subdir / template_name
        if not template.is_file():
            errors.append(f"missing packaged template: {template}")

    if testrun.is_file():
        text = testrun.read_text(encoding="utf-8", errors="replace")
        if f"Road.FName = {subdir}/{road_name}" not in text:
            errors.append("TestRun road path was not rewritten")
        for template_name in template_names:
            expected = f"Template.FName = {subdir}/{template_name}"
            if expected not in text:
                errors.append(f"TestRun template path was not rewritten: {template_name}")
        if "Limit = t {}" in text:
            errors.append("TestRun still contains empty FollowTraj limit: Limit = t {}")
    return errors


def package(args: argparse.Namespace) -> tuple[Path, list[str]]:
    package_root = args.package_root / args.scenario
    subdir = args.subdir.strip("/\\")
    road_name = args.road.name
    template_names = [template.name for template in args.templates]

    changes = rewrite_testrun_paths(
        args.testrun,
        package_root / "Data" / "TestRun" / subdir / args.scenario,
        road_name,
        template_names,
        subdir,
    )
    copy_file(args.road, package_root / "Data" / "Road" / subdir / road_name)
    for template in args.templates:
        copy_file(template, package_root / "Data" / "Traffic" / "Template" / subdir / template.name)

    errors = verify_package(package_root, args.scenario, road_name, template_names, subdir)
    if errors:
        raise SystemExit("Package verification failed:\n" + "\n".join(f"- {error}" for error in errors))

    if args.install:
        if not args.project:
            raise SystemExit("--install requires --project")
        project_data = args.project / "Data"
        copy_file(
            package_root / "Data" / "TestRun" / subdir / args.scenario,
            project_data / "TestRun" / subdir / args.scenario,
        )
        copy_file(
            package_root / "Data" / "Road" / subdir / road_name,
            project_data / "Road" / subdir / road_name,
        )
        for template_name in template_names:
            copy_file(
                package_root / "Data" / "Traffic" / "Template" / subdir / template_name,
                project_data / "Traffic" / "Template" / subdir / template_name,
            )

    return package_root, changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--testrun", type=Path, required=True)
    parser.add_argument("--road", type=Path, required=True)
    parser.add_argument("--templates", type=Path, nargs="+", required=True)
    parser.add_argument(
        "--package-root",
        type=Path,
        default=Path("workspace/carmaker_llm_scenario_skill/packages"),
    )
    parser.add_argument("--subdir", default="LLM_Generated")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--project", type=Path)
    args = parser.parse_args()

    package_root, changes = package(args)
    print(f"package_root={package_root}")
    for change in changes:
        print(f"rewrite={change}")
    if args.install:
        print(f"installed_to={args.project}")


if __name__ == "__main__":
    main()
