#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, when, regexp_replace,
    to_timestamp, hour, dayofweek, dayofmonth, udf
)
from pyspark.sql.types import ArrayType, DoubleType
from pyspark.ml.feature import StringIndexer, OneHotEncoder
from pyspark.ml import Pipeline

def main():
    print(" able to run ")


if __name__ =='__main__':
    main()