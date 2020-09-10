sudo cp /home/ubuntu/Stream_Server/stream_server.service /etc/systemd/system/stream_server.service
sudo systemctl start stream_server
sudo systemctl enable stream_server
sudo systemctl status stream_server
sudo cp /home/ubuntu/Stream_Server/stream_server.conf /etc/nginx/sites-available/stream_server
sudo ln -s /etc/nginx/sites-available/stream_server /etc/nginx/sites-enabled
sudo systemctl restart nginx