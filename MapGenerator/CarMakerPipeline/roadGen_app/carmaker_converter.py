from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import importlib
import os
import sys
import zipfile


DEFAULT_CARMAKER_ROOT = Path(r"C:\IPG\carmaker")


class ConverterError(RuntimeError):
    pass


@dataclass
class ConversionResult:
    rd5_path: Path
    errors: list[str]
    warnings: list[str]


def find_carmaker_home() -> Path | None:
    if not DEFAULT_CARMAKER_ROOT.exists():
        return None
    candidates = sorted(DEFAULT_CARMAKER_ROOT.glob("win64-*"), key=lambda path: path.name, reverse=True)
    for candidate in candidates:
        if (candidate / "Python" / "IPGRoad").exists() and (candidate / "bin").exists():
            return candidate
    return None


def _extract_ipgroad_wheel(cm_home: Path, cache_dir: Path) -> Path:
    wheel_dir = cm_home / "Python" / "IPGRoad"
    wheels = sorted(wheel_dir.glob("ipgroad-*.whl"), reverse=True)
    if not wheels:
        raise ConverterError(f"ipgroad wheel not found under {wheel_dir}")

    wheel = wheels[0]
    target = cache_dir / wheel.stem / "purelib"
    package_dir = target / "ipgroad"
    if package_dir.exists():
        return target

    cache_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            marker = ".data/purelib/"
            if marker not in name:
                continue
            relative = name.split(marker, 1)[1]
            if not relative:
                continue
            dest = target / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not name.endswith("/"):
                dest.write_bytes(archive.read(name))
    return target


def _load_ipgroad(cm_home: Path, cache_dir: Path):
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(cm_home / "bin"))

    try:
        return importlib.import_module("ipgroad")
    except ModuleNotFoundError:
        purelib = _extract_ipgroad_wheel(cm_home, cache_dir)
        sys.path.insert(0, str(purelib))
        return importlib.import_module("ipgroad")


def _collect_messages(ipgroad, road, message_type: int) -> list[str]:
    result: list[str] = []
    messages = ipgroad.tRoadMessageList()
    ipgroad.RoadGetMessageList(road, message_type, messages)
    try:
        for index in range(messages.nMsgList):
            message = ipgroad.tRoadMessageArray_getitem(messages.msg, index)
            result.append(str(message.msg))
    finally:
        ipgroad.RoadDeleteMessageList(road, messages)
    if hasattr(ipgroad, "RoadClearMessageBuffer"):
        ipgroad.RoadClearMessageBuffer(road, message_type)
    return result


def convert_xodr_to_rd5(
    xodr_path: Path,
    rd5_path: Path,
    *,
    cm_home: Path | None = None,
    cache_dir: Path | None = None,
) -> ConversionResult:
    xodr_path = Path(xodr_path)
    rd5_path = Path(rd5_path)
    if not xodr_path.exists():
        raise ConverterError(f"OpenDRIVE file not found: {xodr_path}")

    cm_home = cm_home or find_carmaker_home()
    if not cm_home:
        raise ConverterError("CarMaker win64 installation with IPGRoad Python API was not found.")

    cache_dir = cache_dir or (Path(__file__).resolve().parent / ".ipgroad_cache")
    ipgroad = _load_ipgroad(cm_home, cache_dir)

    config = cm_home / "Data" / "Road" / "Config" / "Signals_DEU_2017.odrcfg"
    if config.exists():
        settings = ipgroad.tRoadReadODRSettings()
        ipgroad.RoadGetReadOpenDRIVEDefault(settings)
        settings.odrConfig = str(config)
        ipgroad.RoadSetReadOpenDRIVE(settings)

    rd5_path.parent.mkdir(parents=True, exist_ok=True)
    road = ipgroad.RoadNew()
    try:
        read_code = ipgroad.RoadReadOpenDRIVE(road, str(xodr_path))
        errors = _collect_messages(ipgroad, road, ipgroad.RMT_Error)
        warnings = _collect_messages(ipgroad, road, ipgroad.RMT_Warn)
        if read_code != ipgroad.ROAD_Ok:
            detail = "; ".join(errors[:3]) if errors else f"error code {read_code}"
            raise ConverterError(f"OpenDRIVE import failed: {detail}")

        write_code = ipgroad.RoadWriteFile(road, str(rd5_path), None)
        errors.extend(_collect_messages(ipgroad, road, ipgroad.RMT_Error))
        warnings.extend(_collect_messages(ipgroad, road, ipgroad.RMT_Warn))
        if write_code != ipgroad.ROAD_Ok:
            detail = "; ".join(errors[:3]) if errors else f"error code {write_code}"
            raise ConverterError(f"RD5 write failed: {detail}")
    finally:
        ipgroad.RoadDelete(road)

    return ConversionResult(rd5_path=rd5_path, errors=errors, warnings=warnings)
