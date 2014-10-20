import threading
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import json
import socket
import time
import datetime
import random
import uuid
 
#dem variables
def numClients():
	return sum(strims.itervalues())

strims = {}

#takes care of updating console
def printStatus():
	threading.Timer(240, printStatus).start()
	print 'Currently connected clients: ' + str(numClients())
	
	for key, value in strims.items():
		print key, value

def resetStrims():
	threading.Timer(21600, resetStrims).start()
	print '##### RESETTING STRIMS LIST. RIP. #####'
	
	strims.clear()

#ayy lmao
#if self.is_enlightened_by(self.intelligence):
#	self.is_euphoric = True

#Stat tracking websocket server
#Hiring PHP developers does not contribute to the quota of employees with disabilities.
class WSHandler(tornado.websocket.WebSocketHandler):
	clients = {}
	ping_every = 15

	def __init__(self, application, request, **kwargs):
		tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
		self.io_loop = tornado.ioloop.IOLoop.instance()

	def check_origin(self, origin):
		return True

	def open(self):
		self.id = uuid.uuid4()
		print 'Opened Websocket connection: (' + self.request.remote_ip + ') ' + socket.getfqdn(self.request.remote_ip + " id: ") + str(self.id)
		self.clients[str(self.id)] = {'id': self.id}
		print len(self.clients)
		# Ping to make sure the agent is alive.
		self.io_loop.add_timeout(datetime.timedelta(seconds=5), self.send_ping)
	
	def on_connection_timeout(self):
		print "-- Client timed out aftter 1 minute"
		self.close()

	def send_ping(self):
		print("<- [PING] " + str(self.id))
		try:
			self.ping(str(self.id))
			self.ping_timeout = self.io_loop.add_timeout(datetime.timedelta(seconds=self.ping_every), self.on_connection_timeout)
		except Exception as ex:
			print("-- Failed to send ping! to: "+ str(self.id) + " because of " + repr(ex))
			self.clients.pop(str(self.id), None)
		
	def on_pong(self, data):
		# We received a pong, remove the timeout so that we don't
		# kill the connection.
		print("-> [PONG] %s" % data)

		if hasattr(self, "ping_timeout"):
			self.io_loop.remove_timeout(self.ping_timeout)

		# Wait 5 seconds before pinging again.
		self.io_loop.add_timeout(datetime.timedelta(seconds=self.ping_every), self.send_ping)


	def on_message(self, message):
		global strims
		global numClients
		fromClient = json.loads(message)

		if fromClient[u'strim'] == "/destinychat?s=strims&stream=":
			fromClient[u'strim'] = "/destinychat"

		#handle session counting - This is a fucking mess :^(
		if fromClient[u'action'] == "join":
			strims.setdefault(fromClient[u'strim'], 0)
			strims[fromClient[u'strim']] += 1
			data_string = json.dumps({"streams":strims[fromClient[u'strim']], "totalviewers":numClients()})
			self.write_message(str(strims[fromClient[u'strim']]) + " OverRustle.com Viewers")
			print 'User Connected: Watching %s' % (fromClient[u'strim'])

		elif fromClient[u'action'] == "unjoin":
			strims.setdefault(fromClient[u'strim'], 0)
			strims[fromClient[u'strim']]  -= 1
			print 'User Disconnected: Was Watching %s' % (fromClient[u'strim'])

		elif fromClient[u'action'] == "viewerCount":
			strims.setdefault(fromClient[u'strim'], 0)
			self.write_message(str(strims[fromClient[u'strim']]) + " OverRustle.com Viewers")

		elif fromClient[u'action'] == "api":
			self.write_message(json.dumps({"streams":strims, "totalviewers":numClients}))

		else:
			print 'WTF: Client sent unknown command >:( %s' % (fromClient[u'action'])


		#remove the dict key if nobody is watching DaFeels
		if strims[fromClient[u'strim']] <= 0:
			#print 'Removing Dict value: %s' % (fromClient[u'strim'])
			strims.pop(fromClient[u'strim'], None)

	def on_close(self):
		print 'Closed Websocket connection: (' + self.request.remote_ip + ') ' + socket.getfqdn(self.request.remote_ip)+ " id: "+str(self.id)
		self.clients.pop(str(self.id), None)
		print len(self.clients)

#print console updates
printStatus()
resetStrims()

#JSON api server
class APIHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps({"streams":strims, "totalviewers":numClients()}))

#GET address handlers
application = tornado.web.Application([
    (r'/ws', WSHandler),
    (r'/api', APIHandler)
])
 
#starts the server on port 9998
if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(9998)
	tornado.ioloop.IOLoop.instance().start()
