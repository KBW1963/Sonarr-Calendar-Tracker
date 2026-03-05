# Native Python

python sonarr_calendar.py

# Docker – rebuild image. These commands need to be execusted in the folder where the DockerFile is located

# Also, I am using Docker-Desktop locally to run the following commands

# On development machine

docker build -t tomita2022/sonarr-calendar:latest .
docker push tomita2022/sonarr-calendar:latest # if using a registry

# TrueNAS folder location

/mnt/truenas/app_configs/dockge/stacks/sonarr-calendar-tracker

# # On TrueNAS (in the stack directory). This is where we can run the docker commands for the app

# Build the app

sudo docker compose build

# Pull the updated image

sudo docker compose pull

# After pulling, you can check the image ID to confirm it's the new one

# Compare the creation time with your local build time

sudo docker images | grep sonarr-calendar

# Recreate the container (this uses the new image)

sudo docker compose up -d

# Watch the logs for the debug output

sudo docker compose logs -f
