from datetime import datetime
from app.funding.model.source import (
    Funding as SourceFunding,
    FundingEvidence as SourceFundingEvidence,
    FundingFeedback as SourceFundingFeedback,
    FundingFixture as SourceFundingFixture,
    FundingTransportationMember as SourceFundingTransportationMember
)
from app.funding.model.target import (
    Funding as TargetFunding,
    FundingTradeDetailFile as TargetFundingTradeDetailFile,
    FundingTradeEvidenceFile as TargetFundingTradeEvidenceFile,
    FundingEtcExpenseFile as TargetFundingEtcExpenseFile,
    FundingFixtureImageFile as TargetFundingFixtureImageFile,
    FundingFixtureSoftwareEvidenceFile as TargetFundingFixtureSoftwareEvidenceFile,
    FundingClubSuppliesImageFile as TargetFundingClubSuppliesImageFile,
    FundingClubSuppliesSoftwareEvidenceFile as TargetFundingClubSuppliesSoftwareEvidenceFile,
    FundingTransportationPassenger as TargetFundingTransportationPassenger,
    FundingFeedback as TargetFundingFeedback,
    Student as TargetStudent,
    Executive as TargetExecutive
)
from app.activity.model.source import Activity as SourceActivity
from app.activity.model.target import Activity as TargetActivity
from config import SourceSession, TargetSession
from app.funding.service.transformation import (
    transform_funding,
    transform_funding_evidence_files,
    transform_funding_transportation_passengers,
    transform_funding_feedbacks,
)

async def migrate_fundings():
    source_session = SourceSession()
    target_session = TargetSession()

    # 원본 데이터 로드
    for i in range(1, 88):  # activity와 동일한 club_id 범위
        print(f"Migrating funding for club {i}...")
        source_fundings = source_session.query(SourceFunding).order_by(SourceFunding.id).filter(SourceFunding.club_id == i).all()
        
        if len(source_fundings) == 0:
            continue
    
        try:
            for source_funding in source_fundings:
                # 변환 로직 실행
                await migrate_funding(target_session, source_session, source_funding)
        except Exception as e:
            print(f"Error during funding migration: {e}, clubId: {i}, fundingId: {source_funding.id}")
        
        # 커밋
        target_session.commit()
        print(f"Funding migration completed successfully. clubId: {i}")

    source_session.close()
    target_session.close()

async def migrate_funding(target_session, source_session, source_funding):
    # 관련된 activity id 찾기
    source_activity = source_session.query(SourceActivity).filter(
        SourceActivity.id == source_funding.purpose
    ).first()
    
    if source_activity:
        activity_d_id = 7 if source_activity.recent_edit < datetime(2024, 3, 1) else 2
        target_activity = target_session.query(TargetActivity).filter(
            TargetActivity.club_id == source_activity.club_id,
            TargetActivity.name == source_activity.title,
            TargetActivity.activity_d_id == activity_d_id
        ).first()
        target_activity_id = target_activity.id if target_activity else None
    else:
        target_activity_id = None

    funding_fixture = source_session.query(SourceFundingFixture).filter(
        SourceFundingFixture.funding_id == source_funding.id
    ).first()

    # 기본 funding 데이터 변환
    transformed_funding = transform_funding(source_funding, target_activity_id, funding_fixture)
    target_funding = TargetFunding(**transformed_funding)
    target_session.add(target_funding)
    target_session.flush()
    target_session.refresh(target_funding)
    target_funding_id = target_funding.id

    # funding evidence 파일 변환
    source_funding_evidences = source_session.query(SourceFundingEvidence).filter(
        SourceFundingEvidence.funding_id == source_funding.id
    ).all()
    
    if source_funding_evidences:
        transformed_files = await transform_funding_evidence_files(
            source_funding,
            target_funding,
            source_funding_evidences,
            target_funding_id
        )
        
        for file_info in transformed_files:
            table_name = file_info.pop('table_name')
            if table_name == "funding_trade_evidence_file":
                target_file = TargetFundingTradeEvidenceFile(**file_info)
            elif table_name == "funding_trade_detail_file":
                target_file = TargetFundingTradeDetailFile(**file_info)
            elif table_name == "funding_etc_expense_file":
                target_file = TargetFundingEtcExpenseFile(**file_info)
            elif table_name == "funding_fixture_image_file":
                target_file = TargetFundingFixtureImageFile(**file_info)
            elif table_name == "funding_fixture_software_evidence_file":
                target_file = TargetFundingFixtureSoftwareEvidenceFile(**file_info)
            elif table_name == "funding_club_supplies_image_file":
                target_file = TargetFundingClubSuppliesImageFile(**file_info)
            elif table_name == "funding_club_supplies_software_evidence_file":
                target_file = TargetFundingClubSuppliesSoftwareEvidenceFile(**file_info)
            
            target_session.add(target_file)

    # transportation passenger 변환
    source_transportation_members = source_session.query(SourceFundingTransportationMember).filter(
        SourceFundingTransportationMember.funding_id == source_funding.id
    ).all()
    
    if source_transportation_members:
        source_member_ids = [member.student_id for member in source_transportation_members]
        target_students = target_session.query(TargetStudent).filter(
            TargetStudent.number.in_(source_member_ids)
        ).all()
        
        transformed_passengers = transform_funding_transportation_passengers(
            source_funding,
            target_students,
            target_funding_id
        )
        
        for transformed_passenger in transformed_passengers:
            target_passenger = TargetFundingTransportationPassenger(**transformed_passenger)
            target_session.add(target_passenger)

    # funding feedback 변환
    source_funding_feedbacks = source_session.query(SourceFundingFeedback).filter(
        SourceFundingFeedback.funding == source_funding.id
    ).all()

    if source_funding_feedbacks:
        source_feedback_student_ids = [feedback.student_id for feedback in source_funding_feedbacks]
        target_executives = target_session.query(TargetExecutive).join(TargetExecutive.student).filter(
            TargetStudent.number.in_(source_feedback_student_ids)
        ).all()
        
        transformed_feedbacks = transform_funding_feedbacks(
            source_funding,
            source_funding_feedbacks,
            target_executives,
            target_funding_id
        )
        
        for transformed_feedback in transformed_feedbacks:
            target_feedback = TargetFundingFeedback(**transformed_feedback)
            target_session.add(target_feedback)
