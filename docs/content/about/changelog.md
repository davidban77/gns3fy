# Upgrading and releases history

```shell
pip install -U gns3fy-next
```

## Releases

### 1.0.0 (2025)

**First release of gns3fy-next** - A fork of gns3fy with enhanced features:

**Enhancement:**

- **GNS3 API v3 Support**: Added full support for GNS3 Server API v3
  - JWT-based authentication for v3 API (automatic token handling)
  - Automatic token refresh on expiry
- **Project Locking Operations**: New methods to manage project locks
  - `get_locked()`: Check if a project is locked
  - `lock_project()`: Lock all drawings and nodes in a project
  - `unlock_project()`: Unlock all drawings and nodes in a project
  - Note: Only available with GNS3 API v3
- **create_drawing Method**: New method to create drawings directly on projects
  - Support for positioning (x, y, z coordinates)
  - Configurable lock and rotation settings
- **Enhanced nodes_inventory**: Now includes:
  - `node_id`: Unique node identifier
  - `status`: Current node status
  - `x`, `y`: Node position coordinates
  - `ports`: Detailed port information
- **Request Timeouts**: Added configurable 10-second timeout for all GNS3 API requests
- **Dependency Updates**:
  - Pydantic: `^1.0` → `^2.0`
  - Python: `^3.6` → `^3.8` (required by Pydantic 2.0)
  - Added `PyJWT` dependency for v3 authentication
  - Added `urllib3` for SSL warning handling

### 0.7.2 (Unreleased - merged into 1.0.0)

**Enhancement:**

- **GNS3 API v3 Support**: Added full support for GNS3 Server API v3
  - JWT-based authentication for v3 API (automatic token handling)
  - Automatic token refresh on expiry
- **Project Locking Operations**: New methods to manage project locks
  - `get_locked()`: Check if a project is locked
  - `lock_project()`: Lock all drawings and nodes in a project
  - `unlock_project()`: Unlock all drawings and nodes in a project
  - Note: Only available with GNS3 API v3
- **create_drawing Method**: New method to create drawings directly on projects
  - Support for positioning (x, y, z coordinates)
  - Configurable lock and rotation settings
- **Enhanced nodes_inventory**: Now includes:
  - `node_id`: Unique node identifier
  - `status`: Current node status
  - `x`, `y`: Node position coordinates
  - `ports`: Detailed port information
- **Request Timeouts**: Added configurable 10-second timeout for all GNS3 API requests
- **Dependency Updates**:
  - Pydantic: `^1.0` → `^2.0`
  - Python: `^3.6` → `^3.8` (required by Pydantic 2.0)
  - Added `PyJWT` dependency for v3 authentication
  - Added `urllib3` for SSL warning handling

### 0.7.1

**Enhancement:**

- Refactored docs for `mkdocs-material` theme
- Improved CircleCI pipeline config to use workflows, parameters and reusable commands
- Changed CI image from `miniconda3` to `circleci`. It has latest `poetry` and `curl` installed, which is needed for testing and publishing coverage.
- Added labels to `create_link` method. [PR-78](https://github.com/davidban77/gns3fy/pull/78)
- Testing is done on a per-python interpreter basis, meaning that `tox` is no longer needed.

### 0.7.0

**Enhancement:**

- Ability to manipulate SVGs. Added new methods: `create_drawing`, `update_drawing`, `delete_drawing` and `get_drawing`. Ref #66
- Added a `drawing_utils.py` module that have some helper functions to generate SVGs in the Project: `generate_rectangle_svg`, `generate_line_svg` and `generate_ellipse_svg`. Also `parsed_x` and `parsed_y` that helps positions the Nodes and drawings in the canvas.
- Python 3.8 support. Ref #68
- Added `upload_compute_image` to the `Gns3Connector` object. Thanks @skeiffer for the contribution. Ref #62

**Fix:**

- Fixes issue closing Project. Ref #71
- Update poetry and fix CI. Ref #64

### 0.6.0

**Enhancement:**

- Added `drawings` attribute. Used to gather information from `Drawing` endpoint, and for that there is also the `get_drawings` method.
- Added `arrange_nodes_circular` method, which as the name indicates it will arrange the nodes configured on a project in a circular fashion. Thanks @Krlosromero for the contribution.

### 0.5.2

**Enhancement:**

- Added `restore_snapshot` to the available snapshot methods of a project

### 0.5.1

**Fix:**

- Argument specification for project snapshot methods
- Cred argument for user-based authentication with a GNS3 server

### 0.5.0

**New features:**

- Extended templates functionality with `create_template`, `update_template` and `delete_template`. Which can be used for migrating templates between GNS3 servers

- Added compute endpoint get method from the REST API. [Compute endpoint](http://api.gns3.net/en/2.2/api/v2/controller/compute.html)
  - `get_computes`: Retrieves attributes and characteristics of the GNS3 server compute that will run the emulations.
  - `get_compute_images`: Lists images configured for a specific emulator on a compute.
  - `get_compute_ports`: Lists configured and used console ports and UDP ports on a compute.

- Added projects snapshots attribute and methods. [Snapshots endpoint](http://api.gns3.net/en/2.2/api/v2/controller/snapshot.html)
  - `snapshots`: Attribute that stores snapshots names, IDs and created times of a project. Updated by the `get_snapshots` method.
  - `get_snapshot`: Retrieves an specific snapshot information.
  - `create_snapshot` and `delete_snapshot`: Creates/Delete an specific snapshot

### 0.4.1

**Fix:**

- Dependency of python to start at version 3.6

### 0.4.0

**New features:**

- Added `get_file` and `write_file` methods to `Node` and `Project`. Useful for interacting with files that reside on the server like README files, `/etc/network/interfaces` file for docker nodes, among other cases

**Fix:**

- A "template not found" message, when creating a `Node` specifiying a missing/wrong template name.

### 0.3.0

**Enhancement:**

- `tox` for pipeline testing. [PR-15](https://github.com/davidban77/gns3fy/pull/15)
- `projects_summary` and `templates_summary` methods for `Gns3Connector`. [PR-17](https://github.com/davidban77/gns3fy/pull/17)
- Improved `nodes_inventory` method. [PR-23](https://github.com/davidban77/gns3fy/pull/23)
- Refactor of `Node` creation, basically changed the API endpoint from Node to Template. [PR-27](https://github.com/davidban77/gns3fy/pull/27)

### 0.2.0

**New features:**

- Ability to create `Project`, `Node` and `Link` instances
- Created most of the methods to interact with the REST API Endpoints.
- Added some commodity methods like `nodes_summary`
- Created the `docs`
- Improved the tests and coverage
- Added CircleCI with the following checks:
  - flake8
  - black formatting
  - pytest

### 0.1.1

**Enhancement:**

- Adding `Gns3Connector` method `get_version`

### 0.1.0

- Initial Push
