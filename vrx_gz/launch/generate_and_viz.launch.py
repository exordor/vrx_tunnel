#!/usr/bin/env python3
# Generate a WAM-V URDF from YAML, then start simulation + RViz using tunnel_viz.

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, RegisterEventHandler, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def _abs(path: str):
    if not path:
        return path
    return path if os.path.isabs(path) else os.path.abspath(path)


def launch_fn(context, *args, **kwargs):
    # Inputs
    component_yaml = LaunchConfiguration('component_yaml').perform(context)
    thruster_yaml = LaunchConfiguration('thruster_yaml').perform(context)
    wamv_target = _abs(LaunchConfiguration('wamv_target').perform(context))

    world = LaunchConfiguration('world').perform(context)
    sim_mode = LaunchConfiguration('sim_mode').perform(context)
    headless = LaunchConfiguration('headless').perform(context)
    paused = LaunchConfiguration('paused').perform(context)
    extra_gz_args = LaunchConfiguration('extra_gz_args').perform(context)
    config_file = LaunchConfiguration('config_file').perform(context)
    robot = LaunchConfiguration('robot').perform(context)
    rviz = LaunchConfiguration('rviz').perform(context)
    rviz_config = LaunchConfiguration('rviz_config').perform(context)

    # Defaults for inputs
    if not component_yaml:
        component_yaml = os.path.join(get_package_share_directory('vrx_gazebo'),
                                      'config', 'wamv_config', 'component_config_rgl.yaml')
    if not thruster_yaml:
        thruster_yaml = os.path.join(get_package_share_directory('vrx_gazebo'),
                                     'config', 'wamv_config', 'thruster_config_mini.yaml')
    if not config_file:
        # Prefer the mini scenario with 40m water-only world if present
        cfg1 = os.path.join(get_package_share_directory('vrx_gz'), 'config', 'water_only_wamv_40_mini.yaml')
        cfg2 = os.path.join(get_package_share_directory('vrx_gz'), 'config', 'water_only_wamv.yaml')
        config_file = cfg1 if os.path.exists(cfg1) else cfg2

    # Resolve share directories needed by the generator
    components_dir = os.path.join(get_package_share_directory('wamv_gazebo'), 'urdf', 'components')
    thrusters_dir = os.path.join(get_package_share_directory('wamv_description'), 'urdf', 'thrusters')
    wamv_gazebo = os.path.join(get_package_share_directory('wamv_gazebo'), 'urdf', 'wamv_gazebo.urdf.xacro')

    # Ensure target directory exists
    os.makedirs(os.path.dirname(wamv_target), exist_ok=True)

    # Step 1: run generator (short-lived process)
    generate_node = Node(
        package='vrx_gazebo',
        executable='generate_wamv.py',
        output='screen',
        parameters=[
            {'wamv_locked': False},
            {'component_yaml': component_yaml},
            {'thruster_yaml': thruster_yaml},
            {'wamv_target': wamv_target},
            {'components_dir': components_dir},
            {'thrusters_dir': thrusters_dir},
            {'wamv_gazebo': wamv_gazebo},
        ],
    )

    # Step 2: after generator exits, start tunnel_viz using the produced URDF
    tunnel_viz_path = os.path.join(get_package_share_directory('vrx_gz'), 'launch', 'tunnel_viz.launch.py')
    start_viz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(tunnel_viz_path),
        launch_arguments={
            'world': world,
            'sim_mode': sim_mode,
            'headless': headless,
            'paused': paused,
            'extra_gz_args': extra_gz_args,
            'config_file': config_file,
            'robot': robot,
            'rviz': rviz,
            'rviz_config': rviz_config,
            # Critical: override URDF used by models in the YAML
            'urdf': wamv_target,
        }.items()
    )

    on_done = RegisterEventHandler(
        OnProcessExit(
            target_action=generate_node,
            on_exit=[start_viz]
        )
    )

    return [generate_node, on_done]


def generate_launch_description():
    return LaunchDescription([
        # Generation inputs
        DeclareLaunchArgument('component_yaml', default_value='', description='Component YAML path'),
        DeclareLaunchArgument('thruster_yaml', default_value='', description='Thruster YAML path'),
        DeclareLaunchArgument('wamv_target', default_value=os.path.join(os.getcwd(), 'tmp', 'wamv_rgl.urdf'), description='Target URDF output path'),
        # Simulation inputs
        DeclareLaunchArgument('world', default_value='water_only'),
        DeclareLaunchArgument('sim_mode', default_value='full'),
        DeclareLaunchArgument('headless', default_value='False'),
        DeclareLaunchArgument('paused', default_value='False'),
        DeclareLaunchArgument('extra_gz_args', default_value=''),
        DeclareLaunchArgument('config_file', default_value=''),
        DeclareLaunchArgument('robot', default_value=''),
        DeclareLaunchArgument('rviz', default_value='True'),
        DeclareLaunchArgument('rviz_config', default_value=''),
        OpaqueFunction(function=launch_fn),
    ])
