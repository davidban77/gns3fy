"""Module for python GNS3 Template entity and useful template related services
"""
from .connector import Connector
from typing import TypeVar, Callable, Any, List, Optional
from enum import Enum
from functools import wraps
from pydantic import BaseModel, PrivateAttr


_TFUNC = TypeVar("_TFUNC", bound=Callable[..., Any])


def verify_attributes(_func: Optional[Any] = None, attrs: List[str] = ["_connector"]):
    """
    Main checker for connector object and respective object's ID for their retrieval
    or actions methods.
    """

    def decorator_verify_attributes(func: _TFUNC) -> _TFUNC:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attr in attrs:
                if getattr(self, attr) is None:
                    raise ValueError(f"Parameter is not set: {attr}")
            return func(self, *args, **kwargs)

        return wrapper  # type: ignore

    if _func is None:
        return decorator_verify_attributes
    else:
        return decorator_verify_attributes(_func)


class TemplateType(Enum):
    cloud = "cloud"
    ethernet_hub = "ethernet_hub"
    ethernet_switch = "ethernet_switch"
    docker = "docker"
    dynamips = "dynamips"
    vpcs = "vpcs"
    traceng = "traceng"
    virtualbox = "virtualbox"
    vmware = "vmware"
    iou = "iou"
    qemu = "qemu"


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
    template_type: Optional[TemplateType] = None

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


def search_template(
    connector: Connector, value: str, type: str = "name"
) -> Optional[Template]:
    """Searches for GNS3 Template from a given template name or ID

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `value (str)`: Template name of ID
    - `type (str)`: Type of attribute. `name` or `template_id`

    Returns:

    - `Optional[Template]`: `Template` if found, else `None`
    """
    try:
        if type == "name":
            return next(tplt for tplt in get_templates(connector) if tplt.name == value)
        elif type == "template_id":
            return next(
                tplt for tplt in get_templates(connector) if tplt.template_id == value
            )
        return None
    except StopIteration:
        return None


def create_template(connector: Connector, name: str) -> Template:
    """Creates a GNS3 Template

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (str)`: Name of the template

    Raises:

    - `ValueError`: If template already exists

    Returns:

    - `Template`: Template object
    """
    _stemplate = search_template(connector, name)

    if _stemplate:
        raise ValueError(f"Template with same name already exists: {name}")

    _template = Template(connector=connector, name=name)

    _template.create()
    return _template


def delete_template(
    connector: Connector, name: Optional[str] = None, template_id: Optional[str] = None
) -> None:
    """Deletes a GNS3 Template

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (Optional[str], optional)`: Template name. Defaults to None.
    - `template_id (Optional[str], optional)`: Template ID. Defaults to None.

    Raises:

    - `ValueError`: If name of template ID is not submitted
    - `ValueError`: If template is not found
    """
    if name is not None:
        _stemplate = search_template(connector, name)
    elif template_id is not None:
        _stemplate = search_template(connector, template_id, type="template_id")
    else:
        raise ValueError("Need to submit either name or template_id")

    if _stemplate is None:
        raise ValueError("Template not found")

    _stemplate.delete()


def duplicate_template(
    connector: Connector, name: Optional[str] = None, template_id: Optional[str] = None
) -> Template:
    """Duplicates a GNS3 Node Template given a template name or ID.

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (Optional[str])`: Template name
    - `template_id (Optional[str])`: Template ID

    Raises:

    - `ValueError`: When neither name nor ID was submitted
    - `ValueError`: If template does not exist

    Returns:

    - `Template`: Template object
    """
    if name is not None:
        _stemplate = search_template(connector, name)
    elif template_id is not None:
        _stemplate = search_template(connector, template_id, type="template_id")
    else:
        raise ValueError("Need to submit either name or template_id")

    if not _stemplate:
        raise ValueError("Template not found")

    _stemplate.get()

    _url = f"{connector.base_url}/templates/{_stemplate.template_id}/duplicate"

    _response = connector.http_call("post", _url).json()

    _template = Template(connector=connector, template_id=_response["template_id"])

    _template.get()

    return _template
