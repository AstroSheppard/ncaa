#!/bin//bash

echo "Retrieving updated data, uploading to excel sheet"
python2 get_538.py
echo "Calculating new 9-12 and 13-16 probabilities"
python2 high_seeds.py

echo "Success"
