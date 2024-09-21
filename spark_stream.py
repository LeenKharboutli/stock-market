import logging
from datetime import datetime

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

# Create keyspace on cassandra (keyspace is like a schema)
# multiple tables per keyspace
def create_keyspace(session):
    """
    """
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """)
    logging.info("Keyspace created successfully!")


def create_table(session):
    """
    
    """
    session.execute("""
        CREATE TABLE IF NOT EXISTS spark_streams.created_users (
            id UUID PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            gender TEXT
            address TEXT,
            post_code TEXT,
            email TEXT,
            username TEXT,
            registered_date TEXT,
            phone TEXT,
            picture TEXT);
    """)

def insert_data(session, **kwargs):
    """
    insert data into cassandra
    """
    logging.info("Inserting data...")

    user_id = kwargs.get('id')
    first_name = kwargs.get('first_name')
    last_name = kwargs.get('last_name')
    gender = kwargs.get('gender')
    address = kwargs.get('address')
    postcode = kwargs.get('postcode')
    email = kwargs.get('email')
    username = kwargs.get('username')
    dob = kwargs.get('dob')
    registered_date = kwargs.get('registered_date')
    phone = kwargs.get('phone')
    picture = kwargs.get('picture')

    try:
        session.execute("""
            INSERT INTO spark_stream.created_users(id, first_name, last_name, gender,
                        address, postcode, email, username, dob, registered_date, phone, picture)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)


        """, (user_id, first_name, last_name, gender, address,
              postcode, email, username, dob, registered_date, phone, picture))
        logging.info(f"Data inserted for {first_name} {last_name}")
    except Exception as e:
        logging.error(f'Failed to insert data:\n{e}')

def create_spark_connection():
    """
    establish connection
        https://mvnrepository.com/artifact/com.datastax.spark/spark-cassandra-connector
        https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10
    """
    s_conn = None

    try:
        s_conn = SparkSession.builder\
            .appName('SparkDataStreaming')\
            .config('spark.jars.packages', "com.datastax.spark:spark-cassandra-connector_2.13:3.51",
                    "org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.1") \
            .config('spark.cassandra.connection.host', 'localhost') \
            .getOrCreate()
        s_conn.sparkContext.setLogLevel("ERROR")
        logging.info("Spark connection created successfully!")
    except Exception as e:
        logging.error(f'Could not connect:\n{e}')
    return s_conn


def connect_to_kafka(spark_conn):
    """
    Using spark connection to read data from Kafka


    Args:
        spark_conn (_type_): _description_

    Returns:
        _type_: _description_
    """
    spark_df = None
    try: 
        spark_df = spark_conn.readStream \
                    .format('kafka') \
                    .option('kafka.bootstrap.servers', 'localhost:9092') \
                    .option('subscribe', 'users_created') \
                    .option('startingOffsets, earliest') \
                    .load()
        logging.info("kafka dataframe created successfully")
    except Exception as e:
        logging.warning(f"kafka dataframe could not be created:\n{e}")

    return spark_df


def create_cassandra_connection():
    """
    establish casssandra connection
    """

    try: 
        # connecting to the cassandra cluster
        cluster = Cluster(['localhost'])
        cas_session = cluster.connect()
        return cas_session
    except Exception as e:
        logging.error(f"Could not create cassandra connection:\n{e}")
        return None


def create_selection_df_from_kafka(spark_df):
    """structure df in such a way that it can be
    inserted into cassandra db

    https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html

    Args:
        spark_df (_type_): _description_
    """

    schema = StructType([
        StructField("id", StringType(), False),
        StructField("first_name", StringType(), False),
        StructField("last_name", StringType(), False),
        StructField("gender", StringType(), False),
        StructField("address", StringType(), False),
        StructField("postcode", StringType(), False),
        StructField("email", StringType(), False),
        StructField("username", StringType(), False),
        StructField("dob", StringType(), False),
        StructField("registered_date", StringType(), False),
        StructField("phone", StringType(), False),
        StructField("picture", StringType(), False)
    ])

    sel = spark_df.selectExpr("CAST(value AS STRING)")\
        .select(from_json(col('value'), schema).alias('data.*'))
    logging.info(sel)

    return sel


if __name__ == "__main__":
    # create spark connection
    spark_conn = create_spark_connection()
    
    if spark_conn is not None:
        # connect to kafka using spark connection
        spark_df = connect_to_kafka(spark_conn)
        selection_df = create_selection_df_from_kafka(spark_df)
        session = create_cassandra_connection()

        if session is not None:
            create_keyspace(session)
            create_table(session)
            # insert_data(session)

            streaming_query = (selection_df.writeStream.format("org.apache.spark.sql.cassandra") \
                                .option('checkpointLocation', '/tmp/checkpoint') \
                                .option('keyspace', 'spark_streams') \
                                .option('table', 'created_users') \
                                .start())
            streaming_query.awaitTermination()
