# VRX Tunnel

VRX Tunnel is a ROS 2 + Gazebo Harmonic workspace tailored for running the Virtual RobotX (VRX) environment with a tunnel scene and an RGL LiDAR-based WAM‑V configuration. It builds on upstream VRX packages and adds:

- A YAML‑driven WAM‑V generation flow (components + thrusters → URDF)
- A one‑shot launch that first generates the URDF and then starts the sim + RViz
- Scenario YAMLs that configure world, RViz, auto‑forward motion, rosbag recording, and teleop mappings

This branch targets ROS 2 Jazzy and Gazebo Harmonic.

## Features

- WAM‑V generation from YAML via `vrx_gazebo` generator
- Tunnel visualization scenario with RViz config and bridges
- RGL LiDAR plugin support (front and omni patterns)
- Auto‑forward helper, rosbag auto‑record, and gamepad teleop

## Requirements

- ROS 2 Jazzy + Gazebo Harmonic set up in your environment
- PyYAML for the generator:
  - Debian/Ubuntu: `sudo apt-get install -y python3-yaml`
  - Or via pip: `python3 -m pip install --user pyyaml`
- RGL Gazebo plugin if you need LiDAR (see link below)

## Quick start

Build and source:

```sh
colcon build --merge-install && source install/setup.zsh
```

Generate URDF and launch (one‑shot):

```sh
ros2 launch vrx_gz generate_and_viz.launch.py \
  component_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/component_config_rgl.yaml \
  thruster_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/thruster_config_mini.yaml \
  wamv_target:=$PWD/tmp/wamv_rgl_mini.urdf \
  config_file:=$(ros2 pkg prefix vrx_gz)/share/vrx_gz/config/water_only_wamv_40_mini.yaml
```

Manual two‑step (optional):

```sh
# 1) Generate URDF
ros2 launch vrx_gazebo generate_wamv.launch.py \
  component_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/component_config_rgl.yaml \
  thruster_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/thruster_config_mini.yaml \
  wamv_target:=./tmp/wamv_rgl_mini.urdf

# 2) Launch sim and override URDF if desired
ros2 launch vrx_gz tunnel_viz.launch.py \
  config_file:=$(ros2 pkg prefix vrx_gz)/share/vrx_gz/config/water_only_wamv_40_mini.yaml \
  urdf:=./tmp/wamv_rgl_mini.urdf
```

Notes:

- Scenario YAMLs accept relative `urdf` paths; these are resolved against your current working directory. Passing `urdf:=...` on the command line overrides the YAML.
- RViz can be toggled via YAML (`launch.rviz.enable/config`) or via launch args (`rviz`, `rviz_config`).

## Configuration

Key config files (installed under `share/vrx_gz/config` and `share/vrx_gazebo/config`):

- `vrx_gz/config/water_only_wamv_40_mini.yaml` — scenario (world/rviz/auto‑forward/rosbag/teleop); uses a relative URDF by default
- `vrx_gazebo/config/wamv_config/component_config_rgl.yaml` — sensors, RGL patterns, cameras, GPS/IMU
- `vrx_gazebo/config/wamv_config/thruster_config_mini.yaml` — mini hull thruster layout

You can adapt the YAMLs and regenerate the URDF at any time.

## Data recording and teleop

- Enable `rosbag.enable: true` in the scenario to auto‑start `ros2 bag record` after a delay.
- Example topics: `/wamv/sensors/imu/data`, `/wamv/scan_front`, `/wamv/scan_omni`.
- Launch gamepad teleop via `ros2 launch vrx_gz usv_joy_teleop.py`.

## Performance tips

- If RViz feels laggy, lower camera FPS/resolution in your sensor config.

## RGL Gazebo plugin

Project: <https://github.com/RobotecAI/RGLGazeboPlugin>

Installation: <https://github.com/RobotecAI/RGLGazeboPlugin#installation>

## More docs

See the detailed usage guide at `src/vrx_tunnel/doc/command.md`.

## Upstream VRX

This workspace builds on the upstream VRX project. For tutorials and reference:

- VRX Wiki: <https://github.com/osrf/vrx/wiki>
- Release video (v2.3): <https://vimeo.com/851696025>


