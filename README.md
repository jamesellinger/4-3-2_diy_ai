# 4/3/2 DIY AI toolchain

This repository represents the instructions for a project I presented at the JALT 2025 International Conference.

**Project Title**: DIY approach for an AI-based toolchain to provide feedback on a 4/3/2/fluency activity

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