### Yggdrasil IBSS net
DNS server: 200:4675:1432:cee7:15a6:7c50:df08:57ac
NTP server: 200:ca5b:f319:e9ba:17ce:9252:50e5:b47c


SSID: Yggdrasil
Frequency: 2462


# The Case for the Pi Mesh Network

Raspberry Pi ZeroW's are cheap, around 10 eur each. They need a power supply (could be battery or solar as well) and a microSD card for the OS. Their on-board wifi-modules support IBSS mode (peer-to-peer ad-hoc mode) to connect with eachother. Using the B.A.T.M.A.N. Linux kernel module, these nodes can route packets through eachother i.e. forming a redundant mesh network. A problem that remains is network addressing, i.e. how is it decided which node gets which IP-address? This is a hard scalability problem that is an academic field by itself, but when dealing with <254 nodes, Link-Local addressing can be used. Basically, each node broadcasts their desired IP address and checks if some other nodes uses it. If there is no conflict, the network is informed through this broadcast of the new node's address. Building on this is mDNS: in the broadcast a hostname can be included (i.e. node1) with each address. This means that other nodes can reach it by resolving node_1.local.

In this configuration, the intranet works basically identical to the "regular" internet, but the backbone is entirely decentralized. There are no central routers, no central DNS server and no central DHCP server. 

Aside from the scaling problem with IP-addresses, there is no innate authentication or encryption and the network is susceptible to DDOS'ing and malicious nodes attempting to impersonate another. As IBSS is unencrypted, all 2.4GHz radio traffic can be monitored by people in physical range.

The range between the nodes is a point of discussion. By default should be around ~30 meters, but using dedicated antennas and/or USB wifi-adapters could be extended (in this case a regular Pi Zero, without the on-board wifi, can be used).

With regards to utility: one node can be made an entry-node through, for example a VPN. Meaning that people can access the network through that node using the internet. Inside the intranet, there could be a number of services running on various nodes, for example:

    node_1 is connected through the Internet using its wired ethernet interface and connected to the intranet via its wifi-adapter. People connecting to the VPN through the wired adapter can as such access the rest of the internal network.

    node_2 could host a content-rich website, such as a self-hosted reddit or forum.

    node_3 could host a messaging server such as IRC or XMPP.

    node_4 could host a game server, such as Minecraft

    node_5 could host a file server.

Of course, additional nodes, including laptops and other devices (as long as they support BATMAN and IBSS mode) can be freely added to and removed from the network. The term "LAN-party" becomes something else entirely :)

### Update #1
Did some additional research and the Yggdrasil project has a working mesh protocol built as an OSI-layer 2 network. It is similar to B.A.T.M.A.N. but has some interesting features as it is right now. Basically, every node gets a unique IPv6 address based on a cryptographic key. Meaning that _all_ connections are end-to-end encrypted. This solves the above authentication and encryption problems. If used instead of B.A.T.M.A.N. in the above implementation, the setup would be more or less this:

Each node gets a link-local address by broadcasting, as in the above situation. However, through subnet/local area network multicasting, they can automagically detect other Yggdrasil nodes and add them as peers. The hypothetical entry node_1 wouldn't have to run a VPN server: people can fire up any Yggdrasil client (for Windows, Linux, Mac, Android, iOS and many other platforms) from anywhere on the Internet, enter node_1's wired IP-address, and enter the intranet. Each node is then reachable through its unique IPv6 address routed through the Yggdrasil network. Yggdrasil also supports public-key based whitelisting, meaning that we could firewall the entry-node to only allow the public keys of Cover members into the intranet.

### Update #2
With regards to more awesome features: within the Covernet we could setup a cryptocurrency limited to that network (i.e. Covercoin). Additionally we could have our own authoritative DNS server so that we can resolve .cover domains. (e.g. wiki.cover).

