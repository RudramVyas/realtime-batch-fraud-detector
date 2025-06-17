from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.sql.functions import udf,  col
from pyspark.sql.types import ArrayType, DoubleType


spark = SparkSession.builder \
    .appName("RandomForest") \
    .enableHiveSupport() \
    .getOrCreate()

df = spark.sql("SELECT * FROM bd_class_project.cc_fraud_trans_processed")

# Optional: Show schema and few rows to verify
df.select("user_id", "transaction_amount", "location_arr", "card_type_arr").show(5)

# Define the UDF once
array_to_vector_udf = udf(lambda arr: Vectors.dense(arr) if arr is not None else None, VectorUDT())

# List your array columns here
arr_cols = [
    "transaction_type_arr",
    "device_type_arr",
    "location_arr",
    "merchant_category_arr",
    "card_type_arr",
    "authentication_method_arr"
]

# For each array col, create a new vector col by applying the UDF
for c in arr_cols:
    new_col_name = c.replace('_arr', '_vec')
    df = df.withColumn(new_col_name, array_to_vector_udf(col(c)))


feature_cols = ['user_id', 'transaction_amount', 'account_balance', 'card_age', 'ip_address_flag',
                'avg_transaction_amount_7d', 'risk_score', 'is_weekend', 'risk_score',
                'previous_fraudulent_activity', 'daily_transaction_count','transaction_distance',
                'device_type_vec', 'merchant_category_vec', 'card_type_vec', 'location_vec', 
                'authentication_method_vec', 'transaction_type_vec']

assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

rf = RandomForestClassifier(labelCol="fraud_label", featuresCol="features", numTrees=100)

pipeline = Pipeline(stages=[assembler, rf])

# Train-test split
train_df, test_df = df.randomSplit([0.7, 0.3], seed=42)

# Train model
model = pipeline.fit(train_df)

# Predictions
predictions = model.transform(test_df)

round_prob_udf = udf(lambda prob: [round(x, 2) for x in prob.toArray()], ArrayType(DoubleType()))

# Show predictions

predictions.select(
    "transaction_id",
    "fraud_label",
    "prediction",
    round_prob_udf("probability").alias("probability_2dp")
).show(50, truncate=False)


