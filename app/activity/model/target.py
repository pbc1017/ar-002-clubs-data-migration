from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    DateTime,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Activity 테이블
class Activity(Base):
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, nullable=False)
    original_name = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    activity_type_enum_id = Column(Integer, nullable=False)
    location = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)
    activity_d_id = Column(Integer, nullable=False)
    activity_status_enum_id = Column(Integer, nullable=False)
    charged_executive_id = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP)
    professor_approved_at = Column(TIMESTAMP)

# ActivityEvidenceFile 테이블
class ActivityEvidenceFile(Base):
    __tablename__ = "activity_evidence_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, nullable=False)
    file_id = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP)

# ActivityFeedback 테이블
class ActivityFeedback(Base):
    __tablename__ = "activity_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, nullable=False)
    executive_id = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP)

# ActivityParticipant 테이블
class ActivityParticipant(Base):
    __tablename__ = "activity_participant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, nullable=False)
    student_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP)

# ActivityT 테이블
class ActivityT(Base):
    __tablename__ = "activity_t"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, nullable=False)
    start_term = Column(DateTime, nullable=False)
    end_term = Column(DateTime, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP)

# Student 테이블
class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    number = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(30), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP)
    executive = relationship("Executive", back_populates="student")

    __table_args__ = (UniqueConstraint("number"),)

# Executive 테이블
class Executive(Base):
    __tablename__ = "executive"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    student_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(30), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP)
    student = relationship("Student", back_populates="executive")

    __table_args__ = (ForeignKeyConstraint(["student_id"], ["student.id"]),)