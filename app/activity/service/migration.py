from model.activity.source import Activity as SourceActivity
from model.activity.source import ActivitySign as SourceActivitySign
from model.activity.source import ActivityEvidence as SourceActivityEvidence
from model.activity.source import ActivityFeedback as SourceActivityFeedback
from model.activity.source import ActivityMember as SourceActivityMember
from model.activity.target import Activity as TargetActivity
from model.activity.target import ActivityT as TargetActivityT
from model.activity.target import ActivityEvidenceFile as TargetActivityEvidenceFile
from model.activity.target import ActivityFeedback as TargetActivityFeedback
from model.activity.target import ActivityParticipant as TargetActivityParticipant
from model.activity.target import Student as TargetStudent
from model.activity.target import Executive as TargetExecutive
from config import SourceSession, TargetSession
from service.transformation import transform_activity, transform_activity_t, transform_activity_participants, transform_activity_feedbacks, transform_activity_evidence_files

async def migrate_activities():
    source_session = SourceSession()
    target_session = TargetSession()

    # 원본 데이터 로드
    for i in range(1, 88):
        print(f"Migrating club {i}...")
        source_activities = source_session.query(SourceActivity).order_by(SourceActivity.id).filter(SourceActivity.club_id == i).all()
        
        if len(source_activities) == 0:
            continue
    
        try:
            for source_activity in source_activities:
                # 변환 로직 실행
                await migrate_activity(target_session, source_session, source_activity)
        except Exception as e:
            print(f"Error during migration: {e}, clubId: {i}")
        
        # 커밋
        target_session.commit()
        print(f"Migration completed successfully. clubId: {i}")

    source_session.close()
    target_session.close()

async def migrate_activity(target_session, source_session, source_activity):
    # activity_t 변환
    source_activity_sign = source_session.query(SourceActivitySign).filter(SourceActivitySign.club_id == source_activity.club_id).order_by(SourceActivitySign.sign_time.desc()).all()
    transformed_activity = transform_activity(source_activity, source_activity_sign)
    target_activity = TargetActivity(**transformed_activity)
    target_session.add(target_activity)
    target_session.flush()
    target_session.refresh(target_activity)
    target_activity_id = target_activity.id

    # activity_t 변환
    transformed_activity_t = transform_activity_t(source_activity, target_activity_id)
    target_activity_t = TargetActivityT(**transformed_activity_t)
    target_session.add(target_activity_t)

    # activity_participant 변환
    source_activity_participants = source_session.query(SourceActivityMember).filter(SourceActivityMember.activity_id == source_activity.id).all()
    if source_activity_participants:
        source_activity_member_ids = [source_activity_participant.member_student_id for source_activity_participant in source_activity_participants]
        target_students = target_session.query(TargetStudent).filter(TargetStudent.number.in_(source_activity_member_ids)).all()
        transformed_activity_participants = transform_activity_participants(source_activity, target_students, target_activity_id)
        for transformed_activity_participant in transformed_activity_participants:
            target_activity_participant = TargetActivityParticipant(**transformed_activity_participant)
            target_session.add(target_activity_participant)

    # activity_feedback 변환
    source_activity_feedbacks = source_session.query(SourceActivityFeedback).filter(SourceActivityFeedback.activity == source_activity.id).all()
    source_activity_feedback_student_ids = [source_activity_feedback.student_id for source_activity_feedback in source_activity_feedbacks]
    target_executives = target_session.query(TargetExecutive).join(TargetExecutive.student) \
        .filter(TargetStudent.number.in_(source_activity_feedback_student_ids)).all()
    if source_activity_feedbacks:
        transformed_activity_feedbacks = transform_activity_feedbacks(source_activity_feedbacks, target_executives, target_activity_id)
        for transformed_activity_feedback in transformed_activity_feedbacks:
            target_activity_feedback = TargetActivityFeedback(**transformed_activity_feedback)
            target_session.add(target_activity_feedback)

    # activity_evidence_file 변환
    source_activity_evidences = source_session.query(SourceActivityEvidence).filter(SourceActivityEvidence.activity_id == source_activity.id).all()
    if source_activity_evidences:
        transformed_activity_evidence_files = await transform_activity_evidence_files(source_activity, source_activity_evidences, target_activity_id)
        for transformed_activity_evidence_file in transformed_activity_evidence_files:
            target_activity_evidence_file = TargetActivityEvidenceFile(**transformed_activity_evidence_file)
            target_session.add(target_activity_evidence_file)



