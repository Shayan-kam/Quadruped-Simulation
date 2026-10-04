import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Read the URDF file directly — no shell escaping issues
    urdf_path = os.path.expanduser('~/quadruped_sim/quadruped.urdf')
    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        )
    ])
