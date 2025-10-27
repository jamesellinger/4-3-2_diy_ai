import configparser
import logging
import os
import pandas as pd
import shutil
import subprocess
import sys
import time
import wave
from io import StringIO

########################################################################################################
#### This section contains the functions that convert the audio files to .wav, transcribe the .wav files 
#### with whisper.cpp, and calculate the words/minute
########################################################################################################

def process_files(input_dir, output_dir, whisper_cpp_loc, num_threads, model_name):
    """
    Converts all files in the input directory to WAV format 
    and saves them in the output directory. Uses whisper.cpp to
    transcribe the WAV files to TXT, then calculates the 
    words/minute for each transcription.

    Args:
        input_dir: Path to the directory containing the files to convert.
        output_dir: Path to the directory where converted WAV files will be saved.
        whisper_cpp_loc: Path to the whisper.cpp ffmpeg_cmd line interface
        num_thread: Number of threads to use during computation
        model_name: Path to the model to be used by whisper.cpp

    Returns:
        A dictionary with the extracted data.
    """

    # Temporary log in memory (only write to file if needed)
    log_stream = StringIO()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(), logging.StreamHandler(log_stream)]
    )

    logger = logging.getLogger()

    # Get a list of all files in the input directory (excluding hidden files)
    # Exclude the log file
    files = [
        f for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f))
        and not f.startswith('.')
        and not f.lower().endswith('.txt')
        ]

    # Check if any files are present to convert
    if not files:
        logging.warning(f"No files found in {input_dir} to convert.")
        return
        
    # # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create a dictionary that will hold the base of each filename, duration, total words, and words per minute
    extracted_data= {}

    # Loop through the files, convert them, get the duration
    for filename in files:
        
        # Get the full path to the input file
        input_file = os.path.join(input_dir, filename)

        # Get the filename without extension 
        base, ext = os.path.splitext(filename)

        # Create the output filename with .wav extension
        output_file = os.path.join(output_dir, base + ".wav")

        # Check if the file is a valid audio file using ffprobe
        try:
            ffprobe_cmd = ["ffprobe", "-v", "error", "-show_streams", "-select_streams", "a", input_file]
            subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError:
            #print(f"Skipping {filename}: not a valid audio file.")
            logging.error(f"Skipping {filename}: not a valid audio file.")
            continue  # Skip this file and move on

        # Convert the file using ffmpeg  (assuming ffmpeg is installed), parameters are those stated in the whisper.cpp GitHub
        ffmpeg_cmd = ["ffmpeg", "-i", input_file, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", output_file]
        subprocess.run(ffmpeg_cmd, check=True)

        # Get duration in seconds from the .wav file
        
        with wave.open(output_file, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            audio_duration = frames / float(rate)

        # Transcribe, use output_file since it's the variable that holds the name of .wav to be transcribed
        ffmpeg_cmd = [whisper_cpp_loc, "-t", num_threads, "-m", model_name, output_file, "-otxt"]
        subprocess.run(ffmpeg_cmd, check=True)

        # Set the text file's filename
        text_file = output_file + ".txt"
        # Get the word count and calculate words per minute
        num_words = count_words(text_file)
        words_per_min = num_words/(audio_duration/60)

        # Add all new data to the dictionary
        extracted_data[base] = {
            "duration": audio_duration,
            "word_count": num_words,
            "wpm": round(words_per_min)
        }

    print(f"Converted all files to WAV and saved them in {output_dir}")
    
    for x, obj in extracted_data.items():
        print(x)
        for y in obj:
            print("\t"+ y + ":", obj[y])

    # Write log file if something was logged
    log_contents = log_stream.getvalue()
    if log_contents.strip():
        with open(os.path.join(output_dir, "error_log.txt"), "w") as f:
            f.write(log_contents)

    # Return a dictionary with all of the extracted data
    return extracted_data


def count_words(filename):
    """
    This function opens a text file and counts the number of words.

    Args:
        filename: The path to the text file.

    Returns:
        The number of words in the text file.
    """
    # Open the file in read mode
    with open(filename, 'r') as f:
    # Read the entire content of the file
        text = f.read()

    # Split the text into words using whitespace as delimiter
    # Punctuation is inlcuded with the word that precedes it
    # and simply counted as part of the word. Shouldn't affect total word count
    words = text.split()

    # Return the number of words
    return len(words)


#----------------------------------------#
##### The main code starts here ##########
#----------------------------------------#

# Check if ffmpeg is installed and in PATH, exit if ffmpeg is not found
if shutil.which("ffmpeg") is None:
    sys.exit("Error: ffmpeg is not installed or not found in PATH.")
else:
    print("ffmpeg is found in PATH.")

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the settings from the settings.txt file located in the same directory as this script
config_file_path = os.path.join(os.path.dirname(__file__), 'settings.txt')
if not os.path.exists(config_file_path):
    print(f"Error: Configuration file '{config_file_path}' does not exist.")
    exit(1)

config.read(config_file_path)

# Set variables using the values from settings.txt
# location of whisper.cpp
whisper_cpp = config.get('DEFAULT', 'whisper_cpp')
# Number of threads to use during computation
threads = config.get('DEFAULT', "threads")
# Location of model for whisper.cpp
model = config.get('DEFAULT', 'model')
# Location of input_dir
input_dir = config.get('DEFAULT', 'input_dir')
output_dir = os.path.join(input_dir,"wav")

# Check if directories exist for whisper_cpp, model, and input_dir. Exit if not found.
if not os.path.exists(whisper_cpp):
    print(f"Error: Could not find whisper CLI at '{whisper_cpp}'")
    exit(1)
if not os.path.exists(model):
    print(f"Error: Model file '{model}' does not exist.")
    exit(1)
if not os.path.exists(input_dir):
    print(f"Error: Input directory '{input_dir}' does not exist.")
    exit(1)

# Check if output_dir ALREADY exists. Exit if it does.
if os.path.exists(output_dir):
    print(f"Error: '{output_dir}' already exists. You might have already run the analysis on this audio.")
    exit(1)

##### Start measuring total time needed to process all files
#start_time = time.time()

# Process the files, create a dictionary with the data, return the dictionary into 
# a DataFrame (and transpose it too)
df = pd.DataFrame(process_files(input_dir, output_dir, whisper_cpp, threads, model)).T

# Save the DataFrame as a CSV file
output_csv = output_dir + "transcribed_output.csv"
df.to_csv(output_csv, index=True)

###### Capture time taken to process all files
#execution_time = time.time() - start_time
#print(f"File transcription and processing time: {execution_time:.2f} seconds")