echo "Register a service:  flask for flask_notification as a services in /etc/systemd/system/flask_notification.service"

{ echo "[Unit]"; 
  echo "Description=flask server for serve autosys classification";
  echo "After=network.target";
  echo " ";
  echo "[Service]";
  echo "Type=simple"
  echo "WorkingDirectory=$PWD";
  echo "Environment="PATH=/home/$USER/anaconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"";
  echo "ExecStart=/home/$USER/anaconda3/bin/python notification.py";
  echo "Restart=always"
  echo "RestartSec=3"
  echo " ";
  echo "[Install]";
  echo "WantedBy=getty.target";
} | tee $PWD/flask_notification.service > /dev/null

mv flask_notification.service /home/$USER/.config/systemd/user/flask_notification.service

loginctl enable-linger $USER

systemctl --user daemon-reload

echo "start flask_notification service via systemctl"
systemctl --user start flask_notification.service
echo "enable flask_notification restart when system boot"
systemctl --user enable flask_notification
