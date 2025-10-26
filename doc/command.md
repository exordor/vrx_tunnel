# VRX-GZ User Guide

## Build

```sh
colcon build --merge-install
```

## Setup

```sh
source install/setup.zsh
```

## Build & Setup in one line

```sh
colcon build --merge-install && source install/setup.zsh
```

## Generate the WAM-V URDF

Prerequisite: ensure PyYAML is available for the generator

- Debian/Ubuntu: `sudo apt-get install -y python3-yaml`
- Or via pip: `python3 -m pip install --user pyyaml`

Recommended (portable paths):

```sh
ros2 launch vrx_gazebo generate_wamv.launch.py \
  component_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/component_config_rgl.yaml \
  thruster_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/thruster_config_mini.yaml \
  wamv_target:=./tmp/wamv_rgl_mini.urdf
```

Notes:

- `wamv_target` may be a relative path (resolved against your current working directory).
- You can customize the component/thruster YAMLs to match your sensor suite and thruster layout.

## Run the simulation

Option A — one-shot (generate URDF, then start sim + RViz):

```sh
ros2 launch vrx_gz generate_and_viz.launch.py \
  component_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/component_config_rgl.yaml \
  thruster_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/thruster_config_mini.yaml \
  wamv_target:=$PWD/tmp/wamv_rgl_mini.urdf \
  config_file:=$(ros2 pkg prefix vrx_gz)/share/vrx_gz/config/water_only_wamv_40_mini.yaml
```

Option B — launch only (URDF already generated):

```sh
ros2 launch vrx_gz tunnel_viz.launch.py \
  config_file:=$(ros2 pkg prefix vrx_gz)/share/vrx_gz/config/water_only_wamv_40_mini.yaml \
  urdf:=./tmp/wamv_rgl_mini.urdf
```

Notes:

- The scenario YAML (`water_only_wamv_40_mini.yaml`) contains `launch` settings and model config. Any `urdf` field in the YAML can be a relative path; it is resolved against the current working directory. The `urdf` launch arg, if provided, overrides the YAML.
- You can override individual launch args on the command line (e.g., `world:=...`, `rviz:=false`).
- RViz settings can be specified via YAML (`launch.rviz.enable/config`) or via the `rviz` / `rviz_config` launch args.

## Data recording

Enable `rosbag.enable: true` in the scenario YAML to auto-start recording after `rosbag.start_delay` seconds (default 0).

- Output dir: `<CWD>/bag/<timestamp>` (e.g., `~/code/tunnel_ws/bag/20250517_153000`)
- Example command (spawned by the launch system):

```sh
ros2 bag record -o ./bag/20250517_153000 -s mcap /clock /wamv/sensors/imu/data /wamv/scan_front
```

If `topics` is empty, recording is skipped with a console notice.

## Control (teleop)

```sh
ros2 launch vrx_gz usv_joy_teleop.py
```

Topics:

- IMU: `/wamv/sensors/imu/data` (link frame: `wamv/imu_wamv_link`)
- RGL point clouds: `/wamv/scan_front`, `/wamv/scan_omni`

## MOLA examples

```sh
MOLA_LIDAR_TOPIC=/wamv/scan_front \
MOLA_IMU_TOPIC=/wamv/sensors/imu/data \
MOLA_TF_BASE_LINK=wamv/base_link \
MOLA_GENERATE_SIMPLEMAP=true \
MOLA_SIMPLEMAP_OUTPUT=front_spiral_map.simplemap \
MOLA_SIMPLEMAP_GENERATE_LAZY_LOAD=true \
MOLA_SAVE_TRAJECTORY=true \
MOLA_TUM_TRAJECTORY_OUTPUT=front_spiral_estimated_trajectory.tum \
mola-lo-gui-rosbag2
```

```sh
MOLA_LIDAR_TOPIC=/wamv/scan_omni \
MOLA_IMU_TOPIC=/wamv/sensors/imu/data \
MOLA_TF_BASE_LINK=wamv/base_link \
MOLA_GENERATE_SIMPLEMAP=true \
MOLA_SIMPLEMAP_OUTPUT=omni_map.simplemap \
MOLA_SIMPLEMAP_GENERATE_LAZY_LOAD=true \
MOLA_SAVE_TRAJECTORY=true \
MOLA_TUM_TRAJECTORY_OUTPUT=omni_map_estimated_trajectory.tum \
mola-lo-gui-rosbag2
```

## RGL Gazebo plugin

Project: <https://github.com/RobotecAI/RGLGazeboPlugin>

See their installation instructions: <https://github.com/RobotecAI/RGLGazeboPlugin#installation>
