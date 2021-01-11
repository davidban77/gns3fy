"""Model for python GNS3 Drawings entity and useful drawing related services
"""
from .connector import Connector
from .base import verify_attributes, BaseResourceModel
from typing import Any, Optional, List
from pydantic import PrivateAttr


class Drawing(BaseResourceModel):
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
    drawing_id: str
    locked: bool = False
    rotation: int = 0
    x: int = 0
    y: int = 0
    z: int = 0

    def __init__(
        self,
        connector: Connector,
        svg: Optional[str] = None,
        project_id: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(svg=svg, project_id=project_id, **data)
        self._connector = connector

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
    def get(self) -> bool:
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
        if _response.status_code == 200:
            self._update(_response.json())
            return True
        else:
            return False

    @verify_attributes(attrs=["_connector", "project_id", "drawing_id"])
    def delete(self) -> bool:
        """
        Deletes a drawing endpoint from the server. It sets to `None` the attributes
        `drawing_id` when executed sucessfully

        **Required Attributes:**

        - `connector`
        - `project_id`
        - `drawing_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/{self.project_id}"
            f"/drawings/{self.drawing_id}"
        )

        _response = self._connector.http_call("delete", _url)

        if _response.status_code == 204:
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector", "drawing_id"])
    def update(self, **kwargs) -> bool:
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

        _response = self._connector.http_call("put", _url, json_data=kwargs)

        # Update object
        if _response.status_code == 201:
            self._update(_response.json())
            return True
        else:
            return False


def get_drawings(connector: Connector, project_id: str) -> List[Drawing]:
    """Retrieves all GNS3 Project Snapshots

    Args:

    - `project (Project)`: Project object

    Returns:

    - `List[Drawing]`: List of Drawing objects
    """

    _raw_drawings = connector.http_call(
        "get",
        url=f"{connector.base_url}/projects/{project_id}/drawings",
    ).json()

    return [Drawing(connector=connector, **_drawing) for _drawing in _raw_drawings]


def create_drawing(
    connector: Connector, project_id: str, svg: str, **kwargs
) -> Drawing:
    """
    Creates a drawing.

    **Required Attributes:**

    - `connector`
    - `project_id`
    - `svg`
    """
    _url = f"{connector.base_url}/projects/{project_id}/drawings"

    _response = connector.http_call("post", _url, json_data=dict(svg=svg, **kwargs))

    # Now update it
    return Drawing(connector=connector, **_response.json())


def generate_rectangle_svg(
    height: int = 100,
    width: int = 200,
    fill: str = "#ffffff",
    fill_opacity: float = 1.0,
    stroke: str = "#000000",
    stroke_width: int = 2,
) -> str:
    return (
        f'<svg height="{height}" width="{width}"><rect fill="{fill}" fill-opacity="'
        f'{fill_opacity}" height="{height}" stroke="{stroke}" stroke-width="'
        f'{stroke_width}" width="{width}" /></svg>'
    )


def generate_ellipse_svg(
    height: float = 200.0,
    width: float = 200.0,
    cx: int = 100,
    cy: int = 100,
    fill: str = "#ffffff",
    fill_opacity: float = 1.0,
    rx: int = 100,
    ry: int = 100,
    stroke: str = "#000000",
    stroke_width: int = 2,
) -> str:
    """Generated an ellipse SVG string for a Drawing"""
    return (
        f'<svg height="{height}" width="{width}"><ellipse cx="{cx}" cy="{cy}" fill="'
        f'{fill}" fill-opacity="{fill_opacity}" rx="{rx}" ry="{ry}" stroke="{stroke}" '
        f'stroke-width="{stroke_width}" /></svg>'
    )


def generate_line_svg(
    height: int = 0,
    width: int = 200,
    x1: int = 0,
    x2: int = 200,
    y1: int = 0,
    y2: int = 0,
    stroke: str = "#000000",
    stroke_width: int = 2,
) -> str:
    """Generated an line SVG string for a Drawing"""
    return (
        f'<svg height="{height}" width="{width}"><line stroke="{stroke}" stroke-width="'
        f'{stroke_width}" x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" /></svg>'
    )


def parsed_x(x: int, obj_width: int = 100) -> int:
    """Parses the X coordinate of an GNS3 drawing object"""
    return x * obj_width


def parsed_y(y: int, obj_height: int = 100) -> int:
    """Parses the Y coordinate of an GNS3 drawing object"""
    return (y * obj_height) * -1
