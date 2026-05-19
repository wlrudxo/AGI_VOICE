from __future__ import annotations

import argparse
import asyncio
import ctypes
import inspect
from pathlib import Path
import os
import subprocess
import sys
import zipfile


APP_DIR = Path(__file__).resolve().parent
SUPPORTED_PYTHON_TAGS = {
    (3, 9): "cp39",
    (3, 10): "cp310",
    (3, 11): "cp311",
    (3, 12): "cp312",
    (3, 13): "cp313",
}
DEFAULT_IPGMOVIE_READY_DELAY = 5.0
DEFAULT_MOVIENX_READY_DELAY = 20.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a CarMaker TestRun at a fixed realtime factor with a movie frontend.")
    parser.add_argument("--project", required=True, type=Path, help="CarMaker project directory.")
    parser.add_argument("--testrun", required=True, type=Path, help="Generated TestRun file path.")
    parser.add_argument("--cm-home", required=True, type=Path, help="CarMaker win64 installation directory.")
    parser.add_argument("--factor", default=5.0, type=float, help="Requested realtime factor.")
    parser.add_argument(
        "--movie-backend",
        choices=("ipgmovie", "movienx"),
        default="ipgmovie",
        help="Movie frontend to launch after the target TestRun is confirmed.",
    )
    parser.add_argument(
        "--movie-ready-delay",
        default=None,
        type=float,
        help=(
            "Seconds to wait after the movie frontend starts before switching to the requested realtime factor. "
            "Default: 5s for IPGMovie, 20s for MovieNX."
        ),
    )
    parser.add_argument(
        "--keep-movie-open",
        action="store_true",
        help="Keep CarMaker/movie windows open after the simulation finishes. Close the windows to end this runner.",
    )
    return parser.parse_args()


def find_one(folder: Path, pattern: str) -> Path:
    matches = sorted(folder.glob(pattern))
    if not matches:
        raise RuntimeError(f"Required CarMaker Python wheel not found: {folder / pattern}")
    return matches[0]


def extract_wheel(wheel_path: Path, target_dir: Path) -> None:
    with zipfile.ZipFile(wheel_path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            relative = Path(member.filename.replace("\\", "/"))
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"Unsafe wheel member path: {member.filename}")
            output_path = target_dir / relative
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(archive.read(member))


def ensure_cmapi_runtime(cm_home: Path) -> Path:
    version = sys.version_info[:2]
    tag = SUPPORTED_PYTHON_TAGS.get(version)
    if not tag:
        raise RuntimeError(
            "CarMaker 15.0.1 does not provide APO/infofiles wheels for "
            f"Python {version[0]}.{version[1]}. Use Python 3.9 through 3.13."
        )

    python_dir = cm_home / "Python"
    wheels = [
        find_one(python_dir, "cmapi-*.whl"),
        find_one(python_dir, f"apoc-*-{tag}-{tag}-win_amd64.whl"),
        find_one(python_dir, f"infofiles-*-{tag}-{tag}-win_amd64.whl"),
    ]

    runtime_dir = APP_DIR / ".cmapi_runtime" / f"{cm_home.name}_{tag}"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    marker = runtime_dir / ".ready"
    signature = "\n".join(f"{wheel.name}:{wheel.stat().st_mtime_ns}" for wheel in wheels)
    if not marker.exists() or marker.read_text(encoding="utf-8", errors="replace") != signature:
        for wheel in wheels:
            extract_wheel(wheel, runtime_dir)
        marker.write_text(signature, encoding="utf-8")
    return runtime_dir


def add_dll_directories(cm_home: Path) -> None:
    folders = [
        cm_home / "bin",
        cm_home / "GUI",
    ]
    if len(cm_home.parents) >= 2:
        folders.append(cm_home.parents[1] / "movienx" / cm_home.name / "bin")

    path_parts = []
    for folder in folders:
        if not folder.exists():
            continue
        path_parts.append(str(folder))
        try:
            os.add_dll_directory(str(folder))
        except (AttributeError, OSError):
            pass
    if path_parts:
        os.environ["PATH"] = os.pathsep.join([*path_parts, os.environ.get("PATH", "")])


