sudo chmod -R 777 *
sudo cp money_transfer_system.service /etc/systemd/system/
sudo systemctl start money_transfer_system.service
sudo systemctl enable money_transfer_system.service
