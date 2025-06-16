CREATE EXTERNAL TABLE IF NOT EXISTS bd_class_project.cc_fraud_trans( 
    Transaction_ID string, 
    User_ID string, 
    Transaction_Amount decimal(10,2), 
    Transaction_Type string, 
    `Timestamp` timestamp, 
    Account_Balance decimal(10,2), 
    Device_Type string, 
    Location string, 
    Merchant_Category string, 
    IP_Address_Flag int, 
    Previous_Fraudulent_Activity int, 
    Daily_Transaction_Count int, 
    Avg_Transaction_Amount_7d decimal(10,2), 
    Failed_Transaction_Count_7d int, 
    Card_Type string, 
    Card_Age int, 
    Transaction_Distance decimal(10,2), 
    Authentication_Method string, 
    Risk_Score decimal(5,4), 
    Is_Weekend int, 
    Fraud_Label int 
) 
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
STORED AS TEXTFILE 
LOCATION '/tmp/US_UK_05052025/class_project/input/raw_data_sqoop/' 
TBLPROPERTIES ("skip.header.line.count"="1");