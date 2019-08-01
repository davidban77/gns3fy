# gns3fy
Python wrapper around [GNS3 Server API](http://api.gns3.net/en/2.2/index.html).

Its main objective is to interact with the GNS3 server in a programatic way, so it can be integrated with the likes of Ansible, docker and scripts.

## Install

```
pip install gns3fy
```

### Development version

Use [poetry](https://github.com/sdispater/poetry) to install the package when cloning it.

## How it works

You can start the library and use the `Gns3Connector` object and the `Project` object.

For example:

```python
import gns3fy

# Define the server object to establish the connection
gns3_server = gns3fy.Gns3Connector("http://<server address>:3080")

# Define the lab you want to load and assign the server connector
lab = gns3fy.Project(name="API_TEST", connector=gns3_server)

# Retrieve its information and display
lab.get()

print(lab)
# Project(project_id='4b21dfb3-675a-4efa-8613-2f7fb32e76fe', name='API_TEST', status='opened', ...

# Access the project attributes
print(f"Name: {lab.name} -- Status: {lab.status} -- Is auto_closed?: {lab.auto_close}")
# Name: API_TEST -- Status: closed -- Is auto_closed?: False

# Open the project
lab.open()
print(lab.status)
# opened

# Verify the stats
print(lab.stats)
# {'drawings': 0, 'links': 4, 'nodes': 6, 'snapshots': 0}

# List the names and status of all the nodes in the project
for node in lab.nodes:
    print(f"Node: {node.name} -- Node Type: {node.node_type} -- Status: {node.status}")
# Node: Ethernetswitch-1 -- Node Type: ethernet_switch -- Status: started
# ...
```

Take a look at the API documentation for complete information about the attributes retrieved.

### Usage of Node and Link objects

You have access to the `Node` and `Link` objects as well, this gives you the ability to start, stop, suspend the individual element in a GNS3 project.

```python
from gns3fy import Node, Link, Gns3Connector

PROJECT_ID = "<some project id>"
server = Gns3Connector("http://<server address>:3080")

alpine1 = Node(project_id=PROJECT_ID, name="alpine-1", connector=server)

alpine1.get()
print(alpine1)
# Node(name='alpine-1', node_type='docker', node_directory= ...

# And you can access the attributes the same way as the project
print(f"Name: {alpine1.name} -- Status: {alpine1.status} -- Console: {alpine1.console}")
# Name: alpine-1 -- Status: started -- Console: 5005

# Stop the node and start (you can just restart it as well)
alpine1.stop()
print(alpine1.status)
# stopped

alpine1.start()
print(alpine1.status)
# started

# You can also see the Link objects assigned to this node
print(alpine1.links)
# [Link(link_id='4d9f1235-7fd1-466b-ad26-0b4b08beb778', link_type='ethernet', ....

# And in the same way you can interact with a Link object
link1 = alpine1.links[0]
print(f"Link Type: {link1.link_type} -- Capturing?: {link1.capturing} -- Endpoints: {link1.nodes}")
# Link Type: ethernet -- Capturing?: False -- Endpoints: [{'adapter_number': 2, ...
```

### Bonus

You also have some commodity methods like the `nodes_summary` and `links_summary`, that if used with a library like `tabulate` you can see the following:

```python
...
from tabulate import tabulate

nodes_summary = lab.nodes_summary(is_print=False)

print(
    tabulate(nodes_summary, headers=["Node", "Status", "Console Port", "ID"])
)
# Node              Status      Console Port  ID
# ----------------  --------  --------------  ------------------------------------
# Ethernetswitch-1  started             5000  da28e1c0-9465-4f7c-b42c-49b2f4e1c64d
# IOU1              started             5001  de23a89a-aa1f-446a-a950-31d4bf98653c
# IOU2              started             5002  0d10d697-ef8d-40af-a4f3-fafe71f5458b
# vEOS-4.21.5F-1    started             5003  8283b923-df0e-4bc1-8199-be6fea40f500
# alpine-1          started             5005  ef503c45-e998-499d-88fc-2765614b313e
# Cloud-1           started                   cde85a31-c97f-4551-9596-a3ed12c08498

links_summary = lab.links_summary(is_print=False)
print(
    tabulate(links_summary, headers=["Node A", "Port A", "Node B", "Port B"])
)
# Node A          Port A       Node B            Port B
# --------------  -----------  ----------------  -----------
# IOU1            Ethernet1/0  IOU2              Ethernet1/0
# vEOS-4.21.5F-1  Management1  Ethernetswitch-1  Ethernet0
# vEOS-4.21.5F-1  Ethernet1    alpine-1          eth0
# Cloud-1         eth1         Ethernetswitch-1  Ethernet7
```
