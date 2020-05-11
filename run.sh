#!/bin/bash

#
# Run Python Script
#

# Local .env
if [ -f .env ]; then
    # Load Environment Variables
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
    # For instance
    #echo $KAGGLE_KEY
fi

# Run Air Quality
cd ./src
python3 air_quality.py
cd ..

# End
echo "Finish!"
