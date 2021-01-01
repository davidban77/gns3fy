"""Model for python GNS3 Drawings entity and useful drawing related services
"""
from .connector import Connector
from .base import verify_attributes
from typing import Any, Optional
from pydantic import BaseModel, PrivateAttr


class Drawing(BaseModel):
    """
    GNS3 Drawing API object. For more information visit:
    [Links Endpoint API information](
    https://gns3-server.readthedocs.io/en/2.2/api/v2/controller/drawing.html)

    **Attributes:**

    - `connector` (object): `Connector` instance used for interaction (**required**)
    - `svg` (str): SVG content of the drawing (**required** when using `create` method)
    - `project_id` (str): Project UUID (**required** when using `create` method)
    - `drawing_id` (str): Drawing UUID (**required** when using `get` method)
    - `locked` (bool): Wether the element is locked or not
    - `rotation` (int): Rotation of the element
    - `x` (int): X Property
    - `y` (int): Y Property
    - `z` (int): Z Property

    **Returns:**

    `Drawing` instance

    **Example:**

    ```python
    >>> drawing = Drawing(svg=<svg str>, connector=<Connector instance>, ...)
    >>> drawing.create()
    >>> print(drawing.rotation)
    0
    ```
    """

    _connector: Connector = PrivateAttr()
    svg: Optional[str] = None
    project_id: Optional[str] = None
    drawing_id: Optional[str] = None
    locked: bool = False
    rotation: int = 0
    x: int = 0
    y: int = 0
    z: int = 0

    class Config:
        validate_assignment = True
        extra = "ignore"

    def __init__(
        self,
        connector: Connector,
        svg: Optional[str] = None,
        project_id: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(svg=svg, project_id=project_id, **data)
        self._connector = connector

    def _update(self, data_dict) -> None:
        # Attributes are validated on assignment
        for k, v in data_dict.items():
            setattr(self, k, v)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Drawing):
            return False
        if self.drawing_id is None:
            raise ValueError("No drawing_id present. Need to initialize first")
        return other.drawing_id == self.drawing_id

    def __hash__(self) -> int:
        if self.drawing_id is None:
            raise ValueError("No drawing_id present. Need to initialize first")
        return hash(self.drawing_id)

    @verify_attributes(attrs=["_connector", "project_id", "drawing_id"])
    def get(self) -> None:
        """
        Retrieves the information from the drawing endpoint.

        **Required Attributes:**

        - `connector`
        - `project_id`
        - `drawing_id`
        """
        _url = (
            f"{self._connector.base_url}/project/{self.project_id}"
            f"/drawings/{self.drawing_id}"
        )
        _response = self._connector.http_call("get", _url)

        # Update object
        self._update(_response.json())

    @verify_attributes(attrs=["_connector", "project_id", "drawing_id"])
    def delete(self) -> None:
        """
        Deletes a drawing endpoint from the server. It sets to `None` the attributes
        `drawing_id` when executed sucessfully

        **Required Attributes:**

        - `connector`
        - `project_id`
        - `drawing_id`
        """
        _url = (
            f"{self._connector.base_url}/project/{self.project_id}"
            f"/drawings/{self.drawing_id}"
        )

        self._connector.http_call("delete", _url)

    @verify_attributes(attrs=["_connector", "svg", "project_id"])
    def create(self) -> None:
        """
        Creates a drawing.

        **Required Attributes:**

        - `connector`
        - `project_id`
        - `svg`
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}/drawings"

        data = self.dict(
            exclude_unset=True,
            exclude={"_connector", "drawing_id"},
        )

        _response = self._connector.http_call("post", _url, json_data=data)

        # Now update it
        self._update(_response.json())

    @verify_attributes(attrs=["project_id", "_connector", "drawing_id"])
    def update(self, **kwargs) -> None:
        """
        Updates the drawing instance by passing the keyword arguments of the attributes
        you want updated

        Example:

        ```python
        drawing01.update(rotation=10)
        ```

        This will update the drawing `rotation` attribute to `10`

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `drawing_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/"
            f"{self.project_id}/drawings/{self.drawing_id}"
        )

        # Apply first values on object to validate types
        for k, v in kwargs.items():
            setattr(self, k, v)

        _response = self._connector.http_call("put", _url, json_data=kwargs)

        # Update object
        self._update(_response.json())
