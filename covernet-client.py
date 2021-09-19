import meshtastic
import sys
import tkinter as tk
import json
from tkinter.scrolledtext import ScrolledText
from pubsub import pub
import hashlib
from tkinter import simpledialog
import time
from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import Base64Encoder
import queue
import threading

class Blockchain:
	
	def __init__(self):
		#As it stands, we hardcode the pubkey of the Covernet Arbiter and the genesis block. This is okay.
		#This means that, by default, we adhere to the Covernet Arbiter.
		self.chain = []
		block = [0, "0", "Genesis block", "fe81582db2e60d3933f31981cb920ea74189e9574695c0915401e6b7332fb758"]
		self.chain.append(block)
		self.arbiterVerifyPubKey = VerifyKey(b"\xf1\xa1\xfe\x17\xf2\x11\xd5NcV\xe9*\xb3\x15\x9a\xc0\xca}jE\xd54\x1d\x10-\x8dQ7iz'M")

	def getHeadIndex(self):
		return len(self.chain)-1

	def getHeadHash(self):
		return self.chain[len(self.chain)-1][3]

	def getHeadBlock(self):
		return self.chain[len(self.chain)-1]

	def getBlock(self, index):
		return self.chain[index]

	def getBlockHash(self, index):
		return self.chain[index][3]

	def getBlockMessage(self, index):
		return self.chain[index][2]

	def verifyBlockIntegrity(self, block):

		#The signed hash of the block must contain the index (to verify timestamp and order), the previous signed hash (to verify the chain integrity) and of course the message itself
		hashBase = str(block[0])+block[1]+block[2]

		#We convert this hash-string to binary in Base64 for the NaCl lib
		hashBaseBin64 = Base64Encoder.encode(hashBase.encode())

		#We decode the Base64 signature for the NaCl lib
		signature_decoded = Base64Encoder.decode(block[3])

		try:
			self.arbiterVerifyPubKey.verify(hashBaseBin64, signature_decoded, encoder=Base64Encoder)
		except:
			return False
		return True

	def verifyBlockValidity(self, block):
		if self.verifyBlockIntegrity(block) and (block[1] == self.getBlockHash(block[0]-1)) and (block[0] == len(self.chain)):
			return True
		else:
			return False

	def verifyChainIntegrity(self):
		for block in self.chain:
			if self.verifyBlockIntegrity(block) == False:
				return False
			else:
				return True

	def verifyChainValidity(self):
		for block in self.chain[1:]:
			print(block)
			if self.verifyBlockValidity(block) == False:
				return False
		return True

	def createNewBlock(self, message):
		if is_arbiter == False:
			print("We are not the arbiter. We cannot create blocks! They would be rejected by the network")
			return

		else:
			index = self.getHeadIndex()+1
			previousBlockHash = self.getHeadHash()

			#The signed hash of the block must contain the index (to verify timestamp and order), the previous signed hash (to verify the chain integrity) and of course the message itself
			hashBase = str(index)+previousBlockHash+message
			
			#We convert this hash-string to binary for the NaCl lib
			hashBaseBin = hashBase.encode()

			#We load the base64-encoded string to use as signing key
			ArbiterSigningKeyPrivate = SigningKey(pubkey.encode(), encoder=Base64Encoder)
			signature_raw = ArbiterSigningKeyPrivate.sign(hashBaseBin, encoder=Base64Encoder)

			#We grab the signature and cast it to a string, so that we can send it
			signature_transmittable = signature_raw.signature.decode()
			block = [index, previousBlockHash, message, signature_transmittable]

		return block

	def getChain(self):
		return self.chain

	def addBlockToChain(self, block):
		self.chain.append(block)

class BlockCache:
	
	def __init__(self):
		self.cache = [0]
		self.index = 1

	def pop(self):
		try:
			currentBlock = self.cache[self.index]
		except: 
			currentBlock = None

		print("Next cached block: "+str(currentBlock))
		if currentBlock == None:
			print("Reached end of the cache")	
			return None
		if isInt(currentBlock):
			print("There is some in the cache but not current")
			print("We may be out of sync (req. next block)")
			self.requestNextMissingBlock()
			return None
		self.index = self.index + 1
		return currentBlock

	def get(self):
		return self.cache

	def requestNextMissingBlock(self):
		requestBlock(self.index)
		time.sleep(2)
		return

	def add(self, block):
		if block[0] >= len(self.cache):
			for i in range(len(self.cache), block[0]+1):
				#print(i)
				self.cache.append(i)
		self.cache[block[0]] = block
		#print(self.cache)
		return

def isInt(s):
	try: 
		int(s)
		return True
	except:
		return False

def isBlock(block):
	#We must first check if this thing can be formatted as json
	try: 
		jsonCompatible = json.loads(block)
	except:
		return False
	print(jsonCompatible)
	
	#If the length is 3 (index, prevhash, message, signature) we can assume it is something akin to a block
	if len(jsonCompatible) == 4:
		return True
	return False

def blockQueueProcessor(queue, blockCache):

	while True:
		try:
			block = queue.get_nowait()
			blockCache.add(block)
		except:
			pass

		#Let´s see if we have an interesting next block
		nextBlock = blockCache.pop()
		if nextBlock is not None:
			#print("The next block in chain is stored in our cache, proceeding")
			if blockchain.verifyBlockValidity(nextBlock):
				#print("Cached block valid, adding")
				writeToOutput(nextBlock[2])
				blockchain.addBlockToChain(nextBlock)
			else:
				print("Cached block not valid. Discarding. Possibly spam or corruption.")
		time.sleep(1)




