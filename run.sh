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

# TODO
echo "TODO"

# End
echo "Finish!"
