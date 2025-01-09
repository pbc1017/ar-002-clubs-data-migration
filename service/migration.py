from model.source import Activity as SourceActivity
from model.source import ActivitySign as SourceActivitySign
from model.source import ActivityEvidenceFile as SourceActivityEvidenceFile
from model.source import ActivityFeedback as SourceActivityFeedback
from model.source import ActivityParticipant as SourceActivityParticipant
from model.target import Activity as TargetActivity
from model.target import ActivityEvidenceFile as TargetActivityEvidenceFile
from model.target import ActivityFeedback as TargetActivityFeedback
from model.target import ActivityParticipant as TargetActivityParticipant
from config import SourceSession, TargetSession
from service.transformation import transform_activity, transform_activity_evidence_file, transform_activity_feedback, transform_activity_participant

def migrate_activities():
    source_session = SourceSession()
    target_session = TargetSession()

    # 원본 데이터 로드
    for i in range(1, 2):
    # for i in range(1, 88):
        source_activities = source_session.query(SourceActivity).order_by(SourceActivity.id).filter(SourceActivity.club_id == i).all()
        preview = [{'id': source_activity.id, 'title': source_activity.title} for source_activity in source_activities]
        # print(preview)
        
        if len(source_activities) == 0:
            continue
    
        # try:
        for source_activity in source_activities:
            # 변환 로직 실행
                migrate_activity(target_session, source_session, source_activity)
        # except Exception as e:
        #     print(f"Error during migration: {e}, clubId: {i}")
        
        # 커밋
        target_session.commit()
        print("Migration completed successfully.")

    source_session.close()
    target_session.close()

def migrate_activity(target_session, source_session, source_activity):

    # activity_t 변환
    source_activity_sign = source_session.query(SourceActivitySign).filter(SourceActivitySign.club_id == source_activity.club_id).order_by(SourceActivitySign.sign_time.desc()).all()
    transformed_activity = transform_activity(source_activity, source_activity_sign)
    target_activity = TargetActivity(**transformed_activity)
    target_session.add(target_activity)
    target_session.flush()
    target_session.refresh(target_activity)
    target_activity_id = target_activity.id

    # activity_evidence_file 변환
    source_activity_evidence_files = source_session.query(SourceActivityEvidenceFile).filter(SourceActivityEvidenceFile.activity_id == source_activity.id).all()
    for source_activity_evidence_file in source_activity_evidence_files:
        transformed_activity_evidence_file = transform_activity_evidence_file(source_activity_evidence_file, target_activity_id)
        target_activity_evidence_file = TargetActivityEvidenceFile(**transformed_activity_evidence_file)
        target_session.add(target_activity_evidence_file)
   
    # activity_feedback 변환
    source_activity_feedbacks = source_session.query(SourceActivityFeedback).filter(SourceActivityFeedback.activity_id == source_activity.id).all()
    for source_activity_feedback in source_activity_feedbacks:
        transformed_activity_feedback = transform_activity_feedback(source_activity_feedback, target_activity_id)
        target_activity_feedback = TargetActivityFeedback(**transformed_activity_feedback)
        target_session.add(target_activity_feedback)

    # activity_participant 변환
    source_activity_participants = source_session.query(SourceActivityParticipant).filter(SourceActivityParticipant.activity_id == source_activity.id).all()
    for source_activity_participant in source_activity_participants:
        transformed_activity_participant = transform_activity_participant(source_activity_participant, target_activity_id)
        target_activity_participant = TargetActivityParticipant(**transformed_activity_participant)
        target_session.add(target_activity_participant)



