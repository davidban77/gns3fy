from functools import wraps
from typing import Optional, Any, Callable, List, TypeVar

from pydantic.main import BaseModel


_TFUNC = TypeVar("_TFUNC", bound=Callable[..., Any])


def verify_attributes(_func: Optional[Any] = None, attrs: List[str] = ["_connector"]):
    """
    Main checker for connector object and respective attributes for their retrieval
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


class BaseResourceModel(BaseModel):
    class Config:
        validate_assignment = True
        extra = "ignore"

    def _update(self, data_dict) -> None:
        # Attributes are validated on assignment
        for k, v in data_dict.items():
            setattr(self, k, v)
