ThisBuild / version := "0.1.0-SNAPSHOT"

ThisBuild / scalaVersion := "2.11.12"

lazy val root = (project in file("."))
  .settings(
    name := "KafkaSample"
  )

libraryDependencies += "org.apache.spark" %% "spark-sql" % "2.4.7"
libraryDependencies += "com.lihaoyi" %% "requests" % "0.8.0"

