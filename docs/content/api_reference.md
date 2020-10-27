<a name="gns3fy"></a>
# gns3fy

<a name="gns3fy.Gns3Connector"></a>
## Gns3Connector Objects

```python
class Gns3Connector()
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

<a name="gns3fy.Gns3Connector.http_call"></a>
### http\_call

```python
 | http_call(method, url, data=None, json_data=None, headers=None, verify=False, params=None)
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

<a name="gns3fy.Gns3Connector.get_version"></a>
### get\_version

```python
 | get_version()
```

Returns the version information of GNS3 server

<a name="gns3fy.Gns3Connector.projects_summary"></a>
### projects\_summary

```python
 | projects_summary(is_print=True)
```

Returns a summary of the projects in the server. If `is_print` is `False`, it
will return a list of tuples like:

`[(name, project_id, total_nodes, total_links, status) ...]`

<a name="gns3fy.Gns3Connector.get_projects"></a>
### get\_projects

```python
 | get_projects()
```

Returns the list of the projects on the server

<a name="gns3fy.Gns3Connector.get_project"></a>
### get\_project

```python
 | get_project(name=None, project_id=None)
```

Retrieves a project from either a name or ID

**Required Attributes:**

- `name` or `project_id`

<a name="gns3fy.Gns3Connector.templates_summary"></a>
### templates\_summary

```python
 | templates_summary(is_print=True)
```

Returns a summary of the templates in the server. If `is_print` is `False`, it
will return a list of tuples like:

`[(name, template_id, template_type, builtin, console_type, category) ...]`

<a name="gns3fy.Gns3Connector.get_templates"></a>
### get\_templates

```python
 | get_templates()
```

Returns the templates defined on the server.

<a name="gns3fy.Gns3Connector.get_template"></a>
### get\_template

```python
 | get_template(name=None, template_id=None)
```

Retrieves a template from either a name or ID

**Required Attributes:**

- `name` or `template_id`

<a name="gns3fy.Gns3Connector.update_template"></a>
### update\_template

```python
 | update_template(name=None, template_id=None, **kwargs)
```

