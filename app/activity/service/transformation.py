import datetime
import os
import shutil
import aiohttp
import aiofiles
import asyncio
from typing import List, Dict

from app.activity.model.source import Activity as SourceActivity, ActivityFeedback as SourceActivityFeedback, ActivitySign as SourceActivitySign
from app.activity.model.target import Student as TargetStudent, Executive as TargetExecutive
from config import API_ACCESS_TOKEN, API_BASE_URL

def transform_activity(
        source_activity: SourceActivity,
        source_activity_sign: List[SourceActivitySign]
    ) -> Dict:
    # recent_edit이 2024-03-01 이전이면 activity_d_id를 7로 설정
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
        professor_approved_at = [sign for sign in source_activity_sign if sign.semester_id == 14]
        if (professor_approved_at):
            professor_approved_at = professor_approved_at[0].sign_time
        else:
            professor_approved_at = None
    else:
        professor_approved_at = [sign for sign in source_activity_sign if sign.semester_id == 15]
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

def transform_activity_t(
        source_activity: SourceActivity,
        target_activity_id: int
    ) -> Dict:
    return {
        "activity_id": target_activity_id,
        "start_term": source_activity.start_date,
        "end_term": source_activity.end_date,
        "created_at": source_activity.recent_edit,
    }

def transform_activity_participants(
        source_activity: SourceActivity,
        target_students: List[TargetStudent],
        target_activity_id: int
    ) -> List[Dict]:
    return [
        {
            "activity_id": target_activity_id,
            "student_id": target_student.id,
            "created_at": source_activity.recent_edit,
        }
        for target_student in target_students
    ]

def transform_activity_feedbacks(
        source_activity_feedbacks: List[SourceActivityFeedback],
        target_executives: List[TargetExecutive],
        target_activity_id: int
    ) -> List[Dict]:
    target_executive_map = {target_executive.student.number: target_executive.id for target_executive in target_executives}

    return [
        {
            "activity_id": target_activity_id,
            "executive_id": target_executive_map[source_activity_feedback.student_id],
            "comment": source_activity_feedback.feedback,
            "created_at": source_activity_feedback.added_time,
        }
        for source_activity_feedback in source_activity_feedbacks
        if source_activity_feedback.feedback != ""
    ]

async def transform_activity_evidence_files(
        source_activity: SourceActivity,
        source_activity_evidences: List,
        target_activity_id: int
    ) -> List[Dict]:
    """
    ActivityEvidence 파일들을 새로운 시스템으로 변환
    1. 파일 다운로드
    2. API를 통해 업로드 URL 획득
    3. 파일 업로드
    4. 결과 반환
    """
    # tmp 디렉토리 초기화
    TMP_DIR = "tmp"
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)

    try:
        # 파일 다운로드 및 메타데이터 준비
        file_metadatas = []
        downloaded_files = []
        
        async with aiohttp.ClientSession() as session:
            for evidence in source_activity_evidences:
                file_name = evidence.description
                tmp_path = os.path.join(TMP_DIR, file_name)
                
                # 파일 다운로드
                async with session.get(evidence.image_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download file: {file_name}")
                    
                    async with aiofiles.open(tmp_path, 'wb') as f:
                        await f.write(await response.read())
                
                # 파일 메타데이터 준비
                file_size = os.path.getsize(tmp_path)
                file_type = file_name.split('.')[-1]
                
                file_metadatas.append({
                    "name": file_name,
                    "type": f"image/{file_type}",
                    "size": file_size
                })
                downloaded_files.append(tmp_path)

        # API를 통해 업로드 URL 획득
        headers = {"Authorization": f"Bearer {API_ACCESS_TOKEN}"}
        max_retries = 3
        
        async def try_api_call():
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{API_BASE_URL}/files/upload",
                    json={"metadata": file_metadatas},
                    headers=headers
                ) as response:
                    if response.status != 201:
                        raise Exception("Failed to get upload URLs")
                    return await response.json()

        # API 호출 재시도 로직
        for attempt in range(max_retries):
            try:
                api_response = await try_api_call()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(1)

        # 파일 업로드
        results = []
        for idx, url_info in enumerate(api_response["urls"]):
            file_path = downloaded_files[idx]
            
            async with aiohttp.ClientSession() as session:
                async with aiofiles.open(file_path, 'rb') as f:
                    file_content = await f.read()
                    
                async with session.put(url_info["uploadUrl"], data=file_content) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to upload file: {url_info['name']}")
            
            results.append({
                "activity_id": target_activity_id,
                "file_id": url_info["fileId"],
                "created_at": source_activity.recent_edit
            })

        return results

    finally:
        # 임시 파일 정리
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)
