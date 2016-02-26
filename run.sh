export SETTINGS="config.DevelopmentConfig"

python manage.py db upgrade

mkdir logs

chmod 777 logs

python run.py
