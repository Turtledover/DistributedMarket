name := "custom-spark-listener"
version := "1.0"
scalaVersion := "2.11.12"
libraryDependencies ++= Seq(
  ("org.apache.spark" %% "spark-core" % "2.4.4").
    exclude("org.mortbay.jetty", "servlet-api").
    exclude("commons-beanutils", "commons-beanutils-core").
    exclude("commons-collections", "commons-collections").
    exclude("commons-logging", "commons-logging").
    exclude("com.esotericsoftware.minlog", "minlog")
)

assemblyOption in assembly := (assemblyOption in assembly).value.copy(includeScala = false)



// assemblyMergeStrategy in assembly := {
//   case _ => MergeStrategy.first
// }