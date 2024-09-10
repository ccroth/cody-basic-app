FROM mysql:latest

# initializing the database with the "players" table
ADD cba_db.sql /docker-entrypoint-initdb.d

EXPOSE 3306