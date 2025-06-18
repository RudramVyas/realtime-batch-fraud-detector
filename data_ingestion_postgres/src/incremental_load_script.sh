#!/bin/bash

# Assign arguments to variables for clearer reference
TABLE="cc_fraud_trans"
HIVE_DATABASE="bd_class_project"
HIVE_TABLE="cc_fraud_trans"

# Variables
hostName="${DB_HOST}"
dbName="${DB_NAME}"
userName="${DB_USERNAME}"
password="${DB_PASSWORD}"
targetDir="/tmp/US_UK_05052025/class_project/input/raw_data_sqoop"
HIVE_URL="jdbc:hive2://ip-172-31-14-3.eu-west-2.compute.internal:10000/${HIVE_DATABASE};"

sudo -u hdfs hdfs dfs -chmod -R 777 /tmp/US_UK_05052025/class_project/input/raw_data_sqoop
sudo -u hdfs hdfs dfs -chmod -R 777 /tmp/US_UK_05052025/class_project/input/raw_data_sqoop/* 

# Fetch the maximum Timestamp value from Hive
lastValue=$(beeline -u "${HIVE_URL}" --silent=true --showHeader=false --outputformat=tsv2 -e \
"SELECT COALESCE(MAX(\`Timestamp\`), '1970-01-01 00:00:00') FROM ${HIVE_TABLE};" | tail -n 1)

# Check if lastValue was retrieved successfully
if [ -z "$lastValue" ]; then
    echo "Error: Failed to retrieve last Timestamp from Hive."
    exit 1
fi

echo "Last recorded Timestamp: $lastValue"
echo "Starting new import from Timestamp greater than $lastValue"

# Perform the incremental Sqoop import
sqoop import \
  --connect jdbc:postgresql://${hostName}:5432/${dbName} \
  --username ${userName} \
  --password ${password} \
  --table ${TABLE} \
  --incremental append \
  --check-column Timestamp \
  --last-value "${lastValue}" \
  --target-dir ${targetDir} \
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