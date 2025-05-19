"""
Agent Coordinator for Embodied Robotic System

This module handles the coordination between perception and action by leveraging
large language models to interpret instructions and generate action plans.

"""

import os
import json
from typing import Dict, List, Any, Union

# Import from our own modules
from models.llm_interface import query_llm_with_history
from .prompts import SYSTEM_PROMPT
from config import DEFAULT_TEXT_MODEL

def coordinate_actions(message_history: List[Dict[str, str]], model_name: str = None) -> Dict[str, Any]:
    """
    Coordinates the agent's actions based on user instructions and system state.
    
    This function takes the conversation history and uses a large language model
    to generate an appropriate action plan consisting of functions to execute
    and a verbal response.
    
    Args:
        message_history: List of message exchanges between user and system
        model_name: Optional model name to use. If None, uses DEFAULT_TEXT_MODEL from config
        
    Returns:
        Dictionary containing the planned functions to execute and response text
    """
    print('Agent planning actions...')
    
    # Use the configured large language model to generate an action plan
    if model_name is None:
        model_name = DEFAULT_TEXT_MODEL
    
    action_plan_raw = query_llm_with_history(message_history, model_name)
    
    # Parse the raw output into a structured action plan
    try:
        # Handle potential formatting issues in the LLM response
        if action_plan_raw.startswith('```json'):
            action_plan_raw = action_plan_raw[7:-3]  # Strip ```json and ```
        
        # Clean up potential formatting issues
        action_plan_raw = action_plan_raw.strip()
        if not action_plan_raw.startswith('{'):
            # Find the first occurrence of { if the model added extra text
            start_idx = action_plan_raw.find('{')
            if start_idx >= 0:
                action_plan_raw = action_plan_raw[start_idx:]
        
        # Parse the JSON response
        action_plan = eval(action_plan_raw)
        
    except Exception as e:
        print(f"Error parsing action plan: {e}")
        print(f"Raw output: {action_plan_raw}")
        # Fallback to a safe default plan
        action_plan = {
            'function': ['back_to_zero()'],
            'response': 'I encountered an error understanding the request. Returning to default position.'
        }
    
    return action_plan


def parse_visual_instruction(instruction: str, coordinates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses a visual instruction with object coordinates to create actionable parameters.
    
    Args:
        instruction: The original instruction (e.g., "Move the red cube onto the plate")
        coordinates: Dictionary containing object coordinates from vision model
        
    Returns:
        Dictionary with parsed parameters for robot action
    """
    # Extract start and end coordinates from vision analysis
    start_coords = None
    end_coords = None
    
    if 'start_xyxy' in coordinates and len(coordinates['start_xyxy']) >= 2:
        # Calculate center point of the starting object
        x1, y1 = coordinates['start_xyxy'][0]
        x2, y2 = coordinates['start_xyxy'][1]
        start_center_x = (x1 + x2) // 2
        start_center_y = (y1 + y2) // 2
        start_coords = [start_center_x, start_center_y]
    
    if 'end_xyxy' in coordinates and len(coordinates['end_xyxy']) >= 2:
        # Calculate center point of the destination object
        x1, y1 = coordinates['end_xyxy'][0]
        x2, y2 = coordinates['end_xyxy'][1]
        end_center_x = (x1 + x2) // 2
        end_center_y = (y1 + y2) // 2
        end_coords = [end_center_x, end_center_y]
    
    return {
        'instruction': instruction,
        'start_object': coordinates.get('start', 'unknown object'),
        'end_object': coordinates.get('end', 'target location'),
        'start_coords': start_coords,
        'end_coords': end_coords
    }
