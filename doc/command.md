# VRX-GZ 使用手册

## 编译

```
colcon build --merge-install
```

## 安装

```
source install/setup.zsh
```

## 机器人urdf

```
ros2 launch vrx_gazebo generate_wamv.launch.py component_yaml:=$(ros2 pkg prefix vrx_gazebo)/share/vrx_gazebo/config/wamv_config/example_component_config_rgl.yaml wamv_target:=./tmp/wamv_rgl.urdf
```


## 运行

```
ros2 launch vrx_gz competition.launch.py world:=water_only sim_mode:=full headless:=False config_file:=$(ros2 pkg prefix vrx_gz)/share/vrx_gz/config/water_only_wamv.yaml
```

## 控制

```
ros2 launch vrx_gz usv_joy_teleop.py
```

