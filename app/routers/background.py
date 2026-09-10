from fastapi import APIRouter, BackgroundTasks, status

from app.background.tasks import process_user_task


router = APIRouter(
    prefix="/background",
    tags=["Background Processing"],
)


@router.post(
    "/users/{user_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def start_user_background_task(
    user_id: int,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(
        process_user_task,
        user_id,
    )

    return {
        "message": "Background task accepted",
        "user_id": user_id,
    }
