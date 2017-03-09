#!/bin/bash
while true; do
  echo "Testing @ $(date)" >>test.log
  ./laser.py >> test.log
done
