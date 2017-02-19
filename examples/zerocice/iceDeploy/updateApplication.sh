#!/bin/bash


icegridadmin --Ice.Config=/opt/uhaService/ice-config/config.grid -e \
    "application add '/opt/uhaService/ice-config/application.xml'"


icegridadmin --Ice.Config=/opt/uhaService/ice-config/config.grid -e \
    "application update '/opt/uhaService/ice-config/application.xml'"

