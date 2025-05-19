"""
Robot Control Module for Embodied Agent

This module handles the direct control of the 6-DOF robotic arm,
including basic movements, joint control, and predefined motion sequences.

"""

import time
import numpy as np
from typing import Tuple, List, Optional, Dict, Any

# Assuming the MyCobot 280 Pi library is available
try:
    from pymycobot.mycobot import MyCobot
    HARDWARE_AVAILABLE = True
except ImportError:
    print("Warning: MyCobot library not available. Running in simulation mode.")
    HARDWARE_AVAILABLE = False

# Import system configuration
from config import ROBOT_CONFIG

# Initialize the robot connection
# For actual hardware, replace with your serial port
if HARDWARE_AVAILABLE:
    try:
        robot = MyCobot("/dev/ttyAMA0", 1000000)
        print("Robot connection established.")
    except Exception as e:
        print(f"Error connecting to robot: {e}")
        HARDWARE_AVAILABLE = False
else:
    robot = None


def back_to_zero() -> None:
    """
    Return all joints to their zero position (default pose).
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Moving all joints to zero position")
        return
    
    try:
        # Slow movement to zero position for safety
        robot.set_speed(ROBOT_CONFIG["default_speed"])
        # Set all 6 joints to their zero positions
        robot.send_angles([0, 0, 0, 0, 0, 0], ROBOT_CONFIG["default_speed"])
        # Wait for movement to complete
        time.sleep(2)
        print("Robot returned to zero position.")
    except Exception as e:
        print(f"Error returning to zero: {e}")


def release_servos() -> None:
    """
    Release all servos to allow manual manipulation of the arm.
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Releasing all servos for manual control")
        return
    
    try:
        robot.release_all_servos()
        print("All servos released. You can now move the arm manually.")
    except Exception as e:
        print(f"Error releasing servos: {e}")


def head_shake() -> None:
    """
    Perform a head shake motion (left-right movement).
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Performing head shake motion")
        return
    
    try:
        # Store current position
        current_angles = robot.get_angles()
        
        # Head shake motion (moving joint 1 left and right)
        for _ in range(2):  # Shake twice
            # Move left
            robot.send_angle(1, 30, 20)
            time.sleep(0.5)
            # Move right
            robot.send_angle(1, -30, 20)
            time.sleep(0.5)
        
        # Return to original position
        robot.send_angles(current_angles, 20)
        time.sleep(1)
        
        print("Head shake completed.")
    except Exception as e:
        print(f"Error in head shake: {e}")


def head_nod() -> None:
    """
    Perform a head nod motion (up-down movement).
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Performing head nod motion")
        return
    
    try:
        # Store current position
        current_angles = robot.get_angles()
        
        # Head nod motion (moving joint 2 up and down)
        for _ in range(2):  # Nod twice
            # Move up
            robot.send_angle(2, -20, 20)
            time.sleep(0.5)
            # Move down
            robot.send_angle(2, 20, 20)
            time.sleep(0.5)
        
        # Return to original position
        robot.send_angles(current_angles, 20)
        time.sleep(1)
        
        print("Head nod completed.")
    except Exception as e:
        print(f"Error in head nod: {e}")


def head_dance() -> None:
    """
    Perform a dance motion combining multiple joint movements.
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Performing dance motion sequence")
        return
    
    try:
        # Store current position
        current_angles = robot.get_angles()
        
        # Set a faster speed for the dance
        robot.set_speed(60)
        
        # Sequence of dance moves
        # Move joint 1 (base rotation)
        robot.send_angle(1, 45, 60)
        time.sleep(0.5)
        robot.send_angle(1, -45, 60)
        time.sleep(0.5)
        
        # Move joints 2 and 3 (arm positions)
        robot.send_angle(2, 30, 60)
        time.sleep(0.3)
        robot.send_angle(3, -30, 60)
        time.sleep(0.3)
        
        # Rotate gripper (joint 6)
        robot.send_angle(6, 90, 60)
        time.sleep(0.3)
        robot.send_angle(6, -90, 60)
        time.sleep(0.3)
        
        # Return to original position
        robot.send_angles(current_angles, 40)
        time.sleep(1)
        
        print("Dance sequence completed.")
    except Exception as e:
        print(f"Error in dance sequence: {e}")


def move_to_coords(X: float, Y: float, Z: Optional[float] = None) -> None:
    """
    Move to specific XYZ coordinates.
    
    Args:
        X: X-coordinate (mm)
        Y: Y-coordinate (mm)
        Z: Z-coordinate (mm), if None, keeps current Z
    """
    if not HARDWARE_AVAILABLE:
        print(f"[SIM] Moving to coordinates X:{X}, Y:{Y}, Z:{Z if Z else 'current'}")
        return
    
    try:
        # Get current position
        current_coords = robot.get_coords()
        
        # Use current Z if not specified
        if Z is None:
            Z = current_coords[2]
        
        # First move up to safe height to avoid collisions
        safe_coords = [current_coords[0], current_coords[1], ROBOT_CONFIG["safe_height"], 
                       current_coords[3], current_coords[4], current_coords[5]]
        robot.send_coords(safe_coords, ROBOT_CONFIG["coordinate_speed"])
        time.sleep(1.5)
        
        # Then move to target XY at safe height
        target_safe_coords = [X, Y, ROBOT_CONFIG["safe_height"], 
                             current_coords[3], current_coords[4], current_coords[5]]
        robot.send_coords(target_safe_coords, ROBOT_CONFIG["coordinate_speed"])
        time.sleep(1.5)
        
        # Finally move down to target Z
        target_coords = [X, Y, Z, current_coords[3], current_coords[4], current_coords[5]]
        robot.send_coords(target_coords, ROBOT_CONFIG["coordinate_speed"])
        time.sleep(1.5)
        
        print(f"Moved to coordinates X:{X}, Y:{Y}, Z:{Z}")
    except Exception as e:
        print(f"Error moving to coordinates: {e}")


def rotate_joint(joint_num: int, angle: float) -> None:
    """
    Rotate a specific joint to a target angle.
    
    Args:
        joint_num: Joint number (1-6)
        angle: Target angle in degrees
    """
    if not HARDWARE_AVAILABLE:
        print(f"[SIM] Rotating joint {joint_num} to {angle} degrees")
        return
    
    try:
        # Validate joint number
        if joint_num < 1 or joint_num > 6:
            print(f"Invalid joint number: {joint_num}. Must be between 1-6.")
            return
            
        # Joint numbers in the library are 0-indexed
        robot.send_angle(joint_num - 1, angle, ROBOT_CONFIG["default_speed"])
        time.sleep(1)
        
        print(f"Joint {joint_num} rotated to {angle} degrees.")
    except Exception as e:
        print(f"Error rotating joint: {e}")


def move_to_overhead_view() -> None:
    """
    Move to a position suitable for taking an overhead photo.
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Moving to overhead viewing position")
        return
    
    try:
        # Predefined overhead view position
        # Typically with camera pointing straight down
        overhead_angles = [0, 30, -30, 0, 90, 0]  # Example angles
        
        robot.send_angles(overhead_angles, ROBOT_CONFIG["default_speed"])
        time.sleep(2)
        
        print("Moved to overhead viewing position.")
    except Exception as e:
        print(f"Error moving to overhead view: {e}")


