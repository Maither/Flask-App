
sudo apt update
sudo apt install nginx

create configuration for nginx to set up a reverse proxy for the flask app
to protect contre dosattack

nano /etc/nginx/sites-enable/flask_app
