#!/usr/bin/env python
# -*- coding: utf-8 -*-


from agent.agent_coordinator import coordinate_actions
from models.llm_interface import SYSTEM_PROMPT
from action.actuators import pump_off
from action.robot_control import back_to_zero, check_camera
from perception.speech import record, speech_recognition, play_wav, tts
import os
import sys
import time


sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def main():
    """
    Main function that orchestrates the embodied agent's perception-action cycle.
    """
    print('\nEmbodied Agent: Listen, See, Act - Multimodal Robotic Control')
    print('Copyright (c) 2025 Zihao Mu, Tongji University\n')

    pump_off()
    play_wav('assets/audio/welcome.wav')

    message_history = []
    message_history.append({"role": "system", "content": SYSTEM_PROMPT})

    try:
        while True:

            back_to_zero()

            instruction_input = input(
                'Start recording? Enter duration in seconds, k for keyboard input, c for default: ')

            if str.isnumeric(instruction_input):
                duration = int(instruction_input)
                record(duration=duration)
                instruction = speech_recognition()
                print(f"Recognized instruction: {instruction}")
            elif instruction_input == 'k':
                instruction = input('Please enter your instruction: ')
            elif instruction_input == 'c':
                instruction = 'First return to zero, then shake head, and put the green block on the basketball'
            else:
                print('No valid instruction provided, exiting')
                raise ValueError('No instruction provided')

            message_history.append({"role": "user", "content": instruction})
            action_plan = coordinate_actions(message_history)

            print('Action plan generated:', action_plan)

            try:
                response = action_plan['response']
                print('Synthesizing speech...')
                tts(response)
                play_wav('temp/tts.wav')

                additional_output = ''
                for action in action_plan['function']:
                    print('Executing action:', action)
                    result = eval(action)
                    if result is not None:
                        additional_output = result

                action_plan['response'] += '. ' + additional_output
                message_history.append(
                    {"role": "assistant", "content": str(action_plan)})

            except Exception as e:
                print(f"Error executing action plan: {e}")

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
