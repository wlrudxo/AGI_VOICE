from __future__ import annotations

import argparse
from datetime import datetime
import os
import math
from pathlib import Path
import random
import re
import shlex
import shutil
import subprocess
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from traffic_core import (
    DEFAULT_ROADGEN_EXPORTS,
    ROOT,
    RoadPackage,
    RoadPackageError,
    PlannedRoute,
    VehiclePlan,
    build_openscenario,
    find_latest_roadgen_export,
    safe_name,
    vehicle_category,
    write_plan,
)
from rd5_core import Rd5Road, build_mapping_report, lane_path_sequence, map_route_to_rd5, write_rd5_with_route
from testrun_core import EgoPlan, TestRunConfig, project_road_reference, write_testrun

ROADGEN_APP = ROOT.parent / "roadGen_app"
if ROADGEN_APP.exists() and str(ROADGEN_APP) not in sys.path:
    sys.path.append(str(ROADGEN_APP))
try:
    from rd5_environment import decorate_rd5_intersections
except Exception:
    decorate_rd5_intersections = None


DEFAULT_MODEL = "1_Vehicles/Audi_S3_2015"
DEFAULT_DRIVER = "Car_Generic_Normal"
DEFAULT_RD5 = Path(r"C:\CM_Projects\MapGen_TEST\Data\Road\figure8_with_high_way_road.rd5")
DEFAULT_CM_PROJECT = Path(r"C:\CM_Projects\MapGen_TEST")
DEFAULT_EGO_MODEL = "Examples/DemoCar_BA"
DEFAULT_EGO_DRIVER = "Car_Normal"
DEFAULT_CARMAKER_HOME = Path(r"C:\IPG\carmaker\win64-15.0.1")
DEFAULT_PEDESTRIAN_MODEL = "2_People/Pedestrian_Male_Casual_01"
TRAFFIC_CONTROL_LABELS = {
    "IPG Driver (AutoDriver)": "ipg_driver",
    "Scripted constant speed": "constant_speed",
}
TRAFFIC_CONTROL_NAMES = {value: label for label, value in TRAFFIC_CONTROL_LABELS.items()}
PEDESTRIAN_MODELS = [
    "2_People/Pedestrian_Male_Casual_01",
    "2_People/Pedestrian_Male_Casual_01_Red",
    "2_People/Pedestrian_Female_Casual_01",
    "2_People/Pedestrian_Female_Sportive_01",
    "2_People/Pedestrian_Female_Child_01_142cm",
]


def find_carmaker_home() -> Path | None:
    if DEFAULT_CARMAKER_HOME.exists():
        return DEFAULT_CARMAKER_HOME
    root = Path(r"C:\IPG\carmaker")
    if not root.exists():
        return None
    candidates = sorted(root.glob("win64-15.0.1"), reverse=True)
    return candidates[0] if candidates else None


