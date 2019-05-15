#!/usr/bin/python
#
# PDS - projekt
# Viktor Kovarik, xkovar77
#
import sys
import paho.mqtt.client as mqtt
import time
import json
import math
import cmath
import mysql.connector
import urllib
from os import environ

from random import random

import threading

from http.server import BaseHTTPRequestHandler, HTTPServer
import http.cookies

import socketserver
import cgi
from os import curdir, sep

def database_not_ready_yet(error, checking_interval_seconds):
    print('Database initialization has not yet finished. Retrying over {0} second(s). The encountered error was: {1}.'
          .format(checking_interval_seconds,
                  repr(error)))
    time.sleep(checking_interval_seconds)


def wait_for_database(host, port, db, user, password, checking_interval_seconds):
    """
    Wait until the database is ready to handle connections.

    This is necessary to ensure that the application docker container
    only starts working after the MySQL database container has finished initializing.

    More info: https://docs.docker.com/compose/startup-order/ and https://docs.docker.com/compose/compose-file/#depends_on .
    """
    print('Waiting until the database is ready to handle connections....')
    database_ready = False
    while not database_ready:
        db_connection = None
        try:
            db_connection = mysql.connector.connect(
                host=host,
                user=user,
                passwd=password
            )
            print('Database connection made.')
            db_connection.ping()
            print('Database ping successful.')
            database_ready = True
            print('The database is ready for handling incoming connections.')
        except mysql.connector.OperationalError as err:
            database_not_ready_yet(err, checking_interval_seconds)
        except mysql.connector.DatabaseError as err:
            database_not_ready_yet(err, checking_interval_seconds)
        except Exception as err:
            database_not_ready_yet(err, checking_interval_seconds)
        finally:
            if db_connection is not None: #and db_connection:
                db_connection.close()

class DB:
    conn = None
    cursor = None
    ip = None # MySQL connection IP
    port = None # MySQL connection port (e.g. 3306)
    user = None # MySQL user account (e.g. root)
    pw = None # MySQL user password
    db_name = None # Database name in MySQL
    charset = None # Character encoding (default: utf8)

    def __init__(self, ip, port, user, pw, db_name, charset=None):
        self.ip = ip
        self.port = port
        self.user = user
        self.pw = pw
        self.db_name = db_name
        if charset is None:
            self.charset = 'utf8'

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.ip,
                user=self.user,
                passwd=self.pw
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor(buffered=True)
            sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = \'"+self.db_name+"\';"
            db_exist = self.mysql_query(sql)
            if not db_exist:
                self.create_db()
            else:
                sql = "USE "+self.db_name+";"
                self.query(sql)
        except ConnectionRefusedError:
            print("Couldn't connect")
            self.cursor.reconnect(attempts=5, delay=30)

    def query(self, sql, sql_tuple=None):
        cursor = self.conn.cursor(buffered=True)
        try:
            if sql_tuple is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, sql_tuple)
        except mysql.connector.ProgrammingError:
            #self.create_db()
            pass
        except mysql.connector.Error:
            self.connect()
            if sql_tuple is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, sql_tuple)
        return cursor

    def get_connection(self):
        return self.conn
    
    def get_cursor(self):
        return self.cursor
    
    def mysql_query(self, sql):
        cursor = self.query(sql)
        match = cursor.fetchall()
        return match

    def create_db(self):
        sql_create_DB = "CREATE DATABASE IF NOT EXISTS "+self.db_name+" /*!40100 DEFAULT CHARACTER SET utf8 */;" + " USE "+self.db_name+";"
        with open('pds_db.sql', 'r') as myfile:
            sql2 = myfile.read()
        sql_create_DB+=sql2
        for sql in sql_create_DB.split(";"):
            if not sql.isspace():
                print(sql)
                self.query(sql)

server = "192.168.1.11"#environ.get('mqtt_host') # FILL IN YOUR CREDENTIALS
port = environ.get('mqtt_port')
mqtt_username = environ.get('mqtt_username') 
mqtt_password = environ.get('mqtt_password')

mysql_host = environ.get('mysql_host')
mysql_port = 3306
mysql_user = "root"
mysql_password = ""
mysql_database = "coffeeesp"

