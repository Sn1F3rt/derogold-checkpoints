# derogold-checkpoints

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
- [DeroGold daemon (v0.7.1 or higher)](https://github.com/derogold/derogold/releases/tag/v0.7.1)

## Installation

```shell
git clone https://github.com/Sn1F3rt/derogold-checkpoints.git
cd derogold-checkpoints
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration (Optional)

Make a copy of the `config.example.py` file and rename it to `config.py`. Edit the parameters as per your requirements.

## Usage

```shell
python generate.py
```

## License

[MIT License](LICENSE)

Copyright &copy; 2024 Sayan "Sn1F3rt" Bhattacharyya
