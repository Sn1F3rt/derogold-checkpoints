# DeroGold Checkpoints Generator

[![License](https://img.shields.io/github/license/Sn1F3rt/derogold-checkpoints)](LICENSE) 

## Table of Contents

- [About](#about)
- [Pre-requisites](#pre-requisites)
- [Installation](#installation)
- [Configuration (Optional)](#configuration-optional)
- [Usage](#usage)
- [License](#license)

## About

A python script to generate checkpoints for the DeroGold blockchain.

## Pre-requisites

- Git
- Python 3.8 or higher (tested on 3.11)
- [DeroGold daemon (v0.7.1 or higher)](https://github.com/derogold/derogold/releases/latest)

## Installation

```shell
# Clone the repository
git clone https://github.com/Sn1F3rt/derogold-checkpoints-generator.git
# Switch to the project directory
cd derogold-checkpoints-generator
# Create a virtual environment
python -m venv .venv
# Activate the virtual environment
source .venv/bin/activate
# Install the dependencies
pip install -r requirements.txt
```


## Configuration (Optional)

The script can be configured using the following methods:

1. Environment variables - Create a `.env` file with the options that you want to set. For example:

    ```shell
    DAEMON_RPC_HOST="localhost"  # Daemon RPC host address (e.g. localhost)
    DAEMON_RPC_PORT=6969  # Daemon RPC port (usually 6969)
    DAEMON_RPC_SSL=0  # Use SSL for daemon RPC (0 for http, 1 for https)
    OUTPUT_FILE_NAME="checkpoints.csv"  # Output file name (e.g. checkpoints.csv)
    ```

2. Command-line arguments - You can run the script with the `--help` option to see the available options.

    ```shell
    python generate.py --help
    ```

## Usage

```shell
python generate.py
```

## License

[MIT License](LICENSE)

Copyright &copy; 2024 Sayan "Sn1F3rt" Bhattacharyya