wait_for_database(mysql_host, mysql_port, mysql_database, mysql_user, mysql_password, 10)

mydb = DB(
    ip=mysql_host, 
    port=mysql_port,
    user=mysql_user,
    pw=mysql_password,
    db_name=mysql_database
)
mydb.connect()


def show_log():
    sql = """SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val, 'action' as `Event` FROM `action`
                UNION
                SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val, 'consumption' as `Event` FROM `consumption`
                UNION
                SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val, 'emptywater' as `Event` FROM `emptywater`
                UNION
                SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val, 'power_on' as `Event` FROM `power_on`
                UNION
                SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val, 'readcard' as `Event` FROM `readcard`
                UNION
                SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val, 'ready' as `Event` FROM `ready`
                ORDER BY time_unix DESC;
            """
    return mydb.mysql_query(sql)

def show_order_history_all():
    sql = """SELECT user_list.username, readcard.val, count(readcard.val) as `count`, config.grams * count(readcard.val) as grams, config.price * count(readcard.val) as price FROM config,readcard
                JOIN user_list WHERE readcard.val = user_list.cardid
                ORDER BY user_list.username
            """
    return mydb.mysql_query(sql)

def show_order_history_since_refill():
    sql = """SELECT user_list.username, readcard.val, count(readcard.val) as `count`, config.grams * count(readcard.val) as grams, config.price * count(readcard.val) as price FROM config, last_refill, readcard
                JOIN user_list WHERE readcard.val = user_list.cardid AND (readcard.`time` >  last_refill.`time`) AND last_refill.id=(SELECT MAX(id) FROM last_refill) HAVING `count` > 0
                ORDER BY user_list.username
            """
    return mydb.mysql_query(sql)

def show_users():
    sql = "SELECT * FROM user_list"
    return mydb.mysql_query(sql)

def show_unregistered_users():
    sql = "SET @cnt=0;"
    mydb.query(sql)
    sql = """SELECT (@cnt := @cnt + 1) AS id, r1.val as cardID, UNIX_TIMESTAMP(r1.`time`) as `time_unix`, COALESCE(u.username, 'unregistered') as username FROM readcard r1 LEFT JOIN user_list u ON r1.val = u.cardid
                WHERE r1.`time` = (SELECT MAX(`time`) FROM readcard r2 WHERE r1.val = r2.val) 
                ORDER BY r1.`time`;
            """
    return mydb.mysql_query(sql)

def register(cardid, username):
    sql="INSERT INTO user_list(cardid, username) VALUES("+str(cardid)+", \'"+str(username)+"\') ON DUPLICATE KEY UPDATE username='"+str(username)+"';"
    if username == "delete":
        sql="DELETE FROM user_list where cardid like \'%"+str(cardid)+"%\'"
    #print(sql)
    mydb.query(sql)
    #mydb.commit()

def refill():
    sql = "INSERT INTO last_refill(val) VALUES (1);"
    mydb.query(sql)
    #mydb.commit()

def show_config():
    sql = "SELECT * FROM config"
    return mydb.mysql_query(sql)

def set_config(price, grams):
    sql = "INSERT INTO config(id, price, grams) VALUES(1, "+str(price)+", "+str(grams)+") ON DUPLICATE KEY UPDATE price="+str(price)+", grams="+str(grams)+";"
    mydb.query(sql)
    #mydb.commit()


# topics which you want to subscribe
topic = ["coffee/stat", "coffee/cmd", "coffee/debug"]

# according to documentation it's better for performance to put into mqtt client whole turple with all topics instead of using loop
def create_mqtt_turple(lst):
    mqtt = list()
    for topic in lst:
        mqtt.append((topic, 0))
    return mqtt

