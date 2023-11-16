"""Support for rasc."""
from __future__ import annotations

from collections.abc import Sequence
from time import time
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.rascalscheduler import (
    ActionEntity,
    Queue,
    QueueEntity,
    RoutineEntity,
    SubRoutineEntity,
)

from .const import DOMAIN, LOGGER

CONFIG_ACTION_ID = "action_id"

INITIAL_STATE = "start"
READY_STATE = "ready"
ACTIVE_STATE = "active"


def setup_rascal_scheduler_entity(hass: HomeAssistant) -> None:
    """Set up RASC scheduler entity."""
    hass.data[DOMAIN] = RascalSchedulerEntity()


def create_x_active_queue(hass: HomeAssistant, entity_id: str) -> None:
    """Create queue for x entity."""
    rascal_scheduler = hass.data[DOMAIN]
    active_routines = rascal_scheduler.get_active_routines()
    active_routines[entity_id] = QueueEntity({})


def delete_x_active_queue(hass: HomeAssistant, entity_id: str) -> None:
    """Delete x entity queue."""
    try:
        rascal_scheduler = hass.data[DOMAIN]
        active_routines = rascal_scheduler.get_active_routines()
        del active_routines[entity_id]
    except (KeyError, ValueError):
        LOGGER.warning("Unable to delete unknown queue %s", entity_id)


# []: break a routine into multiple subroutines
def dag_operator(
    hass: HomeAssistant,
    data_operation_type: str,
    action_script: Sequence[dict[str, Any]],
    routine: RoutineEntity,
) -> list[SubRoutineEntity]:
    """Analyze data dependencies and break the routine into multiple subroutines."""
    subroutines = []
    entities = []

    cur_time = time()
    for _step, _action in enumerate(action_script):
        start_time = cur_time + _step * 10
        entity = ActionEntity(
            hass,
            None,
            _action,
            routine,
            start_time,
        )
        entities.append(entity)
        subroutine = SubRoutineEntity(hass, None, entities, routine, start_time)

        subroutines.append(subroutine)

    return subroutines


# []: change the state of the routines
# def routine_state_change(oldstate: str, newstate: str, subroutine: SubRoutineEntity):
#     """change the routine from old state to new state"""

#     match newstate:
#         case READY_STATE:
#         case ACTIVE_STATE:

#         case _:
#             LOGGER.error("Unable to process unknown state %s", newstate)


#     LOGGER.debug("Change the subroutine %s state from %s to %s", )


# # []add subroutines to ready routines
# def add_routines_to_ready_routines(
#     hass: HomeAssistant, subroutines: list[SubRoutineEntity]
# ) -> None:
#     """Add routines to ready routines."""
#     rascal_scheduler = hass.data[DOMAIN]
#     ready_routines = rascal_scheduler.get_ready_routines()

#     for subroutine in subroutines:
#         ready_routines[subroutine.get_start_time] = subroutine


class BaseActiveRoutine:
    """Base class for active routines."""

    _active_routines: dict[str, QueueEntity]

    def get_active_routines(self) -> dict[str, QueueEntity]:
        """Get active routines."""
        return self._active_routines


class BaseReadyRoutine:
    """Base class for ready routines."""

    _ready_routines: dict[str, QueueEntity]

    def get_ready_routines(self) -> dict[str, QueueEntity]:
        """Get ready routines."""
        return self._ready_routines


class RascalSchedulerEntity(BaseActiveRoutine, BaseReadyRoutine):
    """Representation of a rascal scehduler entity."""

    def __init__(self):
        """Initialize rascal scheduler entity."""
        self._active_routines = Queue({})  # key: device, value: actions
        self._ready_routines = Queue({})  # key: timestamp, value: subroutines
