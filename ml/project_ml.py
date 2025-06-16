#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator

def main():
    # Print working directory
    cwd = os.getcwd()
    print("Working directory is: {}".format(cwd))

    # 1) Initialize Spark
    conf = SparkConf().setAppName("FraudDetection_RF")
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)

    # 2) Read Parquet directly (no Hive)
    parquet_path = "/tmp/US_UK_05052025/class_project/input/ml_data/parquet_flattened"
    df = sqlContext.read.parquet(parquet_path)

    # 3) Drop non-features
    to_drop = [
        "user_id", "Timestamp",
        "transaction_type", "device_type", "location",
        "merchant_category", "card_type", "authentication_method"
    ]
    label_col = "fraud_label"
    df = df.drop(*to_drop)

    # 4) Assemble feature vector
    feature_cols = [c for c in df.columns if c != label_col]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

    # 5) Random Forest setup
    rf = RandomForestClassifier(
        featuresCol="features",
        labelCol=label_col,
        predictionCol="prediction",
        probabilityCol="probability",
        rawPredictionCol="rawPrediction",
        numTrees=100,
        maxDepth=5,
        seed=42
    )

    pipeline = Pipeline(stages=[assembler, rf])

    # 6) 70/30 split
    train_df, test_df = df.randomSplit([0.7, 0.3], seed=42)

    # 7) Train
    model = pipeline.fit(train_df)

    # 8) Predict & sample
    preds = model.transform(test_df)
    preds.select(label_col, "probability", "prediction").show(5)

    # 9) Evaluate AUC
    evaluator = BinaryClassificationEvaluator(
        labelCol=label_col,
        rawPredictionCol="rawPrediction",
        metricName="areaUnderROC"
    )
    auc = evaluator.evaluate(preds)
    print("Test AUC = {:.4f}".format(auc))
    # 10) Save the model under cwd/model on the local filesystem
    model_dir = os.path.join(cwd, "model")
    local_model_uri = "file://" + model_dir

    print("Saving model to: {}".format(local_model_uri))
    model.write().overwrite().save(local_model_uri)
    print("Model successfully saved to local FS.")

    sc.stop()

if __name__ == "__main__":
    main()