# callback which is called when some data arrives
def on_message(client, userdata, message):
    try:
        global cur_topic
        global cur_json
        cur_topic = message.topic
        cur_json = message.payload.decode('utf-8')
        if cur_json and cur_topic:
            #client.publish("coffee/debug", cur_json, qos=0, retain=False)
            #print("message received " , cur_json)
            #print("message topic=",cur_topic)
            #print("message qos=",message.qos)
            #print("message retain flag=",message.retain)
            if cur_topic == "coffee/stat":

                data = json.loads(cur_json)
                field = next(iter(data))
                #print(field)
                #print(data)
                #set_flag(data, cur_topic)
                if field == "Action":
                    sql = "INSERT INTO " + field.lower() + " (val) VALUES ('" + str(data[field]) +"')"
                elif field == "ReadCard":
                    sql = "INSERT INTO " + field.lower() + " (val) VALUES (" + str(int(data[field])) +")"
                    make_coffee(data[field])
                else:
                    sql = "INSERT INTO " + field.lower() + " (val) VALUES (" + str(int(data[field])) +")"
                #sql = "INSERT INTO Ready (val) VALUES ('2')"
                mydb.query(sql)
                #mydb.commit()
            if cur_topic == "coffee/debug":
                data = json.loads(cur_json)
                field = next(iter(data))
                if field == "select":
                    pom = json.dumps(mydb.mysql_query(str(data[field]))).encode()
                    client.publish("coffee/debug", pom, qos=0, retain=False)
                elif field == "insert":
                    sql = str(data[field])
                    mydb.query(sql)
                    client.publish("coffee/debug", "DONE", qos=0, retain=False)
                elif field == "stop":
                    client.publish("coffee/debug", "STOPPING", qos=0, retain=False)
                    client.disconnect()

            #coffee_data[cur_topic] = float(data['value'])
            cur_json = ""
            cur_topic = ""

        #print(data)

    # What happends when you receive corrupted MQTT Message
    except ValueError:
        cur_json = ""
        cur_topic = ""
    '''except UnicodeDecodeError:
        cur_topic = ""
        cur_json = "" '''

def machine_ready():
    ready = True 
    emptywater = False
    power_on = True
    sql = "SELECT * FROM ready WHERE val=1 ORDER BY id DESC LIMIT 1" # is ready
    mycursor = mydb.query(sql)
    match = mycursor.fetchone()
    if match == None:
        ready = False
    sql = "SELECT * FROM emptywater WHERE val=0 ORDER BY id DESC LIMIT 1" # is not empty
    mycursor = mydb.query(sql)
    match = mycursor.fetchone()
    if match == None: 
        emptywater = True
    sql = "SELECT * FROM power_on WHERE val=1 ORDER BY id DESC LIMIT 1" # machine is on
    mycursor = mydb.query(sql)
    match = mycursor.fetchone()
    if match == None:
        power_on = False    
    return ready and power_on and not emptywater


def make_coffee(current_tag):
    sql = "SELECT * FROM user_list WHERE cardID="+str(current_tag)+" AND enabled=1"
    mycursor = mydb.query(sql)
    match = mycursor.fetchone()
    #print (match)
    if match == None:
        return
    elif machine_ready():
        client.publish("coffee/cmd","{\"MakeCoffee\":1}", qos=0, retain=False)
        sql = "INSERT INTO  consumption (val) VALUES (" + str(int(current_tag)) + ")"
        mydb.query(sql)
        #mydb.commit()
    else:
        return