### Update #3
I've been doing some additional research into packet radio and an Internet of Things radio implementation called LoRa. It quickly became obvious to me that setting up TCP/IP over LoRa manually would be quite expensive. However, I later came across some hardware built by a hobbyist called "rnode". It is a *complete* €69.00 USB LoRa modem that can be attached to any computer. Using the magic of Linux, it can be easily made into a virtual ethernet adapter for said computer. Plus, because it is a universal module, it can also be used for other radio-related purposes. The actual range and possible need for external antenna remains to be seen, but in an urban environment should range in the kilometers per node. The bandwidth and latency are a limiting factor, as the latency will possibly range into hundreds of milliseconds and the bandwidth between 10 and 20 kbps. This is enough for loading simple web pages within seconds, but not much beyond that. Setting up a long-range mesh network - possibly covering the entire city - becomes possible, but the cost of individual nodes is fairly high.

### Update #4
So apparently there's a project called meshtastic.org which aims to use cheap single-board LoRa modules to send and relay messages in a mesh network. This project has done all of the low-level networking stuff and is easy to use. The modules are even slower than rnode and regular TCP/IP is unlikely to work properly, so no true intranet as in the above scenarios. However, they cost around €15-25 per node and have a range of multiple kilometers. Meshtastic provides a Python library, which we could use to write our own end-user programs to send messages and stuff to other nodes. All in all not as exciting as the other options, but far, far cheaper per node and we get to write GUI programs for Cover members.



## Ideas

Raspberry Pi mesh network @ Bernoulliborg
    Could include a "regular" wifi access point through which people can connect into the mesh, or one node could function as an internet-connected VPN server through which people can remotely connect to the local network
    Price is around €20-€25 per node, could be solar powered if deployed under a light source or outside
    Could host services such as a blogging platform, IRC server, and some websites
    Has the novelty of being a fully working, self-healing, self-configuring isolated physical intranet

Peer-to-peer client application hosted on IPFS
    Could be written in JavaScript and/or WebAssembly, using some kind of data storage on IPFS to communicate with peers

Packet radio throughout Groningen
    Radio equipment is very expensive; would be limited to only a couple of nodes and throughput is in the range of 5kb/s
ng, we can sign and encrypt all messages using PGP. All nodes would still relay this "private" message, but it would only be decipherable by the receipient
Network of Tor .onion sites
    Could be setup in a similar spirit as the mesh network with various services, but wouldn't really have anything special going for it

Writing an Android/iOS app that uses bluetooth and/or wifi for communication
    Has been done before: https://briarproject.org/

Using wifi/bluetooth radio's for something other than above
    Cheap and widely available; has utility when using regular TCP/IP


## Meshtastic application idea - Python tkinter GUI that implements an async forum and mail

A client that listens for packets that arrive on the node. Using a central server would very much simplify the architecture, but it would cause a lot of unneccesary bandwidth usage as the server may not be near. Instead, it is more bandwidth-efficient (as storage space is not a constraint) to have each node store the entire dataset locally and serve it to neighbouring clients. The network therefore requires a couple of nodes that are online 24/7

- An internet gateway that allows access to the Covernet without directly connecting a board to your PC. If I understand correctly, the Meshtastic Python library has a TCPInterface option which basically creates a serial interface over internet between a board and a client in the same way that a direct USB connection would. This would make the network accessible to people without a node, but only one user can use a board at one time.

### Update 1 - The Blockchain
In essence, we leverage Meshtastic's existing firmware and Python API to establish and interact with the mesh network. In principle, each node should relay any and all messages to all other nodes. Nodes announce the most recent block in the chain to other nodes; if a node is behind, it will request one of its peers to provide it with the missing blocks.

Each block consists of:
- A text message (can be PGP-encrypted; should include whether it is a forum post or mail directed to an individual)
- PGP-signed hash of the message
- Hash of the block
- Hash of the previous block

Each block is treated as a single "message" for Meshtastic API purposes.

Forum posts are simple, public messages signed with a PGP key to verify the authenticity of the sender.
1-to-1 mails are messages which are _also_ relayed through the entire network, but encrypted using the receipients public PGP key. 

