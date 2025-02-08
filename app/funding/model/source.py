from sqlalchemy import (
    Boolean,
    Column,
    ForeignKeyConstraint,
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

class Funding(Base):
    __tablename__ = "Funding"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    club_id = Column(Integer, ForeignKey("Club.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("Semester.id"), nullable=False)
    expenditure_date = Column(Date, nullable=False)
    expenditure_amount = Column(Integer, nullable=False)
    approved_amount = Column(Integer, nullable=False)
    purpose = Column(String(255), nullable=False)
    is_transportation = Column(Boolean, nullable=False)
    is_non_corporate_transaction = Column(Boolean, nullable=False)
    is_food_expense = Column(Boolean, nullable=False)
    is_labor_contract = Column(Boolean, nullable=False)
    is_external_event_participation_fee = Column(Boolean, nullable=False)
    is_publication = Column(Boolean, nullable=False)
    is_profit_making_activity = Column(Boolean, nullable=False)
    is_joint_expense = Column(Boolean, nullable=False)
    additional_explanation = Column(Text)
    funding_feedback_type = Column(Integer, ForeignKey("FundingFeedbackType.id"))
    funding_executive = Column(Integer, ForeignKey("ExecutiveMember.student_id"))
    is_committee = Column(Boolean, nullable=False)
    recent_edit = Column(DateTime)
    recent_feedback = Column(DateTime)

class FundingEvidence(Base):
    __tablename__ = "FundingEvidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, ForeignKey("Funding.id", onupdate="CASCADE", ondelete="SET NULL"))
    funding_evidence_type_id = Column(Integer, ForeignKey("FundingEvidenceType.id", onupdate="CASCADE", ondelete="SET NULL"))
    image_url = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

class FundingEvidenceType(Base):
    __tablename__ = "FundingEvidenceType"

    type_id = Column(Integer, primary_key=True)
    funding_evidence_type = Column(String(255))

class FundingFeedback(Base):
    __tablename__ = "FundingFeedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding = Column(Integer, ForeignKey("Funding.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("ExecutiveMember.student_id"), nullable=False)
    added_time = Column(DateTime, nullable=False)
    feedback = Column(Text, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ("student_id",),
            ("ExecutiveMember.student_id",),
            name="FundingFeedback_ExecutiveMember_student_id_fk"
        ),
        ForeignKeyConstraint(
            ("funding",),
            ("Funding.id",),
            name="FundingFeedback_Funding_id_fk"
        ),
    )


class FundingFeedbackType(Base):
    __tablename__ = "FundingFeedbackType"

    type_id = Column(Integer, primary_key=True)
    funding_feedback_type = Column(String(255))


class FundingFixture(Base):
    __tablename__ = "FundingFixture"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, ForeignKey("Funding.id", onupdate="CASCADE", ondelete="SET NULL"))
    funding_fixture_type_id = Column(Integer, ForeignKey("FundingFixtureType.type_id", onupdate="CASCADE", ondelete="SET NULL"))
    fixture_name = Column(String(255))
    fixture_type_id = Column(Integer, ForeignKey("FundingFixtureObjectType.type_id", onupdate="CASCADE", ondelete="SET NULL"))
    usage_purpose = Column(Text)
    is_software = Column(Boolean)
    software_proof_text = Column(Text)

    __table_args__ = (
        ForeignKeyConstraint(
            ("funding_id",),
            ("Funding.id",),
            name="FundingFixture_Funding_id_fk"
        ),
        ForeignKeyConstraint(
            ("funding_fixture_type_id",),
            ("FundingFixtureType.type_id",),
            name="FundingFixture_FundingFixtureType_type_id_fk"
        ),
        ForeignKeyConstraint(
            ("fixture_type_id",),
            ("FundingFixtureObjectType.type_id",),
            name="FundingFixture_FundingFixtureObjectType_type_id_fk"
        ),
    )


class FundingFixtureObjectType(Base):
    __tablename__ = "FundingFixtureObjectType"

    type_id = Column(Integer, primary_key=True)
    fixture_object_type = Column(String(255))


class FundingFixtureType(Base):
    __tablename__ = "FundingFixtureType"

    type_id = Column(Integer, primary_key=True)
    funding_fixture_type = Column(String(255))

class FundingNoncorp(Base):
    __tablename__ = "FundingNoncorp"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, ForeignKey("Funding.id", onupdate="CASCADE", ondelete="SET NULL"))
    trader_name = Column(String(255))
    trader_account_number = Column(String(255))
    waste_explanation = Column(Text)

    __table_args__ = (
        ForeignKeyConstraint(
            ("funding_id",),
            ("Funding.id",),
            name="FundingNoncorp_Funding_id_fk"
        ),
    )


class FundingTransportation(Base):
    __tablename__ = "FundingTransportation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    funding_id = Column(Integer, ForeignKey("Funding.id", onupdate="CASCADE", ondelete="SET NULL"))
    transportation_type_id = Column(Integer, ForeignKey("FundingTransportationType.type_id", onupdate="CASCADE", ondelete="SET NULL"))
    origin = Column(String(255))
    destination = Column(String(255))
    purpose_of_use = Column(Text)
    cargo_list = Column(Text)
    place_validity = Column(Text)

    __table_args__ = (
        ForeignKeyConstraint(
            ("funding_id",),
            ("Funding.id",),
            name="FundingTransportation_Funding_id_fk"
        ),
        ForeignKeyConstraint(
            ("transportation_type_id",),
            ("FundingTransportationType.type_id",),
            name="FundingTransportation_FundingTransportationType_type_id_fk"
        ),
    )


class FundingTransportationMember(Base):
    __tablename__ = "FundingTransportationMember"

    funding_id = Column(Integer, ForeignKey("Funding.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("Member.student_id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("funding_id", "student_id"),
        ForeignKeyConstraint(
            ("funding_id",),
            ("Funding.id",),
            name="FundingTransportationMember_Funding_id_fk"
        ),
        ForeignKeyConstraint(
            ("student_id",),
            ("Member.student_id",),
            name="FundingTransportationMember_Member_student_id_fk"
        ),
    )


class FundingTransportationType(Base):
    __tablename__ = "FundingTransportationType"

    type_id = Column(Integer, primary_key=True)
    transportation_type = Column(String(255))