def MQTT(stop_event, mydb):
    global client
    client = mqtt.Client("PDS-coffee-backend-" + str(round(random()*10)))
    client.username_pw_set(mqtt_username,mqtt_password)
    client.connect(server)
        
    client.publish("coffee/debug","Client started", qos=0, retain=False)

    client.on_message=on_message

    mqtt_topics = create_mqtt_turple(topic)

    # subscribe to all topics at once
    client.subscribe(mqtt_topics)

    '''
    data = dict()

    global cur_topic
    global cur_json
    cur_topic = ""
    cur_json = ""
    '''
    client.loop_forever()
                
    # If we try to exit program by keyboard interrupt (CTRL+C) then we need to disconnect from MQTT first.
    print("Exiting automation client and stopping MQTT subscriptions and disconnecting from DB")
    #client.loop_stop()
    mydb.get_connection().close()
    sys.exit()
            

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
    
        
    # GET sends back a Hello world message
    def do_GET(self):
        #print(self.path)
        
        cookies = http.cookies.SimpleCookie(self.headers.get('Cookie'))
        
        '''
        ## DEBUG ##
        sql="SHOW TABLES;"
        tables = mydb.mysql_query(sql)
        client.publish("coffee/debug", json.dumps(tables).encode(), qos=0, retain=False)
        s = [str(i) for i in tables]
        pom = ','.join(s)
        client.publish("coffee/debug", pom, qos=0, retain=False)
        #####################
        '''

        #print(cookies)
        if 'coffee_user' in cookies.keys():
            url = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('api', None) # https://stackoverflow.com/questions/8928730/processing-http-get-input-parameter-on-server-side-in-python
            if url == None:
                if self.path=="/":
                    self.path="/index.html"
                try:
                    #Check the file extension required and
                    #set the right mime type

                    sendReply = False
                    if self.path.endswith(".html"):
                        mimetype='text/html'
                        sendReply = True
                    if self.path.endswith(".jpg"):
                        mimetype='image/jpg'
                        sendReply = True
                    if self.path.endswith(".gif"):
                        mimetype='image/gif'
                        sendReply = True
                    if self.path.endswith(".js"):
                        mimetype='application/javascript'
                        sendReply = True
                    if self.path.endswith(".css"):
                        mimetype='text/css'
                        sendReply = True
                    if self.path.endswith(".txt"):
                        mimetype='text/plain'
                        sendReply = True
                    
                    if sendReply == True:
                        #Open the static file requested and send it
                        f = open(curdir + sep + self.path, mode='rb') 
                        self.send_response(200)
                        self.send_header('Content-type',mimetype)
                        self.end_headers()
                        self.wfile.write(f.read())
                        f.close()
                    return

                except IOError:
                    self.send_error(404,'File Not Found: %s' % self.path)
            
            else:
                self._set_headers()
                if 'log' in url:
                    self.wfile.write(json.dumps(show_log()).encode())
                elif 'orders' in url:
                    self.wfile.write(json.dumps(show_order_history_all()).encode())
                elif 'orders_since_refill' in url:
                    self.wfile.write(json.dumps(show_order_history_since_refill()).encode())
                elif 'users' in url:
                    self.wfile.write(json.dumps(show_users()).encode())
                elif 'unregistered_users' in url:
                    self.wfile.write(json.dumps(show_unregistered_users()).encode())
                elif 'configure' in url:
                        self.wfile.write(json.dumps(show_config()).encode())
                else:
                    self.wfile.write(json.dumps({'error': 'unknown_parameter'}).encode())
        else:
            mimetype='text/html'
            self.send_response(200)
            self.send_header('Content-type',mimetype)
            self.end_headers()
            html = """<form action="" method="post">Password: <input type="password" name="password" required><input type="submit"></form>"""
            self.wfile.write(bytes(html, 'utf-8'))
            
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        
        # refuse to receive non-json content
        '''if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return'''
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        #message = json.loads(self.rfile.read(length))
        data = self.rfile.read(length).decode()

        url = urllib.parse.parse_qs(data)
        # add a property to the object, just to mess with data
        #message['received'] = 'ok'
        # send the message back
        #self._set_headers()
        #self.wfile.write(json.dumps(message).encode())
    
        #print(url)
        if not 'password' in url.keys():
            self.send_response(301)
            self.send_header("Refresh", 0)
            self.end_headers()
        
        if 'refill' in url.keys():
            refill()
        if 'cardid' in url.keys() and 'username' in url.keys():
            register(url['cardid'][0], url['username'][0])
        if 'price' in url.keys() and 'grams' in url.keys():
            set_config(url['price'][0], url['grams'][0])
        if 'password' in url.keys():
            if url['password'][0] == mqtt_password:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                #print("password ok")
                cookie = http.cookies.SimpleCookie()
                cookie['coffee_user'] = True
                self.send_header("Set-Cookie", cookie.output(header='', sep=''))
                self.end_headers()
                html = """<meta http-equiv="refresh" content="1">"""
                self.wfile.write(bytes(html, 'utf-8'))
        


        
def run(server_class=HTTPServer, handler_class=Server, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print('Starting httpd on port %d...' % port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received: EXITING')
        client.publish("coffee/debug","{\"stop\":true}", qos=0, retain=False)
        pill2kill.set()
        th.join()
    finally:
        httpd.server_close()

if __name__ == "__main__":
    from sys import argv


    pill2kill = threading.Event()
    th = threading.Thread(target=MQTT, args=(pill2kill,mydb,))
    th.start()
 
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