Note that we do not use Meshtastic's API to differentiate between nodes or authenticate them. We do not need Meshtastic's built-in encryption as PGP and blockchain solves the authentication and encryption problems for us. 

In principle, we could also interact with this blockchain over TCP/IP. We could "bridge" the LoRa Covernet with the internet using bridge nodes.

I still need to think of a good consensus algorithm to ensure that all nodes agree on the correct chain. In particular, I haven't solved what happens when two nodes attempt to add a block to the end of the chain simultaneously (or if they're out of sync). In Bitcoin, the longest chain always wins (so just a matter of chance which blocks are broadcasted earlier to other nodes) and the blocks contained in the other chains are discarded. Obviously, we don't want to discard the messages in the other chains; we want them to join the main chain! I guess a node can check if their block has been included in the longest chain or if it has been orphaned, and if so, attempt to add it again to the main chain. The hashing algorithms shouldn't be fast: it should not be easy to continuously spam the network (and building ambiguity over what the most recent block is!) by generating blocks.

For the sake of simplicity, we should just give one vote to each node and ignore a Proof of Work/Proof of Stake algorithm. This will render the network vulnerable to Sybil, 51% and spam attacks, but I don't think resisting that should be within the scope of this project. Crucially, this means that someone firing up a bunch of nodes or creating a mass chain of blocks can overpower the network. It should absolutely not be possible to get to this condition by accident. 

We assume that all nodes are interested in keeping the network alive: there is no "reward" for publishing and distributing blocks as in Bitcoin.

Advantages of this system:
- Authentication of senders by their public key
- end-to-end encryption of private messages using a recipients public key
- Asynchronous; decentralised; fairly bandwidth-efficient; maximizes use of local storage to minimize required bandwidth
- Relay nodes can be dumb and simple: no software or configuration is required beyond Meshtastic's initial config and "relay any and all messages to all other nodes"
- Only user nodes have to use the Covernet software to actually process the blockchain and send/receive blocks.
      - However, there should be a couple of relay nodes that run the chain for accessability

Disadvantages of this system:
- If "backbone" nodes go offline, the network can get into a pretty serious state of desynchronization.
- New nodes will probably take _quite_ a while to get the latest block during the initial sync. This will get progressively worse as the blockchain grows in size. A possible, simple solution is to provide a bootstrap file every day or week on a public internet repository that can be loaded onto nodes to speed up the initial sync.
- LoRa is slow and the relaying, additional encryption/authentication and signalling of nodes takes up valueable air time. The amount of concurrent, actively "instant messaging" users is probably countable with one hand. The system should really be treated as a forum/email to be checked every couple of hours, and not as an instant-messaging platform.

#### An example of how this would work:

Bob wants to publish a message on the Covernet forum. He uses the Covernet GUI to write a post and presses "send". The software signs the post with Bob's private PGP key. It then creates a block that includes the message (block number 19; this is the new Height), the PGP-signed hash of the message, the hash of the most recent block on the chain, and the hash of the block itself (crucially including the hash of the previous block!!!). The software then forwards this block to the Meshtastic API. Meshtastic, using its autoconfig magic, sends this block to Meshtastic nodes in the vicinity using the LoRa module connected via USB. Dumb Meshtastic nodes (literally only a LoRa module connected to electricity) make sure that this block (in the form of a raw Meshtastic message) is propagated to all other nodes.

