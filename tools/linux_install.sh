#!/bin/bash

download_files () {
    wget https://raw.githubusercontent.com/senapk/indexer/master/indexer.py -O ~/bin/indexer.py
    chmod +x ~/bin/indexer.py
}

export_path () {
    file="/home/${USER}/.profile"
    new_path="PATH=\"\$HOME/bin:\$PATH\""
    grep "$new_path" $file > /dev/null
    if [ $? -ne 0 ]; then
        echo "Inserting ~/bin in path!"
        echo "" >> $file
        echo $new_path >> $file
    fi
    export $new_path
}

mkdir -p ~/bin
download_files
export_path
echo "DONE"

