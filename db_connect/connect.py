import psycopg2

def connect(query):
    """ Connect to the PostgreSQL database server """
    conn = None
 
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        
        # database connection parameters
        host = "localhost"  
        database = "sdb_project"
        user = "waldo"
        password = ""

        conn = psycopg2.connect(host = host, database = database, user = user, password = password)
        
        # create a cursor
        cur = conn.cursor()
        
        # execute a statement
        cur.execute(query)
        conn.commit()
        data = cur.fetchall()

        # close the communication with the PostgreSQL
        cur.close()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return(error, False)
        
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            return(data, True)

if __name__ == '__main__':
    query1 = "SELECT id, fclass, geom FROM berlin_osm_green_areas;"
    query0 = "SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_name = 'berlin_osm_green_areas';"
    fetched_tuple  = connect(query1)
    if fetched_tuple [1]:
        for elem in fetched_tuple[0]:
            print(elem)