Updates a template by giving its name or UUID. For more information [API INFO]
(http://api.gns3.net/en/2.2/api/v2/controller/template/
templatestemplateid.html#put-v2-templates-template-id)

**Required Attributes:**

- `name` or `template_id`

<a name="gns3fy.Gns3Connector.create_template"></a>
### create\_template

```python
 | create_template(**kwargs)
```

Creates a template by giving its attributes. For more information [API INFO]
(http://api.gns3.net/en/2.2/api/v2/controller/template/
templates.html#post-v2-templates)

**Required Attributes:**

- `name`
- `compute_id` by default is 'local'
- `template_type`

<a name="gns3fy.Gns3Connector.delete_template"></a>
### delete\_template

```python
 | delete_template(name=None, template_id=None)
```

Deletes a template by giving its attributes. For more information [API INFO]
(http://api.gns3.net/en/2.2/api/v2/controller/template/
templatestemplateid.html#id16)

**Required Attributes:**

- `name` or `template_id`

<a name="gns3fy.Gns3Connector.get_nodes"></a>
### get\_nodes

```python
 | get_nodes(project_id)
```

Retieves the nodes defined on the project

**Required Attributes:**

- `project_id`

<a name="gns3fy.Gns3Connector.get_node"></a>
### get\_node

```python
 | get_node(project_id, node_id)
```

Returns the node by locating its ID.

**Required Attributes:**

- `project_id`
- `node_id`

<a name="gns3fy.Gns3Connector.get_links"></a>
### get\_links

```python
 | get_links(project_id)
```

Retrieves the links defined in the project.

**Required Attributes:**

- `project_id`

<a name="gns3fy.Gns3Connector.get_link"></a>
### get\_link

```python
 | get_link(project_id, link_id)
```

Returns the link by locating its ID.

**Required Attributes:**

- `project_id`
- `link_id`

<a name="gns3fy.Gns3Connector.create_project"></a>
### create\_project

```python
 | create_project(**kwargs)
```

Pass a dictionary type object with the project parameters to be created.

**Required Attributes:**

- `name`

**Returns**

JSON project information

<a name="gns3fy.Gns3Connector.delete_project"></a>
### delete\_project

```python
 | delete_project(project_id)
```

Deletes a project from server.

**Required Attributes:**

- `project_id`

<a name="gns3fy.Gns3Connector.get_computes"></a>
### get\_computes

```python
 | get_computes()
```

Returns a list of computes.

**Returns:**

List of dictionaries of the computes attributes like cpu/memory usage

<a name="gns3fy.Gns3Connector.get_compute"></a>
### get\_compute

```python
 | get_compute(compute_id="local")
```

Returns a compute.

**Returns:**

Dictionary of the compute attributes like cpu/memory usage

<a name="gns3fy.Gns3Connector.get_compute_images"></a>
### get\_compute\_images

```python
 | get_compute_images(emulator, compute_id="local")
```

Returns a list of images available for a compute.

**Required Attributes:**

- `emulator`: the likes of 'qemu', 'iou', 'docker' ...
- `compute_id` By default is 'local'

**Returns:**

List of dictionaries with images available for the compute for the specified
emulator

<a name="gns3fy.Gns3Connector.upload_compute_image"></a>
### upload\_compute\_image

```python
 | upload_compute_image(emulator, file_path, compute_id="local")
```

uploads an image for use by a compute.

**Required Attributes:**

- `emulator`: the likes of 'qemu', 'iou', 'docker' ...
- `file_path`: path of file to be uploaded
- `compute_id` By default is 'local'

<a name="gns3fy.Gns3Connector.get_compute_ports"></a>
### get\_compute\_ports

```python
 | get_compute_ports(compute_id="local")
```

Returns ports used and configured by a compute.

**Required Attributes:**

- `compute_id` By default is 'local'

**Returns:**

Dictionary of `console_ports` used and range, as well as the `udp_ports`

<a name="gns3fy.verify_connector_and_id"></a>
### verify\_connector\_and\_id

```python
verify_connector_and_id(f)
```

Main checker for connector object and respective object's ID for their retrieval
or actions methods.

<a name="gns3fy.Link"></a>
## Link Objects

```python
@dataclass(config=Config)
class Link()
```

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

<a name="gns3fy.Link.get"></a>
### get

```python
 | @verify_connector_and_id
 | get()
```

Retrieves the information from the link endpoint.

**Required Attributes:**

- `project_id`
- `connector`
- `link_id`

<a name="gns3fy.Link.delete"></a>
### delete

```python
 | @verify_connector_and_id
 | delete()
```

Deletes a link endpoint from the project. It sets to `None` the attributes
`link_id` when executed sucessfully

**Required Attributes:**

- `project_id`
- `connector`
- `link_id`

<a name="gns3fy.Link.create"></a>
### create

```python
 | create()
```

Creates a link endpoint

**Required Attributes:**

- `project_id`
- `connector`
- `nodes`

<a name="gns3fy.Node"></a>
## Node Objects

```python
@dataclass(config=Config)
class Node()
```

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

<a name="gns3fy.Node.get"></a>
### get

```python
 | @verify_connector_and_id
 | get(get_links=True)
```

Retrieves the node information. When `get_links` is `True` it also retrieves the
links respective to the node.

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

<a name="gns3fy.Node.get_links"></a>
### get\_links

```python
 | @verify_connector_and_id
 | get_links()
```

Retrieves the links of the respective node. They will be saved at the `links`
attribute

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

<a name="gns3fy.Node.start"></a>
### start

```python
 | @verify_connector_and_id
 | start()
```

Starts the node.

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

<a name="gns3fy.Node.stop"></a>
### stop

```python
 | @verify_connector_and_id
 | stop()
```

Stops the node.

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

<a name="gns3fy.Node.reload"></a>
### reload

```python
 | @verify_connector_and_id
 | reload()
```

Reloads the node.

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

<a name="gns3fy.Node.suspend"></a>
### suspend

```python
 | @verify_connector_and_id
 | suspend()
```

Suspends the node.

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

<a name="gns3fy.Node.update"></a>
### update

```python
 | @verify_connector_and_id
 | update(**kwargs)
```

Updates the node instance by passing the keyword arguments of the attributes
you want updated

Example:

```python
router01.update(name="router01-CSX")
```

This will update the project `auto_close` attribute to `True`

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Node.create"></a>
### create

```python
 | create()
```

Creates a node.

By default it will fetch the nodes properties for creation based on the
`template` or `template_id` attribute supplied. This can be overriden/updated
by sending a dictionary of the properties under `extra_properties`.

**Required Node instance attributes:**

- `project_id`
- `connector`
- `compute_id`: Defaults to "local"
- `template` or `template_id` - if not passed as arguments

<a name="gns3fy.Node.delete"></a>
### delete

```python
 | @verify_connector_and_id
 | delete()
```

Deletes the node from the project. It sets to `None` the attributes `node_id`
and `name` when executed successfully

**Required Attributes:**

- `project_id`
- `connector`
- `node_id`

<a name="gns3fy.Node.get_file"></a>
### get\_file

```python
 | @verify_connector_and_id
 | get_file(path)
```

Retrieve a file in the node directory.

**Required Attributes:**

- `project_id`
- `connector`
- `path`: Node's relative path of the file

<a name="gns3fy.Node.write_file"></a>
### write\_file

```python
 | @verify_connector_and_id
 | write_file(path, data)
```

Places a file content on a specified node file path. Used mainly for docker
images.

Example to update an alpine docker network interfaces:

```python
>>> data = '''
    auto eth0
    iface eth0 inet dhcp
    '''

>>> alpine_node.write_file(path='/etc/network/interfaces', data=data)
```

**Required Attributes:**

- `project_id`
- `connector`
- `path`: Node's relative path of the file
- `data`: Data to be included in the file

<a name="gns3fy.Project"></a>
## Project Objects

```python
@dataclass(config=Config)
class Project()
```

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
-.`drawings` (list): List of drawings present on the project
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

<a name="gns3fy.Project.get"></a>
### get

```python
 | get(get_links=True, get_nodes=True, get_stats=True)
```

Retrieves the projects information.

- `get_links`: When true it also queries for the links inside the project
- `get_nodes`: When true it also queries for the nodes inside the project
- `get_stats`: When true it also queries for the stats inside the project

It `get_stats` is set to `True`, it also verifies if snapshots and drawings are
inside the project and stores them in their respective attributes
(`snapshots` and `drawings`)

**Required Attributes:**

- `connector`
- `project_id` or `name`

<a name="gns3fy.Project.create"></a>
### create

```python
 | create()
```

Creates the project.

**Required Attributes:**

- `name`
- `connector`

<a name="gns3fy.Project.update"></a>
### update

```python
 | @verify_connector_and_id
 | update(**kwargs)
```

Updates the project instance by passing the keyword arguments of the attributes
you want updated

Example:

```python
lab.update(auto_close=True)
```

This will update the project `auto_close` attribute to `True`

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.delete"></a>
### delete

```python
 | @verify_connector_and_id
 | delete()
```

Deletes the project from the server. It sets to `None` the attributes
`project_id` and `name` when executed successfully

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.close"></a>
### close

```python
 | @verify_connector_and_id
 | close()
```

Closes the project on the server.

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.open"></a>
### open

```python
 | @verify_connector_and_id
 | open()
```

Opens the project on the server.

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.get_stats"></a>
### get\_stats

```python
 | @verify_connector_and_id
 | get_stats()
```

Retrieve the stats of the project.

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.get_file"></a>
### get\_file

```python
 | @verify_connector_and_id
 | get_file(path)
```

Retrieve a file in the project directory. Beware you have warranty to be able to
access only to file global to the project.

**Required Attributes:**

- `project_id`
- `connector`
- `path`: Project's relative path of the file

<a name="gns3fy.Project.write_file"></a>
### write\_file

```python
 | @verify_connector_and_id
 | write_file(path, data)
```

Places a file content on a specified project file path. Beware you have warranty
to be able to access only to file global to the project.

Example to create a README.txt for the project:

```python
>>> data = '''
    This is a README description!
    '''

>>> project.write_file(path='README.txt', data=data)
```

**Required Attributes:**

- `project_id`
- `connector`
- `path`: Project's relative path of the file
- `data`: Data to be included in the file

<a name="gns3fy.Project.get_nodes"></a>
### get\_nodes

```python
 | @verify_connector_and_id
 | get_nodes()
```

Retrieve the nodes of the project.

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.get_links"></a>
### get\_links

```python
 | @verify_connector_and_id
 | get_links()
```

Retrieve the links of the project.

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.start_nodes"></a>
### start\_nodes

```python
 | @verify_connector_and_id
 | start_nodes(poll_wait_time=5)
```

Starts all the nodes inside the project.

- `poll_wait_time` is used as a delay when performing the next query of the
nodes status.

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.stop_nodes"></a>
### stop\_nodes

```python
 | @verify_connector_and_id
 | stop_nodes(poll_wait_time=5)
```

Stops all the nodes inside the project.

- `poll_wait_time` is used as a delay when performing the next query of the
nodes status.

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.reload_nodes"></a>
### reload\_nodes

```python
 | @verify_connector_and_id
 | reload_nodes(poll_wait_time=5)
```

Reloads all the nodes inside the project.

- `poll_wait_time` is used as a delay when performing the next query of the
nodes status.

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.suspend_nodes"></a>
### suspend\_nodes

```python
 | @verify_connector_and_id
 | suspend_nodes(poll_wait_time=5)
```

Suspends all the nodes inside the project.

- `poll_wait_time` is used as a delay when performing the next query of the
nodes status.

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.nodes_summary"></a>
### nodes\_summary

```python
 | nodes_summary(is_print=True)
```

Returns a summary of the nodes insode the project. If `is_print` is `False`, it
will return a list of tuples like:

`[(node_name, node_status, node_console, node_id) ...]`

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.nodes_inventory"></a>
### nodes\_inventory

```python
 | nodes_inventory()
```

Returns an inventory-style dictionary of the nodes

Example:

`{
    "router01": {
        "server": "127.0.0.1",
        "name": "router01",
        "console_port": 5077,
        "type": "vEOS"
    }
}`

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.links_summary"></a>
### links\_summary

```python
 | links_summary(is_print=True)
```

Returns a summary of the links insode the project. If `is_print` is False, it
will return a list of tuples like:

`[(node_a, port_a, node_b, port_b) ...]`

**Required Attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.get_node"></a>
### get\_node

```python
 | get_node(name=None, node_id=None)
```

Returns the Node object by searching for the `name` or the `node_id`.

**Required Attributes:**

- `project_id`
- `connector`

**Required keyword arguments:**
- `name` or `node_id`

**NOTE:** Run method `get_nodes()` manually to refresh list of nodes if
necessary

<a name="gns3fy.Project.get_link"></a>
### get\_link

```python
 | get_link(link_id)
```

Returns the Link object by locating its ID

**Required Attributes:**

- `project_id`
- `connector`
- `link_id`

**NOTE:** Run method `get_links()` manually to refresh list of links if
necessary

<a name="gns3fy.Project.create_node"></a>
### create\_node

```python
 | create_node(**kwargs)
```

Creates a node. To know available parameters see `Node` object, specifically
the `create` method. The most basic example would be:

```python
project.create_node(name='test-switch01', template='Ethernet switch')
```

**Required Project instance attributes:**

- `project_id`
- `connector`

**Required keyword aguments:**

- `template` or `template_id`

<a name="gns3fy.Project.create_link"></a>
### create\_link

```python
 | create_link(node_a, port_a, node_b, port_b)
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

<a name="gns3fy.Project.get_snapshots"></a>
### get\_snapshots

```python
 | @verify_connector_and_id
 | get_snapshots()
```

Retrieves list of snapshots of the project

**Required Project instance attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.get_snapshot"></a>
### get\_snapshot

```python
 | get_snapshot(name=None, snapshot_id=None)
```

Returns the Snapshot by searching for the `name` or the `snapshot_id`.

**Required Attributes:**

- `project_id`
- `connector`

**Required keyword arguments:**
- `name` or `snapshot_id`

<a name="gns3fy.Project.create_snapshot"></a>
### create\_snapshot

```python
 | @verify_connector_and_id
 | create_snapshot(name)
```

Creates a snapshot of the project

**Required Project instance attributes:**

- `project_id`
- `connector`

**Required keyword aguments:**

- `name`

<a name="gns3fy.Project.delete_snapshot"></a>
### delete\_snapshot

```python
 | @verify_connector_and_id
 | delete_snapshot(name=None, snapshot_id=None)
```

Deletes a snapshot of the project

**Required Project instance attributes:**

- `project_id`
- `connector`

**Required keyword aguments:**

- `name` or `snapshot_id`

<a name="gns3fy.Project.restore_snapshot"></a>
### restore\_snapshot

```python
 | @verify_connector_and_id
 | restore_snapshot(name=None, snapshot_id=None)
```

Restore a snapshot from disk

**Required Project instance attributes:**

- `project_id`
- `connector`

**Required keyword aguments:**

- `name` or `snapshot_id`

<a name="gns3fy.Project.arrange_nodes_circular"></a>
### arrange\_nodes\_circular

```python
 | arrange_nodes_circular(radius=120)
```

Re-arrgange the existing nodes
in a circular fashion

**Attributes:**

- project instance created

**Example**

```python
>>> proj = Project(name='project_name', connector=Gns3connector)
>>> proj.arrange_nodes()
```

<a name="gns3fy.Project.get_drawing"></a>
### get\_drawing

```python
 | get_drawing(drawing_id=None)
```

Returns the drawing by searching for the `svg` or the `drawing_id`.

**Required Attributes:**

- `project_id`
- `connector`

**Required keyword arguments:**
- `svg` or `drawing_id`

<a name="gns3fy.Project.get_drawings"></a>
### get\_drawings

```python
 | @verify_connector_and_id
 | get_drawings()
```

Retrieves list of drawings  of the project

**Required Project instance attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.create_drawing"></a>
### create\_drawing

```python
 | @verify_connector_and_id
 | create_drawing(svg, locked=False, x=10, y=10, z=1)
```

Creates a drawing on the project

**Required Project instance attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.update_drawing"></a>
### update\_drawing

```python
 | @verify_connector_and_id
 | update_drawing(drawing_id, svg=None, locked=None, x=None, y=None, z=None)
```

Updates a drawing on the project

**Required Project instance attributes:**

- `project_id`
- `connector`

<a name="gns3fy.Project.delete_drawing"></a>
### delete\_drawing

```python
 | @verify_connector_and_id
 | delete_drawing(drawing_id=None)
```

Deletes a drawing of the project

**Required Project instance attributes:**

- `project_id`
- `connector`

**Required keyword aguments:**

- `drawing_id`

