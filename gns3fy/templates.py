"""Model for python GNS3 Template entity and useful template related services
"""
from .connector import Connector
from .base import verify_attributes, BaseResourceModel
from typing import Any, Optional, List, Dict
from pydantic import PrivateAttr, validator


TEMPLATE_TYPES = [
    "cloud",
    "nat",
    "ethernet_hub",
    "ethernet_switch",
    "frame_relay_switch",
    "atm_switch",
    "docker",
    "dynamips",
    "vpcs",
    "traceng",
    "virtualbox",
    "vmware",
    "iou",
    "qemu",
]


class Template(BaseResourceModel):
    """
    GNS3 Template API object. For more information visit:
    [Links Endpoint API information](
    https://gns3-server.readthedocs.io/en/2.2/api/v2/controller/template.html)

    **Attributes:**

    - `connector` (object): `Connector` instance used for interaction (**required**)
    - `name` (str): Template name (**required** when using `create` method)
    - `template_id` (str): Template UUID(**required** to be set when using `get` method)
    - `compute_id` (str): Compute identifier (**required**, default=local)
    - `builtin` (bool): If template is a GNS3 builtin template
    - `category` (str): Category of the template
    - `default_name_format` (str): Default name format
    - `symbol` (str): Symbol of the template
    - `template_type` (enum): Possible values: cloud,ethernet_hub,ethernet_switch,
    docker,dynamips,vpcs,traceng,virtualbox,vmware,iou,qemu

    **Returns:**

    `Template` instance

    **Example:**

    ```python
    >>> template = Template(name=<template name>, connector=<Connector instance>)
    >>> template.get()
    >>> print(template.template_type)
    'ethernet'
    ```
    """

    _connector: Connector = PrivateAttr()
    name: str
    template_id: str
    compute_id: Optional[str] = "local"
    builtin: bool = False
    category: Optional[str] = None
    default_name_format: Optional[str] = None
    symbol: Optional[str] = None
    template_type: Optional[str] = None

    @validator("template_type")
    def valid_template(cls, v):
        if not any(x for x in TEMPLATE_TYPES if x == v):
            raise ValueError("Not a valid GNS3 Template")
        return v

    class Config:
        validate_assignment = True
        # This will allow for extra settings when creating template
        extra = "allow"

    def __init__(
        self,
        connector: Connector,
        name: Optional[str] = None,
        template_id: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(name=name, template_id=template_id, **data)
        self._connector = connector

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Template):
            return False
        if self.template_id is None:
            raise ValueError("No template_id present. Need to initialize first")
        return other.template_id == self.template_id

    def __hash__(self) -> int:
        if self.template_id is None:
            raise ValueError("No template_id present. Need to initialize first")
        return hash(self.template_id)

    @verify_attributes(attrs=["_connector", "template_id"])
    def get(self) -> bool:
        """
        Retrieves the information from the template endpoint.

        **Required Attributes:**

        - `connector`
        - `template_id`
        """
        # Get template
        _url = f"{self._connector.base_url}/templates/{self.template_id}"
        _response = self._connector.http_call("get", _url)

        # Update object
        if _response.status_code == 200:
            self._update(_response.json())
            return True
        else:
            return False

    @verify_attributes(attrs=["_connector", "template_id"])
    def delete(self) -> bool:
        """
        Deletes a template endpoint from the server.

        **Required Attributes:**

        - `connector`
        - `template_id`
        """
        _url = f"{self._connector.base_url}/templates/{self.template_id}"

        _response = self._connector.http_call("delete", _url)

        if _response.status_code == 204:
            return True
        else:
            return False

    @verify_attributes(attrs=["_connector", "template_id"])
    def update(self, **kwargs) -> bool:
        """
        Updates the template by passing the keyword arguments of the attributes
        you want updated

        Example:

        ```python
        >>> template_eos.update(name="Arista vEOS", template_id=<template id>)
        ```

        This will update the template `name` attribute to `"Arista vEOS"`

        **Required Attributes:**

        - `template_id`
        - `connector`
        """
        _url = f"{self._connector.base_url}/templates/{self.template_id}"

        _response = self._connector.http_call("put", _url, json_data=kwargs)

        # Update object
        if _response.status_code == 200:
            self._update(_response.json())
            return True
        else:
            return False


def get_templates(connector: Connector) -> List[Template]:
    """Retrieves all GNS3 Node Templates

    Args:

    - `connector (Connector)`: GNS3 connector object

    Returns:

    - `List[Template]`: List of Template objects
    """
    _raw_templates = connector.http_call(
        "get", url=f"{connector.base_url}/templates"
    ).json()

    return [Template(connector=connector, **_template) for _template in _raw_templates]


def create_template(
    connector: Connector,
    name: str,
    template_type: str,
    compute_id: str = "local",
    **kwargs: Dict[str, Any],
) -> Template:
    """Creates a GNS3 Template

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (str)`: Name of the template
    - `kwargs (Dict[str, Any])`: Keyword attributes of the template to create

    Raises:

    - `ValueError`: If template already exists

    Returns:

    - `Template`: Template object
    """
    _url = f"{connector.base_url}/templates"

    data = dict(name=name, template_type=template_type, compute_id=compute_id, **kwargs)

    _response = connector.http_call("post", _url, json_data=data)

    return Template(connector=connector, **_response.json())
