from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Activity 테이블
class Activity(Base):
    __tablename__ = "Activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    activity_type_id = Column(Integer, ForeignKey("ActivityType.id", onupdate="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    location = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    proof_text = Column(Text)
    feedback_type = Column(Integer, ForeignKey("ActivityFeedbackType.id", onupdate="CASCADE", ondelete="SET NULL"))
    recent_edit = Column(DateTime)
    recent_feedback = Column(DateTime)

# Activity_init 테이블
class ActivityInit(Base):
    __tablename__ = "Activity_init"

    id = Column(Integer, primary_key=True)
    club_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    activity_type_id = Column(Integer, ForeignKey("ActivityType.id", onupdate="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    location = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    proof_text = Column(Text)
    feedback_type = Column(Integer, ForeignKey("ActivityFeedbackType.id", onupdate="CASCADE", ondelete="SET NULL"))
    recent_edit = Column(DateTime)
    recent_feedback = Column(DateTime)

# ActivityEvidence 테이블
class ActivityEvidence(Base):
    __tablename__ = "ActivityEvidence"

    activity_id = Column(Integer, ForeignKey("Activity.id", onupdate="CASCADE"), nullable=False)
    image_url = Column(Text, nullable=False)
    description = Column(String(511), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("activity_id", "description"),)

# ActivityFeedback 테이블
class ActivityFeedback(Base):
    __tablename__ = "ActivityFeedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity = Column(Integer, ForeignKey("Activity.id", onupdate="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("ExecutiveMember.student_id"), nullable=False)
    added_time = Column(DateTime, nullable=False)
    feedback = Column(Text)

# ActivityMember 테이블
class ActivityMember(Base):
    __tablename__ = "ActivityMember"

    activity_id = Column(Integer, ForeignKey("Activity.id"), nullable=False)
    member_student_id = Column(Integer, ForeignKey("Member.student_id"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("activity_id", "member_student_id"),)

# ActivitySign 테이블
class ActivitySign(Base):
    __tablename__ = "ActivitySign"

    semester_id = Column(Integer, ForeignKey("Semester.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    club_id = Column(Integer, ForeignKey("Club.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    sign_time = Column(DateTime, nullable=False)

    __table_args__ = (PrimaryKeyConstraint("semester_id", "club_id", "sign_time"),)
