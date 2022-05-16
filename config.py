import logging

listen_port = 8080
app_debug = True
db_user = 'yugabyte'
db_password = 'Hackathon22!'
database = 'yugabyte'
schema = 'ysql_idiversity'
db_host = '20.55.116.99'
db_port = 5433

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)
