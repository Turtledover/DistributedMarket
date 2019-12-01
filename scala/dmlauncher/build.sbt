name := "dmlauncher"
version := "1.0"
scalaVersion := "2.11.12"
libraryDependencies ++= Seq(
  ("org.postgresql" % "postgresql" % "42.2.8"),
  ("org.apache.spark" %% "spark-launcher" % "2.4.4" % "provided")
)
