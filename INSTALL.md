## Clone Stream_Server directory to a PATH
    ```
    git clone URL /home/ec2-user
    ```

## Configure as a service:
    ```
    sudo cp /home/ec2-user/Stream_Server/stream_server.service /etc/systemd/system/stream_server.service
    sudo systemctl start stream_server
    sudo systemctl enable stream_server
    sudo systemctl status stream_server
    ```

## Configure Nginx:
    ```
    sudo cp /home/ec2-user/Stream_Server/stream_server.conf /etc/nginx/sites-available/stream_server
    sudo ln -s /etc/nginx/sites-available/stream_server /etc/nginx/sites-enabled
    sudo systemctl restart nginx
    sudo ufw allow 'Nginx Full'
    sudo ufw delete allow 'Nginx HTTP'
    iptables -A INPUT -p tcp --dport 443 -j ACCEPT
    ```