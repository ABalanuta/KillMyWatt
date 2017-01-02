install:
	sudo mkdir -p /opt/killmywatt
	sudo cp killmywatt.py /opt/killmywatt/
	sudo chmod +x /opt/killmywatt/killmywatt.py 
	sudo cp killmywatt.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl stop killmywatt.service
	sudo systemctl start killmywatt.service
	sudo systemctl status killmywatt.service
	sudo systemctl enable killmywatt.service
	
	sudo cp check_link.sh /opt/killmywatt/check_link.sh
	sudo chmod +x /opt/killmywatt/check_link.sh
	sudo cp check_link.service /etc/systemd/system/
	sudo cp check_link.timer /etc/systemd/system/	
	
	systemctl enable check_link.timer
	systemctl start check_link.timer
