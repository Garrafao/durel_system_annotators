from enum import Enum


class StatusEnum(Enum):
    """
    StatusEnum class represents the different statuses of a task.

    Attributes:
        TASK_PENDING (str): Represents the status when a task is pending.
        TASK_STARTED (str): Represents the status when a task is started.
        TASK_COMPLETED (str): Represents the status when a task is completed.
        TASK_FAILED (str): Represents the status when a task has failed.
    """
    TASK_PENDING = 'TASK_PENDING'
    TASK_STARTED = 'TASK_STARTED'
    TASK_COMPLETED = 'TASK_COMPLETED'
    TASK_FAILED = 'TASK_FAILED'