def find_movienx_exe(cm_home: Path) -> Path:
    version_name = cm_home.name
    candidates = []
    if len(cm_home.parents) >= 2:
        candidates.append(cm_home.parents[1] / "movienx" / version_name / "bin" / "MovieNX.exe")
    candidates.extend(
        [
            Path(r"C:\IPG") / "movienx" / version_name / "bin" / "MovieNX.exe",
            cm_home / "GUI" / "Movie.exe",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise RuntimeError(f"MovieNX executable not found for {cm_home}")


def testrun_reference(project_dir: Path, testrun_path: Path) -> Path:
    data_testrun = (project_dir / "Data" / "TestRun").resolve()
    try:
        return testrun_path.resolve().relative_to(data_testrun)
    except ValueError:
        return Path(testrun_path.name)


def prepare_imports(cm_home: Path) -> None:
    if not (cm_home / "bin" / "CarMaker.win64.exe").exists():
        raise RuntimeError(f"CarMaker executable not found: {cm_home / 'bin' / 'CarMaker.win64.exe'}")
    runtime_dir = ensure_cmapi_runtime(cm_home)
    sys.path.insert(0, str(runtime_dir))
    add_dll_directories(cm_home)


def application_pid(application: object) -> int | None:
    if isinstance(application, int):
        return application if application > 0 else None
    if isinstance(application, subprocess.Popen):
        return application.pid if application.pid and application.pid > 0 else None
    getter = getattr(application, "get_pid", None)
    if not callable(getter):
        return None
    try:
        pid = int(getter())
    except Exception:
        return None
    return pid if pid > 0 else None


def process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    kernel32 = ctypes.windll.kernel32
    process_query_limited_information = 0x1000
    still_active = 259
    handle = kernel32.OpenProcess(process_query_limited_information, False, int(pid))
    if not handle:
        return False
    try:
        exit_code = ctypes.c_ulong()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        return exit_code.value == still_active
    finally:
        kernel32.CloseHandle(handle)


async def wait_for_user_to_close_apps(applications: list[tuple[str, object]]) -> None:
    pids = [(name, pid) for name, app in applications if (pid := application_pid(app))]
    if not pids:
        print("No application PIDs were available; keeping the CMAPI runner alive.", flush=True)
        while True:
            await asyncio.sleep(60.0)

    print(
        "Simulation finished. Leaving applications open: "
        + ", ".join(f"{name} pid={pid}" for name, pid in pids),
        flush=True,
    )
    print("Close CarMaker/movie windows to end this runner.", flush=True)
    while any(process_is_alive(pid) for _name, pid in pids):
        await asyncio.sleep(1.0)


def run_interactive(
    project_dir: Path,
    testrun_path: Path,
    factor: float,
    keep_movie_open: bool,
    movie_ready_delay: float,
    movie_backend: str,
    cm_home: Path,
) -> None:
    import cmapi

    startup_factor = 0.01
    startup_confirm_timeout = 3.0

    async def main() -> None:
        print("Loading CarMaker project and TestRun.", flush=True)
        cmapi.Project.load(project_dir)
        testrun = cmapi.Project.instance().load_testrun_parametrization(
            testrun_reference(project_dir, testrun_path)
        )
        variation = cmapi.Variation.create_from_testrun(testrun)
        if hasattr(variation, "set_name"):
            variation.set_name(testrun_path.name)
        if hasattr(variation, "set_initial_realtimefactor"):
            variation.set_initial_realtimefactor(startup_factor)

        simcontrol = cmapi.SimControlInteractive()
        simcontrol.set_variation(variation)

        async def call_optional_simcontrol(method_name: str) -> bool:
            method = getattr(simcontrol, method_name, None)
            if method is None:
                return False
            result = method()
            if inspect.isawaitable(result):
                await result
            return True

        master = cmapi.CarMaker()
        print("Starting CarMaker master application.", flush=True)
        await simcontrol.set_master(master)

        movie = None
        movie_process = None
        connected = False
        movie_started = False
        try:
            print("Connecting interactive simulation control.", flush=True)
            await simcontrol.start_and_connect()
            connected = True

            print(
                f"Setting temporary startup realtime factor to {startup_factor:g} "
                "until the target TestRun is confirmed.",
                flush=True,
            )
            simcontrol.set_realtimefactor(startup_factor)
            print("Starting simulation.", flush=True)
            await simcontrol.start_sim()
            print("Simulation start command returned; waiting for target TestRun time to advance.", flush=True)
            paused_for_movie = False
            try:
                await asyncio.wait_for(
                    simcontrol.create_quantity_condition(lambda time_s: time_s > 0.001, "Time").wait(),
                    timeout=startup_confirm_timeout,
                )
                print("Target TestRun is running; pausing while IPGMovie starts.", flush=True)
                try:
                    paused_for_movie = await call_optional_simcontrol("pause_sim")
                    if not paused_for_movie:
                        print("pause_sim is not available; IPGMovie will attach while running.", flush=True)
                except Exception as exc:
                    print(f"pause_sim failed; IPGMovie will attach while running: {exc}", flush=True)
            except asyncio.TimeoutError:
                print(
                    f"Target TestRun did not advance within {startup_confirm_timeout:g}s. "
                    "Starting IPGMovie before switching to the requested realtime factor.",
                    flush=True,
                )

            if movie_backend == "movienx":
                master_pid = application_pid(master)
                if not master_pid:
                    raise RuntimeError("Could not determine CarMaker PID for MovieNX attachment.")
                movienx_exe = find_movienx_exe(cm_home)
                movie_args = [
                    str(movienx_exe),
                    "-apppid",
                    str(master_pid),
                    "-projectdir",
                    str(project_dir),
                    "-renderapi",
                    "direct3d12",
                ]
                print("Starting MovieNX: " + " ".join(movie_args), flush=True)
                movie_process = subprocess.Popen(movie_args, cwd=str(movienx_exe.parent))
                movie_started = True
            else:
                movie = cmapi.IPGMovie()
                movie.attach_to_cm(master)
                await movie.start()
                movie_started = True
            if movie_ready_delay > 0:
                print(f"Waiting {movie_ready_delay:g}s for {movie_backend} to become ready.", flush=True)
                await asyncio.sleep(movie_ready_delay)

            print(f"Setting realtime factor to {factor:g}.", flush=True)
            simcontrol.set_realtimefactor(factor)
            if paused_for_movie:
                print("Resuming simulation after IPGMovie startup.", flush=True)
                try:
                    await call_optional_simcontrol("resume_sim")
                except Exception as exc:
                    print(f"resume_sim failed; continuing with current simulator state: {exc}", flush=True)
            print("Waiting for finish condition.", flush=True)
            await simcontrol.create_simstate_condition(cmapi.ConditionSimState.finished).wait()
            print("Simulation reached finished state.", flush=True)
            if keep_movie_open:
                connected = False
                movie_started = False
                movie_label = "MovieNX" if movie_backend == "movienx" else "IPGMovie"
                movie_app = movie_process if movie_backend == "movienx" else movie
                await wait_for_user_to_close_apps([("CarMaker", master), (movie_label, movie_app)])
        finally:
            if connected:
                await simcontrol.stop_and_disconnect()
            if movie is not None and movie_started:
                await movie.stop()
            if movie_process is not None and movie_started and movie_process.poll() is None:
                movie_process.terminate()

    cmapi.Task.run_main_task(main())


def main() -> int:
    args = parse_args()
    movie_ready_delay = args.movie_ready_delay
    if movie_ready_delay is None:
        movie_ready_delay = (
            DEFAULT_MOVIENX_READY_DELAY if args.movie_backend == "movienx" else DEFAULT_IPGMOVIE_READY_DELAY
        )
    print(f"Project: {args.project}", flush=True)
    print(f"TestRun: {args.testrun}", flush=True)
    print(f"CarMaker home: {args.cm_home}", flush=True)
    print(f"Realtime factor: {args.factor}", flush=True)
    print(f"Movie ready delay: {movie_ready_delay}", flush=True)
    print(f"Movie backend: {args.movie_backend}", flush=True)
    print(f"Keep movie open: {args.keep_movie_open}", flush=True)
    print(f"Python: {sys.executable} ({sys.version.split()[0]})", flush=True)
    prepare_imports(args.cm_home)
    run_interactive(
        args.project,
        args.testrun,
        args.factor,
        args.keep_movie_open,
        movie_ready_delay,
        args.movie_backend,
        args.cm_home,
    )
    print("CMAPI interactive run finished.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
