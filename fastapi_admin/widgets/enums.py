import enum
from typing import Tuple, Any, Type, Dict, TypeVar

_T = TypeVar("_T")

class ChoicesMeta(enum.EnumMeta):
    """A metaclass for creating a enum choices."""

    def __new__(mcs: Type[_T], classname: str, bases: Tuple[Type[Any],], class_dict: Dict[Any, Any], **kwds: Any) -> _T:
        labels = []
        for key in class_dict._member_names:
            value = class_dict[key]
            if (
                    isinstance(value, (list, tuple)) and
                    len(value) > 1 and
                    isinstance(value[-1], (Promise, str))
            ):
                *value, label = value
                value = tuple(value)
            else:
                label = key.replace('_', ' ').title()
            labels.append(label)
            # Use dict.__setitem__() to suppress defenses against double
            # assignment in enum's classdict.
            dict.__setitem__(class_dict, key, value)
        cls = super().__new__(mcs, classname, bases, class_dict, **kwds)  # type: _T
        for member, label in zip(cls.__members__.values(), labels):
            member._label_ = label
        return enum.unique(cls)

    def __contains__(cls, member):
        if not isinstance(member, enum.Enum):
            # Allow non-enums to match against member values.
            return any(x.value == member for x in cls)
        return super().__contains__(member)

    @property
    def names(cls):
        empty = ['__empty__'] if hasattr(cls, '__empty__') else []
        return empty + [member.name for member in cls]

    @property
    def choices(cls):
        empty = [(None, cls.__empty__)] if hasattr(cls, '__empty__') else []
        return empty + [(member.value, member.label) for member in cls]

    @property
    def labels(cls):
        return [label for _, label in cls.choices]

    @property
    def values(cls):
        return [value for value, _ in cls.choices]
