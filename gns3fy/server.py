import os
from gns3fy import templates
from gns3fy import projects
from .connector import Connector
from typing import Dict, Any, List, Optional, Union


class Server:
    def __init__(
        self,
        url: Union[str, Connector],
        user: Optional[str] = None,
        cred: Optional[str] = None,
        verify: bool = False,
        api_version: int = 2,
        retries: int = 3,
        timeout: int = 5,
        proxies: Optional[Dict[str, Any]] = None,
    ) -> None:
        if isinstance(url, Connector):
            self.connector = url
        elif isinstance(url, str):
            self.connector = Connector(
                url=url,
                user=user,
                cred=cred,
                verify=verify,
                api_version=api_version,
                retries=retries,
                timeout=timeout,
                proxies=proxies,
            )
        else:
            raise ValueError(f"Value not supported {url}")
        self.projects = dict()
        self.templates = dict()

    def get_projects(self) -> None:
        self.projects = {p.name: p for p in projects.get_projects(self.connector)}

    def get_templates(self) -> None:
        self.templates = {t.name: t for t in templates.get_templates(self.connector)}

    def get_version(self) -> Dict[str, Any]:
        """Returns the version information of GNS3 server

        Args:

        - `connector (Connector)`: GNS3 connector object

        Returns:

        - `Dict[str, Any]`: GNS3 server version and if is local server
        """
        return self.connector.http_call(
            "get", url=f"{self.connector.base_url}/version"
        ).json()

    def get_computes(self) -> List[Dict[str, Any]]:
        """Returns a list of computes.

        Args:

        - `connector (Connector)`: GNS3 connector object

        Returns:

        - `List[Dict]`List of dictionaries of the computes attributes like cpu/memory
        usage
        """
        _url = f"{self.connector.base_url}/computes"
        return self.connector.http_call("get", _url).json()

    def get_compute_ports(self, compute_id: str = "local") -> Dict[str, Any]:
        """
        Returns ports used and configured by a compute.

        Args:

        - `connector (Connector)`: GNS3 connector object
        - `compute_id (str)`: GNS3 Compute ID. Default local

        **Returns:**

        Dictionary of `console_ports` used and range, as well as the `udp_ports`
        """
        _url = f"{self.connector.base_url}/computes/{compute_id}/ports"
        return self.connector.http_call("get", _url).json()

    def get_compute_images(
        self, emulator: str, compute_id: str = "local"
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of images available for a compute.

        Args:

        - `connector (Connector)`: GNS3 connector object
        - `emulator (str)`: Emulator. For example: `docker`, `iou`, `qemu`, and so on...
        - `compute_id (str)`: GNS3 Compute ID. Default local

        Returns:

        - `List[Dict]: `List of dictionaries with images available for the compute for
        the specified emulator
        """
        _url = f"{self.connector.base_url}/computes/{compute_id}/{emulator}/images"
        return self.connector.http_call("get", _url).json()

    def upload_compute_image(
        self, emulator: str, file_path: str, compute_id: str = "local"
    ) -> bool:
        """
        uploads an image for use by a compute.

        Args:

        - `connector (Connector)`: GNS3 connector object
        - `emulator (str)`: Emulator. For example: `docker`, `iou`, `qemu`, and so on...
        - `file_path`: path of file to be uploaded
        - `compute_id` By default is 'local'
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find file: {file_path}")

        _filename = os.path.basename(file_path)
        _url = (
            f"{self.connector.base_url}/computes/{compute_id}/"
            f"{emulator}/images/{_filename}"
        )

        _response = self.connector.http_call(
            "post", _url, data=open(file_path, "rb")  # type: ignore
        )

        if _response.status_code == 200:
            return True
        else:
            return False

    def search_project(self, name: str) -> Optional[projects.Project]:
        """Searches for GNS3 Project from a given project name or ID
        Args:
        - `connector (Connector)`: GNS3 connector object
        - `name (Optional[str], optional)`: Project name. Defaults to None.
        - `project_id (Optional[str], optional)`: Project ID. Defaults to None.
        Raises:
        - `ValueError`: If name or project ID is not submitted
        Returns:
        - `Optional[Project]`: `Project` if found, else `None`
        """
        self.get_projects()
        _project = self.projects.get(name)
        if _project:
            _project.get()
        return _project

    def create_project(self, name: str, **kwargs: Dict[str, Any]) -> projects.Project:
        """Creates a GNS3 Project

        Args:

        - `connector (Connector)`: GNS3 connector object
        - `name (str)`: Name of the project
        - `kwargs (Dict[str, Any])`: Keyword attributes of the project to create

        Raises:

        - `ValueError`: If project already exists

        Returns:

        - `Project`: Project object
        """
        _sproject = self.search_project(name)

        if _sproject:
            raise ValueError(f"Project {name} already created")

        return projects.create_project(connector=self.connector, name=name, **kwargs)

    def delete_project(self, name: str) -> bool:
        """Deletes a GNS3 Project

        Args:

        - `connector (Connector)`: GNS3 connector object
        - `name (Optional[str], optional)`: Project name. Defaults to None.
        - `project_id (Optional[str], optional)`: Project ID. Defaults to None.

        Raises:

        - `ValueError`: If name of project ID is not submitted
        - `ValueError`: If project is not found
        """
        _sproject = self.search_project(name)

        if _sproject is None:
            raise ValueError(f"Project {name} not found")

        if _sproject.delete():
            self.projects.pop(_sproject.name)
            return True
        else:
            return False

    def search_template(self, name: str) -> Optional[templates.Template]:
        """Searches for GNS3 Template from a given template name or ID
        Args:
        - `connector (Connector)`: GNS3 connector object
        - `name (Optional[str], optional)`: Template name. Defaults to None.
        - `template_id (Optional[str], optional)`: Template ID. Defaults to None.
        Raises:
        - `ValueError`: If name or template ID is not submitted
        Returns:
        - `Optional[Template]`: `Template` if found, else `None`
        """
        self.get_templates()
        return self.templates.get(name)

    def create_template(
        self, name: str, template_type: str, **kwargs: Dict[str, Any]
    ) -> templates.Template:
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
        self.get_templates()
        _stemplate = self.templates.get(name)

        if _stemplate:
            raise ValueError(f"Template {name} already exists")

        _template = templates.create_template(
            connector=self.connector, name=name, template_type=template_type, **kwargs
        )

        return _template

    def delete_template(self, name: str) -> bool:
        """Deletes a GNS3 Template

        Args:

        - `connector (Connector)`: GNS3 connector object
        - `name (Optional[str], optional)`: Template name. Defaults to None.
        - `template_id (Optional[str], optional)`: Template ID. Defaults to None.

        Raises:

        - `ValueError`: If name or template ID is not submitted
        - `ValueError`: If template is not found
        """
        self.get_templates()
        _stemplate = self.templates.get(name)

        if _stemplate is None:
            raise ValueError(f"Template {name} not found")

        if _stemplate.delete():
            self.templates.pop(_stemplate.name)
            return True
        else:
            return False
