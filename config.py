import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'turbine-db.mysql.database.azure.com'),
    'user': os.environ.get('DB_USER', 'turbineadmin'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME', 'turbinedb'),
    'ssl_disabled': False
}

ALARM_THRESHOLD = 75

EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

