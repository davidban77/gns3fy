# Welcome to gns3fy Docs!

gns3fy is a Python wrapper around [GNS3 Server API](http://api.gns3.net/en/2.2/index.html).

Its main objective is to interact with the GNS3 server in a programatic way, so it can be integrated with the likes of Ansible, docker and scripts.

## Install

```
pip install gns3fy
```

### Development version

Use [poetry](https://github.com/sdispater/poetry) to install the package when cloning it.


## Quick Start

```
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

## Release Notes

Please see the [Release Notes](changelog.md) for details
