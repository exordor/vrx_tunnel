# 操作记录（tunnel 场景改造）

日期：2025-09-14

- 水面与波浪
  - `worlds/water_only.sdf`：降低 wavefield 增益 gain=0.05，增大周期 period=10，使隧道内更平稳。
- RGL 点云桥接
  - 新增 `bridges.rgl_pointcloud()`，桥接 `/scan_front`、`/scan_omni` → ROS `PointCloud2`。
  - USV 默认添加两条桥接；RViz 话题：`/wamv/scan_front`、`/wamv/scan_omni`。
- 传感器帧一致性
  - `wamv_rgl_lidar.xacro` 固定 `<frame>` 为真实链接帧（`wamv/<name>_link`）。
  - `wamv_gazebo.urdf.xacro` 关闭 `<publish_sensor_pose>`，避免实体帧 TF 噪声。
  - IMU 侧：
    - 仅桥接 legacy 话题 `/sensors/imu/imu/data`；
    - 新增 `vrx_ros/imu_frame_relay` 将 `frame_id` 改写为 `wamv/imu_wamv_link` 并转发至 `/sensors/imu/data`。
- 启动改进
  - 新增 `launch/tunnel_viz.launch.py`：一键启动仿真+RViz，支持从 YAML 注入参数。
  - `robot_state_publisher` 不再加 `frame_prefix`，避免 `wamv/wamv/...`。
- 自动前进
  - 新增 `vrx_ros/auto_forward`：恒推力直行控制（支持 thrust/bias/rate/duration）。
  - `tunnel_viz.launch.py` 支持开关与参数注入；示例 YAML：`config/water_only_wamv.yaml`。
- 其他
  - `vrx_gazebo` 包声明依赖 `python3-yaml`，并在工具缺失时给出提示。

## 快速使用

```
colcon build --merge-install && source install/setup.zsh
ros2 launch vrx_gz tunnel_viz.launch.py world:=water_only config_file:=$(ros2 pkg prefix vrx_gz)/share/vrx_gz/config/water_only_wamv.yaml
```

- 开启自动前进（命令行覆盖）：
```
ros2 launch vrx_gz tunnel_viz.launch.py world:=water_only auto_forward:=True auto_forward_thrust:=400.0 auto_forward_duration:=20.0
```

- RViz 话题：
  - IMU：`/wamv/sensors/imu/data`
  - 点云：`/wamv/scan_front`、`/wamv/scan_omni`
