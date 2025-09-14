# VRX-GZ 使用手册

## 编译

```
colcon build --merge-install
```

## 安装

```
source install/setup.zsh
```

## 编译并安装

```
colcon build --merge-install && source install/setup.zsh
```

## 机器人urdf

Prereqs: ensure PyYAML is available for the generator:

- Debian/Ubuntu: `sudo apt-get install -y python3-yaml`
- Or via pip: `python3 -m pip install --user pyyaml`

Then generate the WAM-V URDF with the RGL config:

```
ros2 launch vrx_gazebo generate_wamv.launch.py component_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/example_component_config_rgl.yaml wamv_target:=./tmp/wamv_rgl.urdf
```


## 运行

```
ros2 launch vrx_gz tunnel_viz.launch.py world:=water_only sim_mode:=full headless:=False config_file:=$(ros2 pkg prefix vrx_gz)/share/vrx_gz/config/water_only_wamv.yaml
```

说明：
- 支持通过 `water_only_wamv.yaml` 注入模型与自动前进配置：
  - `auto_forward.enable`：是否启用自动前进
  - `auto_forward.thrust/bias/rate/duration`：推力、差分、频率与持续时间（秒）
- 也可在命令行覆盖：

```
ros2 launch vrx_gz tunnel_viz.launch.py world:=water_only auto_forward:=True auto_forward_thrust:=400.0 auto_forward_duration:=20.0
```

## 控制

```
ros2 launch vrx_gz usv_joy_teleop.py
```

IMU与点云：
- IMU 推荐订阅：`/wamv/sensors/imu/data`（已统一为链接帧 `wamv/imu_wamv_link`）
- RGL 点云：`/wamv/scan_front`、`/wamv/scan_omni`
