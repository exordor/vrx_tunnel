#!/usr/bin/env python3
# Standalone launch: run simulation and RViz with the tunnel RViz config.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, SetLaunchConfiguration
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import os
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
    world = LaunchConfiguration('world').perform(context)
    sim_mode = LaunchConfiguration('sim_mode').perform(context)
    headless = LaunchConfiguration('headless').perform(context).lower() == 'true'
    paused = LaunchConfiguration('paused').perform(context).lower() == 'true'
    extra_gz_args = LaunchConfiguration('extra_gz_args').perform(context)

    robot_name = LaunchConfiguration('name').perform(context)
    model_type = LaunchConfiguration('model').perform(context)
    robot_urdf = LaunchConfiguration('urdf').perform(context)
    config_file = LaunchConfiguration('config_file').perform(context)
    robot = LaunchConfiguration('robot').perform(context)

    rviz = LaunchConfiguration('rviz').perform(context)
    rviz_config = LaunchConfiguration('rviz_config').perform(context)

    processes = []

    # Simulation (gz sim + GUI based on headless)
    world_base, _ = os.path.splitext(world)
    processes.extend(vrx_gz.launch.simulation(world_base, headless, paused, extra_gz_args))
    world_base = os.path.basename(world_base)

    # Models (YAML config or single model)
    models = []
    if config_file:
        with open(config_file, 'r') as stream:
            models = Model.FromConfig(stream)
        # Load optional auxiliary settings from YAML (e.g., auto_forward)
        try:
            with open(config_file, 'r') as s2:
                cfg = yaml.safe_load(s2) or {}
            af = cfg.get('auto_forward', {}) if isinstance(cfg, dict) else {}
            if isinstance(af, dict):
                enable = str(af.get('enable', False))
                thrust = str(af.get('thrust', 15.0))
                bias = str(af.get('bias', 0.0))
                rate = str(af.get('rate', 10.0))
                duration = str(af.get('duration', 0.0))
                processes.extend([
                    SetLaunchConfiguration('auto_forward', enable),
                    SetLaunchConfiguration('auto_forward_thrust', thrust),
                    SetLaunchConfiguration('auto_forward_bias', bias),
                    SetLaunchConfiguration('auto_forward_rate', rate),
                    SetLaunchConfiguration('auto_forward_duration', duration),
                ])
        except Exception:
            pass
        if robot_urdf and robot_urdf != '':
            if robot and robot != '':
                for m in models:
                    if m.model_name == robot:
                        m.set_urdf(robot_urdf)
            else:
                for m in models:
                    m.set_urdf(robot_urdf)
    else:
        m = Model(robot_name, model_type, [-532, 162, 0, 0, 0, 1])
        if robot_urdf and robot_urdf != '':
            m.set_urdf(robot_urdf)
        models.append(m)

    processes.extend(vrx_gz.launch.spawn(sim_mode, world_base, models, robot))

    # RViz (optional)
    if rviz.lower() == 'true':
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
        OpaqueFunction(function=launch_fn),
    ])
