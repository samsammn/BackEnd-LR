import psycopg2

dbName     = "LeaveRequest"
dbUser     = "postgres"
dbPassword = "fahmi12345"
dbHost     = "localhost"
dbPort     = "5432"

connection = psycopg2.connect(
        database=dbName,
        user=dbUser,
        password=dbPassword,
        host=dbHost,
        port=dbPort
    )