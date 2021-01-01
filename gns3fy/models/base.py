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

    # # NOTE: Workaround for returning Enum type values
    # def dict(
    #     self,
    #     *,
    #     include=None,
    #     exclude=None,
    #     by_alias=False,
    #     skip_defaults=None,
    #     exclude_unset=False,
    #     exclude_defaults=False,
    #     exclude_none=False,
    # ):
    #     _data = super().dict(
    #         include=include,
    #         exclude=exclude,
    #         by_alias=by_alias,
    #         skip_defaults=skip_defaults,
    #         exclude_unset=exclude_unset,
    #         exclude_defaults=exclude_defaults,
    #         exclude_none=exclude_none,
    #     )
    #     _copia = dict()
    #     for k, v in _data.items():
    #         if isinstance(v, Enum):
    #             v = v.value
    #         _copia.update({k: v})
    #     return _copia