def onReceive(packet, interface): # called when a packet arrives

	global syncing
	global is_arbiter
	global blockCache
	global blockQueue

	message = str(packet["decoded"]["text"])

	#We distribute the blocks in our chain regardless of whether we are the arbiter
	if isInt(message):
		if message == "-1":
			print("We´re at the head, apparently")
			return

		if message == "-2":
			print("We distribute the head block")
			requestedBlock = blockchain.getHeadBlock()
			sendBlock(requestedBlock)
			return

		requestBlockIndex = message
		print("Sending requested block "+requestBlockIndex)
		try:
			requestedBlock = blockchain.getBlock(int(requestBlockIndex))
			sendBlock(requestedBlock)
		except:
			print("No newer block!")
			interface.sendText("-1")
			return
		return

	# We are the arbiter - we accept messages and publish them
	if is_arbiter:
		print("Publishing foreign message")
		sender = str(packet["from"])
		newBlock = blockchain.createNewBlock(sender+": "+message)
		blockchain.addBlockToChain(newBlock)
		sendBlock(newBlock)
		writeToOutput(sender+": "+message)
		return

	# We are not the arbiter - we receive blocks and attempt to add them to our chain
	else:
		block = json.loads(str(packet["decoded"]["text"]))
		print(block)

		if block[0] < blockchain.getHeadIndex()+1:
			print("We already have this block, discarding.")
			return
		else:
			print("Current or future block, putting in the cache")
			blockQueue.put(block)

		
		#if syncing:
		#	requestNextBlock()



def sendMessage(event):

	inputText = input.get()

	#We are the Holy Arbiter. We can use our chain for sending stuff
	if is_arbiter:
		print("Publishing our own message")
		message = str(interface.getMyNodeInfo()["num"])+" ♛: "+inputText
		writeToOutput(message)
		newBlock = blockchain.createNewBlock(message)
		blockchain.addBlockToChain(newBlock)
		sendBlock(newBlock)

		return
	#We are not the Arbiter and must humbly request publication		
	else:
		print("Requesting publication")
		interface.sendText(inputText, wantAck=True)


def initCovernet(interface):

	#meshtastic --set region EU865 --set is_router true --ch-shortfast --ch-set psk none --port /dev/ttyUSB0

	node = interface.getNode("^local")
	ch = node.channels[0]
	ch.settings.psk = bytes([0])
	
   # ch.settings.bandwidth = 125
  #  ch.settings.spread_factor = 7
   # ch.settings.coding_rate = 4

	node.radioConfig.preferences.is_router = True
	node.radioConfig.preferences.region = 3

	node.writeChannel(0)
	node.setOwner("Covernet Node", "CN")
	node.writeConfig()

#def onConnection(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
	# defaults to broadcast, specify a destination ID if you wish
	#interface.sendText("hello mesh")


def sendBlock(block):
	print(json.dumps(block))
	interface.sendText(json.dumps(block), wantAck=True)

def requestBlock(index):
	interface.sendText(str(index), wantAck=True)

def requestNextBlock():
	requestBlock(blockchain.getHeadIndex()+1)

def requestHead():
	print("Requesting the head")
	interface.sendText("-2", wantAck=True)

def requestBlockGUI():
	index = (simpledialog.askstring(title="Request block", prompt="Enter the index here"))
	requestBlock(int(index))

def requestSyncGUI():
	requestHead()

def generatePrivKey():
	privKeyBase64 = SigningKey.generate().encode(encoder=Base64Encoder).decode()
	return privKeyBase64

def loadPrivKey(base64Seed):
	base64Bin = Base64Encoder.decode(base64Seed)
	signingkey = SigningKey(base64Bin)
	return signingkey

def writeToOutput(textMessage):
	text.config(state='normal')
	text.insert(tk.END, textMessage+"\n")
	text.config(state='disabled')
	input.delete(0, tk.END)

defaultHopLimit = 9

root = tk.Tk()
root.title("Covernet Client")
root.geometry("700x700")

menubar = tk.Menu(root)

root['menu'] = menubar
menu_file = tk.Menu(menubar, tearoff=0)
menu_processing = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(menu=menu_file, label='File')
menubar.add_cascade(menu=menu_processing, label='Settings')

menu_file.add_command(label='Exit', command=exit)
menu_processing.add_command(label='Request block', command=requestBlockGUI)
menu_processing.add_command(label='Request sync', command=requestSyncGUI)
text = ScrolledText(root, height = 40, width=100) 
text.config(state='disabled')
text.pack()

root.bind('<Return>', sendMessage)
input = tk.Entry(root,  width = 100)
input.pack()

blockchain = Blockchain()


syncing = True
blockQueue = queue.Queue()
blockCache = BlockCache()

pub.subscribe(onReceive, "meshtastic.receive.text")

try:
	if sys.argv[2]:
		is_arbiter = True
		pubkey = sys.argv[2]
except:
	is_arbiter = False


interface = meshtastic.SerialInterface(sys.argv[1])
#initCovernet(interface)
print(interface.getMyNodeInfo()["num"])

#blockQueue = queue.Queue()
blockQueueProcessorThread = threading.Thread(target=blockQueueProcessor, args=(blockQueue,blockCache,), daemon=True)
blockQueueProcessorThread.start()


root.mainloop()