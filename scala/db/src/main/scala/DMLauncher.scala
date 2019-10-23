package turtledover

import org.apache.spark.launcher.{SparkLauncher, SparkAppHandle}
import org.apache.spark.launcher.SparkAppHandle.Listener
import java.util.concurrent.CountDownLatch

object DMLauncher {
    def main(args: Array[String]) {
        // println("args length=" + args.length)
        // for(arg <- args) {
        //     println(arg)
        // }
        
        /* Parse arguments */
        val arglist = args.toList
        type OptionMap = Map[Symbol, String]
        def nextOption(map : OptionMap, list: List[String]) : OptionMap = {
            def isSwitch(s : String) = (s(0) == '-')
            list match {
                case Nil => map
                case "--archives" :: value :: tail => 
                    nextOption(map ++ Map('archives -> value), tail)
                case "--entry" :: value :: tail =>
                    nextOption(map ++ Map('entry -> value), tail)
                case "--py-files" :: value :: tail =>
                    nextOption(map ++ Map('pyfiles -> value), tail)
                case "--appArgs" :: value :: tail =>
                    nextOption(map ++ Map('appArgs -> value), tail)
                case "--jobid" :: value :: tail =>
                    nextOption(map ++ Map('jobid -> value), tail)
                case option :: tail => 
                    println("Unknown option " + option) 
                    sys.exit(1)
            }
        }
        val options = nextOption(Map(),arglist)
        println(options)
        
        val entry = options.getOrElse('entry, "")
        val jobid = options.getOrElse('jobid, "")
        if(entry.isEmpty() || jobid.isEmpty()) {
            println("Entry or JobId not provided")
            sys.exit(1)
        }
        println("jobid=" + jobid)
        println("entry=" + entry)

        val countDownLatch = new CountDownLatch(1)
        val job = new SparkLauncher()
            .setMaster("yarn")
            .setDeployMode("cluster")
            .addSparkArg("--queue", "default")
            .addSparkArg("--num-executors", "2")
            .addSparkArg("--executor-memory", "2G")
            .setConf("spark.eventLog.enabled", "true")
            .setConf("spark.eventLog.dir", "hdfs://master:9000/shared/log/")
            .setConf("spark.dynamicAllocation.enabled", "false")
            .setConf("spark.yarn.maxAppAttempts", "1")
            .setConf("spark.executorEnv.LD_LIBRARY_PATH", sys.env("LIB_JVM") + ":" + sys.env("LIB_HDFS"))
            .setConf("spark.executorEnv.CLASSPATH", sys.env("CLASSPATH"))
            .setConf("spark.executorEnv.LIB_HDFS", sys.env("LIB_HDFS"))
            .setConf("spark.executorEnv.LIB_JVM", sys.env("LIB_JVM"))
            .setConf("spark.yarn.appMasterEnv.PYSPARK_PYTHON", sys.env("PYSPARK_PYTHON"))
            .setConf("spark.pyspark.python", sys.env("PYSPARK_PYTHON"))
            .setConf("spark.yarn.appMasterEnv.PYTHONPATH", sys.env("PYSPARK_PYTHON"))
            .setConf("spark.executorEnv.SPARK_YARN_USER_ENV", sys.env("SPARK_YARN_USER_ENV"))
            .setAppResource(entry.toString())
            .setVerbose(true)
            // .addSparkArg("--archives", "hdfs://master:9000/user/root/mnist/input/data/mnist.zip#mnist")
            // .addAppArgs("--output", "mnist/output", "--format", "csv")

        if(options.contains('archives)) {
            val archives = options.getOrElse('archives, "")
            println("archives=" + archives)
            job.addSparkArg("--archives", archives)
        }

        if(options.contains('pyfiles)) {
            job.addPyFile(options.getOrElse('pyfiles, ""))
        }

        if(options.contains('appArgs)) {
            /* TODO: Handle command with space later */
            val appArgs = options.getOrElse('appArgs, "").split(" ")
            job.addAppArgs(appArgs:_*)
        }

        val db = new DMJobsDB()
        db.connect()

        val appHandle = job.startApplication(new SparkAppHandle.Listener() {
            // val lastState = SparkAppHandle.State.UNKNOWN
            def infoChanged(handle: SparkAppHandle): Unit = {
                
            }

            def stateChanged(handle: SparkAppHandle): Unit = {
                val appState = handle.getState()
                println(s"Spark App Id [${handle.getAppId}] State Changed. State [${handle.getState}]")

                if(appState == SparkAppHandle.State.SUBMITTED) {
                    db.update_status(jobid, "submitted")
                    db.update_spark_id(jobid, handle.getAppId)
                } else if(appState == SparkAppHandle.State.RUNNING) {
                    db.update_status(jobid, "running")
                } else if(appState == SparkAppHandle.State.FAILED) {
                    db.update_status(jobid, "failed")
                } else if(appState == SparkAppHandle.State.FINISHED) {
                    db.update_status(jobid, "finished")
                } else if(appState == SparkAppHandle.State.KILLED) {
                    db.update_status(jobid, "killed")
                } else if(appState == SparkAppHandle.State.LOST) {
                    db.update_status(jobid, "lost")
                }

                if(appState != null && appState.isFinal) {
                    countDownLatch.countDown //waiting until spark driver exits
                }
            }
        })

        countDownLatch.await()
        
        println("app_id=" + appHandle.getAppId())
        println("app_id=" + appHandle.getState())
    }
}