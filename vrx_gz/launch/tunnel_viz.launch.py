#!/usr/bin/env python3
# Standalone launch: run simulation and RViz with the tunnel RViz config.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, SetLaunchConfiguration, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import os
from datetime import datetime
import io
from ament_index_python.packages import get_package_share_directory
import yaml

import vrx_gz.launch
from vrx_gz.model import Model


def _resolve_rviz_config(default_path: str):
    # Prefer explicit arg; else try package share config; else fall back to provided default path
    try:
        share_cfg = os.path.join(get_package_share_directory('vrx_gz'), 'config', 'tunnel.rviz')
        if os.path.exists(share_cfg):
            return share_cfg
    except Exception:
        pass
    return default_path


def launch_fn(context, *args, **kwargs):
    def _as_bool(value, default):
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            norm = value.strip().lower()
            if norm in ('1', 'true', 'yes', 'on'):
                return True
            if norm in ('0', 'false', 'no', 'off'):
                return False
        return default

    def _config_sections(cfg):
        sections = []
        if isinstance(cfg, dict):
            for key in ('launch', 'simulation', 'sim', 'settings'):
                subsection = cfg.get(key)
                if isinstance(subsection, dict):
                    sections.append(subsection)
            sections.append(cfg)
        return sections

    def _lookup(sections, keys):
        for section in sections:
            for key in keys:
                if key in section and section[key] is not None:
                    return section[key]
        return None

    world = LaunchConfiguration('world').perform(context)
    sim_mode = LaunchConfiguration('sim_mode').perform(context)
    headless = _as_bool(LaunchConfiguration('headless').perform(context), False)
    paused = _as_bool(LaunchConfiguration('paused').perform(context), False)
    extra_gz_args = LaunchConfiguration('extra_gz_args').perform(context)

    robot_name = LaunchConfiguration('name').perform(context)
    model_type = LaunchConfiguration('model').perform(context)
    robot_urdf = LaunchConfiguration('urdf').perform(context)
    config_file = LaunchConfiguration('config_file').perform(context)
    robot = LaunchConfiguration('robot').perform(context)

    rviz_enable = _as_bool(LaunchConfiguration('rviz').perform(context), True)
    rviz_config = LaunchConfiguration('rviz_config').perform(context)

    config_data = {}
    config_text = ''
    if config_file:
        with open(config_file, 'r') as stream:
            config_text = stream.read()
        try:
            loaded = yaml.safe_load(config_text)
            config_data = loaded if loaded is not None else {}
        except Exception:
            config_data = {}

    def _expand_path(p: str) -> str:
        # Expand ~ and environment variables, then make absolute if still relative (cwd-based)
        if not isinstance(p, str) or p.strip() == '':
            return p
        p2 = os.path.expandvars(os.path.expanduser(p))
        if not os.path.isabs(p2):
            p2 = os.path.abspath(os.path.join(os.getcwd(), p2))
        return p2

    def _rewrite_urdf_fields(obj):
        # Recursively walk dict/list and expand 'urdf' string fields
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                if k == 'urdf' and isinstance(v, str):
                    new_obj[k] = _expand_path(v)
                else:
                    new_obj[k] = _rewrite_urdf_fields(v)
            return new_obj
        elif isinstance(obj, list):
            return [_rewrite_urdf_fields(v) for v in obj]
        else:
            return obj

    if isinstance(config_data, (dict, list)):
        config_data = _rewrite_urdf_fields(config_data)

    sections = _config_sections(config_data)

    value = _lookup(sections, ['world', 'world_name'])
    if value is not None:
        world = str(value)

    value = _lookup(sections, ['sim_mode', 'mode'])
    if value is not None:
        sim_mode = str(value)

    value = _lookup(sections, ['headless'])
    if value is not None:
        headless = _as_bool(value, headless)

    value = _lookup(sections, ['paused'])
    if value is not None:
        paused = _as_bool(value, paused)

    value = _lookup(sections, ['extra_gz_args', 'gz_args', 'gazebo_args'])
    if value is not None:
        extra_gz_args = str(value)

    value = _lookup(sections, ['robot', 'selected_robot'])
    if value is not None:
        robot = str(value)

    rviz_value = _lookup(sections, ['rviz'])
    if isinstance(rviz_value, dict):
        rviz_enable = _as_bool(rviz_value.get('enable', rviz_value.get('enabled', rviz_enable)), rviz_enable)
        cfg_path = rviz_value.get('config', rviz_value.get('file'))
        if cfg_path is not None:
            rviz_config = str(cfg_path)
    elif rviz_value is not None:
        rviz_enable = _as_bool(rviz_value, rviz_enable)

    alt = _lookup(sections, ['rviz_enable', 'use_rviz'])
    if alt is not None:
        rviz_enable = _as_bool(alt, rviz_enable)

    alt_cfg = _lookup(sections, ['rviz_config', 'rviz_file'])
    if alt_cfg is not None:
        rviz_config = str(alt_cfg)

    processes = []

    # Simulation (gz sim + GUI based on headless)
    world_base, _ = os.path.splitext(world)
    processes.extend(vrx_gz.launch.simulation(world_base, headless, paused, extra_gz_args))
    world_base = os.path.basename(world_base)

    # Models (YAML config or single model)
    models = []
    bag_process = None
    if config_file:
        models_source = config_text
        if isinstance(config_data, dict) and 'models' in config_data:
            models_source = yaml.safe_dump(config_data['models'])
        loaded_models = Model.FromConfig(io.StringIO(models_source)) if models_source else None
        if isinstance(loaded_models, list):
            models = loaded_models
        elif loaded_models:
            models = [loaded_models]

        # Load optional auxiliary settings from YAML (e.g., auto_forward / rosbag)
        af_cfg = _lookup(sections, ['auto_forward'])
        if isinstance(af_cfg, dict):
            enable = str(af_cfg.get('enable', False))
            thrust = str(af_cfg.get('thrust', 15.0))
            bias = str(af_cfg.get('bias', 0.0))
            rate = str(af_cfg.get('rate', 10.0))
            duration = str(af_cfg.get('duration', 0.0))
            processes.extend([
                SetLaunchConfiguration('auto_forward', enable),
                SetLaunchConfiguration('auto_forward_thrust', thrust),
                SetLaunchConfiguration('auto_forward_bias', bias),
                SetLaunchConfiguration('auto_forward_rate', rate),
                SetLaunchConfiguration('auto_forward_duration', duration),
                SetLaunchConfiguration('auto_forward_delay', str(af_cfg.get('start_delay', 5.0))),
            ])

        bag_cfg = _lookup(sections, ['rosbag', 'bag_record'])
        if isinstance(bag_cfg, dict):
            bag_enable = _as_bool(bag_cfg.get('enable', False), False)
            topics = bag_cfg.get('topics', []) if bag_enable else []
            if bag_enable and isinstance(topics, list) and len(topics) > 0:
                topics = [str(t) for t in topics if isinstance(t, str) and t]
                if topics:
                    storage = str(bag_cfg.get('format', bag_cfg.get('storage', 'mcap')))
                    base_dir = os.path.join(os.getcwd(), 'bag')
                    os.makedirs(base_dir, exist_ok=True)
                    bag_name = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_path = os.path.join(base_dir, bag_name)
                    record_cmd = ['ros2', 'bag', 'record', '-o', output_path, '-s', storage]
                    record_cmd.extend(topics)
                    delay = bag_cfg.get('start_delay', bag_cfg.get('delay', 0.0))
                    try:
                        delay_val = float(delay)
                    except Exception:
                        delay_val = 0.0
                    bag_action = ExecuteProcess(
                        cmd=record_cmd,
                        name='rosbag_record',
                        output='screen',
                    )
                    if delay_val > 0.0:
                        bag_process = TimerAction(period=delay_val, actions=[bag_action])
                    else:
                        bag_process = bag_action
            elif bag_enable:
                print('[tunnel_viz.launch] rosbag enabled but no topics configured; skipping bag record.')

        if robot_urdf and robot_urdf != '':
            target_models = models if models else []
            if robot and robot != '':
                target_models = [m for m in models if m.model_name == robot]
            for m in target_models:
                m.set_urdf(robot_urdf)
    else:
        m = Model(robot_name, model_type, [-532, 162, 0, 0, 0, 1])
        if robot_urdf and robot_urdf != '':
            m.set_urdf(robot_urdf)
        models.append(m)

    processes.extend(vrx_gz.launch.spawn(sim_mode, world_base, models, robot))

    if bag_process is not None:
        processes.append(bag_process)

    # RViz (optional)
    if rviz_enable:
        cfg = rviz_config
        if not cfg:
            # Try to use a packaged config if present
            cfg = _resolve_rviz_config(os.path.join(os.getcwd(), 'tunnel.rviz'))
        rviz_args = []
        if cfg and os.path.exists(cfg):
            rviz_args.extend(['-d', cfg])
        processes.append(Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=rviz_args,
            parameters=[{'use_sim_time': True}],
        ))

    return processes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='water_only', description='World name or path'),
        DeclareLaunchArgument('sim_mode', default_value='full', description='full|sim|bridge'),
        DeclareLaunchArgument('headless', default_value='False'),
        DeclareLaunchArgument('paused', default_value='False'),
        DeclareLaunchArgument('extra_gz_args', default_value=''),
        DeclareLaunchArgument('name', default_value='wamv'),
        DeclareLaunchArgument('model', default_value='wam-v'),
        DeclareLaunchArgument('urdf', default_value=''),
        DeclareLaunchArgument('config_file', default_value='', description='YAML config for model/components'),
        DeclareLaunchArgument('robot', default_value=''),
        # RViz controls
        DeclareLaunchArgument('rviz', default_value='True', description='Start RViz2'),
        DeclareLaunchArgument('rviz_config', default_value='', description='Path to RViz config (.rviz)'),
        # Auto forward options (can be overridden by YAML via SetLaunchConfiguration)
        DeclareLaunchArgument('auto_forward', default_value='False', description='Enable auto-forward controller'),
        DeclareLaunchArgument('auto_forward_thrust', default_value='15.0'),
        DeclareLaunchArgument('auto_forward_bias', default_value='0.0'),
        DeclareLaunchArgument('auto_forward_rate', default_value='10.0'),
        DeclareLaunchArgument('auto_forward_duration', default_value='0.0'),
        DeclareLaunchArgument('auto_forward_delay', default_value='5.0'),
        OpaqueFunction(function=launch_fn),
    ])
