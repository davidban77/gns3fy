"""Model for python GNS3 Template entity and useful template related services
"""
from .connector import Connector
from .base import verify_attributes
from typing import Any, Optional
from pydantic import BaseModel, PrivateAttr, validator


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


class Template(BaseModel):
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
    name: Optional[str] = None
    template_id: Optional[str] = None
    compute_id: str = "local"
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

    def _update(self, data_dict) -> None:
        # Attributes are validated on assignment
        for k, v in data_dict.items():
            setattr(self, k, v)

    @verify_attributes(attrs=["_connector", "template_id"])
    def get(self) -> None:
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
        self._update(_response.json())

    @verify_attributes(attrs=["_connector", "template_id"])
    def delete(self) -> None:
        """
        Deletes a template endpoint from the server.

        **Required Attributes:**

        - `connector`
        - `template_id`
        """
        _url = f"{self._connector.base_url}/templates/{self.template_id}"

        self._connector.http_call("delete", _url)

    @verify_attributes(attrs=["_connector", "template_id"])
    def update(self, **kwargs) -> None:
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

        # Apply first values on object to validate types
        for k, v in kwargs.items():
            setattr(self, k, v)

        _response = self._connector.http_call("put", _url, json_data=kwargs)

        # Update object
        self._update(_response.json())

    @verify_attributes(attrs=["_connector"])
    def create(self) -> None:
        """
        Creates a template. Is important to highlight that the default attributes are
        explicitly specified and that this Model *allows* extra attributes to be passed,
        making the model suitable for updating any kind of template in GNS3.

        For example:

        ```python
        >>> data = dict(template_type="qemu", adapters=...)
        # Note that `adapters` is an attribute related to the `qemu` hosts
        >>> template_eos = Template(name="Arista vEOS", **data)
        >>> template.create()
        ```

        **Required Attributes:**

        - `connector`
        """
        _url = f"{self._connector.base_url}/templates"

        data = {
            k: v
            for k, v in self.dict().items()
            if k not in ("_connector", "__initialised__")
            if v is not None
        }

        _response = self._connector.http_call("post", _url, json_data=data)

        # Now update it
        self._update(_response.json())
