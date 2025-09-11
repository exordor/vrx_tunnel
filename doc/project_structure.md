# VRX 仿真项目结构梳理（Gazebo Harmonic + ROS 2 Jazzy）

本文档概述当前工作空间的目录结构、关键包职责、启动方式与构建运行方法，便于快速上手与协作。

## 概览

- 工作空间根目录包含由 `colcon build` 生成的 `build/`、`install/`、`log/`，以及源码目录 `src/`。
- VRX 仿真源码位于 `src/vrx_tunnel/`，其中包含 Gazebo 端、ROS 端与模型资源等多个包。
- 推荐环境：Gazebo Harmonic 与 ROS 2 Jazzy（详见 `src/vrx_tunnel/README.md`）。

## 顶层目录

- `src/`: 源码根目录。
- `build/`: 构建中间产物（自动生成）。
- `install/`: 安装与可执行入口（自动生成）。
- `log/`: 构建与运行日志（自动生成）。
- `.vscode/`: VS Code 项目配置（C/C++ 索引、编译器配置等）。

> 常规开发仅需修改 `src/` 下内容；`build/install/log` 均由 `colcon` 生成，无需手改。

## `src/vrx_tunnel` 结构

- `README.md`: VRX 项目介绍与文档导航。
- `vrx_gz/`: Gazebo 端（任务世界、仿真插件、启动文件等）。
- `vrx_ros/`: ROS 2 端（工具节点、TF/桥接相关资源）。
- `vrx_urdf/`: 机器人与竞赛相关模型、URDF/Xacro、生成脚本与配置。
- `docker/`: Dockerfile 与 `docker-compose.yml`，用于容器化开发/构建。
- `images/`: 文档配图。

### 核心包说明

1) `vrx_gz`（Gazebo 仿真端）

- 作用：提供 Gazebo 世界（SDF）、海浪/浮力/计分等 C++ 插件，以及统一的启动流程。
- 关键文件：
  - 构建与包定义：`src/vrx_tunnel/vrx_gz/CMakeLists.txt`，`src/vrx_tunnel/vrx_gz/package.xml`
  - 启动：`src/vrx_tunnel/vrx_gz/launch/competition.launch.py`
  - 世界与模型：`src/vrx_tunnel/vrx_gz/worlds/*.sdf`，`src/vrx_tunnel/vrx_gz/models/**`
- 典型插件（在 `CMakeLists.txt` 中可见）：海浪 `Waves`、多面体浮力阻力 `PolyhedraBuoyancyDrag`、各任务计分插件（Stationkeeping/Wayfinding/Acoustic 等）。

2) `vrx_ros`（ROS 2 工具节点）

- 作用：ROS 侧工具与支撑（TF 广播、相机光学坐标发布等），与 `ros_gz` 桥协同。
- 关键文件：
  - 构建与包定义：`src/vrx_tunnel/vrx_ros/CMakeLists.txt`，`src/vrx_tunnel/vrx_ros/package.xml`
  - 源码：`src/vrx_tunnel/vrx_ros/src/optical_frame_publisher.cc`，`src/vrx_tunnel/vrx_ros/src/pose_tf_broadcaster.cc`
  - 启动：`src/vrx_tunnel/vrx_ros/launch/monitor_sim.py`

3) `vrx_urdf`（模型与描述）

- 子包 `vrx_gazebo`：VRX 模型、配置、生成脚本（例如 `scripts/generate_wamv.py`）。
  - `src/vrx_tunnel/vrx_urdf/vrx_gazebo/CMakeLists.txt`
  - `src/vrx_tunnel/vrx_urdf/vrx_gazebo/package.xml`
- 子包 `wamv_gazebo`：WAM-V 在 Gazebo 的模板与示例。
  - `src/vrx_tunnel/vrx_urdf/wamv_gazebo/package.xml`
- 子包 `wamv_description`：WAM-V 的 URDF/Xacro 与网格资源。
- 资源目录：`models/`、`config/`、`launch/`、`urdf/` 等。

## 典型启动路径（competition.launch.py）

入口：`src/vrx_tunnel/vrx_gz/launch/competition.launch.py`

- 主要参数：
  - `world`: 世界名（默认 `sydney_regatta`）。
  - `sim_mode`: `full`（仿真+桥接）、`sim`（仅仿真）、`bridge`（仅桥接）。
  - `bridge_competition_topics`: 是否桥接竞赛相关话题（默认 `True`）。
  - `config_file`: 可选 YAML 配置，批量定义要生成/加载的模型。
  - `robot`: 指定从配置中选取的机器人名称（可选）。
  - `headless`: 无 GUI 运行（`True/False`）。
  - `urdf`: 自定义 WAM-V URDF（可选）。
  - `paused`: 启动时暂停仿真。
  - `competition_mode`: 竞赛模式（禁用调试话题）。
  - `extra_gz_args`: 传递给 `gz sim` 的附加参数。
  - `name`/`model`: 直接指定生成的机器人名与模型类型（未给 `config_file` 时使用）。
- 执行流程（简述）：
  1. 解析参数，若提供 `config_file`，则从 YAML 读取并构造 `Model` 列表，否则按 `name`/`model` 构造默认模型。
  2. 启动 `gz` 仿真进程（可传 `headless`/`paused`/`extra_gz_args`）。
  3. 按世界与模式 `spawn` 机器人模型。
  4. 若 `sim_mode` 为 `full/bridge` 且开启 `bridge_competition_topics`，启动 ROS–Gazebo 桥接。

## 构建与运行

1) 构建

```bash
colcon build
```

2) 进入环境

```bash
source install/setup.bash
```

3) 启动仿真（示例）

```bash
# 默认世界，完整模式（含桥接）
ros2 launch vrx_gz competition.launch.py

# 指定世界与模式
ros2 launch vrx_gz competition.launch.py \
  world:=sydney_regatta sim_mode:=full headless:=False

# 使用自定义 URDF 或批量配置文件
ros2 launch vrx_gz competition.launch.py urdf:=/path/to/wamv.urdf
ros2 launch vrx_gz competition.launch.py config_file:=/path/to/config.yaml
```

## 依赖与版本（摘要）

- Gazebo 库（在 `vrx_gz/CMakeLists.txt` 可见）：
  - `gz-sim8`、`gz-common5`（graphics）
  - `gz-math7`、`gz-msgs10`、`gz-transport13`
  - `gz-plugin2`、`gz-rendering8`、`gz-sensors8`
  - `sdformat14`、`Eigen3`
- ROS 2 依赖（在 `vrx_ros/package.xml` 可见）：
  - `rclcpp`、`geometry_msgs`、`sensor_msgs`、`rosgraph_msgs`
  - `tf2`、`tf2_ros`、`ros_gz_interfaces`

> 完整依赖以各 `package.xml` 与 `CMakeLists.txt` 为准，建议按仓库 README 指引准备环境。

## 常见开发动作

- 调试模型/世界：修改 `src/vrx_tunnel/vrx_gz/worlds/*.sdf` 或 `models/**`，重启仿真验证。
- 自定义机器人：在 `vrx_urdf/` 下调整 WAM-V 组件与参数，或用 `generate_wamv.py` 生成变体。
- ROS 工具节点：在 `vrx_ros/src/*.cc` 实现新的 TF/工具节点，并通过 `launch/` 组织运行。

## 参考

- 项目总览与教程：`src/vrx_tunnel/README.md`
- 竞赛与文档：VRX Wiki / Issues（README 中提供链接）

