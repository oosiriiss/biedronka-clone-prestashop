sudo systemctl start docker
cd ../docker/
sudo docker compose down -v
sudo docker compose up -d