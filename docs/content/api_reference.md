## `Gns3Connector` Objects

```python
def __init__(self, url=None, user=None, cred=None, verify=False, api_version=2)
```

Connector to be use for interaction against GNS3 server controller API.

**Attributes:**

- `url` (str): URL of the GNS3 server (**required**)
- `user` (str): User used for authentication
- `cred` (str): Password used for authentication
- `verify` (bool): Whether or not to verify SSL
- `api_version` (int): GNS3 server REST API version
- `api_calls`: Counter of amount of `http_calls` has been performed
- `base_url`: url passed + api_version
- `session`: Requests Session object

**Returns:**

`Gns3Connector` instance

**Example:**

```python
>>> server = Gns3Connector(url="http://<address>:3080")
>>> print(server.get_version())
{'local': False, 'version': '2.2.0b4'}
```

### `Gns3Connector.__init__()`

```python
def __init__(self, url=None, user=None, cred=None, verify=False, api_version=2)
```


### `Gns3Connector.create_session()`

```python
def create_session(self)
```

Creates the requests.Session object and applies the necessary parameters

### `Gns3Connector.http_call()`

```python
def http_call(self, method, url, data=None, json_data=None, headers=None, verify=False, params=None)
```

Performs the HTTP operation actioned

**Required Attributes:**

- `method` (enum): HTTP method to perform: get, post, put, delete, head,
patch (**required**)
- `url` (str): URL target (**required**)
- `data`: Dictionary or byte of request body data to attach to the Request
- `json_data`: Dictionary or List of dicts to be passed as JSON object/array
- `headers`: ictionary of HTTP Headers to attach to the Request
- `verify`: SSL Verification
- `params`: Dictionary or bytes to be sent in the query string for the Request

### `Gns3Connector.error_checker()`

```python
@staticmethod
def error_checker(response_obj)
```

Returns the error if found

### `Gns3Connector.get_version()`

```python
def get_version(self)
```

Returns the version information of GNS3 server

### `Gns3Connector.get_projects()`

```python
def get_projects(self)
```

Returns the list of the projects on the server

### `Gns3Connector.get_project_by_name()`

```python
def get_project_by_name(self, name)
```

Retrives a specific project

### `Gns3Connector.get_project_by_id()`

```python
def get_project_by_id(self, id)
```

Retrives a specific project by id

### `Gns3Connector.get_templates()`

```python
def get_templates(self)
```

Returns the templates defined on the server

### `Gns3Connector.get_template_by_name()`

```python
def get_template_by_name(self, name)
```

Retrives a specific template searching by name

### `Gns3Connector.get_template_by_id()`

```python
def get_template_by_id(self, id)
```

Retrives a specific template by id

### `Gns3Connector.get_nodes()`

```python
def get_nodes(self, project_id)
```

Retieves the nodes defined on the project

### `Gns3Connector.get_node_by_id()`

```python
def get_node_by_id(self, project_id, node_id)
```

Returns the node by locating its ID

### `Gns3Connector.get_links()`

```python
def get_links(self, project_id)
```

Retrieves the links defined in the project

### `Gns3Connector.get_link_by_id()`

```python
def get_link_by_id(self, project_id, link_id)
```

Returns the link by locating its ID

### `Gns3Connector.create_project()`

```python
def create_project(self, kwargs)
```

Pass a dictionary type object with the project parameters to be created.
Parameter `name` is mandatory. Returns project

### `Gns3Connector.delete_project()`

```python
def delete_project(self, project_id)
```

Deletes a project from server

## `Link` Objects

