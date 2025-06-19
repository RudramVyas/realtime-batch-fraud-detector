// Enable JUnit-style report plugin
enablePlugins(JUnitXmlReportPlugin)


libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-sql" % "3.4.1" % "provided",
  "org.apache.spark" %% "spark-sql-kafka-0-10" % "3.4.1" % "provided",
  "org.scalatest" %% "scalatest" % "3.2.15" % Test,
  "org.apache.spark" %% "spark-streaming" % "3.4.1" % "provided"
)

// Tell sbt to look for tests in big_data_project/test/scala instead of default src/test/scala. Custom test directory
Test / scalaSource := baseDirectory.value / "big_data_project" / "test" / "scala"



// Ensure test output directory for Jenkins
testOptions ++= Seq(
  Tests.Argument(TestFrameworks.ScalaTest, "-u", "target/test-reports"),
  Tests.Argument("-oDF")
)

// Explicitly register test framework
testFrameworks += new TestFramework("org.scalatest.tools.Framework")