"""
Actuators Control Module for Embodied Agent

This module handles the control of various actuators connected to the robotic system,
including the vacuum pump, LEDs, and other external devices.

"""

import time
import os
from typing import Optional, Tuple

# Assuming hardware control is available
try:
    from pymycobot.mycobot import MyCobot
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    print("Warning: Hardware control libraries not available. Running in simulation mode.")
    HARDWARE_AVAILABLE = False

# Set up GPIO pins if hardware is available
if HARDWARE_AVAILABLE:
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        
        # Define pins
        PUMP_PIN = 20
        LED_RED_PIN = 17
        LED_GREEN_PIN = 27
        LED_BLUE_PIN = 22
        
        # Setup pins as outputs
        GPIO.setup(PUMP_PIN, GPIO.OUT)
        GPIO.setup(LED_RED_PIN, GPIO.OUT)
        GPIO.setup(LED_GREEN_PIN, GPIO.OUT)
        GPIO.setup(LED_BLUE_PIN, GPIO.OUT)
        
        # Initialize PWM for LED control
        led_red = GPIO.PWM(LED_RED_PIN, 100)
        led_green = GPIO.PWM(LED_GREEN_PIN, 100)
        led_blue = GPIO.PWM(LED_BLUE_PIN, 100)
        
        # Start PWM with 0% duty cycle
        led_red.start(0)
        led_green.start(0)
        led_blue.start(0)
        
        print("GPIO initialized for actuator control.")
    except Exception as e:
        print(f"Error setting up GPIO: {e}")
        HARDWARE_AVAILABLE = False


def pump_on() -> None:
    """
    Turn on the vacuum pump for object grasping.
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Vacuum pump activated")
        return
    
    try:
        GPIO.output(PUMP_PIN, GPIO.HIGH)
        print("Vacuum pump activated.")
    except Exception as e:
        print(f"Error activating pump: {e}")


def pump_off() -> None:
    """
    Turn off the vacuum pump to release objects.
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Vacuum pump deactivated")
        return
    
    try:
        GPIO.output(PUMP_PIN, GPIO.LOW)
        print("Vacuum pump deactivated.")
    except Exception as e:
        print(f"Error deactivating pump: {e}")


def change_led_color(instruction: str) -> str:
    """
    Change the LED color based on a natural language instruction.
    
    Args:
        instruction: Natural language instruction describing the desired color
        
    Returns:
        Description of the action taken
    """
    if not HARDWARE_AVAILABLE:
        print(f"[SIM] Setting LED color: {instruction}")
        return f"LED color changed to match: {instruction}"
    
    try:
        # Extract color information from the instruction
        from models.llm_interface import extract_color_info
        
        # Get RGB values for the requested color
        rgb = extract_color_info(instruction)
        
        if not rgb:
            rgb = (0, 0, 255)  # Default to blue if color extraction failed
        
        # Set the LED color
        set_led_rgb(rgb[0], rgb[1], rgb[2])
        
        return f"LED color changed to {instruction}"
    except Exception as e:
        print(f"Error changing LED color: {e}")
        return "I couldn't change the LED color"


def set_led_rgb(red: int, green: int, blue: int) -> None:
    """
    Set the LED color using RGB values (0-255).
    
    Args:
        red: Red component (0-255)
        green: Green component (0-255)
        blue: Blue component (0-255)
    """
    if not HARDWARE_AVAILABLE:
        print(f"[SIM] Setting LED RGB: ({red}, {green}, {blue})")
        return
    
    try:
        # Convert 0-255 range to 0-100 for PWM
        red_duty = int(red * 100 / 255)
        green_duty = int(green * 100 / 255)
        blue_duty = int(blue * 100 / 255)
        
        # Set PWM duty cycles
        led_red.ChangeDutyCycle(red_duty)
        led_green.ChangeDutyCycle(green_duty)
        led_blue.ChangeDutyCycle(blue_duty)
        
        print(f"LED color set to RGB: ({red}, {green}, {blue})")
    except Exception as e:
        print(f"Error setting LED color: {e}")


def turn_off_leds() -> None:
    """
    Turn off all LEDs.
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] All LEDs turned off")
        return
    
    try:
        # Set all PWM duty cycles to 0
        led_red.ChangeDutyCycle(0)
        led_green.ChangeDutyCycle(0)
        led_blue.ChangeDutyCycle(0)
        
        print("All LEDs turned off.")
    except Exception as e:
        print(f"Error turning off LEDs: {e}")


def flash_led(color: Tuple[int, int, int], times: int = 3, interval: float = 0.3) -> None:
    """
    Flash LED in specified color.
    
    Args:
        color: RGB tuple (0-255 for each component)
        times: Number of flashes
        interval: Time between flashes in seconds
    """
    if not HARDWARE_AVAILABLE:
        print(f"[SIM] Flashing LED {times} times with color RGB: {color}")
        return
    
    try:
        for _ in range(times):
            # Turn on with specified color
            set_led_rgb(color[0], color[1], color[2])
            time.sleep(interval)
            
            # Turn off
            turn_off_leds()
            time.sleep(interval)
            
        print(f"LED flashed {times} times.")
    except Exception as e:
        print(f"Error flashing LED: {e}")


def cleanup() -> None:
    """
    Clean up GPIO and release resources when program exits.
    """
    if not HARDWARE_AVAILABLE:
        print("[SIM] Cleaned up actuator resources")
        return
    
    try:
        # Turn off all actuators
        pump_off()
        turn_off_leds()
        
        # Clean up GPIO
        GPIO.cleanup()
        
        print("All actuator resources cleaned up.")
    except Exception as e:
        print(f"Error in cleanup: {e}")