Among these nodes are Alice and Trudy. They not only have a LoRa module, but have it connected to the Covernet software (they're smart nodes). Their LoRa module with Meshtastic informs the software that there is a new Meshtastic message. After decoding it, it turns out to be a new block. The Covernet software checks if the block is valid, that is, whether the hash of the previous block that it includes is valid and whether the hash it provided for itself is valid. If not, the block is ignored. If it is valid, it is shown in the GUI and the locally stored chain is updated. The software sends a message using the Meshtastic API that there is a new block and informs connected smart nodes of the block update.

Alice has stored Bob's public key in the past as she received it through another medium, and the Covernet software automatically verifies that the message contained in the above block was indeed signed by Bob. 

Sending private messages is identical to forum posts, except that the message is encrypted using the receipient's public key and is therefore only readable by the receipient. The Covernet GUI detects this and omits the message from the public forum.

Now, Eve has launched the Covernet software after the above took place. She is at Height 13. The software sends a Meshtastic message to the network and asks what the next block in the chain is. The software learns that the current Height is 19 and their chain is thus out of date! The software sends another message and requests the chain of blocks leading up to the most recent one. A smart node answers and provides her with the blocks. Eve's software verifies the chain of blocks to guarantee the integrity of the data. 


### Update 2 - Conflict resolution
I've been thinking some more about how to handle consensus regarding diverging chains. A potential, but undemocratic solution is to assign an Arbiter node by public key. 

Three approaches:

1. The Arbiter broadcasts which chain is primary and valid
    As the Arbiter receives blocks, it then uniquely transmits as it confirms that it is the current head. Other nodes are informed of a block's acceptance or rejection and must modify their chains accordingly. This may cause some bandwidth-waste as nodes may have to re-compute and re-transmit their blocks when many blocks are being published.

2. Only the Arbiter may publish to the chain
    Normal nodes essentially send requests to the Arbiter for their message to be adsorbed the chain. This solves the entire problem as the chain becomes an ordinary queue BUT it is remarkably inefficient as every single message has to propagate to the Arbiter first before it is published to the entire network. This would also change the underlying communications:

When a node wants to publish a forum post or send a private mail, it has to relay a message to the Arbiter (through Meshtastic) first. The Arbiter then publishes and broadcasts a new block. In essence, the network is then more akin to a client-server model. Only the storage would be distributed: not the writing and publishing. I thought about it a bit and it is still far more efficient than a plain server-client model, as storage and chain-reading is still very efficient as it can be requested from any neighbour. The Arbiter itself cannot modify the chain nor will the network die when it is offline: it will simply only not be able to publish things. The Arbiter could decide to not publish certain messages.

3. The Arbiter does conflict resolution only
    Same as 1 but then more passive: only when it encounters diverging changes will it make a statement. Very efficient, but will suffer tremendously when the network is under load as tonnes of blocks will have to be discarded.

4. Bitcoin style longest-chain only
    The naive approach is to simply accept the chain which is the longest without an Arbiter. As nodes encounter chains which are longer than their own, they will drop their chain en prepare to re-broadcast their messages. However, this may cause the awkward situation where multiple chains run asynchronously.



Having given it some thought, it is tempting to go with a publisher Arbiter to instantly solve all read-write race conditions. In order for blocks to be valid, it must be signed by the Arbiter. All other blocks are rejected. This further prevents tampering and disrupting the network: faulty or malicious nodes cannot fill the chain with junk and spam as they are not permitted to write to the chain.

### Update 3 - Hypothetical protocol
Functions:

requestNextBlock:

requestHead:
    Request the neighbour with the highest signal strength what the most recent block is.

onReceive > blockpart
    Attempt to assemble the block
        If block is incomplete after a while, ask for missing block pieces
    
        Complete block:
            If it is an old or invalid block, do nothing.
            If it is a new and valid block, add to the chain and rebroadcast _once_ with hoplimit 0.

OnReceive > requestNextBlockPacket
        Fetch the block, divide it into messages and send it to the requester.


Arbiter functions:

publishBlock:
    Create a block, divide it into messages and send them with hoplimit 0 to all neighbours. Use get_ack to see if any node retransmits it.

### Update 4 - Some experimentation
Having experimented with Meshtastic last month, there is a bit of an issue. Aside from having to think very hard about efficient synchronization, the LoRa meshtastic modules are also very unreliable. They sometimes reboot when flooded with commands and don't always send messages reliably. Not sure if bugs or hardware limitations. Regardless: programming the Covernet is a relative pain at the moment, will look at it more during the summer. Currently, the code is very buggy and shitty. Could use some help reviewing / testing stuff.