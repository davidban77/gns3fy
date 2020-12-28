"""Module for python GNS3 Drawings entity and useful drawing related services
"""
from .connector import Connector
from .projects import Project
from typing import TypeVar, Callable, Any, List, Optional
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

        data = {
            k: v
            for k, v in self.dict().items()
            if k not in ("_connector", "__initialised__")
            if v is not None
        }

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

        # TODO: Verify that the passed kwargs are supported ones
        _response = self._connector.http_call("put", _url, json_data=kwargs)

        # Update object
        self._update(_response.json())


def get_drawings(project: Project) -> List[Drawing]:
    """Retrieves all GNS3 Project Snapshots

    Args:

    - `project (Project)`: Project object

    Returns:

    - `List[Drawing]`: List of Drawing objects
    """

    _raw_drawings = project._connector.http_call(
        "get",
        url=f"{project._connector.base_url}/projects/{project.project_id}/drawings",
    ).json()

    return [
        Drawing(connector=project._connector, **_drawing)
        for _drawing in _raw_drawings
    ]


def search_drawing(
    project: Project, value: str, type: str = "svg"
) -> Optional[Drawing]:
    """Searches for GNS3 Drawing from a given drawing svg or ID

    Args:

    - `project (Project)`: Project object
    - `value (str)`: Drawing name of ID
    - `type (str)`: Type of attribute. `name` or `drawing_id`

    Returns:

    - `Optional[Drawing]`: `Drawing` if found, else `None`
    """
    # Refresh project
    project.get(drawings=True)

    try:
        if type == "svg":
            return next(draw for draw in get_drawings(project) if draw.svg == value)
        elif type == "drawing_id":
            return next(
                draw for draw in get_drawings(project) if draw.drawing_id == value
            )
        return None
    except StopIteration:
        return None


def create_drawing(project: Project, svg: str) -> Drawing:
    """Creates a GNS3 Project Drawing

    Args:

    - `project (Project)`: Project object
    - `svg (str)`: Drawing svg

    Raises:

    - `ValueError`: If drawing is already created

    Returns:

    - `Drawing`: Drawing object
    """

    _sdrawing = search_drawing(project, svg)

    if _sdrawing:
        raise ValueError(f"Drawing with same svg already exists: {_sdrawing}")

    _drawing = Drawing(
        connector=project._connector, project_id=project.project_id, svg=svg
    )

    _drawing.create()
    project.drawings.add(_drawing)
    return _drawing


def delete_drawing(
    project: Project, name: Optional[str] = None, drawing_id: Optional[str] = None
) -> None:
    """Deletes GNS3 Project Drawing

    Args:

    - `project (Project)`: Project object
    - `name (Optional[str], optional)`: Drawing name. Defaults to None.
    - `drawing_id (Optional[str], optional)`: Drawing ID. Defaults to None.

    Raises:

    - `ValueError`: When neither name nor ID was submitted
    - `ValueError`: When drawing was not found
    """

    if name is not None:
        _sdrawing = search_drawing(project, name)
    elif drawing_id is not None:
        _sdrawing = search_drawing(project, drawing_id, type="drawing_id")
    else:
        raise ValueError("Need to submit either name or drawing_id")

    if _sdrawing is None:
        raise ValueError("Snapshot not found")

    _sdrawing.delete()
    project.drawings.remove(_sdrawing)


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
    return (
        f'<svg height="{height}" width="{width}"><line stroke="{stroke}" stroke-width="'
        f'{stroke_width}" x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" /></svg>'
    )


def parsed_x(x: int, obj_width: int = 100) -> int:
    return x * obj_width


def parsed_y(y: int, obj_height: int = 100) -> int:
    return (y * obj_height) * -1
