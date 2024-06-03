#!/bin/bash

echo "Build docker image for the topologyproject."
docker build -t topologyproject --file ./Dockerfile .
docker image prune
