#!/bin/bash

echo "pyenv 切り替え"
# pyenv 初期化
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# 使いたいPythonバージョンに切り替え
pyenv local non-direct_wordbase
# 実際のPythonコマンド
python --version

echo "モジュールインストール"
pip install -r setup/requirements.txt

echo "Wordnetデータのインストール"
python setup/wordnet_setup.py
