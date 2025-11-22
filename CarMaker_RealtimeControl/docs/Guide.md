
# User Accessible Quantities (UAQ) Documentation Guide

This document provides a guide to the extracted User Accessible Quantities (UAQ) files from Chapter 26 of the CarMaker Reference Manual. The content has been split into multiple files for easier navigation, categorized by subsystem.

## Classification Overview

The PDF and text files are organized by the major functional blocks of the CarMaker simulation.

| File Name | Page Range | Topic | Description |
|-----------|------------|-------|-------------|
| **UAQ_01_General_Control** | 2-13 | General & Control | Core simulation timers (TCPU, TGPU), Environment (Weather, Road), Driving Maneuvers (DrivMan), Driver inputs, and basic Vehicle Control signals. |
| **UAQ_02_Car** | 14-25 | Car Body & Aero | Vehicle body dynamics (Car.ConBdy...), Aerodynamics (Car.Aero...), and general vehicle kinematics. |
| **UAQ_03_Suspension** | 25-44 | Suspension | Detailed suspension quantities including Buffer, Damper, Spring, Stabilizer, and Elasto-Kinematics (Car.Susp...). |
| **UAQ_04_Suspension_Tire_Brake** | 45-55 | Tire & Brake | Tire forces and dynamics (Car.Tire...), Brake system (Car.Brake...), and Steering system details. |
| **UAQ_05_Powertrain** | 56-68 | Powertrain | Complete powertrain system: Engine, Clutch, Gearbox, Planetary Gear, Driveline, Battery, Electric Motor, and Power Supply. |
| **UAQ_06_Sensor_Part1** | 69-81 | Sensors (Part 1) | Perception sensors including Object Sensors, Radar, Camera, and Lidar. |
| **UAQ_06_Sensor_Part2** | 82-90 | Sensors (Part 2) | Navigation and physical sensors: GNSS (GPS), IMU (Inertial Measurement Unit), Road Sensors, and Collision detection. |
| **UAQ_07_Trailer** | 91-97 | Trailer | Trailer specific quantities: Body dynamics, Hitch forces, and Suspension for trailers. |
| **UAQ_08_Traffic** | 98-102 | Traffic | Traffic object information, states, and interactions. |

## How to Use
- **For Simulation Setup**: Refer to `UAQ_01_General_Control` for time, environment, and driver inputs.
- **For Vehicle Dynamics Analysis**: Use `UAQ_02_Car`, `UAQ_03_Suspension`, and `UAQ_04_Suspension_Tire_Brake`.
- **For Powertrain Modeling**: Check `UAQ_05_Powertrain`.
- **For ADAS/AV Development**: `UAQ_06_Sensor_Part1` and `UAQ_06_Sensor_Part2` contain all sensor outputs.

Each `.txt` file contains the raw extracted text from the corresponding pages of the manual.