class TrafficGenApp(tk.Tk):
    def __init__(
        self,
        *,
        initial_folder: Path | None = None,
        initial_rd5: Path | None = None,
        initial_project: Path | None = None,
        initial_scenario: str | None = None,
    ) -> None:
        super().__init__()
        self.title("Traffic Route Generator")
        self.geometry("1320x820")
        self.minsize(1080, 680)

        latest = find_latest_roadgen_export()
        self.folder_var = tk.StringVar(value=str(initial_folder or latest or DEFAULT_ROADGEN_EXPORTS))
        self.start_lane_var = tk.StringVar()
        self.goal_lane_var = tk.StringVar()
        self.include_uturns_var = tk.BooleanVar(value=False)
        self.allow_lane_changes_var = tk.BooleanVar(value=True)
        self.checkpoint_lanes_var = tk.StringVar()
        self.click_target_var = tk.StringVar(value="start")
        self.route_name_var = tk.StringVar(value="route_1")
        self.vehicle_name_var = tk.StringVar(value="Vehicle_1")
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        self.driver_model_var = tk.StringVar(value=DEFAULT_DRIVER)
        self.traffic_control_var = tk.StringVar(value="IPG Driver (AutoDriver)")
        self.speed_var = tk.DoubleVar(value=50.0)
        self.start_s_var = tk.DoubleVar(value=0.0)
        self.lane_offset_var = tk.DoubleVar(value=0.0)
        self.start_delay_var = tk.DoubleVar(value=0.0)
        self.rd5_path_var = tk.StringVar(value=str(initial_rd5 or DEFAULT_RD5) if (initial_rd5 or DEFAULT_RD5.exists()) else "")
        self.cm_project_var = tk.StringVar(value=str(initial_project or DEFAULT_CM_PROJECT))
        self.scenario_name_var = tk.StringVar(value=initial_scenario or "route_traffic")
        self.cm_home_var = tk.StringVar(value=str(find_carmaker_home() or DEFAULT_CARMAKER_HOME))
        self.ego_enabled_var = tk.BooleanVar(value=True)
        self.ego_route_name_var = tk.StringVar(value="")
        self.ego_model_var = tk.StringVar(value=DEFAULT_EGO_MODEL)
        self.ego_driver_var = tk.StringVar(value=DEFAULT_EGO_DRIVER)
        self.ego_speed_var = tk.DoubleVar(value=50.0)
        self.ego_start_s_var = tk.DoubleVar(value=0.0)
        self.ego_lane_offset_var = tk.DoubleVar(value=0.0)
        self.duration_var = tk.DoubleVar(value=1000.0)
        self.ped_model_var = tk.StringVar(value="Random")
        self.ped_density_var = tk.DoubleVar(value=8.0)
        self.ped_speed_min_var = tk.DoubleVar(value=3.0)
        self.ped_speed_max_var = tk.DoubleVar(value=5.5)
        self.ped_offset_min_var = tk.DoubleVar(value=-2.3)
        self.ped_offset_max_var = tk.DoubleVar(value=-1.8)
        self.ped_direction_var = tk.StringVar(value="Random")
        self.ped_start_delay_span_var = tk.DoubleVar(value=0.0)

        self.package: RoadPackage | None = None
        self.current_route = None
        self.display_route = None
        self.display_route_owner = ""
        self.saved_routes = []
        self.vehicles: list[VehiclePlan] = []
        self.last_rd5_route_result = None
        self.last_testrun_path: Path | None = None
        self.last_testrun_project: Path | None = None
        self.bounds: tuple[float, float, float, float] | None = None
        self.selected_lane_id: str | None = None
        self.hover_lane_id: str | None = None
        self.view_zoom = 1.0
        self.view_pan_x = 0.0
        self.view_pan_y = 0.0
        self.is_panning = False
        self.pan_start_x = 0.0
        self.pan_start_y = 0.0
        self.pan_origin_x = 0.0
        self.pan_origin_y = 0.0

        self._build_ui()
        if initial_folder or latest:
            self.after(100, self.load_package)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=(10, 8))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="RoadGen export folder").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.folder_var).grid(row=0, column=1, sticky="ew", padx=(8, 6))
        ttk.Button(top, text="Browse", command=self.browse_folder).grid(row=0, column=2, padx=2)
        ttk.Button(top, text="Load", command=self.load_package).grid(row=0, column=3, padx=2)
        ttk.Button(top, text="Latest", command=self.use_latest).grid(row=0, column=4, padx=2)

        body = ttk.PanedWindow(self, orient="horizontal")
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        left = ttk.Frame(body, padding=(0, 0, 8, 0))
        center = ttk.Frame(body)
        right = ttk.Frame(body, padding=(8, 0, 0, 0))
        body.add(left, weight=0)
        body.add(center, weight=1)
        body.add(right, weight=0)

        left_content = self._build_scrollable_panel(left)
        self._build_left(left_content)
        self._build_center(center)
        self._build_right(right)

    def _build_scrollable_panel(self, parent: ttk.Frame) -> ttk.Frame:
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        canvas = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        canvas.configure(yscrollcommand=scroll.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        def update_scroll_region(_event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_content_width(event: tk.Event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def on_mousewheel(event: tk.Event) -> None:
            widget = self.winfo_containing(event.x_root, event.y_root)
            while widget is not None:
                if widget in (parent, canvas, content):
                    canvas.yview_scroll(int(-event.delta / 120), "units")
                    return "break"
                widget = widget.master
            return None

        content.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", fit_content_width)
        canvas.bind_all("<MouseWheel>", on_mousewheel, add="+")
        return content

    def _build_left(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)

        route_box = ttk.LabelFrame(parent, text="Route Planner", padding=8)
        route_box.grid(row=0, column=0, sticky="ew")
        route_box.columnconfigure(1, weight=1)

        ttk.Label(route_box, text="Start lane").grid(row=0, column=0, sticky="w", pady=2)
        self.start_combo = ttk.Combobox(route_box, textvariable=self.start_lane_var, state="readonly", width=28)
        self.start_combo.grid(row=0, column=1, sticky="ew", pady=2)
        self.start_combo.bind("<<ComboboxSelected>>", self.on_route_input_changed)

        ttk.Label(route_box, text="Goal lane").grid(row=1, column=0, sticky="w", pady=2)
        self.goal_combo = ttk.Combobox(route_box, textvariable=self.goal_lane_var, state="readonly", width=28)
        self.goal_combo.grid(row=1, column=1, sticky="ew", pady=2)
        self.goal_combo.bind("<<ComboboxSelected>>", self.on_route_input_changed)

        ttk.Label(route_box, text="Checkpoints").grid(row=2, column=0, sticky="w", pady=2)
        self.checkpoint_entry = ttk.Entry(route_box, textvariable=self.checkpoint_lanes_var, width=28)
        self.checkpoint_entry.grid(row=2, column=1, sticky="ew", pady=2)
        self.checkpoint_entry.bind("<KeyRelease>", self.on_route_input_changed)

        pick_frame = ttk.Frame(route_box)
        pick_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 2))
        pick_frame.columnconfigure(1, weight=1)
        ttk.Label(pick_frame, text="Canvas click").grid(row=0, column=0, sticky="w", padx=(0, 8))
        targets = [("Start", "start"), ("Goal", "goal"), ("Checkpoint", "checkpoint")]
        for column, (label, value) in enumerate(targets, start=1):
            ttk.Radiobutton(
                pick_frame,
                text=label,
                value=value,
                variable=self.click_target_var,
                command=self.redraw,
            ).grid(
                row=0, column=column, sticky="w", padx=(0, 6)
            )

        ttk.Button(route_box, text="Clear Checkpoints", command=self.clear_checkpoints).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=2
        )
        ttk.Checkbutton(route_box, text="Allow lane changes", variable=self.allow_lane_changes_var).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(6, 2)
        )
        ttk.Checkbutton(route_box, text="Allow U-turn connections", variable=self.include_uturns_var).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=2
        )
        ttk.Button(route_box, text="Plan Shortest Route", command=self.plan_route).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=2
        )
        ttk.Button(route_box, text="Swap Start/Goal", command=self.swap_start_goal).grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=2
        )

        vehicle_box = ttk.LabelFrame(parent, text="Traffic Vehicle (optional)", padding=8)
        vehicle_box.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        vehicle_box.columnconfigure(1, weight=1)

        rows = [
            ("Current route name", self.route_name_var),
            ("Vehicle name", self.vehicle_name_var),
            ("Model", self.model_var),
            ("Driver", self.driver_model_var),
            ("Motion", self.traffic_control_var),
            ("Target speed km/h", self.speed_var),
            ("Route s forward m", self.start_s_var),
            ("Lateral offset m", self.lane_offset_var),
            ("Start delay s", self.start_delay_var),
        ]
        for row, (label, variable) in enumerate(rows):
            ttk.Label(vehicle_box, text=label).grid(row=row, column=0, sticky="w", pady=2)
            if label == "Motion":
                ttk.Combobox(
                    vehicle_box,
                    textvariable=variable,
                    values=list(TRAFFIC_CONTROL_LABELS),
                    state="readonly",
                    width=26,
                ).grid(row=row, column=1, sticky="ew", pady=2)
            else:
                ttk.Entry(vehicle_box, textvariable=variable, width=28).grid(row=row, column=1, sticky="ew", pady=2)

        ttk.Button(vehicle_box, text="Add Traffic Vehicle On Current Route", command=self.add_vehicle).grid(
            row=len(rows), column=0, columnspan=2, sticky="ew", pady=(8, 2)
        )
        ttk.Button(vehicle_box, text="Save Traffic Plan", command=self.save_plan).grid(
            row=len(rows) + 1, column=0, columnspan=2, sticky="ew", pady=2
        )
        ttk.Button(vehicle_box, text="Generate XOSC", command=self.generate_xosc).grid(
            row=len(rows) + 2, column=0, columnspan=2, sticky="ew", pady=2
        )

        pedestrian_box = ttk.LabelFrame(parent, text="Random Pedestrians", padding=8)
        pedestrian_box.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        pedestrian_box.columnconfigure(1, weight=1)

        ped_rows = [
            ("Model", self.ped_model_var),
            ("Density persons/km", self.ped_density_var),
            ("Speed min km/h", self.ped_speed_min_var),
            ("Speed max km/h", self.ped_speed_max_var),
            ("Offset min m", self.ped_offset_min_var),
            ("Offset max m", self.ped_offset_max_var),
            ("Direction", self.ped_direction_var),
            ("Start delay span s", self.ped_start_delay_span_var),
        ]
        for row, (label, variable) in enumerate(ped_rows):
            ttk.Label(pedestrian_box, text=label).grid(row=row, column=0, sticky="w", pady=2)
            if label == "Model":
                ttk.Combobox(
                    pedestrian_box,
                    textvariable=variable,
                    values=["Random", *PEDESTRIAN_MODELS],
                    state="readonly",
                    width=28,
                ).grid(row=row, column=1, sticky="ew", pady=2)
            elif label == "Direction":
                ttk.Combobox(
                    pedestrian_box,
                    textvariable=variable,
                    values=["Random", "Forward", "Reverse"],
                    state="readonly",
                    width=28,
                ).grid(row=row, column=1, sticky="ew", pady=2)
            else:
                ttk.Entry(pedestrian_box, textvariable=variable, width=28).grid(
                    row=row, column=1, sticky="ew", pady=2
                )
        ttk.Button(
            pedestrian_box,
            text="Add Pedestrians On Selected Lane",
            command=self.add_random_pedestrians,
        ).grid(row=len(ped_rows), column=0, columnspan=2, sticky="ew", pady=(8, 2))
        ttk.Button(
            pedestrian_box,
            text="Remove Generated Pedestrians",
            command=self.remove_generated_pedestrians,
        ).grid(row=len(ped_rows) + 1, column=0, columnspan=2, sticky="ew", pady=2)

        rd5_box = ttk.LabelFrame(parent, text="RD5 Route Mapping", padding=8)
        rd5_box.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        rd5_box.columnconfigure(0, weight=1)
        ttk.Entry(rd5_box, textvariable=self.rd5_path_var).grid(row=0, column=0, sticky="ew", pady=2)
        ttk.Button(rd5_box, text="Browse RD5", command=self.browse_rd5).grid(row=1, column=0, sticky="ew", pady=2)
        ttk.Button(rd5_box, text="Analyze Current Route Against RD5", command=self.analyze_rd5_mapping).grid(
            row=2, column=0, sticky="ew", pady=2
        )
        ttk.Button(rd5_box, text="Write Route Into RD5 Copy", command=self.write_rd5_route_copy).grid(
            row=3, column=0, sticky="ew", pady=2
        )

        testrun_box = ttk.LabelFrame(parent, text="CarMaker TestRun", padding=8)
        testrun_box.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        testrun_box.columnconfigure(1, weight=1)

        ttk.Label(testrun_box, text="Project").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(testrun_box, textvariable=self.cm_project_var, width=28).grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Button(testrun_box, text="...", width=3, command=self.browse_project).grid(row=0, column=2, padx=(4, 0))

        ttk.Label(testrun_box, text="TestRun name").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(testrun_box, textvariable=self.scenario_name_var, width=28).grid(
            row=1, column=1, columnspan=2, sticky="ew", pady=2
        )
        ttk.Label(testrun_box, text="CarMaker home").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(testrun_box, textvariable=self.cm_home_var, width=28).grid(row=2, column=1, sticky="ew", pady=2)
        ttk.Button(testrun_box, text="...", width=3, command=self.browse_carmaker_home).grid(
            row=2, column=2, padx=(4, 0)
        )
        ttk.Label(testrun_box, text="Output").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Label(testrun_box, text="Project Data/Road + Data/TestRun").grid(
            row=3, column=1, columnspan=2, sticky="w", pady=2
        )
        ttk.Checkbutton(
            testrun_box,
            text="Add ego car",
            variable=self.ego_enabled_var,
            command=self.refresh_vehicle_tree,
        ).grid(
            row=4, column=0, columnspan=3, sticky="w", pady=2
        )
        ttk.Label(testrun_box, text="Ego route").grid(row=5, column=0, sticky="w", pady=2)
        ttk.Entry(testrun_box, textvariable=self.ego_route_name_var, width=28, state="readonly").grid(
            row=5, column=1, sticky="ew", pady=2
        )
        ttk.Button(testrun_box, text="Use Current", command=self.set_ego_route).grid(row=5, column=2, padx=(4, 0))

        ego_rows = [
            ("Ego model", self.ego_model_var),
            ("Ego driver", self.ego_driver_var),
            ("Ego speed", self.ego_speed_var),
            ("Ego route s m", self.ego_start_s_var),
            ("Ego lateral offset m", self.ego_lane_offset_var),
            ("Duration s", self.duration_var),
        ]
        for offset, (label, variable) in enumerate(ego_rows, start=6):
            ttk.Label(testrun_box, text=label).grid(row=offset, column=0, sticky="w", pady=2)
            ttk.Entry(testrun_box, textvariable=variable, width=28).grid(
                row=offset, column=1, columnspan=2, sticky="ew", pady=2
            )

        ttk.Button(testrun_box, text="Generate TestRun", command=self.generate_testrun).grid(
            row=6 + len(ego_rows), column=0, columnspan=3, sticky="ew", pady=(8, 2)
        )
        ttk.Button(
            testrun_box,
            text="Generate + Run 5x + IPGMovie",
            command=self.generate_and_run_carmaker,
        ).grid(
            row=7 + len(ego_rows), column=0, columnspan=3, sticky="ew", pady=2
        )

        vehicles_box = ttk.LabelFrame(parent, text="Vehicles", padding=8)
        vehicles_box.grid(row=5, column=0, sticky="nsew", pady=(10, 0))
        parent.rowconfigure(5, weight=1)
        vehicles_box.columnconfigure(0, weight=1)
        vehicles_box.rowconfigure(0, weight=1)

        self.vehicle_tree = ttk.Treeview(
            vehicles_box,
            columns=("actor", "route", "speed", "start"),
            show="headings",
            height=7,
        )
        self.vehicle_tree.heading("actor", text="Actor")
        self.vehicle_tree.heading("route", text="Route")
        self.vehicle_tree.heading("speed", text="Speed")
        self.vehicle_tree.heading("start", text="route s / delay")
        self.vehicle_tree.column("actor", width=150)
        self.vehicle_tree.column("route", width=140)
        self.vehicle_tree.column("speed", width=58, anchor="e")
        self.vehicle_tree.column("start", width=82, anchor="e")
        self.vehicle_tree.grid(row=0, column=0, sticky="nsew")
        self.vehicle_tree.bind("<<TreeviewSelect>>", self.show_vehicle_details)
        scroll = ttk.Scrollbar(vehicles_box, orient="vertical", command=self.vehicle_tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.vehicle_tree.configure(yscrollcommand=scroll.set)

        ttk.Button(vehicles_box, text="Remove Selected", command=self.remove_vehicle).grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0)
        )
        self.vehicle_detail_text = tk.Text(vehicles_box, height=8, wrap="word")
        self.vehicle_detail_text.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self.set_text(self.vehicle_detail_text, "Select Ego, traffic, or pedestrian actor to inspect details.")

    def _build_center(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(parent, bg="#f8fafc", highlightthickness=1, highlightbackground="#cbd5e1")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda _event: self.redraw())
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<MouseWheel>", self.on_canvas_wheel)
        self.canvas.bind("<Button-4>", self.on_canvas_wheel)
        self.canvas.bind("<Button-5>", self.on_canvas_wheel)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Leave>", self.on_canvas_leave)

        self.log_text = tk.Text(parent, height=7, wrap="word")
        self.log_text.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.log("Load a RoadGen export folder to inspect SUMO lane connections.")

    def _build_right(self, parent: ttk.Frame) -> None:
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        notebook = ttk.Notebook(parent)
        notebook.grid(row=0, column=0, sticky="nsew")

        summary_tab = ttk.Frame(notebook, padding=6)
        route_tab = ttk.Frame(notebook, padding=6)
        conn_tab = ttk.Frame(notebook, padding=6)
        notebook.add(summary_tab, text="Summary")
        notebook.add(route_tab, text="Route")
        notebook.add(conn_tab, text="Connections")

        summary_tab.rowconfigure(0, weight=1)
        summary_tab.columnconfigure(0, weight=1)
        self.summary_text = tk.Text(summary_tab, width=44, wrap="word")
        self.summary_text.grid(row=0, column=0, sticky="nsew")

        route_tab.rowconfigure(0, weight=1)
        route_tab.columnconfigure(0, weight=1)
        self.route_text = tk.Text(route_tab, width=54, wrap="none")
        self.route_text.grid(row=0, column=0, sticky="nsew")

        conn_tab.rowconfigure(0, weight=1)
        conn_tab.columnconfigure(0, weight=1)
        self.conn_tree = ttk.Treeview(conn_tab, columns=("from", "via", "to", "dir"), show="headings")
        for column, title, width in [
            ("from", "From", 110),
            ("via", "Via", 110),
            ("to", "To", 110),
            ("dir", "Dir", 44),
        ]:
            self.conn_tree.heading(column, text=title)
            self.conn_tree.column(column, width=width)
        self.conn_tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(conn_tab, orient="vertical", command=self.conn_tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.conn_tree.configure(yscrollcommand=scroll.set)

    def browse_folder(self) -> None:
        initial = self.folder_var.get() or str(DEFAULT_ROADGEN_EXPORTS)
        selected = filedialog.askdirectory(initialdir=initial, title="Select RoadGen export folder")
        if selected:
            self.folder_var.set(selected)
            self.load_package()

    def use_latest(self) -> None:
        latest = find_latest_roadgen_export()
        if not latest:
            messagebox.showinfo("Latest", "No RoadGen export folder was found.")
            return
        self.folder_var.set(str(latest))
        self.load_package()

    def browse_rd5(self) -> None:
        initial = self.rd5_path_var.get() or str(Path(r"C:\CM_Projects"))
        selected = filedialog.askopenfilename(
            initialdir=str(Path(initial).parent if initial else Path(r"C:\CM_Projects")),
            title="Select CarMaker RD5 road file",
            filetypes=[("CarMaker road", "*.rd5"), ("All files", "*.*")],
        )
        if selected:
            self.rd5_path_var.set(selected)

    def browse_project(self) -> None:
        initial = self.cm_project_var.get() or str(Path(r"C:\CM_Projects"))
        selected = filedialog.askdirectory(initialdir=initial, title="Select CarMaker project folder")
        if selected:
            self.cm_project_var.set(selected)

    def browse_carmaker_home(self) -> None:
        initial = self.cm_home_var.get() or str(DEFAULT_CARMAKER_HOME)
        selected = filedialog.askdirectory(initialdir=initial, title="Select CarMaker win64 installation folder")
        if selected:
            self.cm_home_var.set(selected)

    def load_package(self) -> None:
        try:
            self.package = RoadPackage.load(Path(self.folder_var.get()))
        except Exception as exc:
            messagebox.showerror("Load Road Package", str(exc))
            self.log(f"Load failed: {exc}")
            return

        self.current_route = None
        self.display_route = None
        self.display_route_owner = ""
        self.saved_routes.clear()
        self.vehicles.clear()
        self.ego_route_name_var.set("")
        self.last_rd5_route_result = None
        self.checkpoint_lanes_var.set("")
        self.selected_lane_id = None
        self.hover_lane_id = None
        self.reset_canvas_view()
        self.refresh_vehicle_tree()

        external_lanes = self.package.external_lanes
        self.start_combo.configure(values=external_lanes)
        self.goal_combo.configure(values=external_lanes)
        if external_lanes:
            self.start_lane_var.set(external_lanes[0])
            self.goal_lane_var.set(external_lanes[min(1, len(external_lanes) - 1)])

        self.set_text(self.summary_text, self.package.summary())
        self.set_text(self.route_text, "No route planned yet.")
        self.sync_rd5_for_loaded_package()
        self.refresh_connections()
        self.compute_bounds()
        self.redraw()
        self.log(f"Loaded package: {self.package.files.folder}")

    def sync_rd5_for_loaded_package(self) -> None:
        if not self.package or not self.package.files.xodr:
            return
        current_text = self.rd5_path_var.get().strip()
        if current_text and self.rd5_matches_loaded_package(Path(current_text)):
            return
        project_dir = Path(self.cm_project_var.get())
        candidate = project_dir / "Data" / "Road" / f"{self.package.files.xodr.stem}.rd5"
        if candidate.exists():
            self.rd5_path_var.set(str(candidate))
            self.log(f"RD5 auto-selected for loaded package: {candidate}")

    def rd5_matches_loaded_package(self, rd5_path: Path) -> bool:
        if not self.package or not self.package.files.xodr or not rd5_path.exists():
            return False
        try:
            rd5 = Rd5Road.load(rd5_path)
        except Exception:
            return False
        if not rd5.original_file:
            return rd5_path.stem == self.package.files.xodr.stem
        original = rd5.original_file.replace("\\\\", "\\").replace("\\", "/").lower()
        expected = str(self.package.files.xodr.resolve()).replace("\\", "/").lower()
        return original == expected

    def refresh_connections(self) -> None:
        children = self.conn_tree.get_children()
        if children:
            self.conn_tree.delete(*children)
        if not self.package:
            return
        for row in self.package.connection_rows(include_internal=False):
            self.conn_tree.insert("", "end", values=(row["from"], row["via"], row["to"], row["dir"]))

    def swap_start_goal(self) -> None:
        start = self.start_lane_var.get()
        goal = self.goal_lane_var.get()
        self.start_lane_var.set(goal)
        self.goal_lane_var.set(start)
        self.on_route_input_changed()

    def clear_checkpoints(self) -> None:
        self.checkpoint_lanes_var.set("")
        self.on_route_input_changed()

    def on_route_input_changed(self, _event=None) -> None:
        self.current_route = None
        self.display_route = None
        self.display_route_owner = ""
        self.last_rd5_route_result = None
        if hasattr(self, "vehicle_tree"):
            self.vehicle_tree.selection_remove(self.vehicle_tree.selection())
        if hasattr(self, "vehicle_detail_text"):
            self.set_text(self.vehicle_detail_text, "Select Ego, traffic, or pedestrian actor to inspect details.")
        self.set_text(self.route_text, "Route planner inputs changed. Click Plan Shortest Route to build a route.")
        self.redraw()

    def plan_route(self) -> None:
        if not self.package:
            messagebox.showinfo("Plan Route", "Load a road package first.")
            return
        checkpoint_lanes = self.parse_checkpoint_lanes()
        try:
            route = self.package.plan_route_via(
                [self.start_lane_var.get(), *checkpoint_lanes, self.goal_lane_var.get()],
                include_uturns=self.include_uturns_var.get(),
                allow_lane_changes=self.allow_lane_changes_var.get(),
            )
        except RoadPackageError as exc:
            messagebox.showerror("Plan Route", str(exc))
            self.log(f"No route: {exc}")
            return

        self.current_route = route
        self.display_route = None
        self.display_route_owner = ""
        self.route_name_var.set(route.name)
        if not self.ego_route_name_var.get():
            self.save_current_route()
            self.ego_route_name_var.set(route.name)
            self.refresh_vehicle_tree()
        self.render_route_text(route)
        self.redraw()
        self.log(f"Planned {route.name}: {len(route.lane_path)} lane steps, {route.total_length:.1f} m")

    def parse_checkpoint_lanes(self) -> list[str]:
        raw = self.checkpoint_lanes_var.get().strip()
        if not raw:
            return []
        return [token for token in re.split(r"[\s,;]+", raw) if token]

    def append_checkpoint_lane(self, lane_id: str) -> None:
        tokens = self.parse_checkpoint_lanes()
        if tokens and tokens[-1] == lane_id:
            return
        tokens.append(lane_id)
        self.checkpoint_lanes_var.set(" ".join(tokens))

    def on_canvas_press(self, event: tk.Event) -> str | None:
        if not self.package:
            return None
        lane_id = self.nearest_lane_id(event.x, event.y, max_distance=16.0)
        if not lane_id:
            self.is_panning = True
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.pan_origin_x = self.view_pan_x
            self.pan_origin_y = self.view_pan_y
            self.hover_lane_id = None
            self.canvas.configure(cursor="fleur")
            return "break"

        self.selected_lane_id = lane_id
        target = self.click_target_var.get()
        if target == "goal":
            self.goal_lane_var.set(lane_id)
            action = "goal"
        elif target == "checkpoint":
            self.append_checkpoint_lane(lane_id)
            action = "checkpoint"
        else:
            self.start_lane_var.set(lane_id)
            action = "start"

        lane = self.package.lanes.get(lane_id)
        lane_kind = "internal lane" if lane and lane.internal else "lane"
        self.on_route_input_changed()
        self.log(f"Selected {lane_kind} {lane_id} as {action}.")
        return "break"

    def on_canvas_drag(self, event: tk.Event) -> str | None:
        if not self.is_panning:
            return None
        self.view_pan_x = self.pan_origin_x + (event.x - self.pan_start_x)
        self.view_pan_y = self.pan_origin_y + (event.y - self.pan_start_y)
        self.redraw()
        return "break"

    def on_canvas_release(self, event: tk.Event) -> str | None:
        if not self.is_panning:
            return None
        self.is_panning = False
        self.canvas.configure(cursor="")
        self.hover_lane_id = self.nearest_lane_id(event.x, event.y, max_distance=12.0)
        self.redraw()
        return "break"

    def on_canvas_wheel(self, event: tk.Event) -> str | None:
        if not self.package or not self.bounds:
            return None
        delta = getattr(event, "delta", 0)
        button_num = getattr(event, "num", None)
        zoom_in = delta > 0 or button_num == 4
        factor = 1.15 if zoom_in else 1 / 1.15
        self.zoom_canvas(event.x, event.y, factor)
        return "break"

    def reset_canvas_view(self) -> None:
        self.view_zoom = 1.0
        self.view_pan_x = 0.0
        self.view_pan_y = 0.0
        self.is_panning = False

    def zoom_canvas(self, x: float, y: float, factor: float) -> None:
        old_zoom = self.view_zoom
        new_zoom = max(0.2, min(20.0, old_zoom * factor))
        if new_zoom == old_zoom:
            return
        canvas_w = max(self.canvas.winfo_width(), 100)
        canvas_h = max(self.canvas.winfo_height(), 100)
        center_x = canvas_w / 2
        center_y = canvas_h / 2
        ratio = new_zoom / old_zoom
        self.view_pan_x = x - center_x - (x - center_x - self.view_pan_x) * ratio
        self.view_pan_y = y - center_y - (y - center_y - self.view_pan_y) * ratio
        self.view_zoom = new_zoom
        self.redraw()

    def on_canvas_motion(self, event: tk.Event) -> None:
        if self.is_panning:
            return
        lane_id = self.nearest_lane_id(event.x, event.y, max_distance=12.0)
        if lane_id == self.hover_lane_id:
            return
        self.hover_lane_id = lane_id
        self.canvas.configure(cursor="hand2" if lane_id else "")
        self.redraw()

    def on_canvas_leave(self, _event: tk.Event) -> None:
        if self.is_panning:
            return
        if self.hover_lane_id is None:
            return
        self.hover_lane_id = None
        self.canvas.configure(cursor="")
        self.redraw()

    def nearest_lane_id(self, x: float, y: float, *, max_distance: float) -> str | None:
        if not self.package or not self.bounds:
            return None
        best_distance = math.inf
        best_lane_id = None
        for lane in self.package.lanes.values():
            if len(lane.shape) < 2:
                continue
            for start, end in zip(lane.shape, lane.shape[1:]):
                x1, y1 = self.to_screen(start)
                x2, y2 = self.to_screen(end)
                distance = self.point_segment_distance(x, y, x1, y1, x2, y2)
                if distance < best_distance:
                    best_distance = distance
                    best_lane_id = lane.id
        if best_distance <= max_distance:
            return best_lane_id
        return None

    @staticmethod
    def point_segment_distance(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        return math.hypot(px - closest_x, py - closest_y)

    def save_route_object(self, route: PlannedRoute, route_name: str | None = None) -> str:
        route_name = safe_name(route_name or route.name)
        route.name = route_name
        for index, saved_route in enumerate(self.saved_routes):
            if saved_route.name == route_name:
                self.saved_routes[index] = route
                break
        else:
            self.saved_routes.append(route)
        return route_name

    def save_current_route(self) -> str:
        if not self.current_route:
            raise RoadPackageError("Plan a route first.")
        return self.save_route_object(self.current_route, self.route_name_var.get() or self.current_route.name)

    def route_lookup(self) -> dict[str, object]:
        routes: dict[str, object] = {}
        for route in self.saved_routes:
            routes[route.name] = route
            routes[safe_name(route.name)] = route
        if self.current_route:
            routes[self.current_route.name] = self.current_route
            typed_name = safe_name(self.route_name_var.get() or self.current_route.name)
            routes[typed_name] = self.current_route
        return routes

    def find_route(self, route_name: str):
        if not route_name:
            return None
        routes = self.route_lookup()
        return routes.get(route_name) or routes.get(safe_name(route_name))

    def show_route_for_vehicle(self, route_name: str, owner: str) -> None:
        route = self.find_route(route_name)
        if not route:
            self.display_route = None
            self.display_route_owner = owner
            self.set_text(self.route_text, f"{owner} route was not found in app memory: {route_name}")
            self.redraw()
            self.log(f"Vehicle route not found in app memory: {route_name}")
            return
        self.display_route = route
        self.display_route_owner = owner
        self.render_route_text(route, view_label=f"Vehicle view: {owner}")
        self.redraw()

    def set_ego_route(self) -> None:
        if not self.current_route:
            messagebox.showinfo("Set Ego Route", "Plan a route first.")
            return
        try:
            route_name = self.save_current_route()
        except RoadPackageError as exc:
            messagebox.showerror("Set Ego Route", str(exc))
            return
        self.ego_route_name_var.set(route_name)
        self.refresh_vehicle_tree()
        self.log(f"Set ego route to {route_name}")

    def render_route_text(self, route, *, view_label: str | None = None) -> None:
        lines = [
            f"Route: {route.name}",
            f"Start: {route.start_lane}",
            f"Goal: {route.goal_lane}",
            f"Length: {route.total_length:.2f} m",
            "",
            "#  Lane                  Edge       XODR road/lane",
            "-- --------------------- ---------- --------------",
        ]
        for index, step in enumerate(route.steps, start=1):
            xodr = ""
            if step.xodr_road_id:
                xodr = f"{step.xodr_road_id}/{step.xodr_lane_id}"
            internal = "*" if step.internal else " "
            lines.append(f"{index:02d}{internal} {step.lane_id:<21} {step.edge_id:<10} {xodr}")
        lines.append("")
        lines.append("* = SUMO internal connector lane")
        if view_label:
            lines = [view_label, ""] + lines
        self.set_text(self.route_text, "\n".join(lines))

    def add_vehicle(self) -> None:
        if not self.current_route:
            messagebox.showinfo("Add Vehicle", "Plan a route first.")
            return

        route_name = self.save_current_route()

        try:
            speed = float(self.speed_var.get())
            start_s = float(self.start_s_var.get())
            lane_offset = float(self.lane_offset_var.get())
            start_delay = float(self.start_delay_var.get())
        except (TypeError, ValueError):
            messagebox.showerror("Add Vehicle", "Speed, route s, lateral offset, and start delay must be numbers.")
            return

        vehicle = VehiclePlan(
            name=safe_name(self.vehicle_name_var.get() or f"Vehicle_{len(self.vehicles) + 1}"),
            route_name=route_name,
            model=self.model_var.get().strip() or DEFAULT_MODEL,
            driver_model=self.driver_model_var.get().strip() or DEFAULT_DRIVER,
            speed_kmh=speed,
            start_s=start_s,
            lane_offset=lane_offset,
            start_delay_s=start_delay,
            control_mode=TRAFFIC_CONTROL_LABELS.get(self.traffic_control_var.get(), "ipg_driver"),
        )
        self.vehicles.append(vehicle)
        self.vehicle_name_var.set(f"Vehicle_{len(self.vehicles) + 1}")
        self.refresh_vehicle_tree()
        self.log(f"Added vehicle {vehicle.name} on {route_name}")

    def is_pedestrian_plan(self, vehicle: VehiclePlan) -> bool:
        return vehicle_category(vehicle.model) == "pedestrian"

    def pedestrian_route_from_selected_lane(self) -> tuple[PlannedRoute | None, str]:
        if not self.package or not self.selected_lane_id:
            return None, ""
        lane = self.package.lanes.get(self.selected_lane_id)
        if not lane:
            raise RoadPackageError(f"Selected lane was not found: {self.selected_lane_id}")
        if lane.internal:
            raise RoadPackageError("Select an external road lane for pedestrian placement, not an internal junction lane.")
        route_name = safe_name(f"ped_{lane.edge_id}_{lane.index}")
        route = PlannedRoute(
            name=route_name,
            start_lane=lane.id,
            goal_lane=lane.id,
            lane_path=[lane.id],
            steps=[self.package.lane_step(lane.id)],
        )
        return route, f"selected lane {lane.id}"

    def rd5_has_visual_sidewalks(self) -> bool:
        rd5_text = self.rd5_path_var.get().strip()
        if not rd5_text:
            return False
        rd5_path = Path(rd5_text)
        if not rd5_path.exists():
            return False
        try:
            text = rd5_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return False
        return "RoadGen City Environment" in text and "Roadside_Sidewalk" in text

    def add_random_pedestrians(self) -> None:
        if not self.package:
            messagebox.showinfo("Add Pedestrians", "Load a road package first.")
            return

        try:
            route, source_label = self.pedestrian_route_from_selected_lane()
            if route:
                route_name = self.save_route_object(route, route.name)
            elif self.current_route:
                route = self.current_route
                source_label = f"current route {route.name}"
                route_name = self.save_current_route()
            else:
                messagebox.showinfo(
                    "Add Pedestrians",
                    "Click a lane in the map, then use Add Pedestrians On Selected Lane.",
                )
                return
        except RoadPackageError as exc:
            messagebox.showerror("Add Pedestrians", str(exc))
            return

        try:
            density = max(0.0, float(self.ped_density_var.get()))
            speed_min = max(0.1, float(self.ped_speed_min_var.get()))
            speed_max = max(0.1, float(self.ped_speed_max_var.get()))
            offset_min = float(self.ped_offset_min_var.get())
            offset_max = float(self.ped_offset_max_var.get())
            delay_span = max(0.0, float(self.ped_start_delay_span_var.get()))
        except (TypeError, ValueError):
            messagebox.showerror(
                "Add Pedestrians",
                "Density, speed range, offset range, and start delay span must be numbers.",
            )
            return
        if speed_min > speed_max:
            speed_min, speed_max = speed_max, speed_min
        if offset_min > offset_max:
            offset_min, offset_max = offset_max, offset_min

        if density <= 0:
            messagebox.showinfo("Add Pedestrians", "Pedestrian density is zero.")
            return

        route_length = max(0.0, float(route.total_length))
        if route_length <= 1.0:
            messagebox.showinfo("Add Pedestrians", "Selected route is too short for pedestrian placement.")
            return

        count = max(1, int(round(route_length * density / 1000.0)))
        rng = random.Random(time.time_ns())
        margin = min(10.0, route_length * 0.2)
        start_s_min = margin
        start_s_max = max(start_s_min, route_length - margin)
        existing_count = sum(1 for vehicle in self.vehicles if self.is_pedestrian_plan(vehicle))
        model_text = self.ped_model_var.get().strip()
        direction_mode = self.ped_direction_var.get().strip().lower()

        for offset_index in range(count):
            start_s = rng.uniform(start_s_min, start_s_max)
            lateral_offset = rng.uniform(offset_min, offset_max)
            speed = rng.uniform(speed_min, speed_max)
            if direction_mode == "reverse":
                direction = -1
            elif direction_mode == "forward":
                direction = 1
            else:
                direction = rng.choice([-1, 1])
            start_delay = rng.uniform(0.0, delay_span) if delay_span > 0 else 0.0
            model = model_text
            if not model or model.lower() == "random":
                model = rng.choice(PEDESTRIAN_MODELS)
            self.vehicles.append(
                VehiclePlan(
                    name=f"Ped_{existing_count + offset_index + 1}",
                    route_name=route_name,
                    model=model,
                    driver_model="",
                    speed_kmh=speed * direction,
                    start_s=start_s,
                    lane_offset=lateral_offset,
                    start_delay_s=start_delay,
                    control_mode="pedestrian",
                )
            )

        self.display_route = route
        self.display_route_owner = f"Pedestrians: {source_label}"
        self.render_route_text(route, view_label=f"Pedestrian generation route: {source_label}")
        if not self.rd5_has_visual_sidewalks():
            self.log("Pedestrian note: selected RD5 does not appear to contain RoadGen visual sidewalk bumps.")
        self.refresh_vehicle_tree()
        self.redraw()
        self.log(
            f"Added {count} pedestrians on {route_name} ({source_label}) at {density:g} persons/km; "
            f"speed {speed_min:g}-{speed_max:g} km/h; offset {offset_min:g}..{offset_max:g} m; "
            f"direction {self.ped_direction_var.get()}"
        )

    def remove_generated_pedestrians(self) -> None:
        before = len(self.vehicles)
        self.vehicles = [vehicle for vehicle in self.vehicles if not self.is_pedestrian_plan(vehicle)]
        removed = before - len(self.vehicles)
        self.refresh_vehicle_tree()
        self.log(f"Removed {removed} generated pedestrians")

    def refresh_vehicle_tree(self) -> None:
        children = self.vehicle_tree.get_children()
        if children:
            self.vehicle_tree.delete(*children)
        if self.ego_enabled_var.get():
            ego_route = self.ego_route_name_var.get() or "(not set)"
            self.vehicle_tree.insert(
                "",
                "end",
                iid="ego",
                values=("Ego", ego_route, f"{float(self.ego_speed_var.get()):g}", f"{float(self.ego_start_s_var.get()):g} / -"),
            )
        for index, vehicle in enumerate(self.vehicles):
            is_pedestrian = self.is_pedestrian_plan(vehicle)
            actor_label = "Pedestrian" if is_pedestrian else "Traffic"
            if not is_pedestrian:
                actor_label = f"{actor_label} {TRAFFIC_CONTROL_NAMES.get(vehicle.control_mode, vehicle.control_mode)}"
            speed_label = f"{abs(vehicle.speed_kmh):g}"
            if is_pedestrian and vehicle.speed_kmh < 0:
                speed_label = f"{speed_label} rev"
            self.vehicle_tree.insert(
                "",
                "end",
                iid=f"traffic:{index}",
                values=(
                    f"{actor_label} {index + 1}: {vehicle.name}",
                    vehicle.route_name,
                    speed_label,
                    f"{vehicle.start_s:g} / {vehicle.start_delay_s:g}",
                ),
            )
        if hasattr(self, "vehicle_detail_text"):
            self.set_text(self.vehicle_detail_text, "Select Ego, traffic, or pedestrian actor to inspect details.")

    def remove_vehicle(self) -> None:
        selected = self.vehicle_tree.selection()
        if not selected:
            return
        indexes = []
        for item in selected:
            if item.startswith("traffic:"):
                indexes.append(int(item.split(":", 1)[1]))
        for index in indexes:
            if 0 <= index < len(self.vehicles):
                self.vehicles.pop(index)
        self.refresh_vehicle_tree()

    def show_vehicle_details(self, _event=None) -> None:
        selected = self.vehicle_tree.selection()
        if not selected:
            return
        item = selected[0]
        route_name = ""
        owner = ""
        if item == "ego":
            route_name = self.ego_route_name_var.get().strip()
            owner = "Ego"
            lines = [
                "Actor: Ego",
                f"Route: {route_name or '(not set)'}",
                f"Speed: {float(self.ego_speed_var.get()):g} km/h",
                f"Route s forward: {float(self.ego_start_s_var.get()):g} m",
                f"Lateral offset: {float(self.ego_lane_offset_var.get()):g} m",
                f"Duration: {float(self.duration_var.get()):g} s",
                f"Model: {self.ego_model_var.get()}",
                f"Driver: {self.ego_driver_var.get()}",
            ]
        elif item.startswith("traffic:"):
            index = int(item.split(":", 1)[1])
            if index >= len(self.vehicles):
                return
            vehicle = self.vehicles[index]
            is_pedestrian = self.is_pedestrian_plan(vehicle)
            actor_label = "Pedestrian" if is_pedestrian else "Traffic"
            control_label = TRAFFIC_CONTROL_NAMES.get(vehicle.control_mode, vehicle.control_mode)
            route_name = vehicle.route_name
            owner = f"{actor_label} {index + 1}: {vehicle.name}"
            lines = [
                f"Actor: {actor_label} {index + 1}",
                f"Name: {vehicle.name}",
                f"Route: {vehicle.route_name}",
                f"Speed: {abs(vehicle.speed_kmh):g} km/h",
                f"Route s forward: {vehicle.start_s:g} m",
                f"Start delay: {vehicle.start_delay_s:g} s",
                f"Lateral offset: {vehicle.lane_offset:g} m",
                f"Duration: {float(self.duration_var.get()):g} s",
                f"Model: {vehicle.model}",
                f"Driver: {vehicle.driver_model}",
                f"Motion: {control_label}",
            ]
            if is_pedestrian:
                lines.insert(4, f"Direction: {'reverse' if vehicle.speed_kmh < 0 else 'forward'}")
        else:
            return
        self.set_text(self.vehicle_detail_text, "\n".join(lines))
        if route_name:
            self.show_route_for_vehicle(route_name, owner)
        else:
            self.display_route = None
            self.display_route_owner = owner
            self.set_text(self.route_text, "Selected vehicle does not have a route yet.")
            self.redraw()

    def save_plan(self) -> None:
        if not self.package:
            messagebox.showinfo("Save Traffic Plan", "Load a road package first.")
            return
        routes = self.collect_routes()
        if not routes:
            messagebox.showinfo("Save Traffic Plan", "Plan at least one route first.")
            return

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = safe_name(self.package.files.folder.name)
        output_dir = ROOT / "exports" / f"{package_name}_{stamp}"
        json_path, report_path = write_plan(self.package, routes, self.vehicles, output_dir)
        self.log(f"Saved traffic plan: {json_path}")
        self.log(f"Saved route report: {report_path}")
        messagebox.showinfo("Save Traffic Plan", f"Saved to {output_dir}")

    def collect_routes(self):
        routes = list(self.saved_routes)
        if self.current_route and not any(route.name == self.current_route.name for route in routes):
            routes.append(self.current_route)
        return routes

    def generate_xosc(self) -> None:
        if not self.package:
            messagebox.showinfo("Generate XOSC", "Load a road package first.")
            return
        routes = self.collect_routes()
        if not routes:
            messagebox.showinfo("Generate XOSC", "Plan at least one route first.")
            return
        if not self.vehicles:
            messagebox.showinfo("Generate XOSC", "Add at least one vehicle first.")
            return

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = safe_name(self.package.files.folder.name)
        output_dir = ROOT / "exports" / f"{package_name}_xosc_{stamp}"
        try:
            json_path, report_path = write_plan(self.package, routes, self.vehicles, output_dir)
            xosc_path, script_path, readme_path = build_openscenario(
                self.package,
                routes,
                self.vehicles,
                output_dir,
                scenario_name=f"{package_name}_traffic",
            )
        except Exception as exc:
            messagebox.showerror("Generate XOSC", str(exc))
            self.log(f"Generate XOSC failed: {exc}")
            return

        self.log(f"Saved traffic plan: {json_path}")
        self.log(f"Saved route report: {report_path}")
        self.log(f"Generated XOSC: {xosc_path}")
        self.log(f"Generated osc2cm helper: {script_path}")
        self.log(f"Generated notes: {readme_path}")
        messagebox.showinfo("Generate XOSC", f"Generated XOSC in {output_dir}")

    def analyze_rd5_mapping(self) -> None:
        if not self.current_route:
            messagebox.showinfo("RD5 Mapping", "Plan a route first.")
            return
        rd5_path = Path(self.rd5_path_var.get())
        try:
            rd5 = Rd5Road.load(rd5_path)
            results = map_route_to_rd5(rd5, self.current_route)
            report = build_mapping_report(rd5, self.current_route, results)
        except Exception as exc:
            messagebox.showerror("RD5 Mapping", str(exc))
            self.log(f"RD5 mapping failed: {exc}")
            return

        sequence = lane_path_sequence(results)
        self.set_text(self.route_text, report)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = ROOT / "exports" / f"rd5_mapping_{stamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "rd5_mapping_report.md"
        report_path.write_text(report, encoding="utf-8")
        self.log(f"RD5 mapped {len(sequence)} LanePath IDs: {' '.join(sequence)}")
        self.log(f"Saved RD5 mapping report: {report_path}")
        messagebox.showinfo(
            "RD5 Mapping",
            f"Mapped {len(sequence)} LanePath IDs.\nReport saved to {report_path}",
        )

    def decorate_rd5_intersections_if_available(self, rd5_path: Path) -> None:
        if decorate_rd5_intersections is None or self.package is None:
            return
        graph_path = self.package.files.graph
        if not graph_path or not graph_path.exists():
            return
        try:
            result = decorate_rd5_intersections(
                rd5_path,
                graph_path=graph_path,
                xodr_path=self.package.files.xodr,
            )
        except Exception as exc:
            self.log(f"Intersection decorations skipped for route RD5: {exc}")
            return
        if result.traffic_light_nodes or result.crosswalk_nodes:
            self.log(
                "Intersection decorations synced to route RD5: "
                f"{result.signal_objects} signal objects, "
                f"{result.crosswalk_markings} crosswalk markings, "
                f"{result.crosswalk_stop_markers} pedestrian stop markers, "
                f"{result.traffic_light_stop_markers} traffic light stop markers, "
                f"{result.traffic_light_stop_lines} traffic light stop lines, "
                f"{result.traffic_light_phase_fixes} off-phase fixes"
            )

    def write_rd5_route_copy(self) -> None:
        if not self.current_route:
            messagebox.showinfo("RD5 Route Writer", "Plan a route first.")
            return
        if self.current_route.is_same_edge_lane_change_only():
            messagebox.showerror(
                "RD5 Route Writer",
                "Same-edge-only lane changes cannot be exported as CarMaker RD5 Routes reliably.\n\n"
                f"Route: {self.current_route.start_lane} -> {self.current_route.goal_lane}\n\n"
                "Choose start/goal lanes on different edges, or add a checkpoint/goal beyond this edge.",
            )
            self.log(
                "RD5 route write blocked: same-edge-only lane change "
                f"{self.current_route.start_lane} -> {self.current_route.goal_lane}"
            )
            return

        rd5_path = Path(self.rd5_path_var.get())
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        route_name = safe_name(self.route_name_var.get() or self.current_route.name)
        output_dir = ROOT / "exports" / f"rd5_route_{stamp}"
        output_rd5 = output_dir / f"{safe_name(rd5_path.stem)}_{route_name}.rd5"
        report_path = output_dir / "rd5_route_write_report.md"

        try:
            rd5 = Rd5Road.load(rd5_path)
            result = write_rd5_with_route(rd5, self.current_route, output_rd5, route_name=route_name)
            self.decorate_rd5_intersections_if_available(result.output_path)
            report_path.write_text(result.report, encoding="utf-8")
        except Exception as exc:
            messagebox.showerror("RD5 Route Writer", str(exc))
            self.log(f"RD5 route write failed: {exc}")
            return

        self.set_text(self.route_text, result.report)
        self.last_rd5_route_result = result
        self.rd5_path_var.set(str(result.output_path))
        self.log(f"Wrote RD5 route copy: {result.output_path}")
        self.log(f"Saved RD5 route write report: {report_path}")
        self.log(f"Route {result.route_name}: {' '.join(result.drv_path_ids)}")
        messagebox.showinfo(
            "RD5 Route Writer",
            "Wrote a route-enabled RD5 copy.\n"
            f"RD5: {result.output_path}\n"
            f"Report: {report_path}",
        )

    def route_ids_from_rd5(self, rd5: Rd5Road, route_names: set[str]) -> dict[str, str]:
        route_ids: dict[str, str] = {}
        for route in rd5.routes.values():
            if not route.name or not route.route_id:
                continue
            candidates = {route.name, safe_name(route.name)}
            for route_name in route_names:
                if route_name in candidates or safe_name(route_name) in candidates:
                    route_ids[route_name] = route.route_id
        return route_ids

    def ensure_routes_enabled_rd5(
        self,
        rd5_output_dir: Path,
        report_dir: Path,
        route_names: set[str],
    ) -> tuple[Path, dict[str, str]]:
        rd5_path = Path(self.rd5_path_var.get())
        if not rd5_path.exists():
            raise RoadPackageError(f"RD5 file does not exist: {rd5_path}")

        current_rd5_path = rd5_path
        rd5 = Rd5Road.load(current_rd5_path)
        route_ids = self.route_ids_from_rd5(rd5, route_names)
        route_map = self.route_lookup()

        rd5_output_dir.mkdir(parents=True, exist_ok=True)
        for route_name in sorted(route_names):
            route = route_map.get(route_name)
            if route and route.is_same_edge_lane_change_only():
                raise RoadPackageError(
                    "CarMaker TestRun generation is disabled for same-edge-only lane changes "
                    f"such as `{route.start_lane}` -> `{route.goal_lane}` on route `{route_name}`. "
                    "Choose start/goal lanes on different edges, or include a downstream checkpoint/goal edge."
                )

        for route_name in sorted(route_names):
            if route_name in route_ids:
                continue
            route = route_map.get(route_name)
            if not route:
                raise RoadPackageError(
                    f"Route '{route_name}' is not saved in the app yet. Plan that route, then set it as ego or add a traffic actor."
                )
            output_rd5 = rd5_output_dir / f"{safe_name(current_rd5_path.stem)}_{route_name}.rd5"
            result = write_rd5_with_route(rd5, route, output_rd5, route_name=route_name)
            self.decorate_rd5_intersections_if_available(result.output_path)
            self.last_rd5_route_result = result
            route_ids[route_name] = result.route_id
            (report_dir / f"rd5_route_write_report_{route_name}.md").write_text(result.report, encoding="utf-8")
            current_rd5_path = result.output_path
            rd5 = Rd5Road.load(current_rd5_path)
            route_ids.update(self.route_ids_from_rd5(rd5, route_names))

        self.decorate_rd5_intersections_if_available(current_rd5_path)
        self.rd5_path_var.set(str(current_rd5_path))
        return current_rd5_path, route_ids

    def generate_testrun(self, *, show_message: bool = True) -> Path | None:
        if not self.ego_enabled_var.get() and not self.vehicles:
            messagebox.showinfo("Generate TestRun", "Enable ego or add at least one traffic actor.")
            return None

        if self.current_route:
            self.save_current_route()

        ego_route_name = safe_name(self.ego_route_name_var.get()) if self.ego_route_name_var.get().strip() else ""
        if self.ego_enabled_var.get() and not ego_route_name:
            if not self.current_route:
                messagebox.showinfo("Generate TestRun", "Plan a route and set it as ego route first.")
                return None
            ego_route_name = self.save_current_route()
            self.ego_route_name_var.set(ego_route_name)

        fallback_name = ego_route_name or (self.vehicles[0].route_name if self.vehicles else "route_testrun")
        scenario_name = safe_name(self.scenario_name_var.get() or f"{fallback_name}_testrun")
        route_names = set()
        if self.ego_enabled_var.get():
            route_names.add(ego_route_name)
        route_names.update(vehicle.route_name for vehicle in self.vehicles)

        try:
            duration_s = float(self.duration_var.get())
            ego_speed = float(self.ego_speed_var.get())
            ego_start_s = float(self.ego_start_s_var.get())
            ego_lane_offset = float(self.ego_lane_offset_var.get())
        except (TypeError, ValueError):
            messagebox.showerror("Generate TestRun", "Ego speed, route s, lateral offset, and duration must be numbers.")
            return None

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = ROOT / "exports" / f"testrun_{scenario_name}_{stamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            project_dir = Path(self.cm_project_var.get())
            road_dir = project_dir / "Data" / "Road"
            testrun_dir = project_dir / "Data" / "TestRun"
            road_dir.mkdir(parents=True, exist_ok=True)
            testrun_dir.mkdir(parents=True, exist_ok=True)

            road_path, route_ids = self.ensure_routes_enabled_rd5(road_dir, output_dir, route_names)
            missing_routes = sorted(name for name in route_names if name not in route_ids)
            if missing_routes:
                raise RoadPackageError(
                    "Missing CarMaker route ObjId for: "
                    + ", ".join(missing_routes)
                    + ". Generate/write those RD5 routes first."
                )

            ego = None
            if self.ego_enabled_var.get():
                ego = EgoPlan(
                    enabled=True,
                    route_name=ego_route_name,
                    vehicle_model=self.ego_model_var.get().strip() or DEFAULT_EGO_MODEL,
                    driver_template=self.ego_driver_var.get().strip() or DEFAULT_EGO_DRIVER,
                    speed_kmh=ego_speed,
                    start_s=ego_start_s,
                    lane_offset=ego_lane_offset,
                )

            project_road_path = road_dir / road_path.name
            if road_path.resolve() != project_road_path.resolve():
                shutil.copy2(road_path, project_road_path)

            self.rd5_path_var.set(str(project_road_path))
            project_config = TestRunConfig(
                scenario_name=scenario_name,
                road_file_ref=project_road_reference(project_dir, project_road_path),
                route_ids=route_ids,
                ego=ego,
                traffic=self.vehicles,
                duration_s=duration_s,
            )
            project_result = write_testrun(project_config, testrun_dir / scenario_name)
            (output_dir / "testrun_project_report.md").write_text(project_result.report, encoding="utf-8")
        except Exception as exc:
            messagebox.showerror("Generate TestRun", str(exc))
            self.log(f"Generate TestRun failed: {exc}")
            return None

        self.last_testrun_path = project_result.output_path
        self.last_testrun_project = project_dir
        self.log(f"Generated project RD5: {project_road_path}")
        self.log(f"Generated project TestRun: {project_result.output_path}")
        self.log(f"Saved TestRun report: {output_dir / 'testrun_project_report.md'}")
        self.set_text(self.route_text, project_result.report)

        message = (
            "Generated CarMaker project files.\n"
            f"RD5: {project_road_path}\n"
            f"TestRun: {project_result.output_path}\n"
            f"Report: {output_dir / 'testrun_project_report.md'}"
        )
        if show_message:
            messagebox.showinfo("Generate TestRun", message)
        return project_result.output_path

    def generate_and_run_carmaker(self) -> None:
        testrun_path = self.generate_testrun(show_message=False)
        if not testrun_path:
            return
        project_dir = self.last_testrun_project or Path(self.cm_project_var.get())
        try:
            cm_home = Path(self.cm_home_var.get())
            python_cmd, python_label = self.find_cmapi_python()
            if not python_cmd:
                raise RoadPackageError(
                    "CarMaker 5x visualization needs the CarMaker CMAPI/APO Python wheels.\n"
                    "This CarMaker 15 install provides wheels for Python 3.9 through 3.13, "
                    "but no compatible interpreter was found.\n\n"
                    "Install Python 3.13 or 3.12, or set CARMAKER_CMAPI_PYTHON to that python.exe.\n"
                    "The TestRun was generated successfully; only the 5x runner was not started."
                )
            runner = Path(__file__).resolve().parent / "carmaker_5x_runner.py"
            if not runner.exists():
                raise RoadPackageError(f"CMAPI runner script was not found: {runner}")
            log_path = self.cmapi_run_log_path(project_dir, testrun_path)
            args = [
                *python_cmd,
                str(runner),
                "--project",
                str(project_dir),
                "--testrun",
                str(testrun_path),
                "--cm-home",
                str(cm_home),
                "--factor",
                "5.0",
                "--movie-ready-delay",
                "5.0",
                "--keep-movie-open",
            ]
            with log_path.open("w", encoding="utf-8") as log_file:
                proc = subprocess.Popen(
                    args,
                    cwd=str(Path(__file__).resolve().parent),
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
                )
            time.sleep(1.0)
            if proc.poll() is not None and proc.returncode:
                log_tail = log_path.read_text(encoding="utf-8", errors="replace")[-3000:]
                raise RoadPackageError(
                    "CMAPI 5x runner exited before the simulation started.\n"
                    f"Log: {log_path}\n\n"
                    f"{log_tail}"
                )
        except Exception as exc:
            messagebox.showerror("Run CarMaker 5x", str(exc))
            self.log(f"Run CarMaker 5x failed: {exc}")
            return

        self.log(f"Started CarMaker CMAPI 5x runner: pid {proc.pid}")
        self.log(f"CMAPI Python: {python_label}")
        self.log(f"Run log: {log_path}")
        self.log(
            "CarMaker/IPGMovie startup continues in the background; the runner waits 5 seconds "
            "after IPGMovie starts before switching the active TestRun to 5x."
        )

    def find_cmapi_python(self) -> tuple[list[str] | None, str]:
        env_value = os.environ.get("CARMAKER_CMAPI_PYTHON", "").strip()
        candidates: list[list[str]] = []
        if env_value:
            env_path = Path(env_value.strip('"'))
            if env_path.exists():
                candidates.append([str(env_path)])
            else:
                candidates.append([part.strip('"') for part in shlex.split(env_value, posix=False)])
        candidates.extend(
            [
                [sys.executable],
                ["py", "-3.13"],
                ["py", "-3.12"],
                ["py", "-3.11"],
                ["py", "-3.10"],
                ["py", "-3.9"],
            ]
        )
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            local_python_root = Path(local_appdata) / "Programs" / "Python"
            for minor in (13, 12, 11, 10, 9):
                candidates.append([str(local_python_root / f"Python3{minor}" / "python.exe")])
        candidates.append(["python"])

        seen: set[tuple[str, ...]] = set()
        for candidate in candidates:
            if not candidate:
                continue
            key = tuple(candidate)
            if key in seen:
                continue
            seen.add(key)
            probe = self.probe_python(candidate)
            if not probe:
                continue
            version, executable = probe
            major, minor = version
            if major == 3 and 9 <= minor <= 13:
                label = f"{executable} (Python {major}.{minor})"
                return candidate, label
        return None, ""

    def probe_python(self, command: list[str]) -> tuple[tuple[int, int], str] | None:
        probe_script = (
            "import sys; "
            "print(f'{sys.version_info.major}.{sys.version_info.minor}'); "
            "print(sys.executable)"
        )
        try:
            completed = subprocess.run(
                [*command, "-c", probe_script],
                capture_output=True,
                text=True,
                timeout=8,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception:
            return None
        if completed.returncode != 0:
            return None
        lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        if len(lines) < 2:
            return None
        try:
            major_text, minor_text = lines[0].split(".", 1)
            version = (int(major_text), int(minor_text))
        except ValueError:
            return None
        return version, lines[1]

    def cmapi_run_log_path(self, project_dir: Path, testrun_path: Path) -> Path:
        config_dir = project_dir / "Data" / "Config"
        config_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return config_dir / f"codex_cmapi_5x_{safe_name(testrun_path.name)}_{stamp}.log"

    def compute_bounds(self) -> None:
        if not self.package:
            self.bounds = None
            return
        points = []
        for lane in self.package.lanes.values():
            points.extend(lane.shape)
        if not points:
            self.bounds = None
            return
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        self.bounds = (min(xs), min(ys), max(xs), max(ys))

    def redraw(self) -> None:
        self.canvas.delete("all")
        if not self.package or not self.bounds:
            self.canvas.create_text(20, 20, text="No road package loaded.", anchor="nw", fill="#475569")
            return

        route = self.display_route if self.display_route_owner else self.current_route
        route_lanes = set(route.lane_path if route else [])
        if self.display_route_owner:
            checkpoint_lanes = []
            start_lane = self.display_route.start_lane if self.display_route else ""
            goal_lane = self.display_route.goal_lane if self.display_route else ""
        else:
            checkpoint_lanes = [token for token in self.parse_checkpoint_lanes() if token in self.package.lanes]
            start_lane = self.start_lane_var.get()
            goal_lane = self.goal_lane_var.get()

        for lane in self.package.lanes.values():
            if lane.id in route_lanes:
                continue
            color = "#e2e8f0" if lane.internal else "#94a3b8"
            width = 1 if lane.internal else 2
            self.draw_lane(lane.shape, color=color, width=width)

        if route:
            self.draw_route(route)

        for lane_id in checkpoint_lanes:
            lane = self.package.lanes.get(lane_id)
            if lane:
                self.draw_lane(lane.shape, color="#8b5cf6", width=7)

        for lane_id, color in [(start_lane, "#16a34a"), (goal_lane, "#dc2626")]:
            lane = self.package.lanes.get(lane_id)
            if lane:
                if route and lane_id in route_lanes:
                    marker_s = lane.length if lane_id == goal_lane else 0.0
                    self.draw_lane_marker(lane, color=color, s_pos=marker_s)
                else:
                    self.draw_lane(lane.shape, color=color, width=7)

        if self.selected_lane_id and self.selected_lane_id not in {start_lane, goal_lane, *checkpoint_lanes}:
            lane = self.package.lanes.get(self.selected_lane_id)
            if lane:
                self.draw_lane(lane.shape, color="#0284c7", width=7)

        if self.hover_lane_id and self.hover_lane_id not in {start_lane, goal_lane, self.selected_lane_id, *checkpoint_lanes}:
            lane = self.package.lanes.get(self.hover_lane_id)
            if lane:
                self.draw_lane(lane.shape, color="#0ea5e9", width=4)

        labeled_edges = set()
        for lane in self.package.lanes.values():
            if lane.internal or lane.edge_id in labeled_edges or not lane.shape:
                continue
            labeled_edges.add(lane.edge_id)
            mid = lane.shape[len(lane.shape) // 2]
            x, y = self.to_screen(mid)
            self.canvas.create_text(x, y - 10, text=lane.edge_id, fill="#334155", font=("Segoe UI", 9, "bold"))

        if route:
            label = self.display_route_owner if self.display_route else route.name
            self.canvas.create_text(
                12,
                12,
                text=f"{label}  {route.total_length:.1f} m",
                anchor="nw",
                fill="#0f172a",
                font=("Segoe UI", 11, "bold"),
            )

        target_label = {"start": "Start", "goal": "Goal", "checkpoint": "Checkpoint"}.get(
            self.click_target_var.get(),
            "Start",
        )
        selected = f" | selected: {self.selected_lane_id}" if self.selected_lane_id else ""
        self.canvas.create_text(
            12,
            34 if route else 12,
            text=f"Click target: {target_label}{selected}",
            anchor="nw",
            fill="#334155",
            font=("Segoe UI", 9),
        )
        self.canvas.create_text(
            12,
            52 if route else 30,
            text=f"Wheel: zoom {self.view_zoom:.2f}x | drag background: pan",
            anchor="nw",
            fill="#64748b",
            font=("Segoe UI", 9),
        )

    def draw_lane(self, shape: list[tuple[float, float]], color: str, width: int, *, smooth: bool = False) -> None:
        if len(shape) < 2:
            return
        coords = []
        for point in shape:
            coords.extend(self.to_screen(point))
        self.canvas.create_line(
            *coords,
            fill=color,
            width=width,
            capstyle="round",
            joinstyle="round",
            smooth=smooth,
            splinesteps=24,
        )

    def draw_route(self, route) -> None:
        if not self.package:
            return
        previous_lane = None
        path = route.lane_path
        for index, lane_id in enumerate(path):
            lane = self.package.lanes.get(lane_id)
            if not lane:
                previous_lane = None
                continue
            next_lane = self.package.lanes.get(path[index + 1]) if index + 1 < len(path) else None

            start_s = 0.0
            end_s = lane.length
            if previous_lane and self.is_same_edge_lane_change(previous_lane, lane):
                _, start_s = self.route_lane_change_window(min(previous_lane.length, lane.length))
            if next_lane and self.is_same_edge_lane_change(lane, next_lane):
                end_s, _ = self.route_lane_change_window(min(lane.length, next_lane.length))

            segment = self.lane_segment_between(lane, start_s, end_s)
            self.draw_lane(segment, color="#f97316", width=5)

            if next_lane and self.is_same_edge_lane_change(lane, next_lane):
                change_start_s, change_end_s = self.route_lane_change_window(min(lane.length, next_lane.length))
                curve = self.lane_change_curve(lane, next_lane, change_start_s, change_end_s)
                self.draw_lane(curve, color="#f97316", width=5, smooth=True)

            previous_lane = lane

    @staticmethod
    def is_same_edge_lane_change(source, target) -> bool:
        return (
            source.edge_id == target.edge_id
            and source.index != target.index
            and source.internal == target.internal
        )

    @staticmethod
    def route_lane_change_s(link_length: float) -> float:
        if link_length <= 0:
            return 5.0
        if link_length <= 10.0:
            return max(link_length / 2.0, 0.1)
        return min(max(link_length * 0.15, 3.0), link_length - 3.0)

    def route_lane_change_window(self, link_length: float) -> tuple[float, float]:
        if link_length <= 0:
            return (0.0, 0.0)
        center = self.route_lane_change_s(link_length)
        span = min(max(link_length * 0.25, 12.0), 36.0, max(link_length - 0.2, 0.1))
        start_s = max(0.0, center - span / 2.0)
        end_s = min(link_length, center + span / 2.0)
        if start_s <= 0.0:
            end_s = min(link_length, span)
        if end_s >= link_length:
            start_s = max(0.0, link_length - span)
        if end_s <= start_s:
            end_s = min(link_length, start_s + max(link_length * 0.1, 0.1))
        return start_s, end_s

    def lane_change_curve(self, source_lane, target_lane, start_s: float, end_s: float) -> list[tuple[float, float]]:
        span = max(end_s - start_s, 0.1)
        handle = span * 0.55
        p0 = self.lane_point_at_s(source_lane, start_s)
        p1 = self.lane_point_at_s(source_lane, min(source_lane.length, start_s + handle))
        p2 = self.lane_point_at_s(target_lane, max(0.0, end_s - handle))
        p3 = self.lane_point_at_s(target_lane, end_s)
        return [self.cubic_bezier(p0, p1, p2, p3, index / 18.0) for index in range(19)]

    @staticmethod
    def cubic_bezier(
        p0: tuple[float, float],
        p1: tuple[float, float],
        p2: tuple[float, float],
        p3: tuple[float, float],
        t: float,
    ) -> tuple[float, float]:
        u = 1.0 - t
        b0 = u * u * u
        b1 = 3.0 * u * u * t
        b2 = 3.0 * u * t * t
        b3 = t * t * t
        return (
            b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0],
            b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1],
        )

    def lane_point_at_s(self, lane, s_pos: float) -> tuple[float, float]:
        shape = lane.shape
        if not shape:
            return (0.0, 0.0)
        if len(shape) == 1:
            return shape[0]
        distances = self.shape_distances(shape)
        total_shape = distances[-1]
        if total_shape <= 1e-9:
            return shape[0]
        target = max(0.0, min(float(s_pos), max(lane.length, 0.0)))
        if lane.length > 1e-9:
            target = total_shape * target / lane.length
        target = max(0.0, min(target, total_shape))
        for index in range(1, len(shape)):
            if distances[index] < target:
                continue
            segment_length = distances[index] - distances[index - 1]
            if segment_length <= 1e-9:
                return shape[index]
            ratio = (target - distances[index - 1]) / segment_length
            x0, y0 = shape[index - 1]
            x1, y1 = shape[index]
            return (x0 + (x1 - x0) * ratio, y0 + (y1 - y0) * ratio)
        return shape[-1]

    def lane_segment_between(self, lane, start_s: float, end_s: float) -> list[tuple[float, float]]:
        if len(lane.shape) < 2:
            return []
        if end_s <= start_s:
            return []
        start_point = self.lane_point_at_s(lane, start_s)
        end_point = self.lane_point_at_s(lane, end_s)
        distances = self.shape_distances(lane.shape)
        total_shape = distances[-1]
        if total_shape <= 1e-9:
            return [start_point, end_point]
        start_target = total_shape * max(0.0, min(start_s, lane.length)) / lane.length if lane.length > 1e-9 else 0.0
        end_target = total_shape * max(0.0, min(end_s, lane.length)) / lane.length if lane.length > 1e-9 else total_shape
        points = [start_point]
        for index, point in enumerate(lane.shape[1:-1], start=1):
            if start_target < distances[index] < end_target:
                points.append(point)
        points.append(end_point)
        return points

    @staticmethod
    def shape_distances(shape: list[tuple[float, float]]) -> list[float]:
        distances = [0.0]
        for start, end in zip(shape, shape[1:]):
            distances.append(distances[-1] + math.hypot(end[0] - start[0], end[1] - start[1]))
        return distances

    def draw_lane_marker(self, lane, color: str, s_pos: float) -> None:
        x, y = self.to_screen(self.lane_point_at_s(lane, s_pos))
        radius = 5
        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=color,
            outline="white",
            width=2,
        )

    def to_screen(self, point: tuple[float, float]) -> tuple[float, float]:
        x, y = self.base_to_screen(point)
        canvas_w = max(self.canvas.winfo_width(), 100)
        canvas_h = max(self.canvas.winfo_height(), 100)
        center_x = canvas_w / 2
        center_y = canvas_h / 2
        return (
            center_x + (x - center_x) * self.view_zoom + self.view_pan_x,
            center_y + (y - center_y) * self.view_zoom + self.view_pan_y,
        )

    def base_to_screen(self, point: tuple[float, float]) -> tuple[float, float]:
        min_x, min_y, max_x, max_y = self.bounds or (0, 0, 1, 1)
        canvas_w = max(self.canvas.winfo_width(), 100)
        canvas_h = max(self.canvas.winfo_height(), 100)
        margin = 44
        scale_x = (canvas_w - margin * 2) / max(max_x - min_x, 1)
        scale_y = (canvas_h - margin * 2) / max(max_y - min_y, 1)
        scale = max(min(scale_x, scale_y), 0.01)
        x = margin + (point[0] - min_x) * scale
        y = canvas_h - margin - (point[1] - min_y) * scale
        return x, y

    def set_text(self, widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def log(self, message: str) -> None:
        now = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{now}] {message}\n")
        self.log_text.see("end")


def main() -> None:
    parser = argparse.ArgumentParser(description="TrafficGen desktop app")
    parser.add_argument("--folder", type=Path, help="RoadGen export folder to load")
    parser.add_argument("--rd5", type=Path, help="CarMaker RD5 file to use")
    parser.add_argument("--project", type=Path, help="CarMaker project root")
    parser.add_argument("--scenario", help="Default TestRun/scenario name")
    args = parser.parse_args()
    app = TrafficGenApp(
        initial_folder=args.folder,
        initial_rd5=args.rd5,
        initial_project=args.project,
        initial_scenario=args.scenario,
    )
    app.mainloop()


if __name__ == "__main__":
    main()
