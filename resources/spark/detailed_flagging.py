""" countWords.py"""
import numpy

from pyspark import SparkContext
from pyspark.shell import spark
from pyspark import SQLContext
from pyspark.sql.types import *
from pyspark.sql.functions import *

import casac

from pyspark.sql.types import IntegerType, FloatType, StructField, StructType

ANTENNA_1 = 1
ANTENNA_2 = 2
TIME = 3
AMPLITUDE = 4

inputs = {
    'input_location': '/Users/dollyg/Projects/IUCAA/output/may14.ms',
    'csv_location': '/Users/dollyg/Projects/IUCAA/output/may14.csv',
    'channel': 100,
    'polarization': 'RR',
    'antenna1': range(0, 29, 1),
    'antenna2': range(0, 29, 1),
    'scan_number': 1,
    'selection': ['amplitude', 'time', 'antenna1', 'antenna2']
}


def get_data():
    ms = casac.casac.ms()
    ms.open(inputs['input_location'])
    ms.selectinit(reset=True)
    ms.selectpolarization(inputs['polarization'])
    ms.selectchannel(start=inputs['channel'])
    ms.select({'scan_number': inputs['scan_number']})
    all_data = ms.getdata(inputs['selection'])
    antenna1s = list(map(lambda antenna: int(antenna), all_data['antenna1']))
    antenna2s = list(map(lambda antenna: int(antenna), all_data['antenna2']))
    times = list(map(lambda time: float(time), all_data['time']))
    amp_data = list(map(lambda amp: float(amp), all_data['amplitude'][0][0]))
    return list(zip(antenna1s, antenna2s, times, amp_data))


def put_data(data):
    ms = casac.casac.ms()
    ms.open(inputs['input_location'])
    ms.selectinit(reset=True)
    ms.selectpolarization(inputs['polarization'])
    ms.selectchannel(start=inputs['channel'])
    ms.select({'scan_number': inputs['scan_number']})
    return ms.putdata(data)


def main():
    data = get_data()
    custom_schema = StructType(
        [StructField("antenna1", IntegerType(), False),
         StructField("antenna2", IntegerType(), False),
         StructField("time", DoubleType(), False),
         StructField("amp", DoubleType(), False)]
    )

    df = spark.createDataFrame(data, custom_schema)
    global_median = df.approxQuantile("amp", [0.50], 0)[0]
    df2 = df.withColumn("flag", lit(False))
    global_mad = df2.withColumn("deviation", abs(col("amp") - global_median))\
        .approxQuantile("deviation", [0.50], 0)[0]
    global_mad_sigma = 1.4826 * global_mad
    print("*******",global_median,global_mad, global_mad_sigma)

    df2.createOrReplaceTempView('data')
    df2.show()
    spark.sql('select distinct(time) from data').show()
    spark.sql("set global_median="+str(global_median))
    spark.sql("set global_mad_sigma="+str(global_mad_sigma*3))
    spark.sql("select time, percentile_approx(amp, 0.5) as median"
                     " from data group by time").show()
    df3_bad_times = spark.sql("select time"
                     " from data group by time having abs(percentile_approx(amp, 0.5) - ${global_median}) > ${global_mad_sigma}").show()



main()