GNS3 Link API object. For more information visit: [Links Endpoint API information](
http://api.gns3.net/en/2.2/api/v2/controller/link/projectsprojectidlinks.html)

**Attributes:**

- `link_id` (str): Link UUID (**required** to be set when using `get` method)
- `link_type` (enum): Possible values: ethernet, serial
- `project_id` (str): Project UUID (**required**)
- `connector` (object): `Gns3Connector` instance used for interaction (**required**)
- `suspend` (bool): Suspend the link
- `nodes` (list): List of the Nodes and ports (**required** when using `create`
method, see Features/Link creation on the docs)
- `filters` (dict): Packet filter. This allow to simulate latency and errors
- `capturing` (bool): Read only property. True if a capture running on the link
- `capture_file_path` (str): Read only property. The full path of the capture file
if capture is running
- `capture_file_name` (str): Read only property. The name of the capture file if
capture is running

**Returns:**

`Link` instance

**Example:**

```python
>>> link = Link(project_id=<pr_id>, link_id=<link_id> connector=<Gns3Connector
instance>)
>>> link.get()
>>> print(link.link_type)
'ethernet'
```

### `Link.get()`

```python
def get(self)
```

Retrieves the information from the link endpoint.

**Required Attributes:**

- `project_id`
- `connector`
- `link_id`

### `Link.delete()`

```python
def delete(self)
```

Deletes a link endpoint from the project. It sets to `None` the attributes
`link_id` when executed sucessfully

**Required Attributes:**

- `project_id`
- `connector`
- `link_id`

### `Link.create()`

```python
def create(self)
```

Creates a link endpoint

**Required Attributes:**

- `project_id`
- `connector`
- `nodes`

## `Node` Objects

GNS3 Node API object. For more information visit: [Node Endpoint API information](
http://api.gns3.net/en/2.2/api/v2/controller/node/projectsprojectidnodes.html)

**Attributes:**

- `name` (str): Node name (**required** when using `create` method)
- `project_id` (str): Project UUID (**required**)
- `node_id` (str): Node UUID (**required** when using `get` method)
- `compute_id` (str): Compute identifier (**required**, default=local)
- `node_type` (enum): frame_relay_switch, atm_switch, docker, dynamips, vpcs,
traceng, virtualbox, vmware, iou, qemu (**required** when using `create` method)
- `connector` (object): `Gns3Connector` instance used for interaction (**required**)
- `template_id`: Template UUID from the which the node is from.
- `template`: Template name from the which the node is from.
- `node_directory` (str): Working directory of the node. Read only
- `status` (enum): Possible values: stopped, started, suspended
- `ports` (list): List of node ports, READ only
- `port_name_format` (str): Formating for port name {0} will be replace by port
number
- `port_segment_size` (int): Size of the port segment
- `first_port_name` (str): Name of the first port
- `properties` (dict): Properties specific to an emulator
- `locked` (bool): Whether the element locked or not
- `label` (dict): TBC
- `console` (int): Console TCP port
- `console_host` (str): Console host
- `console_auto_start` (bool): Automatically start the console when the node has
started
- `command_line` (str): Command line use to start the node
- `custom_adapters` (list): TBC
- `height` (int): Height of the node, READ only
- `width` (int): Width of the node, READ only
- `symbol` (str): Symbol of the node
- `x` (int): X position of the node
- `y` (int): Y position of the node
- `z (int): Z position of the node

**Returns:**

`Node` instance

**Example:**

```python
>>> alpine = Node(name="alpine1", node_type="docker", template="alpine",
project_id=<pr_id>, connector=<Gns3Connector instance>)
>>> alpine.create()
>>> print(alpine.node_id)
'SOME-UUID-GENERATED'
```

### `Node.get()`

```python
def get(self, get_links=True)
```

Retrieves the node information. When `get_links` is `True` it also retrieves the
links respective to the node.

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

### `Node.get_links()`

```python
def get_links(self)
```

Retrieves the links of the respective node. They will be saved at the `links`
attribute

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

### `Node.start()`

```python
def start(self)
```

Starts the node.

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

### `Node.stop()`

```python
def stop(self)
```

Stops the node.

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

### `Node.reload()`

```python
def reload(self)
```

Reloads the node.

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

### `Node.suspend()`

```python
def suspend(self)
```

Suspends the node.

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

### `Node.create()`

```python
def create(self, extra_properties={})
```

Creates a node.

By default it will fetch the nodes properties for creation based on the
`template` or `template_id` attribute supplied. This can be overriden/updated
by sending a dictionary of the properties under `extra_properties`.

**Required Attributes:**

- `project_id`
- `connector`
- `compute_id`: Defaults to "local"
- `name`
- `node_type`
- `template` or `template_id`

### `Node.delete()`

```python
def delete(self)
```

Deletes the node from the project. It sets to `None` the attributes `node_id`
and `name` when executed successfully

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

## `Project` Objects

GNS3 Project API object. For more information visit: [Project Endpoint API
information](http://api.gns3.net/en/2.2/api/v2/controller/project/projects.html)

**Attributes:**

- `name`: Project name (**required** when using `create` method)
- `project_id` (str): Project UUID (**required**)
- `connector` (object): `Gns3Connector` instance used for interaction (**required**)
- `status` (enum): Possible values: opened, closed
- `path` (str): Path of the project on the server
- `filename` (str): Project filename
- `auto_start` (bool): Project start when opened
- `auto_close` (bool): Project auto close when client cut off the notifications feed
- `auto_open` (bool): Project open when GNS3 start
- `drawing_grid_size` (int): Grid size for the drawing area for drawings
- `grid_size` (int): Grid size for the drawing area for nodes
- `scene_height` (int): Height of the drawing area
- `scene_width` (int): Width of the drawing area
- `show_grid` (bool): Show the grid on the drawing area
- `show_interface_labels` (bool): Show interface labels on the drawing area
- `show_layers` (bool): Show layers on the drawing area
- `snap_to_grid` (bool): Snap to grid on the drawing area
- `supplier` (dict): Supplier of the project
- `variables` (list): Variables required to run the project
- `zoom` (int): Zoom of the drawing area
- `stats` (dict): Project stats
- `nodes` (list): List of `Node` instances present on the project
- `links` (list): List of `Link` instances present on the project

**Returns:**

`Project` instance

**Example:**

```python
>>> lab = Project(name="lab", connector=<Gns3Connector instance>)
>>> lab.create()
>>> print(lab.status)
'opened'
```

### `Project.get()`

```python
def get(self, get_links=True, get_nodes=True, get_stats=True)
```

Retrieves the projects information.

- `get_links`: When true it also queries for the links inside the project
- `get_nodes`: When true it also queries for the nodes inside the project
- `get_stats`: When true it also queries for the stats inside the project

**Required Attributes:**

- `connector`
- `project_id` or `name`

### `Project.create()`

```python
def create(self)
```

Creates the project.

**Required Attributes:**

- `name`
- `connector`

### `Project.update()`

```python
def update(self, kwargs)
```

Updates the project instance by passing the keyword arguments of the attributes
you want to be updated

Example: `lab.update(auto_close=True)`

This will update the project `auto_close` attribute to `True`

**Required Attributes:**

- `project_id`
- `connector`

### `Project.delete()`

```python
def delete(self)
```

Deletes the project from the server. It sets to `None` the attributes
`project_id` and `name` when executed successfully

**Required Attributes:**

- `project_id`
- `connector`

### `Project.close()`

```python
def close(self)
```

Closes the project on the server.

**Required Attributes:**

- `project_id`
- `connector`

### `Project.open()`

```python
def open(self)
```

Opens the project on the server.

**Required Attributes:**

- `project_id`
- `connector`

### `Project.get_stats()`

```python
def get_stats(self)
```

Retrieve the stats of the project.

**Required Attributes:**

- `project_id`
- `connector`

### `Project.get_nodes()`

```python
def get_nodes(self)
```

Retrieve the nodes of the project.

**Required Attributes:**

- `project_id`
- `connector`

### `Project.get_links()`

```python
def get_links(self)
```

Retrieve the links of the project.

**Required Attributes:**

- `project_id`
- `connector`

### `Project.start_nodes()`

```python
def start_nodes(self, poll_wait_time=5)
```

Starts all the nodes inside the project.

- `poll_wait_time` is used as a delay when performing the next query of the
nodes status.

**Required Attributes:**

- `project_id`
- `connector`

### `Project.stop_nodes()`

```python
def stop_nodes(self, poll_wait_time=5)
```

Stops all the nodes inside the project.

- `poll_wait_time` is used as a delay when performing the next query of the
nodes status.

**Required Attributes:**

- `project_id`
- `connector`

### `Project.reload_nodes()`

```python
def reload_nodes(self, poll_wait_time=5)
```

Reloads all the nodes inside the project.

- `poll_wait_time` is used as a delay when performing the next query of the
nodes status.

**Required Attributes:**

- `project_id`
- `connector`

### `Project.suspend_nodes()`

```python
def suspend_nodes(self, poll_wait_time=5)
```

Suspends all the nodes inside the project.

- `poll_wait_time` is used as a delay when performing the next query of the
nodes status.

**Required Attributes:**

- `project_id`
- `connector`

### `Project.nodes_summary()`

```python
def nodes_summary(self, is_print=True)
```

Returns a summary of the nodes insode the project. If `is_print` is `False`, it
will return a list of tuples like:

`[(node_name, node_status, node_console, node_id) ...]`

**Required Attributes:**

- `project_id`
- `connector`

### `Project.nodes_inventory()`

```python
def nodes_inventory(self)
```

Returns an inventory-style with the nodes of the project

Example:

`{
    "router01": {
        "hostname": "127.0.0.1",
        "name": "router01",
        "console_port": 5077,
        "type": "vEOS"
    }
}`

**Required Attributes:**

- `project_id`
- `connector`

### `Project.links_summary()`

```python
def links_summary(self, is_print=True)
```

Returns a summary of the links insode the project. If `is_print` is False, it
will return a list of tuples like:

`[(node_a, port_a, node_b, port_b) ...]`

**Required Attributes:**

- `project_id`
- `connector`

### `Project.get_node()`

```python
def get_node(self, name=None, node_id=None)
```

Returns the Node object by searching for the `name` or the `node_id`.

**Required Attributes:**

- `project_id`
- `connector`
- `name` or `node_id`

**NOTE:** Run method `get_nodes()` manually to refresh list of nodes if
necessary

### `Project.get_link()`

```python
def get_link(self, link_id)
```

Returns the Link object by locating its ID

**Required Attributes:**

- `project_id`
- `connector`
- `link_id`

**NOTE:** Run method `get_links()` manually to refresh list of links if
necessary

### `Project.create_node()`

```python
def create_node(self, name=None, kwargs)
```

Creates a node.

**Required Attributes:**

- `project_id`
- `connector`
- `name`
- `node_type`
- `compute_id`: Defaults to "local"
- `template` or `template_id`

### `Project.create_link()`

```python
def create_link(self, node_a, port_a, node_b, port_b)
```

Creates a link.

**Required Attributes:**

- `project_id`
- `connector`
- `node_a`: Node name of the A side
- `port_a`: Port name of the A side (must match the `name` attribute of the
port)
- `node_b`: Node name of the B side
- `port_b`: Port name of the B side (must match the `name` attribute of the
port)

