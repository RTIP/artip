""" countWords.py"""
from pyspark import SparkContext
from pyspark import SQLContext
from pyspark.sql.types import *
from pyspark.sql import Row

sc = SparkContext("local", "PhaseCalib App")
sqlContext = SQLContext(sc)
custom_schema = StructType([StructField("phase", FloatType(), False)])
df = sqlContext.read.options(header='true').schema(custom_schema).csv('new_phase_data.csv')
df.describe().show()
def calibrate(row):
	return Row(row['phase']*2)
calibrated_rdd = df.rdd.map(calibrate)

calibrated_df = sqlContext.createDataFrame(calibrated_rdd, custom_schema)
calibrated_df.describe().show()
calibrated_df.write.option("header", "true").save("calibrated_phase_data.csv")

sc.stop()
