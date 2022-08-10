# home-station-controller

MicroPython controller for Home Station project

# How to

1. Get Thonny https://thonny.org/
2. Connect the microcontroller
3. Save [main.py](/main.py) file on it
4. Change network info in lines 9-10
5. Restart microcontroller
6. Controller should be connected to wifi
7. Check by running in browser https://CONTROLLER_IP/check

# Project overview

Whole project consists of 5 main repositories, each having different purpose:

- [home-station-server](https://github.com/esavaner/home-station-server) - Node.js server that can be mounted on any linux machine (preferably on Raspberry Pi 4), that handles all controllers, client requests and acts like a database for everything. Also contains OpenWeather OneCall api setup, to get current and forecast weather data
- [home-station-controller](https://github.com/esavaner/home-station-controller) - Python file for a controller (preferably on Raspberry Pi Pico W) to set it up, so it can be able to set and read any type of sensors, currently supported on the sever
- [home-station-packages](https://github.com/esavaner/home-station-packages) - npm package that contains all types, utilities, hooks and assets that are shared between the server, web client, and mobile client
- [home-station-client](https://github.com/esavaner/home-station-client) - React website to display current info about controller sensors, manage them and also set up location for OpenWeather OneCall
- [home-station-mobile](https://github.com/esavaner/home-station-mobile) - React Native application that mimics functionality of **home-station-client**

# Project connections

Chart showing how packages interact with each other

![project connections](/assets/connections.png)

# Website designs

Figma designs can be found [here](https://www.figma.com/file/zHWLBOdtJaTYtbc2qcsg4u/Domowa-stacja-pogodowa?node-id=0%3A1)
