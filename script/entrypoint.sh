#!/bin/bash
set -e

# Install custom python package if requirements.txt is present
if [ -e "/opt/airflow/requirements.txt" ]; then
    $(command -v pip) install --user -r requirements.txt
fi

# Initialize the database if it doesn't exist
if [ ! -f "/opt/airflow/airflow.db" ]; then
    airflow db init 
    airflow users create --username admin --firstname admin --lastname admin --role Admin --email admin@example.com --password admin
fi


echo "db upgrading"
$(command -v airflow) db upgrade
echo "finished with db upgrade"

exec airflow webserver