"""Helpers to execute rasc entities."""
from __future__ import annotations

from collections.abc import Iterator, MutableMapping, MutableSequence, Sequence
from datetime import datetime
import random
import string
from time import time
from typing import Any, TypeVar

from homeassistant.core import Context, HomeAssistant

from .template import utcnow

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")
T = TypeVar("T")

CONFIG_ACTION_ID = "action_id"


def generate_random_id(n: int) -> str:
    """Generate random id."""
    res = "".join(random.choices(string.ascii_lowercase + string.digits, k=n))
    return res


class RoutineEntity:
    """A class that describes routine entities for Rascal Scheduler."""

    def __init__(
        self,
        hass: HomeAssistant,
        routine_id: str,
        action_script: Sequence[dict[str, Any]],
        variables: dict[str, Any] | None,
        context: Context | None,
        trigger_time: datetime | None = None,
    ) -> None:
        """Initialize a routine entity."""
        self.routine_id = routine_id
        self._hass = hass

        # for _step, _action in enumerate(action_script):
        #     _action[CONFIG_ACTION_ID] = routine_id + str(_step)

        self.action_script = action_script
        self.variables = variables
        self.context = context

        if trigger_time is None:
            self._trigger_time = utcnow(self._hass)
        else:
            self._trigger_time = trigger_time

    @property
    def get_start_time(self) -> datetime:
        """Get start time."""
        return self._trigger_time


class SubRoutineEntity:
    """A class that describes subroutine entities for Rascal Scheduler."""

    def __init__(
        self,
        hass: HomeAssistant,
        subroutine_id: str | None,
        subroutine: list[ActionEntity],
        routine: RoutineEntity,
        start_time: float | None = None,
    ) -> None:
        """Initialize a subroutine entity."""
        self._hass = hass

        if subroutine_id is None:
            self.subroutine_id = (
                routine.routine_id + "-" + generate_random_id(len(routine.routine_id))
            )
            for _no, _entity in enumerate(subroutine):
                _entity.action[CONFIG_ACTION_ID] = self.subroutine_id + "-" + str(_no)
        else:
            self.subroutine_id = subroutine_id

        self.subroutine = subroutine
        self.routine = routine

        if start_time is None:
            self._start_time = time()
        else:
            self._start_time = start_time

    @property
    def get_start_time(self) -> float:
        """Get start time."""
        return self._start_time


class ActionEntity:
    """A class that describes action entities for Rascal Scheduler."""

    def __init__(
        self,
        hass: HomeAssistant,
        action_id: str | None,
        action: dict[str, Any],
        routine: RoutineEntity,
        start_time: float | None,
    ) -> None:
        """Initialize an action entity."""
        self._hass = hass

        if action_id is not None:
            self.action_id = action_id

        self.action = action
        self.routine = routine

        if start_time is None:
            self._start_time = time()
        else:
            self._start_time = start_time

    @property
    def get_start_time(self) -> float:
        """Get start time."""
        return self._start_time


class Queue(MutableMapping[_KT, _VT]):
    """Representation of an queue for rascal scheduler."""

    __slots__ = ("_queue",)

    _queue: dict[_KT, _VT]

    def __init__(self, queue: Any) -> None:
        """Initialize a queue entity."""
        if queue is None:
            self._queue = {}
        else:
            self._queue = queue

    def __getitem__(self, __key: _KT) -> _VT:
        """Get item."""
        return self._queue[__key]

    def __delitem__(self, __key: _KT) -> None:
        """Delete item."""
        del self._queue[__key]

    def __iter__(self) -> Iterator[_KT]:
        """Iterate items."""
        return iter(self._queue)

    def __len__(self) -> int:
        """Get the size of the queue."""
        return len(self._queue)

    def __setitem__(self, __key: _KT, __value: _VT) -> None:
        """Set item."""
        self._queue[__key] = __value


class QueueEntity(MutableSequence[_VT]):
    """Representation of an queue for rascal scheduler."""

    __slots__ = ("_queue_entities",)

    _queue_entities: list[_VT]

    def __init__(self, queue_entities: Any) -> None:
        """Initialize a queue entity."""
        if queue_entities is None:
            self._queue_entities = []
        else:
            self._queue_entities = queue_entities

    def __getitem__(self, __key: Any) -> Any:
        """Get item."""
        return self._queue_entities[__key]

    def __delitem__(self, __key: Any) -> Any:
        """Delete item."""
        self._queue_entities.pop(__key)

    def __len__(self) -> int:
        """Get the size of the queue."""
        return len(self._queue_entities)

    def __setitem__(self, __key: Any, __value: Any) -> None:
        """Set item."""
        self._queue_entities[__key] = __value

    def insert(self, __key: Any, __value: Any) -> None:
        """Insert key value pair."""
        self._queue_entities.insert(__key, __value)
