import os
from launch import LaunchDescription
from launch.actions import OpaqueFunction, IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.launch_description_sources import load_python_launch_file_as_module
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
import launch_ros
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node, SetParameter
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    
    robot_ip = DeclareLaunchArgument(
        "robot_ip",
        default_value="192.168.106.99",
        description="Robot IP",
    )

    use_gripper = DeclareLaunchArgument(
        "use_gripper",
        default_value="true",
        description="Use gripper",
    )

    use_fake_hardware = DeclareLaunchArgument(
        "use_fake_hardware",
        default_value="true",
        description="Use fake hardware",
    )

    # set up controller manager for Franka Robotics Panda arm under namespace panda
    moveit_config = (
            MoveItConfigsBuilder(robot_name="panda", package_name="franka_robotiq_moveit_config")
            .robot_description(file_path=get_package_share_directory("franka_robotiq_description") + "/urdf/robot.urdf.xacro",
                mappings={
                    "robot_ip": LaunchConfiguration("robot_ip"),
                    "robotiq_gripper": LaunchConfiguration("use_gripper"),
                    "use_fake_hardware": LaunchConfiguration("use_fake_hardware"),
                    })
            .robot_description_semantic("config/panda.srdf.xacro")
            .trajectory_execution("config/moveit_controllers.yaml")
            .to_moveit_configs()
            )

    panda_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            moveit_config.robot_description,
            os.path.join(get_package_share_directory("franka_robotiq_moveit_config"), "config", "panda_controllers.yaml"),
            ],
        output="both",
        namespace="panda",
        condition=UnlessCondition(LaunchConfiguration('use_fake_hardware'))
    )

    panda_control_node_mj = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            moveit_config.robot_description,
            os.path.join(get_package_share_directory("franka_robotiq_moveit_config"), "config", "panda_controllers_mujoco.yaml"),
            ],
        output="both",
        namespace="panda",
        condition=IfCondition(LaunchConfiguration('use_fake_hardware'))
    )

    # set up controller manager for robotiq gripper under namespace robotiq
    robotiq_xacro = os.path.join(
            get_package_share_directory("robotiq_description"),
            "urdf",
            "robotiq_2f_85_gripper.urdf.xacro",
            )

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            robotiq_xacro,
            " ",
            "use_fake_hardware:=",
            LaunchConfiguration('use_fake_hardware'),
        ]
    )

    robotiq_description_param = {
        "robot_description": launch_ros.parameter_descriptions.ParameterValue(
            robot_description_content, value_type=str
        )
    }

    robotiq_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robotiq_description_param,
            os.path.join(get_package_share_directory("franka_robotiq_moveit_config"), "config", "robotiq_controllers.yaml",)
            ],
        output="both",
        namespace="robotiq",
        condition=UnlessCondition(LaunchConfiguration('use_fake_hardware'))
    )

    robotiq_control_node_mj = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robotiq_description_param,
            os.path.join(get_package_share_directory("franka_robotiq_moveit_config"), "config", "robotiq_controllers_mujoco.yaml",)
            ],
        output="both",
        namespace="robotiq",
        condition=IfCondition(LaunchConfiguration('use_fake_hardware'))
    )

    load_panda_controllers = []
    for controller in [                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        'joint_state_broadcaster',                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
        'joint_trajectory_controller'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        #'joint_impedance_example_controller',                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
        #'gravity_compensation_example_controller',                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
    ]:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
        load_panda_controllers += [                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
            ExecuteProcess(                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                cmd=["ros2 run controller_manager spawner {} -c /panda/controller_manager".format(controller)],                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                shell=True,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                output="screen",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
            )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        ]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
    load_robotiq_controllers = []                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
    robotiq_controllers = ['robotiq_gripper_controller','robotiq_state_broadcaster', 'robotiq_activation_controller']                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    for controller in robotiq_controllers:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
        if controller == 'robotiq_activation_controller':                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
            load_robotiq_controllers += [                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
                ExecuteProcess(                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                    cmd=["ros2 run controller_manager spawner {} -c /robotiq/controller_manager".format(controller)],                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
                    shell=True,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                    output="screen",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
                    condition=UnlessCondition(LaunchConfiguration('use_fake_hardware'))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
                )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
            ]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        else:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                

            load_robotiq_controllers += [
                ExecuteProcess(
                    cmd=["ros2 run controller_manager spawner {} -c /robotiq/controller_manager".format(controller)],
                    shell=True,
                    output="screen",
                )
            ]

    return LaunchDescription(
        [
            robot_ip, 
            use_gripper,
            use_fake_hardware,
            panda_control_node,
            robotiq_control_node,
        ]
        + load_panda_controllers
        + load_robotiq_controllers
        )
