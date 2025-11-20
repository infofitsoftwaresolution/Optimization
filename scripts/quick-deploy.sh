#!/bin/bash

echo " Quick deployment..."

cd /home/ec2-user/Optimization
git pull origin main
pip3 install -r requirements.txt
sudo systemctl restart streamlit-optimization.service

echo " Deployment initiated. Check status with: sudo systemctl status streamlit-optimization.service"
