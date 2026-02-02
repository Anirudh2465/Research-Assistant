from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String)
    problem_statement = Column(Text)
    status = Column(String, default="active")  # active / paused / completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    tasks = relationship("Task", back_populates="project")
    # ideas = relationship("Idea", back_populates="project") # Optional linkage if origin is project

class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text)
    status = Column(String, default="draft")  # draft / mature / rejected
    origin = Column(String)  # research / project
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tasks = relationship("Task", back_populates="idea")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    due_datetime = Column(DateTime(timezone=True))
    importance = Column(Integer, default=1) # 1-5
    severity = Column(Integer, default=1)   # 1-5
    
    linked_project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    linked_idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=True)
    
    status = Column(String, default="pending") # pending / done / in_progress / skipped
    task_type = Column(String, default="generic") # reading / coding / writing / submission / experiment

    project = relationship("Project", back_populates="tasks")
    idea = relationship("Idea", back_populates="tasks")

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    authors = Column(String)
    year = Column(Integer)
    source = Column(String) # arXiv / journal
    pdf_path = Column(String)
    ingestion_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    files = relationship("File", back_populates="paper")

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_type = Column(String, nullable=False) # pdf / image / embedding
    path = Column(String, nullable=False)
    related_paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    paper = relationship("Paper", back_populates="files")

class CeleryJob(Base):
    __tablename__ = "celery_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String, nullable=False)
    status = Column(String)
    payload = Column(Text) # JSON string
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
