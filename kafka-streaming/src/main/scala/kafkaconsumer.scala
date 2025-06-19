import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object kafkaconsumer {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().appName("KafkaToJson").master("local[*]").getOrCreate()

    // Define the Kafka parameters
    val kafkaParams = Map[String, Object](
      "bootstrap.servers" -> "ip-172-31-14-3.eu-west-2.compute.internal:9092",
      "key.deserializer" -> "org.apache.kafka.common.serialization.StringDeserializer",
      "value.deserializer" -> "org.apache.kafka.common.serialization.StringDeserializer",
      "group.id" -> "group1",
      "auto.offset.reset" -> "earliest",
      "enable.auto.commit" -> (false: java.lang.Boolean)
    )

    // Define the Kafka topic to subscribe to
    val topic = "realtimeData"

    // Define the schema for the JSON messages
    val schema = StructType(Seq(
      StructField("Transaction_ID", StringType),
      StructField("User_ID", StringType),
      StructField("Transaction_Amount", DoubleType),
      StructField("Transaction_Type", StringType),
      StructField("Timestamp", StringType),
      StructField("Account_Balance", DoubleType),
      StructField("Device_Type", StringType),
      StructField("Location", StringType),
      StructField("Merchant_Category", StringType),
      StructField("IP_Address_Flag", StringType),
      StructField("Previous_Fraudulent_Activity", StringType),
      StructField("Daily_Transaction_Count", IntegerType),
      StructField("Avg_Transaction_Amount_7d", DoubleType),
      StructField("Failed_Transaction_Count_7d", IntegerType),
      StructField("Card_Type", StringType),
      StructField("Card_Age", IntegerType),
      StructField("Transaction_Distance", DoubleType),
      StructField("Authentication_Method", StringType),
      StructField("Risk_Score", DoubleType),
      StructField("Is_Weekend", StringType)
    ))

    // Read the JSON messages from Kafka as a DataFrame
    val df = spark.readStream.format("kafka")
      .option("kafka.bootstrap.servers", " ip-172-31-8-235.eu-west-2.compute.internal:9092,ip-172-31-14-3.eu-west-2.compute.internal:9092")
      .option("subscribe", topic)
      .option("startingOffsets", "latest")
      .load()
      .select(from_json(col("value").cast("string"), schema).as("data"))
      .selectExpr("data.*")
    // Add the current timestamp column when reading the DataFrame
    val df1 = df.withColumn("TimeDetails", current_timestamp())

    // Write the DataFrame as CSV files to HDFS
    df1.writeStream.format("csv")
      .option("checkpointLocation", "/tmp/US_UK_05052025/class_project/input/raw_data_realtime/checkpoint")
      .option("path", "/tmp/US_UK_05052025/class_project/input/raw_data_realtime/data")
      .start().awaitTermination()
  }
}