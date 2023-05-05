#!/bin/bash
while true; do
  npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css --watch
  sleep 1
done

