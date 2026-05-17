from __future__ import annotations

import copy
import json
import math
import shutil
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from carmaker_converter import ConverterError, convert_xodr_to_rd5
from rd5_environment import (
    CITY_DENSITY_MAX,
    CITY_DENSITY_MIN,
    EnvironmentError,
    decorate_rd5_city,
    decorate_rd5_intersections,
    decorate_rd5_safety_margins,
)
from server import ROOT, clean_id, find_osc2cm, generate_project, slugify


TEMPLATES = ROOT / "templates"
DEFAULT_CARMAKER_PROJECTS = Path(r"C:\CM_Projects")
BASE_CANVAS_SCALE = 3.0
MIN_CANVAS_SCALE = 0.5
MAX_CANVAS_SCALE = 24.0


class RoadGenDesktop(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Road Graph Generator")
        self.geometry("1240x780")
        self.minsize(1020, 640)

        TEMPLATES.mkdir(exist_ok=True)

        self.nodes: list[dict] = []
        self.edges: list[dict] = []
        self.template_paths: list[Path] = []
        self.last_result: dict | None = None

        self.mode = tk.StringVar(value="select")
        self.project_name = tk.StringVar(value="road_graph")
        self.environment_var = tk.StringVar(value="None")
        self.city_seed_var = tk.StringVar(value="Stable")
        self.city_density_var = tk.DoubleVar(value=1.0)
        self._city_density_updating = False
        self.selected_nodes: set[str] = set()
        self.selected_edges: set[str] = set()
        self.edge_start: str | None = None

        self.drag_nodes: set[str] = set()
        self.drag_origin_world: tuple[float, float] | None = None
        self.drag_origin_positions: dict[str, tuple[float, float]] = {}
        self.panning = False
        self.pointer_origin = (0.0, 0.0)
        self.pan_origin = (0.0, 0.0)
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.scale = BASE_CANVAS_SCALE

        self.node_id_var = tk.StringVar()
        self.node_type_var = tk.StringVar(value="priority")
        self.node_x_var = tk.StringVar()
        self.node_y_var = tk.StringVar()
        self.edge_id_var = tk.StringVar()
        self.edge_from_var = tk.StringVar()
        self.edge_to_var = tk.StringVar()
        self.edge_lanes_var = tk.IntVar(value=1)
        self.edge_speed_var = tk.DoubleVar(value=50.0)
        self.edge_twoway_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.refresh_templates()
        self.load_template("figure8")

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self, padding=(10, 8))
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.columnconfigure(1, weight=1)
        toolbar.columnconfigure(11, weight=1)

        ttk.Label(toolbar, text="Project").grid(row=0, column=0, sticky="w")
        ttk.Entry(toolbar, textvariable=self.project_name, width=28).grid(row=0, column=1, sticky="w", padx=(8, 16))

        for index, (label, value) in enumerate(
            [("Select", "select"), ("Node", "node"), ("Edge", "edge")],
            start=2,
        ):
            ttk.Radiobutton(toolbar, text=label, value=value, variable=self.mode, command=self._mode_changed).grid(
                row=0, column=index, padx=2
            )

        ttk.Button(toolbar, text="Save Template", command=self.save_graph).grid(row=0, column=5, padx=(16, 2))
        ttk.Button(toolbar, text="Load Template", command=self.load_graph).grid(row=0, column=6, padx=2)
        ttk.Button(toolbar, text="Generate XODR", command=self.generate_xodr).grid(row=0, column=7, padx=(16, 2))
        ttk.Button(toolbar, text="Copy To CarMaker", command=self.copy_to_carmaker_project).grid(row=0, column=8, padx=2)
        ttk.Label(toolbar, text="Env").grid(row=0, column=9, sticky="e", padx=(12, 4))
        ttk.Combobox(
            toolbar,
            textvariable=self.environment_var,
            values=["None", "City"],
            state="readonly",
            width=8,
        ).grid(row=0, column=10, sticky="w")
        ttk.Label(toolbar, text="City Seed").grid(row=0, column=11, sticky="e", padx=(12, 4))
        ttk.Combobox(
            toolbar,
            textvariable=self.city_seed_var,
            values=["Stable", "Random"],
            state="readonly",
            width=8,
        ).grid(row=0, column=12, sticky="w")
        ttk.Label(toolbar, text="City Density").grid(row=1, column=9, sticky="e", padx=(12, 4), pady=(4, 0))
        density_spin = ttk.Spinbox(
            toolbar,
            textvariable=self.city_density_var,
            from_=CITY_DENSITY_MIN,
            to=CITY_DENSITY_MAX,
            increment=0.5,
            width=6,
            command=self.normalize_city_density,
        )
        density_spin.grid(row=1, column=10, sticky="w", pady=(4, 0))
        density_spin.bind("<MouseWheel>", self.on_city_density_wheel)
        density_spin.bind("<FocusOut>", lambda _event: self.normalize_city_density())
        density_scale = ttk.Scale(
            toolbar,
            variable=self.city_density_var,
            from_=CITY_DENSITY_MIN,
            to=CITY_DENSITY_MAX,
            orient=tk.HORIZONTAL,
            command=self.on_city_density_scale,
            length=170,
        )
        density_scale.grid(row=1, column=11, sticky="ew", padx=(8, 4), pady=(4, 0))
        density_scale.bind("<MouseWheel>", self.on_city_density_wheel)
        ttk.Label(toolbar, text=f"wheel/slider, max {CITY_DENSITY_MAX:g}").grid(
            row=1, column=12, sticky="w", pady=(4, 0)
        )

        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        body.grid(row=1, column=0, sticky="nsew")

        left = ttk.Frame(body, padding=10)
        left.columnconfigure(0, weight=1)
        body.add(left, weight=0)

        ttk.Label(left, text="Built-in Templates").grid(row=0, column=0, sticky="w")
        for row, (label, template) in enumerate(
            [
                ("Figure 8", "figure8"),
                ("Nine", "nine"),
                ("Y", "y"),
                ("T", "t"),
            ],
            start=1,
        ):
            ttk.Button(left, text=label, command=lambda item=template: self.load_template(item)).grid(
                row=row, column=0, sticky="ew", pady=2
            )

        ttk.Separator(left).grid(row=5, column=0, sticky="ew", pady=10)
        ttk.Label(left, text="Template Files").grid(row=6, column=0, sticky="w")

        list_frame = ttk.Frame(left)
        list_frame.grid(row=7, column=0, sticky="nsew", pady=(4, 6))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        left.rowconfigure(7, weight=1)

        self.template_list = tk.Listbox(list_frame, height=10, exportselection=False)
        self.template_list.grid(row=0, column=0, sticky="nsew")
        self.template_list.bind("<Double-Button-1>", lambda _event: self.load_graph())
        template_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.template_list.yview)
        template_scroll.grid(row=0, column=1, sticky="ns")
        self.template_list.configure(yscrollcommand=template_scroll.set)

        ttk.Button(left, text="Save Current", command=self.save_graph).grid(row=8, column=0, sticky="ew", pady=2)
        ttk.Button(left, text="Load Selected", command=self.load_graph).grid(row=9, column=0, sticky="ew", pady=2)
        ttk.Button(left, text="Refresh Folder", command=self.refresh_templates).grid(row=10, column=0, sticky="ew", pady=2)

        ttk.Separator(left).grid(row=11, column=0, sticky="ew", pady=10)
        ttk.Button(left, text="Delete Selected", command=self.delete_selected).grid(row=12, column=0, sticky="ew", pady=2)
        ttk.Button(left, text="Clear", command=self.clear_graph).grid(row=13, column=0, sticky="ew", pady=2)

        center = ttk.Frame(body)
        center.rowconfigure(0, weight=1)
        center.columnconfigure(0, weight=1)
        body.add(center, weight=1)

        self.canvas = tk.Canvas(center, bg="#f7f8fa", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<MouseWheel>", self.on_canvas_wheel)
        self.canvas.bind("<Button-4>", self.on_canvas_wheel)
        self.canvas.bind("<Button-5>", self.on_canvas_wheel)
        self.canvas.bind("<Configure>", lambda _event: self.redraw())

        right = ttk.Frame(body, padding=10)
        right.columnconfigure(0, weight=1)
        body.add(right, weight=0)

        ttk.Label(right, text="Inspector").grid(row=0, column=0, sticky="w")
        self.inspector = ttk.Frame(right)
        self.inspector.grid(row=1, column=0, sticky="nsew", pady=(8, 12))

        ttk.Label(right, text="Output").grid(row=2, column=0, sticky="w")
        self.output = tk.Text(right, width=44, height=15, wrap="word")
        self.output.grid(row=3, column=0, sticky="nsew", pady=(8, 0))
        right.rowconfigure(3, weight=1)

    def _mode_changed(self) -> None:
        self.edge_start = None
        self.drag_nodes = set()
        self.panning = False
        self.redraw()

    @staticmethod
    def is_multi_select(event: tk.Event) -> bool:
        return bool(event.state & 0x0001 or event.state & 0x0004)

    def log(self, text: str) -> None:
        self.output.insert("end", text + "\n")
        self.output.see("end")

    @staticmethod
    def clamp_city_density(value: float) -> float:
        value = max(CITY_DENSITY_MIN, min(float(value), CITY_DENSITY_MAX))
        return round(value * 2.0) / 2.0

    def set_city_density(self, value: float) -> None:
        if self._city_density_updating:
            return
        self._city_density_updating = True
        try:
            self.city_density_var.set(self.clamp_city_density(value))
        finally:
            self._city_density_updating = False

    def normalize_city_density(self) -> None:
        try:
            value = float(self.city_density_var.get())
        except (tk.TclError, TypeError, ValueError):
            value = 1.0
        self.set_city_density(value)

    def on_city_density_scale(self, value: str) -> None:
        try:
            self.set_city_density(float(value))
        except (TypeError, ValueError):
            return

    def on_city_density_wheel(self, event: tk.Event) -> str:
        step = 0.5 if event.delta > 0 else -0.5
        try:
            current = float(self.city_density_var.get())
        except (tk.TclError, TypeError, ValueError):
            current = 1.0
        self.set_city_density(current + step)
        return "break"

    def clear_inspector(self) -> None:
        for child in self.inspector.winfo_children():
            child.destroy()

    def render_inspector(self) -> None:
        self.clear_inspector()
        node_count = len(self.selected_nodes)
        edge_count = len(self.selected_edges)

        if node_count == 0 and edge_count == 0:
            ttk.Label(self.inspector, text="Select nodes or edges.").grid(row=0, column=0, sticky="w")
            ttk.Label(self.inspector, text="Wheel to zoom, drag empty space to pan.").grid(
                row=1, column=0, sticky="w", pady=(4, 0)
            )
            return

        if node_count == 1 and edge_count == 0:
            self.render_single_node(next(iter(self.selected_nodes)))
            return

        if edge_count == 1 and node_count == 0:
            self.render_single_edge(next(iter(self.selected_edges)))
            return

        row = 0
        ttk.Label(self.inspector, text=f"{node_count} node(s), {edge_count} edge(s) selected").grid(
            row=row, column=0, columnspan=2, sticky="w"
        )
        row += 1

        if node_count:
            first = self.find_node(next(iter(self.selected_nodes)))
            self.node_type_var.set(str(first.get("type", "priority")) if first else "priority")
            ttk.Separator(self.inspector).grid(row=row, column=0, columnspan=2, sticky="ew", pady=8)
            row += 1
            ttk.Label(self.inspector, text="Node Type").grid(row=row, column=0, sticky="w", pady=3)
            ttk.Combobox(
                self.inspector,
                textvariable=self.node_type_var,
                values=["priority", "traffic_light", "traffic_light_crosswalk", "crosswalk", "right_before_left"],
                state="readonly",
                width=18,
            ).grid(row=row, column=1, sticky="ew", pady=3)
            row += 1
            ttk.Button(self.inspector, text="Apply Node Type", command=self.apply_node_type).grid(
                row=row, column=0, columnspan=2, sticky="ew", pady=(6, 2)
            )
            row += 1

        if edge_count:
            first_edge = self.find_edge(next(iter(self.selected_edges)))
            if first_edge:
                self.edge_lanes_var.set(int(first_edge.get("numLanes", 1)))
                self.edge_speed_var.set(float(first_edge.get("speedKmh", 50.0)))
                self.edge_twoway_var.set(bool(first_edge.get("twoWay", True)))
            ttk.Separator(self.inspector).grid(row=row, column=0, columnspan=2, sticky="ew", pady=8)
            row += 1
            self._row_spin("Lanes", self.edge_lanes_var, 1, 6, row)
            row += 1
            self._row_entry("Speed km/h", self.edge_speed_var, row)
            row += 1
            ttk.Checkbutton(self.inspector, text="Bidirectional", variable=self.edge_twoway_var).grid(
                row=row, column=0, columnspan=2, sticky="w", pady=3
            )
            row += 1
            ttk.Button(self.inspector, text="Apply Edge Properties", command=self.apply_edge_properties).grid(
                row=row, column=0, columnspan=2, sticky="ew", pady=(6, 2)
            )

        self.inspector.columnconfigure(1, weight=1)

    def render_single_node(self, node_id: str) -> None:
        node = self.find_node(node_id)
        if not node:
            self.selected_nodes.discard(node_id)
            self.render_inspector()
            return
        self.node_id_var.set(str(node["id"]))
        self.node_type_var.set(str(node.get("type", "priority")))
        self.node_x_var.set(f"{float(node['x']):.2f}")
        self.node_y_var.set(f"{float(node['y']):.2f}")
        self._row_entry("ID", self.node_id_var, 0)
        self._row_entry("X", self.node_x_var, 1)
        self._row_entry("Y", self.node_y_var, 2)
        ttk.Label(self.inspector, text="Type").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Combobox(
            self.inspector,
            textvariable=self.node_type_var,
            values=["priority", "traffic_light", "traffic_light_crosswalk", "crosswalk", "right_before_left"],
            state="readonly",
            width=18,
        ).grid(row=3, column=1, sticky="ew", pady=3)
        ttk.Button(self.inspector, text="Apply", command=self.apply_inspector).grid(
            row=9, column=0, columnspan=2, sticky="ew", pady=(10, 2)
        )
        self.inspector.columnconfigure(1, weight=1)

    def render_single_edge(self, edge_id: str) -> None:
        edge = self.find_edge(edge_id)
        if not edge:
            self.selected_edges.discard(edge_id)
            self.render_inspector()
            return
        self.edge_id_var.set(str(edge["id"]))
        self.edge_from_var.set(str(edge["from"]))
        self.edge_to_var.set(str(edge["to"]))
        self.edge_lanes_var.set(int(edge.get("numLanes", 1)))
        self.edge_speed_var.set(float(edge.get("speedKmh", 50.0)))
        self.edge_twoway_var.set(bool(edge.get("twoWay", True)))
        self._row_entry("ID", self.edge_id_var, 0)
        self._row_entry("From", self.edge_from_var, 1)
        self._row_entry("To", self.edge_to_var, 2)
        self._row_spin("Lanes", self.edge_lanes_var, 1, 6, 3)
        self._row_entry("Speed km/h", self.edge_speed_var, 4)
        ttk.Checkbutton(self.inspector, text="Bidirectional", variable=self.edge_twoway_var).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=3
        )
        ttk.Button(self.inspector, text="Apply", command=self.apply_inspector).grid(
            row=9, column=0, columnspan=2, sticky="ew", pady=(10, 2)
        )
        self.inspector.columnconfigure(1, weight=1)

    def _row_entry(self, label: str, variable: tk.Variable, row: int) -> None:
        ttk.Label(self.inspector, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Entry(self.inspector, textvariable=variable, width=20).grid(row=row, column=1, sticky="ew", pady=3)

    def _row_spin(self, label: str, variable: tk.Variable, start: int, end: int, row: int) -> None:
        ttk.Label(self.inspector, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Spinbox(self.inspector, from_=start, to=end, textvariable=variable, width=18).grid(
            row=row, column=1, sticky="ew", pady=3
        )

    def apply_inspector(self) -> None:
        try:
            if len(self.selected_nodes) == 1 and not self.selected_edges:
                self.apply_single_node(next(iter(self.selected_nodes)))
            elif len(self.selected_edges) == 1 and not self.selected_nodes:
                self.apply_single_edge(next(iter(self.selected_edges)))
        except Exception as exc:
            messagebox.showerror("Inspector", str(exc))
            return
        self.redraw()
        self.render_inspector()

    def apply_single_node(self, node_id: str) -> None:
        node = self.find_node(node_id)
        if not node:
            return
        new_id = clean_id(self.node_id_var.get(), node_id)
        if new_id != node_id and self.find_node(new_id):
            raise ValueError(f"Node '{new_id}' already exists.")
        node["id"] = new_id
        node["x"] = float(self.node_x_var.get())
        node["y"] = float(self.node_y_var.get())
        node["type"] = self.node_type_var.get()
        for edge in self.edges:
            if edge["from"] == node_id:
                edge["from"] = new_id
            if edge["to"] == node_id:
                edge["to"] = new_id
        self.selected_nodes = {new_id}

    def apply_single_edge(self, edge_id: str) -> None:
        edge = self.find_edge(edge_id)
        if not edge:
            return
        new_id = clean_id(self.edge_id_var.get(), edge_id)
        if new_id != edge_id and self.find_edge(new_id):
            raise ValueError(f"Edge '{new_id}' already exists.")
        if not self.find_node(self.edge_from_var.get()) or not self.find_node(self.edge_to_var.get()):
            raise ValueError("Edge endpoint node does not exist.")
        edge["id"] = new_id
        edge["from"] = self.edge_from_var.get()
        edge["to"] = self.edge_to_var.get()
        edge["numLanes"] = max(1, int(self.edge_lanes_var.get()))
        edge["speedKmh"] = max(1.0, float(self.edge_speed_var.get()))
        edge["twoWay"] = bool(self.edge_twoway_var.get())
        self.selected_edges = {new_id}

    def apply_node_type(self) -> None:
        for node_id in list(self.selected_nodes):
            node = self.find_node(node_id)
            if node:
                node["type"] = self.node_type_var.get()
        self.redraw()
        self.render_inspector()

    def apply_edge_properties(self) -> None:
        try:
            lanes = max(1, int(self.edge_lanes_var.get()))
            speed = max(1.0, float(self.edge_speed_var.get()))
        except Exception as exc:
            messagebox.showerror("Inspector", str(exc))
            return
        for edge_id in list(self.selected_edges):
            edge = self.find_edge(edge_id)
            if edge:
                edge["numLanes"] = lanes
                edge["speedKmh"] = speed
                edge["twoWay"] = bool(self.edge_twoway_var.get())
        self.redraw()
        self.render_inspector()

    def screen_to_world(self, x: float, y: float) -> tuple[float, float]:
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        return (x - width / 2 - self.pan_x) / self.scale, (height / 2 + self.pan_y - y) / self.scale

    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        return width / 2 + self.pan_x + x * self.scale, height / 2 + self.pan_y - y * self.scale

    def on_canvas_press(self, event: tk.Event) -> None:
        node_id = self.hit_node(event.x, event.y)
        edge_id = self.hit_edge(event.x, event.y)
        mode = self.mode.get()
        multi = self.is_multi_select(event)

        self.drag_nodes = set()
        self.drag_origin_positions = {}
        self.drag_origin_world = None
        self.panning = False

        if mode == "node":
            if not node_id:
                x, y = self.screen_to_world(event.x, event.y)
                node_id = self.next_node_id()
                self.nodes.append({"id": node_id, "x": round(x, 2), "y": round(y, 2), "type": "priority"})
            self.select_only("node", node_id)
            self.render_inspector()
            self.redraw()
            return

        if mode == "edge":
            if not node_id:
                return
            if self.edge_start is None:
                self.edge_start = node_id
                self.select_only("node", node_id)
            elif self.edge_start != node_id:
                self.edges.append(
                    {
                        "id": self.next_edge_id(),
                        "from": self.edge_start,
                        "to": node_id,
                        "numLanes": 1,
                        "speedKmh": 50.0,
                        "twoWay": True,
                    }
                )
                self.select_only("edge", self.edges[-1]["id"])
                self.edge_start = None
            self.render_inspector()
            self.redraw()
            return

        if node_id:
            if multi:
                self.toggle_selection("node", node_id)
            else:
                if node_id not in self.selected_nodes:
                    self.select_only("node", node_id)
                self.start_node_drag(node_id, event.x, event.y)
        elif edge_id:
            if multi:
                self.toggle_selection("edge", edge_id)
            else:
                self.select_only("edge", edge_id)
        else:
            if not multi:
                self.clear_selection()
            self.start_pan(event.x, event.y)

        self.render_inspector()
        self.redraw()

    def on_canvas_drag(self, event: tk.Event) -> None:
        if self.drag_nodes and self.drag_origin_world:
            current_x, current_y = self.screen_to_world(event.x, event.y)
            start_x, start_y = self.drag_origin_world
            dx = current_x - start_x
            dy = current_y - start_y
            for node_id, (origin_x, origin_y) in self.drag_origin_positions.items():
                node = self.find_node(node_id)
                if node:
                    node["x"] = round(origin_x + dx, 2)
                    node["y"] = round(origin_y + dy, 2)
            self.redraw()
            self.render_inspector()
            return

        if self.panning:
            dx = event.x - self.pointer_origin[0]
            dy = event.y - self.pointer_origin[1]
            self.pan_x = self.pan_origin[0] + dx
            self.pan_y = self.pan_origin[1] + dy
            self.redraw()

    def on_canvas_release(self, _event: tk.Event) -> None:
        self.drag_nodes = set()
        self.drag_origin_positions = {}
        self.drag_origin_world = None
        self.panning = False

    def on_canvas_wheel(self, event: tk.Event) -> str:
        button_num = getattr(event, "num", None)
        delta = getattr(event, "delta", 0)
        zoom_in = delta > 0 or button_num == 4
        factor = 1.15 if zoom_in else 1 / 1.15
        self.zoom_canvas(event.x, event.y, factor)
        return "break"

    def zoom_canvas(self, screen_x: float, screen_y: float, factor: float) -> None:
        old_scale = self.scale
        next_scale = max(MIN_CANVAS_SCALE, min(MAX_CANVAS_SCALE, old_scale * factor))
        if math.isclose(next_scale, old_scale):
            return
        world_x, world_y = self.screen_to_world(screen_x, screen_y)
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        self.scale = next_scale
        self.pan_x = screen_x - width / 2 - world_x * next_scale
        self.pan_y = screen_y - height / 2 + world_y * next_scale
        self.redraw()

    def reset_canvas_view(self) -> None:
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.scale = BASE_CANVAS_SCALE
        self.panning = False

    def start_node_drag(self, node_id: str, screen_x: float, screen_y: float) -> None:
        if node_id not in self.selected_nodes:
            self.selected_nodes = {node_id}
            self.selected_edges = set()
        self.drag_nodes = set(self.selected_nodes)
        self.drag_origin_world = self.screen_to_world(screen_x, screen_y)
        self.drag_origin_positions = {
            item_id: (float(node["x"]), float(node["y"]))
            for item_id in self.drag_nodes
            if (node := self.find_node(item_id))
        }

    def start_pan(self, screen_x: float, screen_y: float) -> None:
        self.panning = True
        self.pointer_origin = (screen_x, screen_y)
        self.pan_origin = (self.pan_x, self.pan_y)

    def select_only(self, kind: str, item_id: str) -> None:
        if kind == "node":
            self.selected_nodes = {item_id}
            self.selected_edges = set()
        else:
            self.selected_nodes = set()
            self.selected_edges = {item_id}

    def toggle_selection(self, kind: str, item_id: str) -> None:
        if kind == "node":
            if item_id in self.selected_nodes:
                self.selected_nodes.remove(item_id)
            else:
                self.selected_nodes.add(item_id)
        else:
            if item_id in self.selected_edges:
                self.selected_edges.remove(item_id)
            else:
                self.selected_edges.add(item_id)

    def clear_selection(self) -> None:
        self.selected_nodes = set()
        self.selected_edges = set()
        self.edge_start = None

    def redraw(self) -> None:
        self.canvas.delete("all")
        self.draw_grid()

        for edge in self.edges:
            start = self.find_node(edge["from"])
            end = self.find_node(edge["to"])
            if not start or not end:
                continue
            x1, y1 = self.world_to_screen(start["x"], start["y"])
            x2, y2 = self.world_to_screen(end["x"], end["y"])
            selected = edge["id"] in self.selected_edges
            color = "#0f766e" if selected else "#52606d"
            width = 5 if selected else 3
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, capstyle="round")
            self.draw_arrow(x1, y1, x2, y2, color)
            if edge.get("twoWay", True):
                self.draw_arrow(x2, y2, x1, y1, color)
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            self.canvas.create_text(mx, my - 10, text=edge["id"], fill="#334155", font=("Segoe UI", 9))

        for node in self.nodes:
            x, y = self.world_to_screen(node["x"], node["y"])
            selected = node["id"] in self.selected_nodes
            pending = self.edge_start == node["id"]
            node_type = str(node.get("type", "priority"))
            if node_type in {"traffic_light", "traffic_light_crosswalk"}:
                fill = "#16a34a" if not selected else "#0ea5e9"
                outline = "#dc2626" if not pending else "#f97316"
            elif node_type == "crosswalk":
                fill = "#f8fafc" if not selected else "#0ea5e9"
                outline = "#64748b" if not pending else "#f97316"
            elif node_type == "right_before_left":
                fill = "#fef3c7" if not selected else "#0ea5e9"
                outline = "#92400e" if not pending else "#f97316"
            else:
                fill = "#0ea5e9" if selected else "#ffffff"
                outline = "#f97316" if pending else "#1f2937"
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill=fill, outline=outline, width=2)
            if node_type in {"traffic_light", "traffic_light_crosswalk"}:
                self.canvas.create_oval(x - 4, y - 5, x - 1, y - 2, fill="#dc2626", outline="")
                self.canvas.create_oval(x - 1.5, y - 1.5, x + 1.5, y + 1.5, fill="#facc15", outline="")
                self.canvas.create_oval(x + 1, y + 2, x + 4, y + 5, fill="#22c55e", outline="")
            if node_type in {"traffic_light_crosswalk", "crosswalk"}:
                for offset in (-4, 0, 4):
                    self.canvas.create_line(
                        x - 7,
                        y + offset,
                        x + 7,
                        y + offset,
                        fill="#0f172a",
                        width=1,
                    )
            self.canvas.create_text(x, y - 20, text=node["id"], fill="#111827", font=("Segoe UI", 9, "bold"))
        self.draw_view_hint()

    def draw_grid(self) -> None:
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        step_world = self.grid_step_world()
        left, top = self.screen_to_world(0, 0)
        right, bottom = self.screen_to_world(width, height)
        min_x, max_x = sorted((left, right))
        min_y, max_y = sorted((bottom, top))
        start_x = math.floor(min_x / step_world) * step_world
        end_x = math.ceil(max_x / step_world) * step_world
        start_y = math.floor(min_y / step_world) * step_world
        end_y = math.ceil(max_y / step_world) * step_world

        x = start_x
        while x <= end_x + step_world * 0.5:
            sx, _ = self.world_to_screen(x, 0)
            self.canvas.create_line(sx, 0, sx, height, fill="#cbd5e1" if math.isclose(x, 0.0) else "#e5e7eb")
            x += step_world

        y = start_y
        while y <= end_y + step_world * 0.5:
            _, sy = self.world_to_screen(0, y)
            self.canvas.create_line(0, sy, width, sy, fill="#cbd5e1" if math.isclose(y, 0.0) else "#e5e7eb")
            y += step_world

    def grid_step_world(self) -> float:
        target_px = 48.0
        raw_step = target_px / max(self.scale, 0.01)
        for step in (5, 10, 20, 50, 100, 200, 500, 1000):
            if step >= raw_step:
                return float(step)
        return 2000.0

    def draw_view_hint(self) -> None:
        height = max(1, self.canvas.winfo_height())
        text = f"Wheel: zoom {self.scale / BASE_CANVAS_SCALE:.2f}x | drag background: pan"
        item = self.canvas.create_text(14, height - 16, text=text, anchor="sw", fill="#64748b", font=("Segoe UI", 9))
        bbox = self.canvas.bbox(item)
        if bbox:
            pad = 5
            rect = self.canvas.create_rectangle(
                bbox[0] - pad,
                bbox[1] - pad,
                bbox[2] + pad,
                bbox[3] + pad,
                fill="#f8fafc",
                outline="#cbd5e1",
            )
            self.canvas.tag_lower(rect, item)

    def draw_arrow(self, x1: float, y1: float, x2: float, y2: float, color: str) -> None:
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length < 20:
            return
        ux = dx / length
        uy = dy / length
        px = x1 + dx * 0.62
        py = y1 + dy * 0.62
        size = 8
        left = (px - ux * size - uy * size * 0.55, py - uy * size + ux * size * 0.55)
        right = (px - ux * size + uy * size * 0.55, py - uy * size - ux * size * 0.55)
        self.canvas.create_polygon(px, py, left[0], left[1], right[0], right[1], fill=color, outline=color)

    def hit_node(self, screen_x: float, screen_y: float) -> str | None:
        for node in reversed(self.nodes):
            x, y = self.world_to_screen(node["x"], node["y"])
            if math.hypot(screen_x - x, screen_y - y) <= 14:
                return str(node["id"])
        return None

    def hit_edge(self, screen_x: float, screen_y: float) -> str | None:
        best_id = None
        best_distance = 8.0
        for edge in self.edges:
            start = self.find_node(edge["from"])
            end = self.find_node(edge["to"])
            if not start or not end:
                continue
            x1, y1 = self.world_to_screen(start["x"], start["y"])
            x2, y2 = self.world_to_screen(end["x"], end["y"])
            distance = point_to_segment_distance(screen_x, screen_y, x1, y1, x2, y2)
            if distance < best_distance:
                best_distance = distance
                best_id = str(edge["id"])
        return best_id

    def find_node(self, node_id: str) -> dict | None:
        return next((node for node in self.nodes if node["id"] == node_id), None)

    def find_edge(self, edge_id: str) -> dict | None:
        return next((edge for edge in self.edges if edge["id"] == edge_id), None)

    def next_node_id(self) -> str:
        index = len(self.nodes) + 1
        while self.find_node(f"N{index}"):
            index += 1
        return f"N{index}"

    def next_edge_id(self) -> str:
        index = len(self.edges) + 1
        while self.find_edge(f"E{index}"):
            index += 1
        return f"E{index}"

    def delete_selected(self) -> None:
        if not self.selected_nodes and not self.selected_edges:
            return
        deleted_nodes = set(self.selected_nodes)
        deleted_edges = set(self.selected_edges)
        self.nodes = [node for node in self.nodes if node["id"] not in deleted_nodes]
        self.edges = [
            edge
            for edge in self.edges
            if edge["id"] not in deleted_edges and edge["from"] not in deleted_nodes and edge["to"] not in deleted_nodes
        ]
        self.clear_selection()
        self.render_inspector()
        self.redraw()

    def clear_graph(self) -> None:
        if not messagebox.askyesno("Clear", "Clear the current graph?"):
            return
        self.nodes = []
        self.edges = []
        self.clear_selection()
        self.reset_canvas_view()
        self.render_inspector()
        self.redraw()

    def load_template(self, name: str) -> None:
        templates = {
            "figure8": (
                [
                    ("L0", -100, 0),
                    ("L1", -65, 55),
                    ("C", 0, 0),
                    ("L2", -65, -55),
                    ("R0", 100, 0),
                    ("R1", 65, 55),
                    ("R2", 65, -55),
                ],
                [
                    ("E1", "L0", "L1"),
                    ("E2", "L1", "C"),
                    ("E3", "C", "L2"),
                    ("E4", "L2", "L0"),
                    ("E5", "C", "R1"),
                    ("E6", "R1", "R0"),
                    ("E7", "R0", "R2"),
                    ("E8", "R2", "C"),
                ],
            ),
            "nine": (
                [
                    ("N1", -70, 0),
                    ("N2", -35, 60),
                    ("N3", 35, 60),
                    ("N4", 70, 0),
                    ("N5", 35, -60),
                    ("N6", -35, -60),
                    ("T1", 115, -45),
                    ("T2", 155, -95),
                ],
                [
                    ("E1", "N1", "N2"),
                    ("E2", "N2", "N3"),
                    ("E3", "N3", "N4"),
                    ("E4", "N4", "N5"),
                    ("E5", "N5", "N6"),
                    ("E6", "N6", "N1"),
                    ("E7", "N4", "T1"),
                    ("E8", "T1", "T2"),
                ],
            ),
            "y": (
                [("N1", -110, -50), ("N2", 0, 0), ("N3", 110, -50), ("N4", 0, 110)],
                [("E1", "N1", "N2"), ("E2", "N2", "N3"), ("E3", "N2", "N4")],
            ),
            "t": (
                [("N1", -120, 0), ("N2", 0, 0), ("N3", 120, 0), ("N4", 0, 110)],
                [("E1", "N1", "N2"), ("E2", "N2", "N3"), ("E3", "N2", "N4")],
            ),
        }
        node_items, edge_items = templates[name]
        self.nodes = [{"id": node_id, "x": x, "y": y, "type": "priority"} for node_id, x, y in node_items]
        self.edges = [
            {"id": edge_id, "from": start, "to": end, "numLanes": 1, "speedKmh": 50.0, "twoWay": True}
            for edge_id, start, end in edge_items
        ]
        self.project_name.set(f"{name}_road")
        self.clear_selection()
        self.reset_canvas_view()
        self.render_inspector()
        self.redraw()

    def graph_payload(self) -> dict:
        return {
            "nodes": copy.deepcopy(self.nodes),
            "edges": copy.deepcopy(self.edges),
        }

    def refresh_templates(self, select_name: str | None = None) -> None:
        TEMPLATES.mkdir(exist_ok=True)
        self.template_paths = sorted(TEMPLATES.glob("*.json"), key=lambda path: path.name.lower())
        self.template_list.delete(0, "end")
        selected_index = None
        for index, path in enumerate(self.template_paths):
            self.template_list.insert("end", path.name)
            if select_name and path.name == select_name:
                selected_index = index
        if selected_index is not None:
            self.template_list.selection_set(selected_index)
            self.template_list.see(selected_index)

    def selected_template_path(self) -> Path | None:
        selection = self.template_list.curselection()
        if not selection:
            return None
        index = int(selection[0])
        if 0 <= index < len(self.template_paths):
            return self.template_paths[index]
        return None

    def save_graph(self) -> None:
        TEMPLATES.mkdir(exist_ok=True)
        file_name = f"{slugify(self.project_name.get())}.json"
        path = TEMPLATES / file_name
        if path.exists() and not messagebox.askyesno("Save Template", f"Overwrite {path.name}?"):
            return
        payload = {"projectName": self.project_name.get(), "graph": self.graph_payload()}
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.refresh_templates(select_name=path.name)
        self.log(f"Saved template: {path}")

    def load_graph(self) -> None:
        path = self.selected_template_path()
        if not path:
            chosen = filedialog.askopenfilename(
                title="Load graph",
                initialdir=str(TEMPLATES),
                filetypes=[("Graph JSON", "*.json"), ("All files", "*.*")],
            )
            if not chosen:
                return
            path = Path(chosen)
        self.load_graph_from_path(path)

    def load_graph_from_path(self, path: Path) -> None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            graph = data.get("graph", data)
            self.nodes = graph.get("nodes", [])
            self.edges = graph.get("edges", [])
            self.project_name.set(data.get("projectName") or path.stem)
        except Exception as exc:
            messagebox.showerror("Load Graph", str(exc))
            return
        self.clear_selection()
        self.reset_canvas_view()
        self.render_inspector()
        self.redraw()
        self.log(f"Loaded template: {path}")

    def generate_xodr(self) -> None:
        payload = {"projectName": self.project_name.get(), "graph": self.graph_payload()}
        try:
            result = generate_project(payload)
        except Exception as exc:
            messagebox.showerror("Generate XODR", str(exc))
            self.log(f"Generation failed: {exc}")
            return

        self.last_result = result
        self.log("")
        self.log(f"Generated: {result['project']}")
        for label, rel_path in result["files"].items():
            abs_path = ROOT / rel_path.lstrip("/")
            self.log(f"{label}: {abs_path}")
        self.log("CarMaker: use the generated .xosc bridge or GUI import; do not load .xodr as a ROAD5 file.")
        messagebox.showinfo("Generate XODR", f"Generated {result['project']}")

    def copy_to_carmaker_project(self) -> None:
        if not self.last_result:
            messagebox.showinfo("Copy To CarMaker", "Generate XODR first.")
            return

        initial_dir = str(DEFAULT_CARMAKER_PROJECTS if DEFAULT_CARMAKER_PROJECTS.exists() else ROOT)
        project_dir = filedialog.askdirectory(title="Select CarMaker project root", initialdir=initial_dir)
        if not project_dir:
            return
        project_path = Path(project_dir)
        data_dir = project_path / "Data"
        if not data_dir.exists():
            if not messagebox.askyesno(
                "Copy To CarMaker",
                "This does not look like a CarMaker project because it has no Data folder. Create Data/OpenSCENARIO/RoadGen anyway?",
            ):
                return

        dest = data_dir / "OpenSCENARIO" / "RoadGen"
        dest.mkdir(parents=True, exist_ok=True)

        files = self.last_result.get("files", {})
        graph_path: Path | None = None
        graph_rel_path = files.get("graph")
        if graph_rel_path:
            candidate = ROOT / graph_rel_path.lstrip("/")
            if candidate.exists():
                graph_path = candidate
        copied: list[Path] = []
        for key in ["xodr", "xosc", "carmakerNotes"]:
            rel_path = files.get(key)
            if not rel_path:
                continue
            src = ROOT / rel_path.lstrip("/")
            if src.exists():
                target = dest / src.name
                shutil.copy2(src, target)
                copied.append(target)

        project_name = slugify(self.project_name.get())
        direct_rd5: Path | None = None
        xodr_path = next((path for path in copied if path.suffix.lower() == ".xodr"), None)
        if xodr_path:
            try:
                result = convert_xodr_to_rd5(xodr_path, data_dir / "Road" / f"{project_name}.rd5")
                direct_rd5 = result.rd5_path
                self.log("")
                self.log(f"Converted XODR to RD5: {direct_rd5}")
                if self.environment_var.get() == "City":
                    try:
                        city_seed = project_name
                        if self.city_seed_var.get() == "Random":
                            city_seed = f"{project_name}-{time.time_ns()}"
                        city_density = self.clamp_city_density(float(self.city_density_var.get()))
                        self.city_density_var.set(city_density)
                        city = decorate_rd5_city(direct_rd5, seed=city_seed, building_density=city_density)
                    except EnvironmentError as exc:
                        self.log(f"City environment skipped: {exc}")
                    except (TypeError, ValueError) as exc:
                        self.log(f"City environment skipped: invalid density ({exc})")
                    else:
                        self.log(
                            f"City environment added: {city.objects_added} buildings on {city.links_used} road links; "
                            f"{city.sidewalk_bumps} visual shoulder+sidewalk strips; "
                            f"density {city.building_density:g}; seed {city.seed}; road lane topology left unchanged"
                        )
                else:
                    try:
                        safety = decorate_rd5_safety_margins(direct_rd5)
                    except EnvironmentError as exc:
                        self.log(f"Safety margins skipped: {exc}")
                    else:
                        self.log(
                            f"Safety margins added: {safety.shoulder_width:g} m shoulder + "
                            f"{safety.sidewalk_width:g} m visual sidewalk on {safety.links_used} road links; "
                            f"road lane topology left unchanged"
                        )
                try:
                    intersections = decorate_rd5_intersections(
                        direct_rd5,
                        graph_path=graph_path,
                        xodr_path=xodr_path,
                    )
                except EnvironmentError as exc:
                    self.log(f"Intersection decorations skipped: {exc}")
                else:
                    if intersections.traffic_light_nodes or intersections.crosswalk_nodes:
                        self.log(
                            f"Intersection decorations added: {intersections.signal_objects} signal objects and "
                            f"{intersections.crosswalk_markings} crosswalk stripes around "
                            f"{intersections.traffic_light_nodes} signal node(s), "
                            f"{intersections.crosswalk_nodes} crosswalk node(s); "
                            f"{intersections.crosswalk_stop_markers} pedestrian stop marker(s), "
                            f"{intersections.traffic_light_stop_markers} traffic light stop marker(s), "
                            f"{intersections.traffic_light_stop_lines} traffic light stop line(s), "
                            f"{intersections.traffic_light_phase_fixes} off-phase fix(es) included"
                        )
                if result.errors:
                    self.log(f"IPGRoad import/write messages: {len(result.errors)}")
                    for message in result.errors[:5]:
                        self.log(f"- {message}")
                    if len(result.errors) > 5:
                        self.log(f"- ... {len(result.errors) - 5} more")
            except ConverterError as exc:
                self.log("")
                self.log(f"Direct IPGRoad XODR->RD5 conversion skipped: {exc}")

        xosc_path = next((path for path in copied if path.suffix.lower() == ".xosc"), None)
        if not xosc_path:
            messagebox.showerror("Copy To CarMaker", "No generated .xosc bridge was found. Generate XODR again.")
            return

        osc2cm = find_osc2cm() or r"C:\IPG\carmaker\win64-15.0.1\bin\osc2cm.exe"
        relative_xosc = xosc_path.relative_to(project_path).as_posix()
        command = (
            f'& "{osc2cm}" --cmprojpath "{project_path}" '
            f'--oscfname "{relative_xosc}" '
            f'--rdfname "{project_name}.rd5" '
            f'--trfname "{project_name}_import" --logtoconsole'
        )
        script = dest / f"run_osc2cm_{project_name}.ps1"
        script.write_text(command + "\n", encoding="utf-8")

        self.log("")
        self.log(f"Copied CarMaker bridge files to: {dest}")
        if direct_rd5:
            self.log(f"Direct ROAD5 output: {direct_rd5}")
        self.log(f"Fallback command to create ROAD5/TestRun:")
        self.log(command)
        self.log(f"Command script: {script}")
        if direct_rd5:
            message = f"Copied {len(copied)} files and created RD5:\n{direct_rd5}"
        else:
            message = f"Copied {len(copied)} files to {dest}"
        messagebox.showinfo("Copy To CarMaker", message)


def point_to_segment_distance(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    dx = x2 - x1
    dy = y2 - y1
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / length_sq))
    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy
    return math.hypot(px - nearest_x, py - nearest_y)


if __name__ == "__main__":
    RoadGenDesktop().mainloop()
