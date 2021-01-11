from .connector import Connector
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class Port(BaseModel):
    name: Optional[str] = None
    node_name: Optional[str] = None
    node_id: Optional[str] = None
    short_name: Optional[str] = None
    adapter_number: Optional[int] = None
    label: Optional[Dict[str, str]] = None
    port_number: Optional[int] = None
    link_type: Optional[str] = None
    data_link_types: Optional[Dict[str, Any]] = None


def get_node_name(connector: Connector, project_id: str, node_id: str) -> str:
    _url = f"{connector.base_url}/projects/{project_id}/nodes/{node_id}"
    _response = connector.http_call("get", _url)
    return _response.json()["name"]


def gen_port_from_links(
    connector: Connector,
    project_id: str,
    port_data: List[Dict[str, Any]],
    resolve_node: bool,
) -> List[Port]:
    """Generate list of ports from data collected on the link nodes"""
    _ports = []
    for _port in port_data:
        _ports.append(
            Port(
                name=_port["label"].get("text"),
                node_name=get_node_name(connector, project_id, _port["node_id"])
                if resolve_node
                else None,
                **_port,
            )
        )
    return _ports
