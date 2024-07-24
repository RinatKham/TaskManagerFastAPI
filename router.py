from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from auth.database import get_async_session, User
from fastapi_users import FastAPIUsers
from models.models import task
from schemas import TaskCreate, TaskUpdate
from auth.manager import get_user_manager
from auth.auth import auth_backend

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


MANAGER_ID = 2
ADMIN_ID = 3


@router.get("/my-tasks")
async def get_my_tasks(
        user: User = Depends(fastapi_users.current_user()),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        user_id = user.id
        query = select(task).where(task.c.user_id == user_id)
        result = await session.execute(query)
        return {
            "status": "success",
            "data": result.all(),
            "details": None
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.get("/")
async def get_all_tasks(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(task)
        result = await session.execute(query)
        return {
            "status": "success",
            "data": result.all(),
            "details": None
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.post("/new-task")
async def add_new_task(
        new_task: TaskCreate,
        user: User = Depends(fastapi_users.current_user()),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if user.role_id == MANAGER_ID or user.role_id == ADMIN_ID:
            stmt = insert(task).values(**new_task.dict())
            await session.execute(stmt)
            await session.commit()
            return {
                "status": "success"
            }
        else:
            return {
                "status": "error",
                "details": "permission denied"
            }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.patch("/finish-{task_id}")
async def finish_task(
        new_status: bool,
        task_id: int,
        user: User = Depends(fastapi_users.current_user()),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if user.id == task.user_id:
            patch = update(task).where(task.c.id == task_id).values(task.done == new_status)
            await session.execute(patch)
            await session.commit()
            return {
                "status": "success"
            }
        elif user.role_id == MANAGER_ID or user.role_id == ADMIN_ID:
            patch = update(task).where(task.c.id == task_id).values(task.done == new_status)
            await session.execute(patch)
            await session.commit()
            return {
                "status": "success"
            }
        else:
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "details": "You do not have permission to perform this action"
            })
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.patch("/edit-{task_id}")
async def edit_task(
        new_task: TaskUpdate,
        task_id: int,
        user: User = Depends(fastapi_users.current_user()),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if user.role_id == MANAGER_ID or user.role_id == ADMIN_ID:
            patch = await session.execute(select(task).where(task.id == task_id))
            old_task = patch.scalars().first()

            if old_task is None:
                raise HTTPException(status_code=404, detail="Task not found")

            if new_task.task_name is not None:
                old_task.task_name = new_task.task_name
            if new_task.description is not None:
                old_task.description = new_task.description
            if new_task.user_id is not None:
                old_task.user_id = new_task.user_id
            if new_task.deadline is not None:
                old_task.deadline = new_task.deadline

            await session.commit()
            await session.refresh(old_task)

            return {
                "status": "success"
            }
        else:
            raise HTTPException(status_code=400, detail={
                "status": "error",
                "details": "You do not have permission to perform this action"
            })
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.delete("/delete-{task_id}")
async def delete_task(
        task_id: int,
        user: User = Depends(fastapi_users.current_user()),
        session: AsyncSession = Depends(get_async_session)
):
    if user.role_id == 2 or user.role_id == 3:
        result = await session.execute(select(task).where(task.id == task_id))
        deleted_task = result.scalars().first()

        if deleted_task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        await session.delete(deleted_task)
        await session.commit()
        return {
            "detail": "Task deleted",
            "data": None,
            "details": None
        }


@router.patch("/take-{task_id}")
async def take_task(
        task_id: int,
        user: User = Depends(fastapi_users.current_user()),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        current_task = await session.execute(select(task).where(task.c.id == task_id))

        if current_task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        if current_task.user_id is not None:
            raise HTTPException(status_code=400, detail="Task is already taken")

        current_task.user_id = user.id

        await session.commit()
        await session.refresh(current_task)
        return {
            "status": "success"
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })
