from typing import Optional, Dict, Any
from pydantic import BaseModel


class Port(BaseModel):
    name: Optional[str] = None
    node_id: Optional[str] = None
    short_name: Optional[str] = None
    adapter_number: Optional[int] = None
    label: Optional[Dict[str, str]] = None
    port_number: Optional[int] = None
    link_type: Optional[str] = None
    data_link_types: Optional[Dict[str, Any]] = None
