#!/bin/bash

# Assign arguments to variables for clearer reference
TABLE="cc_fraud_trans"
HIVE_DATABASE="bd_class_project"
HIVE_TABLE="cc_fraud_trans"

# Variables
HOSTNAME='172.31.14.3'
DBNAME='testdb'
USERNAME='consultants'
PASSWORD='WelcomeItc@2022'
TARGET_DIR="/tmp/US_UK_05052025/class_project/input/raw_data_sqoop"
HIVE_URL="jdbc:hive2://ip-172-31-14-3.eu-west-2.compute.internal:10000/${HIVE_DATABASE};"

sudo -u hdfs hdfs dfs -chmod -R 777 /tmp/US_UK_05052025/class_project/input/raw_data_sqoop
sudo -u hdfs hdfs dfs -chmod -R 777 /tmp/US_UK_05052025/class_project/input/raw_data_sqoop/* 

# Fetch the maximum Timestamp value from Hive
LAST_VALUE=$(beeline -u "${HIVE_URL}" --silent=true --showHeader=false --outputformat=tsv2 -e \
"SELECT COALESCE(MAX(\`Timestamp\`), '1970-01-01 00:00:00') FROM ${HIVE_TABLE};" | tail -n 1)

# Check if LAST_VALUE was retrieved successfully
if [ -z "$LAST_VALUE" ]; then
    echo "Error: Failed to retrieve last Timestamp from Hive."
    exit 1
fi

echo "Last recorded Timestamp: $LAST_VALUE"
echo "Starting new import from Timestamp greater than $LAST_VALUE"

# Perform the incremental Sqoop import
sqoop import \
    --connect jdbc:postgresql://${HOSTNAME}:5432/${DBNAME} \
    --username ${USERNAME} \
    --password ${PASSWORD} \
    --table ${TABLE} \
    --incremental append \
    --check-column Timestamp \
    --last-value ${LAST_VALUE} \
    --target-dir ${TARGET_DIR} \
    --m 1 \
    --as-textfile
	
# Check if the Sqoop import was successful
if [ $? -eq 0 ]; then
    echo "Sqoop Incremental Import Successful"
    echo "New data should now be available in Hive table ${HIVE_DATABASE}.${HIVE_TABLE}"
else
    echo "Sqoop Incremental Import Failed"
    exit 1
fi