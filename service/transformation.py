import datetime


def transform_activity(source_activity, source_activity_sign):
    # recent_edit이 2024-03-01 이전이면 activity_d_id를 1로 설정
    if (source_activity.recent_edit < datetime.datetime(2024, 3, 1)):
        activity_d_id = 7
    else:
        activity_d_id = 2

    if (source_activity.activity_type_id == 1):
        activity_type_enum_id = 3
    elif (source_activity.activity_type_id == 2):
        activity_type_enum_id = 1
    else:
        activity_type_enum_id = 2

    # 리스트에서 semesterId가 activity_d_id = 7 일경우 14, 아닐경우 15인 데이터 중 sign_time이 가장 최신인 데이터를 찾아서 반환
    if (activity_d_id == 7):
        professor_approved_at = [sign for sign in source_activity_sign if sign.semesterId == 14]
        if (professor_approved_at):
            professor_approved_at = professor_approved_at[0].sign_time
        else:
            professor_approved_at = None
    else:
        professor_approved_at = [sign for sign in source_activity_sign if sign.semesterId == 15]
        if (professor_approved_at):
            professor_approved_at = professor_approved_at[0].sign_time
        else:
            professor_approved_at = None

    # 데이터 변환 로직
    return {
        "club_id": source_activity.club_id,
        "original_name": source_activity.title,
        "name": source_activity.title,
        "activity_d_id": activity_d_id,
        "activity_status_enum_id": source_activity.feedback_type,
        "activity_type_enum_id": activity_type_enum_id,
        "location": source_activity.location,
        "purpose": source_activity.purpose,
        "detail": source_activity.content,
        "evidence": source_activity.proof_text or "",
        "created_at": source_activity.recent_edit,
        "updated_at": source_activity.recent_feedback or source_activity.recent_edit,
        "professor_approved_at": professor_approved_at,
    }

def transform_activity_evidence_file(source_activity_evidence_file, target_activity_id):
    return {
        "activity_id": target_activity_id,
        "file_name": source_activity_evidence_file.file_name,
        "file_path": source_activity_evidence_file.file_path,
    }

def transform_activity_feedback(source_activity_feedback, target_activity_id):
    return {
        "activity_id": target_activity_id,
        "feedback_type": source_activity_feedback.feedback_type,
        "feedback_content": source_activity_feedback.feedback_content,
    }

def transform_activity_participant(source_activity_participant, target_activity_id):
    return {
        "activity_id": target_activity_id,
        "user_id": source_activity_participant.user_id,
    }
