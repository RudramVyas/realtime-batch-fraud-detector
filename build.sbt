libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-sql" % "3.4.1" % "provided",
  "org.apache.spark" %% "spark-sql-kafka-0-10" % "3.4.1" % "provided",
  "org.apache.spark" %% "spark-streaming" % "3.4.1" % "provided",
  "org.scalatest" %% "scalatest" % "3.2.15" % Test,
  "com.lihaoyi" %% "requests" % "0.8.0" // Required to support `requests._` import
)

// Custom test directory
Test / scalaSource := baseDirectory.value / "big_data_project" / "test" / "scala"

// Only console output
testOptions += Tests.Argument("-oDF")

// Register test framework
testFrameworks += new TestFramework("org.scalatest.tools.Framework")
