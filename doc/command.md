# VRX-GZ 使用手册

## 编译

```sh
colcon build --merge-install
```

## 安装

```sh
source install/setup.zsh
```

## 编译并安装

```sh
colcon build --merge-install && source install/setup.zsh
```

## 机器人urdf

```sh
ros2 launch vrx_gazebo generate_wamv.launch.py component_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/example_component_config_rgl.yaml wamv_target:=./tmp/wamv_rgl.urdf
```

Prereqs: ensure PyYAML is available for the generator:

- Debian/Ubuntu: `sudo apt-get install -y python3-yaml`
- Or via pip: `python3 -m pip install --user pyyaml`

Then generate the WAM-V URDF with the RGL config:

```sh
ros2 launch vrx_gazebo generate_wamv.launch.py component_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/example_component_config_rgl.yaml wamv_target:=./tmp/wamv_rgl.urdf
```

## 运行

```sh
ros2 launch vrx_gz tunnel_viz.launch.py config_file:=$(ros2 pkg prefix vrx_gz)/share/vrx_gz/config/water_only_wamv.yaml
```

说明：

- `launch` 配置块集中启动参数：
  - `launch.world/sim_mode/headless/paused/extra_gz_args`
  - `launch.rviz.enable` 与 `launch.rviz.config`
- 模型与自动前进参数仍写在同一文件：
  - `auto_forward.enable`：是否启用自动前进
  - `auto_forward.thrust/bias/rate/duration/start_delay`：推力、差分、频率、持续时间与启动延迟（秒）
    - 未指定时默认延迟 5s 后再推力启动，可用 `start_delay: 0.0` 取消
- `rosbag` 配置块启用 ros2 bag 录制：
  - `rosbag.enable`：是否开启录制（默认关闭）
  - `rosbag.format`：存储格式，支持 `sqlite3` / `mcap` 等 `ros2 bag` 支持的格式
  - `rosbag.start_delay`：仿真启动后延迟多少秒再开始录制
  - `rosbag.topics`：需要录制的 topic 列表
- 如需临时调整，仍可在命令行覆盖单个参数（例如 `world:=...`）。

## 数据录制

配置文件中启用 `rosbag.enable: true` 后，启动仿真时会在 `rosbag.start_delay` 秒后自动运行 `ros2 bag record`（默认为 0 秒）。

- 录制目录：`<工作目录>/bag/<启动时间>`（例如 `~/code/tunnel_ws/bag/20250517_153000`）
- 命令参数示例（由 launch 自动生成）：

```sh
ros2 bag record -o ./bag/20250517_153000 -s mcap /clock /wamv/sensors/imu/data /wamv/scan_front
```

若未配置 `topics`，则不会启动录制并在终端给出提示。

## 控制

```sh
ros2 launch vrx_gz usv_joy_teleop.py
```

IMU与点云：

- IMU 推荐订阅：`/wamv/sensors/imu/data`（已统一为链接帧 `wamv/imu_wamv_link`）
- RGL 点云：`/wamv/scan_front`、`/wamv/scan_omni`


## mola

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
