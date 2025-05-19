"""
Teaching Mode Module for Embodied Agent

This module implements the teaching mode functionality that allows users to
manually guide the robot through movements, which can then be replicated automatically.

"""

import time
import json
import os
import numpy as np
from typing import List, Dict, Any, Optional

# Assuming hardware control is available
try:
    from pymycobot.mycobot import MyCobot
    HARDWARE_AVAILABLE = True
except ImportError:
    print("Warning: MyCobot library not available. Running in simulation mode.")
    HARDWARE_AVAILABLE = False

# Import necessary functions
from action.robot_control import back_to_zero, release_servos
from config import PATHS

# Define path for storing teaching recordings
TEACHING_DATA_DIR = os.path.join(PATHS["temp_dir"], "teachings")

# Create directory if it doesn't exist
if not os.path.exists(TEACHING_DATA_DIR):
    os.makedirs(TEACHING_DATA_DIR)

# Initialize robot connection if available
if HARDWARE_AVAILABLE:
    try:
        robot = MyCobot("/dev/ttyAMA0", 1000000)
    except Exception as e:
        print(f"Error connecting to robot: {e}")
        HARDWARE_AVAILABLE = False
else:
    robot = None


def teaching_mode() -> str:
    """
    Enter teaching mode to record and then replay manual movements.
    
    This function:
    1. Releases all servos to allow manual movement
    2. Records the positions at regular intervals
    3. Replays the recorded movement
    
    Returns:
        Message describing the outcome
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Teaching mode: recording and replaying movements")
        return "Simulation: Teaching mode completed successfully"
    
    try:
        positions = []
        recording_time = 10  # seconds to record
        sample_rate = 5      # positions per second
        
        print("\n=== TEACHING MODE ===")
        print("I'll release the servos so you can move me manually.")
        print(f"I'll record your movements for {recording_time} seconds.")
        print("After recording, I'll replay the movement.")
        print("Press Enter to start...")
        input()
        
        # Release all servos for manual movement
        release_servos()
        print("Servos released. You can now move the arm manually.")
        print("Recording started...")
        
        # Record positions at regular intervals
        start_time = time.time()
        while time.time() - start_time < recording_time:
            # Get current angles
            angles = robot.get_angles()
            if angles:
                positions.append(angles)
                print(".", end="", flush=True)
            time.sleep(1 / sample_rate)
        
        print("\nRecording complete.")
        print(f"Recorded {len(positions)} positions.")
        
        # Save the recording
        recording_id = int(time.time())
        recording_path = os.path.join(TEACHING_DATA_DIR, f"teaching_{recording_id}.json")
        with open(recording_path, 'w') as f:
            json.dump(positions, f)
        
        print("Movement saved. Ready to replay.")
        print("Press Enter to replay...")
        input()
        
        # Replay the recorded movement
        print("Replaying recorded movement...")
        replay_teaching(recording_id)
        
        return f"Teaching completed and saved as ID: {recording_id}"
    
    except Exception as e:
        print(f"Error in teaching mode: {e}")
        # Try to restore control
        try:
            if robot:
                robot.power_on()
                time.sleep(1)
                back_to_zero()
        except:
            pass
        
        return "Teaching mode encountered an error"


def replay_teaching(teaching_id: Optional[int] = None, filepath: Optional[str] = None) -> None:
    """
    Replay a previously recorded teaching movement.
    
    Args:
        teaching_id: ID of the teaching to replay
        filepath: Direct path to the teaching file (alternative to teaching_id)
    """
    if not HARDWARE_AVAILABLE:
        print(f"[SIM] Replaying teaching ID: {teaching_id}")
        return
    
    try:
        # Determine the file path
        if filepath:
            recording_path = filepath
        elif teaching_id:
            recording_path = os.path.join(TEACHING_DATA_DIR, f"teaching_{teaching_id}.json")
        else:
            # If no specific teaching specified, use the most recent one
            teaching_files = sorted([f for f in os.listdir(TEACHING_DATA_DIR) if f.startswith('teaching_')])
            if teaching_files:
                recording_path = os.path.join(TEACHING_DATA_DIR, teaching_files[-1])
            else:
                print("No teaching recordings found.")
                return
        
        # Check if file exists
        if not os.path.exists(recording_path):
            print(f"Teaching file not found: {recording_path}")
            return
        
        # Load the recorded positions
        with open(recording_path, 'r') as f:
            positions = json.load(f)
        
        print(f"Loaded {len(positions)} positions from recording.")
        
        # Make sure the robot is powered on
        robot.power_on()
        time.sleep(1)
        
        # Replay the positions
        print("Replaying movement...")
        for i, angles in enumerate(positions):
            robot.send_angles(angles, 80)  # Higher speed for smooth replay
            # Calculate appropriate delay for smooth motion
            # Shorter delays for smoother playback
            delay = 0.05 if i % 3 == 0 else 0
            time.sleep(delay)
        
        print("Replay complete.")
        
    except Exception as e:
        print(f"Error replaying teaching: {e}")


def list_teachings() -> List[Dict[str, Any]]:
    """
    List all saved teaching recordings.
    
    Returns:
        List of dictionaries with teaching metadata
    """
    try:
        teachings = []
        
        if not os.path.exists(TEACHING_DATA_DIR):
            print("Teaching directory does not exist.")
            return teachings
        
        # Get all teaching files
        teaching_files = [f for f in os.listdir(TEACHING_DATA_DIR) if f.startswith('teaching_') and f.endswith('.json')]
        
        for file in teaching_files:
            try:
                # Extract ID from filename
                teaching_id = int(file.split('_')[1].split('.')[0])
                # Get file modification time
                file_path = os.path.join(TEACHING_DATA_DIR, file)
                mod_time = os.path.getmtime(file_path)
                # Get file size
                size = os.path.getsize(file_path)
                
                teachings.append({
                    'id': teaching_id,
                    'filename': file,
                    'datetime': time.ctime(mod_time),
                    'size_kb': round(size / 1024, 2)
                })
            except Exception as e:
                print(f"Error processing teaching file {file}: {e}")
        
        # Sort by timestamp (newest first)
        teachings.sort(key=lambda x: x['id'], reverse=True)
        
        return teachings
    
    except Exception as e:
        print(f"Error listing teachings: {e}")
        return []


def delete_teaching(teaching_id: int) -> bool:
    """
    Delete a saved teaching recording.
    
    Args:
        teaching_id: ID of the teaching to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        file_path = os.path.join(TEACHING_DATA_DIR, f"teaching_{teaching_id}.json")
        
        if not os.path.exists(file_path):
            print(f"Teaching file not found: {file_path}")
            return False
        
        os.remove(file_path)
        print(f"Teaching {teaching_id} deleted.")
        return True
        
    except Exception as e:
        print(f"Error deleting teaching: {e}")
        return False
