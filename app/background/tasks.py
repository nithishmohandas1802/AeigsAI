import time


def process_user_task(user_id: int):
    """
    Simulates a long-running background operation.
    """

    time.sleep(5)

    with open(
        "background_task.log",
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            f"Background task completed for user {user_id}\n"
        )
