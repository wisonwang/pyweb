#!/bin/bash

mkdir -p /opt/uhaService/db/registry
mkdir -p /opt/uhaService/db/data
mkdir -p /opt/uhaService/ice-config
mkdir -p /opt/uhaService/db/node
cp -rf *.json /opt/uhaService/ice-config
cp -rf config.* /opt/uhaService/ice-config
cp -rf *.xml /opt/uhaService/ice-config


icegridnode --Ice.Config=/opt/uhaService/ice-config/config.grid

