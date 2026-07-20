# 🐕 ROS 2 Quadruped Robot Simulation

A complete ROS 2 and Gazebo digital twin pipeline for a custom quadruped robot inspired by the Boston Dynamics Spot architecture. This repository covers the end-to-end workflow from 3D CAD modeling to URDF kinematic definition, physics integration, and simulated environment deployment.

---

## 📌 Project Overview

This project focuses on designing, rigging, and simulating a four-legged autonomous robot capable of navigating complex interior spaces. The primary testing target is a digital twin of the **Chai Center** environment.

* **Robot Architecture:** Quadruped design based on Spot-like link/joint proportions.
* **Middleware:** ROS 2 (Humble / Jazzy).
* **Simulator:** Gazebo (Ignition / Fortress / Harmonic).
* **Description Format:** URDF / Xacro macros for modular joint configuration.

---

## 🛠 System Architecture & Data Flow

```text
+------------------+       +-------------------+       +--------------------+
| 3D Meshes (.stl) | ----> | URDF / Xacro File | ----> | Gazebo Physics Engine |
+------------------+       +-------------------+       +--------------------+
                                    ^                            |
                                    | (Joint Commands)           | (Sensors / TFs)
                                    v                            v
                           +-------------------+       +--------------------+
                           | ros2_control Node | <---> | ROS 2 Nav2 / Teleop|
                           +-------------------+       +--------------------+
