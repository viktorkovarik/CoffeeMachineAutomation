#!/usr/bin/python
#
# PDS - projekt
# Viktor Kovařík, xkovar77
#
import sys
import paho.mqtt.client as mqtt
import time
import json
import math
import cmath
import mysql.connector
import urllib

import threading

from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import cgi
from os import curdir, sep


server = "mqtt.nesad.fit.vutbr.cz" #"192.168.2.1"    # FILL IN YOUR CREDENTIALS
port = 1883
mqtt_username = "nesAtFit" #""
mqtt_password = "kolize311"

'''
server = "localhost" #"192.168.2.1"    # FILL IN YOUR CREDENTIALS
port = 1883
mqtt_username = "" #""
mqtt_password = ""
'''

mydb = mysql.connector.connect(
  host="gm.sgve.eu",
  user="sgve",
  passwd="ifilius2521",
  database="pds"
)

#HTTP PORT for API
#port=8080


global mycursor
mycursor = mydb.cursor()
'''sql = "INSERT INTO Ready (val) VALUES ('2')"
mycursor.execute(sql)

mycursor.execute("SELECT * FROM ready")


myresult = mycursor.fetchall()

for x in myresult:
  print(x)

'''

def mysql_query(sql):
    mycursor.execute(sql)
    match = mycursor.fetchall()
    #print(match)
    return match

def show_log():
    sql = """SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val FROM `action`
                UNION
                SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val FROM `consumption`
                UNION
                SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val FROM `emptywater`
                UNION
                SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val FROM `power_on`
                UNION
                SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val FROM `readcard`
                UNION
                SELECT UNIX_TIMESTAMP(`time`) as `time_unix`, val FROM `ready`
                ORDER BY time_unix DESC;
            """
    return mysql_query(sql)

def show_order_history_all():
    sql = """SELECT count(readcard.val) as `count`, readcard.val, user_list.username FROM readcard
                JOIN user_list WHERE readcard.val = user_list.cardid
                GROUP BY user_list.username
            """
    return mysql_query(sql)

def show_order_history_last_30_days():
    sql = """SELECT count(readcard.val) as `count`, readcard.val, user_list.username FROM readcard
            JOIN user_list WHERE readcard.val = user_list.cardid and (readcard.`time` > DATE_SUB(now(), INTERVAL 30 DAY))
            GROUP BY user_list.username
            """
    return mysql_query(sql)

def show_users():
    sql = "SELECT * FROM user_list"
    return mysql_query(sql)


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
        #print("message received " , cur_json)
        #print("message topic=",cur_topic)
        #print("message qos=",message.qos)
        #print("message retain flag=",message.retain)
    except UnicodeDecodeError:
        cur_topic = ""
        cur_json = ""

def machine_ready():
    ready = True 
    emptywater = False
    power_on = True
    sql = "SELECT * FROM ready WHERE val='1' ORDER BY id DESC LIMIT 1" # is ready
    mycursor.execute(sql)
    match = mycursor.fetchone()
    if match == None:
        ready = False
    sql = "SELECT * FROM emptywater WHERE val='0' ORDER BY id DESC LIMIT 1" # is not empty
    mycursor.execute(sql)
    match = mycursor.fetchone()
    if match == None: 
        emptywater = True
    sql = "SELECT * FROM power_on WHERE val='1' ORDER BY id DESC LIMIT 1" # machine is on
    mycursor.execute(sql)
    match = mycursor.fetchone()
    if match == None:
        power_on = False    
    return ready and power_on and not emptywater


def make_coffee(current_tag):
    sql = "SELECT * FROM user_list WHERE cardID=\'"+str(current_tag)+"\' AND enabled=1"
    mycursor.execute(sql)
    match = mycursor.fetchone()
    #print (match)
    if match == None:
        return
    elif machine_ready():
        client.publish("coffee/cmd","{\"MakeCoffee\":1}", qos=0, retain=False)
        sql = "INSERT INTO  consumption (val) VALUES (" + str(int(current_tag)) + ")"
        mycursor.execute(sql)
        mydb.commit()
    else:
        return

def MQTT(stop_event):
    global client
    client = mqtt.Client("PDS-coffee-backend")
    client.username_pw_set(mqtt_username,mqtt_password)
    client.connect(server)
        
    client.publish("coffee/debug","Client started", qos=0, retain=False)

    client.on_message=on_message

    mqtt_topics = create_mqtt_turple(topic)

    # subscribe to all topics at once
    client.subscribe(mqtt_topics)

    data = dict()

    global cur_topic
    global cur_json
    cur_topic = ""
    cur_json = ""
    while not stop_event.wait(1):
        try:
            client.loop()
            # filling state class with data
            if cur_json and cur_topic:
                #print(str(state.last_luminosities))
                if cur_topic == "coffee/stat":
                    data = json.loads(cur_json)
                    field = next(iter(data))
                    #print(field)
                    #print(data)
                    #set_flag(data, cur_topic)
                    if field == "Action":
                        sql = "INSERT INTO " + field + " (val) VALUES ('" + str(data[field]) +"')"
                    elif field == "ReadCard":
                        sql = "INSERT INTO " + field + " (val) VALUES (" + str(int(data[field])) +")"
                        make_coffee(data[field])
                    else:
                        sql = "INSERT INTO " + field + " (val) VALUES (" + str(int(data[field])) +")"
                    #sql = "INSERT INTO Ready (val) VALUES ('2')"
                    mycursor.execute(sql)
                    mydb.commit()

                #coffee_data[cur_topic] = float(data['value'])
                cur_json = ""
                cur_topic = ""

            #print(data)

        # What happends when you receive corrupted MQTT Message
        except ValueError:
            continue        
    # If we try to exit program by keyboard interrupt (CTRL+C) then we need to disconnect from MQTT first.
    print("Exiting automation client and stopping MQTT subscriptions and disconnecting from DB")
    client.loop_stop()
    mydb.close()
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
            elif 'orders_30days' in url:
                self.wfile.write(json.dumps(show_order_history_last_30_days()).encode())
            elif 'users' in url:
                self.wfile.write(json.dumps(show_users()).encode())
            else:
                self.wfile.write(json.dumps({'error': 'unknown_parameter'}).encode())
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))
        
        # add a property to the object, just to mess with data
        message['received'] = 'ok'
        
        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(message).encode())
        
def run(server_class=HTTPServer, handler_class=Server, port=8008):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print('Starting httpd on port %d...' % port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received: EXITING')
        pill2kill.set()
        th.join()
    finally:
        httpd.server_close()

if __name__ == "__main__":
    from sys import argv

    pill2kill = threading.Event()
    th = threading.Thread(target=MQTT, args=(pill2kill,))
    th.start()
 
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

