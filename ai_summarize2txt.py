import configparser
import os
import json
import requests

########################################################################################################
#### This section contains the functions that send the text data to LM Studio 
########################################################################################################

def summarize_transcript(transcript_text, system_instruction, model, user_prompt, temperature, max_tokens, stream):
    """
    Sends the transcript text to LM Studio's chat completions endpoint for summarization.
    
    Args:
        transcript_text (str): The transcript to summarize.
        system_instruction (str): The system-level instruction for the model.
        user_prompt (str): The prompt given by the user.
        temperature (float): Controls randomness in the output.
        max_tokens (int): Maximum tokens for the output (-1 means no limit).
        stream (bool): Whether to stream the output.
    
    Returns:
        str: The summary returned by LM Studio.
    """
    api_url = "http://localhost:1234/v1/chat/completions"  # Update if necessary
    
    payload = {
        "model": model,  
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt + transcript_text}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        
        # Adjust parsing based on the response structure
        summary = data["choices"][0]["message"]["content"]
        return summary
    except Exception as e:
        print(f"Error summarizing transcript: {e}")
        return "Error summarizing transcript."

def batch_process_transcripts(model, transcript_dir, output_json, output_txt_dir, system_instruction, user_prompt, temperature, max_tokens, stream):
    """
    Processes all .txt files in the transcript_dir, sends them to LM Studio for summarization,
    saves the results in a JSON file, and writes individual summary .txt files.
    """
    summaries = {}

    # Ensure the directory for summary txt files exists
    os.makedirs(output_txt_dir, exist_ok=True)
    
    for filename in os.listdir(transcript_dir):
        if filename.lower().endswith(".txt"):
            file_path = os.path.join(transcript_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                transcript_text = file.read()
            
            print(f"Processing: {filename}")
            summary = summarize_transcript(transcript_text, system_instruction, model, user_prompt, temperature, max_tokens, stream)
            summaries[filename] = summary
            
            # Write individual summary .txt file
            summary_filename = os.path.splitext(filename)[0] + "_summary.txt"
            summary_file_path = os.path.join(output_txt_dir, summary_filename)
            with open(summary_file_path, 'w', encoding='utf-8') as summary_file:
                summary_file.write(summary)
    
    # Write the summaries dictionary to a JSON file
    with open(output_json, 'w', encoding='utf-8') as json_file:
        json.dump(summaries, json_file, indent=4)
    
    print(f"Summaries saved to {output_json}")
    print(f"Individual summary text files saved to {output_txt_dir}")

#----------------------------------------#
##### The main code starts here ##########
#----------------------------------------#

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the settings from the settings.txt file located in the same directory as this script
config_file_path = os.path.join(os.path.dirname(__file__), 'settings.txt')
if not os.path.exists(config_file_path):
    print(f"Error: Configuration file '{config_file_path}' does not exist.")
    exit(1)

config.read(config_file_path)

# Set variables using the values from settings.txt

# Location of transcripts .txt files created by transcibe_and_count.py
input_dir = config.get('DEFAULT', 'input_dir')

# Set directory for output of summary text files
transcript_directory = os.path.join(input_dir,"wav")

# Directory to save individual summary .txt files
output_txt_directory = os.path.join(input_dir,"summary_texts")
#output_txt_directory = "summary_texts"

# JSON file to save all summaries
output_json_file = os.path.join(input_dir,"summary_texts","summaries.json")
#output_json_file = "summaries.json"

# Set AI model for summary
ai_model = config.get('DEFAULT', 'ai_model')

# System instruction for the LM Studio model.
system_instruction = config.get('DEFAULT', 'system_instruction')

# User prompt to accompany the transcript.
user_prompt = config.get('DEFAULT', 'user_prompt')

# Set model inference parameters
inf_temperature = config.get('DEFAULT', 'temperature')
inf_max_tokens = config.get('DEFAULT', 'max_tokens')

# Summarize the transcripts created by transcribe_and_count.py

batch_process_transcripts(
    ai_model, 
    transcript_directory, 
    output_json_file, 
    output_txt_directory, 
    system_instruction, 
    user_prompt,
    temperature=inf_temperature, 
    max_tokens=inf_max_tokens, 
    stream=False)
