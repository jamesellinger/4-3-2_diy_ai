# 4/3/2 DIY AI toolchain

This repository represents the instructions for a project I presented at the JALT 2025 International Conference.

**Project Title**: DIY approach for an AI-based toolchain to provide feedback on a 4/3/2/fluency activity

For more details about the project itself please check ```JALT 2025 Poster.pdf```.

The main aim was to develop a custom toolchain for use on a consumer-grade PC that:

1. uses open-source tools to generate transcripts of student speeches from a 4/3/2 fluency activity
2. provides point-by-point feedback using a locally-run AI large language model

This tool was developed on an Apple M2 Mac Mini with the following specs:

- Chip: Apple M2
- RAM: 16 gb
- CPU: 8 cores
- GPU: 10 cores
- macOS Sequoia
- Python 3.12.1

I have also confirmed that this tool works on an Apple MacBook Pro with an M1 Pro chip, Python 3.13.7, following these instructions.

Disclaimer: I am not a professional programmer (indeed some of the code was edited or generated using AI). I have done my best to document how to recreate this tool on an Apple Silicon based computer. It may work for you simply by following the instructions, but it might also require some tweaking.

# Software required to put this tool together

[Homebrew](https://brew.sh) (package manager for macOS): This is probably the easiest way to install some of the following packages and ensure that they properly end up in the PATH.

**Python 3**: Used to tie together the other software in this tool. If it is not installed on your system, then get in via Homebrew.

[whisper.cpp](https://github.com/ggml-org/whisper.cpp): Used to transcribe student's recorded audio into a TXT file.

**cmake**: Used to compile whisper.cpp. Install via Homebrew.

**ffmpeg**: Used to convert student audio files into WAV format as required by whisper.cpp. Install via Homebrew.

[LM Studio](https://lmstudio.ai): Used to run an LLM locally to provide point-by-point feedback on a student's speech. *LM Studio is not open-source and I am considering switching to Ollama*.

# 1. Setup whisper.cpp and build whisper-cli

GitHub repository for whisper.cpp: https://github.com/ggml-org/whisper.cpp

Instructions below are based on the instructions found at the repository. 

Clone the whisper.cpp repository:

```
git clone https://github.com/ggml-org/whisper.cpp.git
```

Navigate into the directory:

```
cd whisper.cpp
```

Download medium size English model, unquantized, in ggml format:

```
sh ./models/download-ggml-model.sh medium.en
```

Build the whisper-cli:

```
cmake -B build
cmake --build build -j --config Release
```

This should result in creation of ```whisper-cli```, which will be used for speech-to-text.

```whisper-cli``` can be found within the directory where you cloned the repository, for example:

```
~/Desktop/whisper.cpp/build/bin/whisper-cli
```

The medium size English model downloaded a few steps ago can similalry be found within the directory where you cloned the repository, for example:

```
~/Desktop/whisper.cpp/models/ggml-medium.en.bin
```

I think that ```whisper-cli``` and ```ggml-medium.en.bin``` can be moved to other locations, the important point is to correctly set the values for ```whisper_cpp``` and ```model``` in ```settings.txt``` as described later.

# 2. Install and setup LM Studio

**LM Studio is only necessary if you want the point-by-point feedback. If you don't intend to use that feature then you can skip this section.**

Download from: [https://lmstudio.ai/download](https://lmstudio.ai/download)

When you run LM Studio for the first time it will walk you through the basic features.

Instructions for downloading a model: [https://lmstudio.ai/docs/app/basics/download-model](https://lmstudio.ai/docs/app/basics/download-model)

Download ```meta-llama-3.1-8b-instruct```

The value for ```ai_model``` in ```settings.txt``` will be set to this, as described later.

The ```temperature``` value for the model is set in ```settings.txt```.

I also found that ```gemma-3-4b-it``` to be decent choice for speed, and ```gemma-3-12b-it``` for giving more detailed feedback, but at the cost of slower performance.

LM Studio needs to be run in server mode before running the Python script described below: [https://lmstudio.ai/docs/developer/core/server](https://lmstudio.ai/docs/developer/core/server)

# 3. Downloading scripts and setting up Python to run the tool

Clone the repository

```
git clone https://github.com/jamesellinger/4-3-2_diy_ai.git
```

Change directory

```
cd 4-3-2_diy_ai
```
Create a Python environment

```
python -m venv env
```

or python3 depending on your system setup

Activate the environment

```
source env/bin/activate
```

Install packages via pip
```
pip install -r requirements.txt
```

# 4. Running the tool

The environment will be active if you are running just after "installing", otherwise please activate it again.

```
cd folder-where-you-downloaded 4-3-2_diy_ai
```

```
source env/bin/activate
```

Edit ```settings.txt``` and make sure that following parameters point to the proper locations (each parameter's detail is explained in ```settings.txt```):

```input_dir```, ```whisper.cpp```, ```model```, and ```ai_model```

Edit the following parameters to make sure the point-by-point feedback is generated as you desire:

```system_instruction```, and ```user_prompt```

### Transcription and word count

make sure that you are running this from the activated environment:

```
python transcribe_and_count.py
```

A new directory called ```wav``` will be created in ```input_dir```. In ```wav``` you will find .txt files that contain the transcribed speeches. A file named ```wavtranscribed_output.csv``` will be created in ```input_dir```, this contains a summary for each speech including: duration in seconds, total word count, and words per minute. 
