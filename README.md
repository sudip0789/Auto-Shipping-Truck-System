# Autonomous Shipping Truck Management Platform

A comprehensive web-based platform for managing autonomous shipping trucks, including vehicle tracking, alert handling, route scheduling, computer vision, and simulation capabilities.

## Features

- **Vehicle Management**: Add, delete, and modify truck information
- **Truck Monitoring/Tracking**: Track truck location and status
- **Alert Management**: Handle and resolve alerts from trucks
- **Route Scheduling**: Schedule and manage routes for trucks
- **Simulation**: Integration with CARLA for simulation
- **Computer Vision**: Camera-based emergency detection

## Tech Stack

- **Frontend**: React 
- **Backend**: Python with Flask
- **Database**: AWS DynamoDB / S3
- **Hosting**: AWS EC2 with Elastic Load Balancer
- **Scaling**: AWS Auto Scaling

## Setup and Installation

Instructions for setting up the project locally and deploying to AWS:

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Configure AWS credentials
4. Run Backend locally: `python3 app.py`
5. Run Frontend locally: `cd frontend && npm install && npm run start`

## AWS Configuration

This project uses the following AWS services:
- EC2 for hosting
- DynamoDB for data storage
- S3 for file storage
- ELB for load balancing
- Auto Scaling for availability

