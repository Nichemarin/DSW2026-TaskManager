from typing import Annotated
from enum import StrEnum
from fastapi import FastAPI, HTTPException, Path, status, Query

app = FastAPI(
    title="TaskFlow RESTful API",
    description="Project and sequential task workflow management API with dependencies and PDF attachments.",
    version="1.0.0",
)

# --- DATOS INICIALES EN MEMORIA (Proyectos 1:N Tareas, y Dependencias entre Tareas) ---


# --- ENUMERACIONES (Inglés técnico) ---
class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


PROJECTS = [
    {"id": 1, "name": "Cloud Migration 2026", "is_active": True},
    {"id": 2, "name": "Mobile App Redesign", "is_active": True},
]

TASKS = [
    {
        "id": 1,
        "title": "Architecture & Security Audit",
        "status": "completed",
        "priority": "high",
        "project_id": 1,
        "is_start_node": True,
        "is_end_node": False,
        "depends_on": [],  # Tarea de inicio: no depende de ninguna otra
        "assignees": ["ana.dev", "carlos.sec"],
    },
    {
        "id": 2,
        "title": "Database Schema Provisioning",
        "status": "in_progress",
        "priority": "high",
        "project_id": 1,
        "is_start_node": False,
        "is_end_node": False,
        "depends_on": [1],  # Requiere que la Tarea 1 esté completada
        "assignees": ["ana.dev"],
    },
    {
        "id": 3,
        "title": "Final Production Deployment",
        "status": "pending",
        "priority": "medium",
        "project_id": 1,
        "is_start_node": False,
        "is_end_node": True,
        "depends_on": [1, 2],  # Tarea final: depende de las tareas 1 y 2
        "assignees": ["carlos.sec", "elena.ops"],
    },
]

# Alias reutilizables con Annotated para validar IDs positivos en las rutas
TaskIdPath = Annotated[
    int,
    Path(
        gt=0,
        title="Task ID",
        description="Unique positive integer identifier of the task",
    ),
]
ProjectIdPath = Annotated[
    int,
    Path(
        gt=0,
        title="Project ID",
        description="Unique positive integer identifier of the project",
    ),
]


@app.get("/tasks", tags=["Tasks"])
async def get_tasks(
    # los valores de consulta opcionales se inicializan en None
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,

    search: Annotated[
        str | None, Query(max_length=50, description="Case-insensitive search by title")
    ] = None,


    project_id: Annotated[
        int | None,
        Query(
            gt=0,
            title="Project ID",
            description="Filter tasks by a positive project identifier",
        ),
    ] = None,

    # Parámetros de paginación robustos
    skip: Annotated[int, Query(ge=0, description="Number of tasks to skip (offset)")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of tasks to return")] = 20,
) -> list[dict]:
    """Retrieve all tasks."""

    filtered_tasks = TASKS

    if project_id:
        filtered_tasks = [t for t in filtered_tasks if t["project_id"] == project_id]

    if status:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]

    if priority:
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]

    if search:
        search_lower = search.lower()

        filtered_tasks = [
            t for t in filtered_tasks if search_lower in t["title"].lower()
        ]

    return filtered_tasks[skip : skip + limit]


# 1. Ruta estática (¡siempre antes que /tasks/{task_id}!)
@app.get("/tasks/start-nodes", tags=["Tasks"])
async def get_start_node_tasks() -> list[dict]:
    """Retrieve all initial tasks (start nodes) that have no prior dependencies."""
    return [task for task in TASKS if task["is_start_node"]]


# 2. Ruta dinámica: Obtener una tarea por su ID o devolver 404 Not Found
@app.get("/tasks/{task_id}", tags=["Tasks"])
async def get_task_by_id(task_id: TaskIdPath) -> dict:
    """Retrieve a single task by its unique ID. Raises 404 if not found."""
    for task in TASKS:
        if task["id"] == task_id:
            return task

    # Si termina el bucle sin éxito, lanzamos un error HTTP 404 en formato JSON
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with id {task_id} not found",
    )


# 3. Ruta anidada (Relación 1:N): Obtener las tareas de un proyecto concreto
@app.get("/projects/{project_id}/tasks", tags=["Projects"])
async def get_tasks_by_project(project_id: ProjectIdPath) -> list[dict]:
    """List all tasks belonging to a specific project ID."""
    # Primero verificamos si el proyecto padre existe
    project_exists = any(p["id"] == project_id for p in PROJECTS)
    if not project_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    return [task for task in TASKS if task["project_id"] == project_id]
