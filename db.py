# Import necessary libraries
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import date
from typing import Optional

app = FastAPI()

# Define database url
database_url = "postgresql://ansha:newpassword@localhost/task_management"

# Create sqlalchemy engine
engine = create_engine(database_url)

# Create session factory
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

# Base class for sqlalchemy models
Base = declarative_base()

# SQLAlchemy ORM Task Model
class TaskORM(Base):
    
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    due_date = Column(Date)
    priority = Column(String)
    status = Column(String, default='pending')


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

# Pydantic Task Model
class Task(BaseModel):
    id: int
    title: str
    description: str = None
    due_date: date
    priority: str
    status: str


# Add task 
@app.post("/tasks", response_model=Task)
async def create_task(task : Task, db:Session=Depends(get_db)):
    db_task = TaskORM(title = task.title, description = task.description, 
                   due_date = task.due_date, priority = task.priority)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Read task
@app.get("/tasks/{task_id}", response_model=Task)
async def read_tasks(task_id: int,  db:Session=Depends(get_db)):
    task = db.query(TaskORM).filter(TaskORM.id==task_id).first()
    if task is None:
        raise HTTPException(status_code = 404, detail= "Not found")
    else:
        return task
    
class UpdateTask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = None

# Update task
@app.post("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: UpdateTask, db:Session=Depends(get_db)):
    db_task = db.query(TaskORM).filter(TaskORM.id==task_id).first()
    if db_task is None:
        raise HTTPException(status_code = 404, detail= "Not found")
    
    db_task.title = task.title if task.title is not None else db_task.title
    db_task.description = task.description if task.description is not None else db_task.description
    db_task.due_date = task.due_date  if task.due_date is not None else db_task.due_date 
    db_task.priority = task.priority  if task.priority is not None else db_task.priority 
    db_task.status = task.status if task.status is not None else db_task.status
    db.commit()
    db.refresh(db_task)
    return db_task

# Delete task
@app.delete("/tasks/{task_id}", response_model=Task)  
async def delete_task(task_id: int,  db:Session=Depends(get_db)):
    task = db.query(TaskORM).filter(TaskORM.id==task_id).first()
    if task is None:
        raise HTTPException(status_code = 404, detail= "Not found")
    
    db.delete(task)
    db.commit()
    return task
    


