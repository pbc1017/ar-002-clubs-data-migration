from sqlalchemy import (
    Boolean,
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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

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

class Funding(Base):
    __tablename__ = "funding"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, nullable=False)
    activity_d_id = Column(Integer, nullable=False)
    funding_status_enum = Column(Integer, nullable=False)
    purpose_activity_id = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    expenditure_date = Column(DateTime, nullable=False)
    expenditure_amount = Column(Integer, nullable=False)
    approved_amount = Column(Integer, nullable=True)
    trade_detail_explanation = Column(Text, nullable=True)
    club_supplies_name = Column(String(255), nullable=True)
    club_supplies_evidence_enum = Column(Integer, nullable=True)
    club_supplies_class_enum = Column(Integer, nullable=True)
    club_supplies_purpose = Column(Text, nullable=True)
    club_supplies_software_evidence = Column(Text, nullable=True)
    number_of_club_supplies = Column(Integer, nullable=True)
    price_of_club_supplies = Column(Integer, nullable=True)
    is_fixture = Column(Boolean, nullable=True)
    fixture_name = Column(String(255), nullable=True)
    fixture_evidence_enum = Column(Integer, nullable=True)
    fixture_class_enum = Column(Integer, nullable=True)
    fixture_purpose = Column(Text, nullable=True)
    fixture_software_evidence = Column(Text, nullable=True)
    number_of_fixture = Column(Integer, nullable=True)
    price_of_fixture = Column(Integer, nullable=True)
    is_transportation = Column(Boolean, nullable=False)
    transportation_enum = Column(Integer, nullable=True)
    origin = Column(String(255), nullable=True)
    destination = Column(String(255), nullable=True)
    purpose_of_transportation = Column(Text, nullable=True)
    is_non_corporate_transaction = Column(Boolean, nullable=False)
    trader_name = Column(String(255), nullable=True)
    trader_account_number = Column(String(255), nullable=True)
    waste_explanation = Column(Text, nullable=True)
    is_food_expense = Column(Boolean, nullable=False)
    food_expense_explanation = Column(Text, nullable=True)
    is_labor_contract = Column(Boolean, nullable=False)
    labor_contract_explanation = Column(Text, nullable=True)
    is_external_event_participation_fee = Column(Boolean, nullable=False)
    external_event_participation_fee_explanation = Column(Text, nullable=True)
    is_publication = Column(Boolean, nullable=False)
    publication_explanation = Column(Text, nullable=True)
    is_profit_making_activity = Column(Boolean, nullable=False)
    profit_making_activity_explanation = Column(Text, nullable=True)
    is_joint_expense = Column(Boolean, nullable=False)
    joint_expense_explanation = Column(Text, nullable=True)
    is_etc_expense = Column(Boolean, nullable=False)
    etc_expense_explanation = Column(Text, nullable=True)
    charged_executive_id = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP)
    edited_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    commented_at = Column(TIMESTAMP)

class FundingClubSuppliesImageFile(Base):
    __tablename__ = "funding_club_supplies_image_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingClubSuppliesSoftwareEvidenceFile(Base):
    __tablename__ = "funding_club_supplies_software_evidence_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingDeadlineD(Base):
    __tablename__ = "funding_deadline_d"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deadline_enum = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

class FundingEtcExpenseFile(Base):
    __tablename__ = "funding_etc_expense_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingExternalEventParticipationFeeFile(Base):
    __tablename__ = "funding_external_event_participation_fee_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingFeedback(Base):
    __tablename__ = "funding_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    executive_id = Column(Integer, nullable=False)
    funding_status_enum = Column(Integer, nullable=False)
    approved_amount = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

class FundingFixtureImageFile(Base):
    __tablename__ = "funding_fixture_image_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingFixtureSoftwareEvidenceFile(Base):
    __tablename__ = "funding_fixture_software_evidence_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingFoodExpenseFile(Base):
    __tablename__ = "funding_food_expense_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingJointExpenseFile(Base):
    __tablename__ = "funding_joint_expense_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingLaborContractFile(Base):
    __tablename__ = "funding_labor_contract_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingProfitMakingActivityFile(Base):
    __tablename__ = "funding_profit_making_activity_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingPublicationFile(Base):
    __tablename__ = "funding_publication_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingTradeDetailFile(Base):
    __tablename__ = "funding_trade_detail_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingTradeEvidenceFile(Base):
    __tablename__ = "funding_trade_evidence_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    file_id = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
    )

class FundingTransportationPassenger(Base):
    __tablename__ = "funding_transportation_passenger"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, nullable=False)
    student_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    deleted_at = Column(TIMESTAMP)

    __table_args__ = (
        ForeignKeyConstraint(["funding_id"], ["funding.id"]),
        ForeignKeyConstraint(["student_id"], ["student.id"]),
    )
