from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = Path(__file__).resolve().parent
ROADGEN_DIR = ROOT / "roadGen_app"
TRAFFICGEN_DIR = ROOT / "trafficGen_app"
ROADGEN_APP = ROADGEN_DIR / "desktop_app.py"
TRAFFICGEN_APP = TRAFFICGEN_DIR / "desktop_app.py"
ROADGEN_EXPORTS = ROADGEN_DIR / "exports"
DEFAULT_CARMAKER_PROJECTS = Path(r"C:\CM_Projects")
DEFAULT_PROJECT = DEFAULT_CARMAKER_PROJECTS / "MapGen_TEST"
SETTINGS_FILE = APP_ROOT / "settings.json"

sys.path.insert(0, str(ROADGEN_DIR))
from carmaker_converter import ConverterError, convert_xodr_to_rd5, find_carmaker_home  # noqa: E402
from rd5_environment import EnvironmentError, decorate_rd5_city  # noqa: E402


def latest_roadgen_export() -> Path | None:
    if not ROADGEN_EXPORTS.exists():
        return None
    folders = [
        path
        for path in ROADGEN_EXPORTS.iterdir()
        if path.is_dir() and list(path.glob("*.xodr")) and list(path.glob("*.net.xml"))
    ]
    if not folders:
        return None
    return max(folders, key=lambda path: path.stat().st_mtime)


def first_file(folder: Path, pattern: str) -> Path | None:
    if not folder.exists():
        return None
    files = sorted(folder.glob(pattern))
    return files[0] if files else None


def slugify(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in "._-" else "_" for char in value.strip())
    cleaned = cleaned.strip("._")
    return cleaned or "road_graph"


class PipelineApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CarMaker Map + Traffic Pipeline")
        self.geometry("980x700")
        self.minsize(860, 620)

        settings = self.load_settings()
        latest = latest_roadgen_export()

        self.project_var = tk.StringVar(value=settings.get("project") or str(DEFAULT_PROJECT))
        self.export_var = tk.StringVar(value=settings.get("export") or str(latest or ROADGEN_EXPORTS))
        self.xodr_var = tk.StringVar(value=settings.get("xodr") or "")
        self.rd5_var = tk.StringVar(value=settings.get("rd5") or "")
        self.scenario_var = tk.StringVar(value=settings.get("scenario") or "route_traffic")
        self.environment_var = tk.StringVar(value=settings.get("environment") or "None")
        self.status_var = tk.StringVar(value="Ready")
        self.auto_follow_var = tk.BooleanVar(value=settings.get("auto_follow_latest", True))
        self.current_export_signature: tuple[str, float] | None = None

        self._build_ui()
        self.refresh_from_export()
        self.after(1500, self.watch_latest_export)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(12, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="CarMaker Map + Traffic Pipeline", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, textvariable=self.status_var).grid(row=0, column=1, sticky="e")

        body = ttk.PanedWindow(self, orient="horizontal")
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        left = ttk.Frame(body, padding=(0, 0, 10, 0))
        right = ttk.Frame(body, padding=(10, 0, 0, 0))
        body.add(left, weight=0)
        body.add(right, weight=1)

        self._build_pipeline(left)
        self._build_status(right)

    def _build_pipeline(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)

        project_box = ttk.LabelFrame(parent, text="CarMaker Project", padding=8)
        project_box.grid(row=0, column=0, sticky="ew")
        project_box.columnconfigure(0, weight=1)
        ttk.Entry(project_box, textvariable=self.project_var, width=56).grid(row=0, column=0, sticky="ew")
        ttk.Button(project_box, text="Browse", command=self.browse_project).grid(row=0, column=1, padx=(6, 0))
        ttk.Button(project_box, text="Open Data/Road", command=self.open_road_folder).grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0)
        )

        road_box = ttk.LabelFrame(parent, text="1. Road Generation", padding=8)
        road_box.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        road_box.columnconfigure(0, weight=1)
        ttk.Button(road_box, text="Open RoadGen App", command=self.open_roadgen).grid(
            row=0, column=0, columnspan=3, sticky="ew"
        )
        ttk.Entry(road_box, textvariable=self.export_var, width=56).grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(road_box, text="Browse", command=self.browse_export).grid(row=1, column=1, padx=(6, 0), pady=(8, 0))
        ttk.Button(road_box, text="Latest", command=self.use_latest_export).grid(row=1, column=2, padx=(4, 0), pady=(8, 0))
        ttk.Button(road_box, text="Refresh Files", command=self.refresh_from_export).grid(
            row=2, column=0, columnspan=3, sticky="ew", pady=(6, 0)
        )
        ttk.Checkbutton(
            road_box,
            text="Auto-follow latest RoadGen export",
            variable=self.auto_follow_var,
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(6, 0))

        convert_box = ttk.LabelFrame(parent, text="2. XODR to RD5", padding=8)
        convert_box.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        convert_box.columnconfigure(1, weight=1)
        ttk.Label(convert_box, text="XODR").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(convert_box, textvariable=self.xodr_var, width=48).grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Button(convert_box, text="...", width=3, command=self.browse_xodr).grid(row=0, column=2, padx=(4, 0))
        ttk.Label(convert_box, text="RD5").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(convert_box, textvariable=self.rd5_var, width=48).grid(row=1, column=1, sticky="ew", pady=2)
        ttk.Button(convert_box, text="...", width=3, command=self.browse_rd5_output).grid(row=1, column=2, padx=(4, 0))
        ttk.Label(convert_box, text="Env").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Combobox(
            convert_box,
            textvariable=self.environment_var,
            values=["None", "City"],
            state="readonly",
            width=12,
        ).grid(row=2, column=1, sticky="w", pady=2)
        ttk.Button(convert_box, text="Convert XODR to RD5", command=self.convert_xodr).grid(
            row=3, column=0, columnspan=3, sticky="ew", pady=(8, 0)
        )

        traffic_box = ttk.LabelFrame(parent, text="3. Route and Traffic", padding=8)
        traffic_box.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        traffic_box.columnconfigure(1, weight=1)
        ttk.Label(traffic_box, text="TestRun name").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(traffic_box, textvariable=self.scenario_var, width=34).grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Button(traffic_box, text="Open TrafficGen With Current Paths", command=self.open_trafficgen).grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )

        actions = ttk.LabelFrame(parent, text="Short Flow", padding=8)
        actions.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        for row, text in enumerate(
            [
                "1. Open RoadGen, draw graph, Generate XODR.",
                "2. The latest RoadGen export is picked up automatically.",
                "3. Convert XODR to RD5.",
                "4. Open TrafficGen, plan routes, then Generate + Run 5x + IPGMovie.",
            ]
        ):
            ttk.Label(actions, text=text).grid(row=row, column=0, sticky="w", pady=2)

    def _build_status(self, parent: ttk.Frame) -> None:
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        summary = ttk.LabelFrame(parent, text="Detected Environment", padding=8)
        summary.grid(row=0, column=0, sticky="ew")
        summary.columnconfigure(1, weight=1)
        rows = [
            ("RoadGen", ROADGEN_APP),
            ("TrafficGen", TRAFFICGEN_APP),
            ("CarMaker", find_carmaker_home() or "Not found"),
        ]
        for row, (label, value) in enumerate(rows):
            ttk.Label(summary, text=label).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Label(summary, text=str(value)).grid(row=row, column=1, sticky="w", pady=2)

        log_box = ttk.LabelFrame(parent, text="Log", padding=8)
        log_box.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        log_box.rowconfigure(0, weight=1)
        log_box.columnconfigure(0, weight=1)
        self.log_text = tk.Text(log_box, wrap="word", height=20)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(log_box, orient="vertical", command=self.log_text.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log("Unified pipeline app started.")

    def browse_project(self) -> None:
        initial = self.project_var.get() or str(DEFAULT_CARMAKER_PROJECTS)
        selected = filedialog.askdirectory(title="Select CarMaker project", initialdir=initial)
        if selected:
            self.project_var.set(selected)
            self.refresh_rd5_default()

    def browse_export(self) -> None:
        selected = filedialog.askdirectory(title="Select RoadGen export", initialdir=str(ROADGEN_EXPORTS))
        if selected:
            self.export_var.set(selected)
            self.refresh_from_export()

    def browse_xodr(self) -> None:
        initial = Path(self.xodr_var.get()).parent if self.xodr_var.get() else Path(self.export_var.get())
        selected = filedialog.askopenfilename(
            title="Select OpenDRIVE XODR",
            initialdir=str(initial),
            filetypes=[("OpenDRIVE", "*.xodr"), ("All files", "*.*")],
        )
        if selected:
            self.xodr_var.set(selected)
            self.refresh_rd5_default()

    def browse_rd5_output(self) -> None:
        initial = Path(self.rd5_var.get()).parent if self.rd5_var.get() else Path(self.project_var.get()) / "Data" / "Road"
        selected = filedialog.asksaveasfilename(
            title="Select RD5 output",
            initialdir=str(initial),
            defaultextension=".rd5",
            filetypes=[("CarMaker RD5", "*.rd5"), ("All files", "*.*")],
        )
        if selected:
            self.rd5_var.set(selected)

    def use_latest_export(self) -> None:
        latest = latest_roadgen_export()
        if not latest:
            messagebox.showinfo("Latest Export", "No RoadGen export with XODR/net.xml was found.")
            return
        self.export_var.set(str(latest))
        self.refresh_from_export()

    def export_signature(self, folder: Path) -> tuple[str, float] | None:
        if not folder.exists():
            return None
        paths = [folder]
        paths.extend(folder.glob("*.xodr"))
        paths.extend(folder.glob("*.net.xml"))
        try:
            timestamp = max(path.stat().st_mtime for path in paths)
            return (str(folder.resolve()), timestamp)
        except OSError:
            return None

    def watch_latest_export(self) -> None:
        try:
            if self.auto_follow_var.get():
                latest = latest_roadgen_export()
                signature = self.export_signature(latest) if latest else None
                if latest and signature and signature != self.current_export_signature:
                    self.export_var.set(str(latest))
                    self.refresh_from_export(source="auto")
                    self.status_var.set("Auto-loaded latest RoadGen export")
        finally:
            self.after(1500, self.watch_latest_export)

    def refresh_from_export(self, source: str = "manual") -> None:
        folder = Path(self.export_var.get())
        xodr = first_file(folder, "*.xodr")
        net = first_file(folder, "*.net.xml")
        if xodr:
            self.xodr_var.set(str(xodr))
            self.refresh_rd5_default()
        self.current_export_signature = self.export_signature(folder)
        self.log("")
        prefix = "Auto-selected" if source == "auto" else "RoadGen export"
        self.log(f"{prefix}: {folder}")
        self.log(f"XODR: {xodr or 'not found'}")
        self.log(f"SUMO net: {net or 'not found'}")
        self.log(f"RD5 output: {self.rd5_var.get() or 'not set'}")
        self.status_var.set("Export refreshed")

    def refresh_rd5_default(self) -> None:
        xodr = Path(self.xodr_var.get()) if self.xodr_var.get() else None
        project = Path(self.project_var.get()) if self.project_var.get() else DEFAULT_PROJECT
        if xodr and xodr.name:
            self.rd5_var.set(str(project / "Data" / "Road" / f"{slugify(xodr.stem)}.rd5"))

    def convert_xodr(self) -> None:
        xodr = Path(self.xodr_var.get())
        rd5 = Path(self.rd5_var.get())
        if not xodr.exists():
            messagebox.showerror("Convert XODR", f"XODR not found:\n{xodr}")
            return
        if not rd5.name:
            messagebox.showerror("Convert XODR", "Set an RD5 output path first.")
            return

        environment = self.environment_var.get()
        self.status_var.set("Converting XODR to RD5...")
        self.log("")
        self.log(f"Converting: {xodr}")
        self.log(f"Output RD5: {rd5}")
        self.log(f"Environment: {environment}")

        def worker() -> None:
            try:
                result = convert_xodr_to_rd5(xodr, rd5)
                city_result = None
                if environment == "City":
                    city_result = decorate_rd5_city(result.rd5_path, seed=xodr.stem)
            except ConverterError as exc:
                self.after(0, lambda: self.finish_conversion_error(str(exc)))
            except EnvironmentError as exc:
                self.after(0, lambda: self.finish_conversion_error(str(exc)))
            except Exception as exc:
                self.after(0, lambda: self.finish_conversion_error(f"{type(exc).__name__}: {exc}"))
            else:
                self.after(
                    0,
                    lambda: self.finish_conversion_success(result.rd5_path, result.errors, result.warnings, city_result),
                )

        threading.Thread(target=worker, daemon=True).start()

    def finish_conversion_success(self, rd5: Path, errors: list[str], warnings: list[str], city_result) -> None:
        self.rd5_var.set(str(rd5))
        self.status_var.set("RD5 conversion complete")
        self.log(f"RD5 written: {rd5}")
        if city_result:
            self.log(
                f"City environment added: {city_result.objects_added} buildings on {city_result.links_used} road links"
            )
        if errors:
            self.log(f"IPGRoad messages: {len(errors)}")
            for message in errors[:8]:
                self.log(f"- {message}")
            if len(errors) > 8:
                self.log(f"- ... {len(errors) - 8} more")
        if warnings:
            self.log(f"Warnings: {len(warnings)}")
        messagebox.showinfo("Convert XODR", f"RD5 written:\n{rd5}")

    def finish_conversion_error(self, message: str) -> None:
        self.status_var.set("RD5 conversion failed")
        self.log(f"Conversion failed: {message}")
        messagebox.showerror("Convert XODR", message)

    def open_roadgen(self) -> None:
        if not ROADGEN_APP.exists():
            messagebox.showerror("Open RoadGen", f"RoadGen app not found:\n{ROADGEN_APP}")
            return
        subprocess.Popen([sys.executable, str(ROADGEN_APP)], cwd=ROADGEN_DIR)
        self.log("Opened RoadGen app.")

    def open_trafficgen(self) -> None:
        if not TRAFFICGEN_APP.exists():
            messagebox.showerror("Open TrafficGen", f"TrafficGen app not found:\n{TRAFFICGEN_APP}")
            return
        args = [sys.executable, str(TRAFFICGEN_APP)]
        if self.export_var.get():
            args.extend(["--folder", self.export_var.get()])
        if self.rd5_var.get():
            args.extend(["--rd5", self.rd5_var.get()])
        if self.project_var.get():
            args.extend(["--project", self.project_var.get()])
        if self.scenario_var.get():
            args.extend(["--scenario", self.scenario_var.get()])
        preset = Path(self.export_var.get()) / "video2map_trafficgen_preset.json" if self.export_var.get() else None
        if preset and preset.exists():
            args.extend(["--preset", str(preset)])
        subprocess.Popen(args, cwd=TRAFFICGEN_DIR)
        self.log("Opened TrafficGen app with current paths.")

    def open_road_folder(self) -> None:
        folder = Path(self.project_var.get()) / "Data" / "Road"
        folder.mkdir(parents=True, exist_ok=True)
        os.startfile(folder)

    def load_settings(self) -> dict:
        if not SETTINGS_FILE.exists():
            return {}
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_settings(self) -> None:
        payload = {
            "project": self.project_var.get(),
            "export": self.export_var.get(),
            "xodr": self.xodr_var.get(),
            "rd5": self.rd5_var.get(),
            "scenario": self.scenario_var.get(),
            "environment": self.environment_var.get(),
            "auto_follow_latest": self.auto_follow_var.get(),
        }
        SETTINGS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def on_close(self) -> None:
        self.save_settings()
        self.destroy()

    def log(self, message: str) -> None:
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")


def main() -> None:
    PipelineApp().mainloop()


if __name__ == "__main__":
    main()