def capture_overhead_image() -> str:
    """
    Take a photo from the current position (typically overhead).
    
    Returns:
        Path to the captured image file
    """
    from perception.vision import capture_image
    
    try:
        # First move to a good position for taking photos
        move_to_overhead_view()
        time.sleep(1)
        
        # Capture the image
        image_path = capture_image()
        
        return f"Image captured and saved to {image_path}"
    except Exception as e:
        print(f"Error capturing image: {e}")
        return "Failed to capture image"


def check_camera() -> None:
    """
    Display the camera feed on screen for a few seconds.
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Displaying camera feed")
        return
    
    try:
        from perception.vision import display_camera_feed
        
        # Display the camera feed for 5 seconds
        display_camera_feed(duration=5)
        
        print("Camera feed displayed.")
    except Exception as e:
        print(f"Error displaying camera feed: {e}")


def move_object(instruction: str) -> str:
    """
    Move an object based on a natural language instruction.
    
    Args:
        instruction: Natural language instruction (e.g., "Put the red cube on the blue box")
        
    Returns:
        Result message
    """
    if not HARDWARE_AVAILABLE:
        print(f"[SIM] Moving object: {instruction}")
        return "Object movement simulated"
    
    try:
        from perception.vision import locate_objects
        from agent.agent_coordinator import parse_visual_instruction
        
        # First take a photo to see the scene
        move_to_overhead_view()
        time.sleep(1)
        
        # Analyze the scene to locate objects
        scene_objects = locate_objects()
        
        # Parse the instruction to determine source and target
        movement_plan = parse_visual_instruction(instruction, scene_objects)
        
        if not movement_plan:
            return "I couldn't understand how to move objects based on your instruction."
        
        # Extract source and target positions
        source = movement_plan.get("source")
        target = movement_plan.get("target")
        
        if not source or not target:
            return "I couldn't identify the source or target objects."
        
        # Execute the movement
        # 1. Move to source position
        move_to_coords(X=source["x"], Y=source["y"], Z=source["z"] + 50)
        move_to_coords(X=source["x"], Y=source["y"], Z=source["z"] + 10)
        
        # 2. Activate vacuum pump to pick up the object
        from action.actuators import pump_on
        pump_on()
        time.sleep(1)
        
        # 3. Lift the object
        move_to_coords(X=source["x"], Y=source["y"], Z=source["z"] + 50)
        
        # 4. Move to target position
        move_to_coords(X=target["x"], Y=target["y"], Z=target["z"] + 50)
        move_to_coords(X=target["x"], Y=target["y"], Z=target["z"] + 20)
        
        # 5. Release the object
        from action.actuators import pump_off
        pump_off()
        time.sleep(1)
        
        # 6. Move away
        move_to_coords(X=target["x"], Y=target["y"], Z=target["z"] + 50)
        
        return f"Successfully moved the object as instructed."
    except Exception as e:
        print(f"Error moving object: {e}")
        return f"Error occurred during object movement: {str(e)}"


def visual_qa(query: str) -> str:
    """
    Answer a visual question about the scene.
    
    Args:
        query: The visual question to answer
        
    Returns:
        Answer to the question
    """
    try:
        from models.llm_interface import query_qwen_vl
        
        # First take a photo to see the scene
        move_to_overhead_view()
        time.sleep(1)
        
        # Capture an image of the scene
        from perception.vision import capture_image
        image_path = capture_image()
        
        # Query the multimodal LLM with the image and question
        answer = query_qwen_vl(image_path, query)
        
        return answer
    except Exception as e:
        print(f"Error in visual QA: {e}")
        return "I couldn't analyze the visual scene to answer your question."
