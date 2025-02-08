import datetime
import os
import shutil
import aiohttp
import aiofiles
import asyncio
from typing import List, Dict

from app.funding.model.source import (
    Funding as SourceFunding,
    FundingEvidence as SourceFundingEvidence,
    FundingFeedback as SourceFundingFeedback,
    FundingFixture as SourceFundingFixture
)
from app.funding.model.target import Student as TargetStudent, Executive as TargetExecutive, Funding as TargetFunding
from config import API_ACCESS_TOKEN, API_BASE_URL

# 상태 매핑
funding_status_mapping = {
    1: 1,  # 검토전 -> Applied
    2: 2,  # 전체승인 -> Approved
    3: 5,  # 부분승인 -> Partial
    4: 3   # 미승인 -> Rejected
}

# 비품 분류 매핑
fixture_class_mapping = {
    1: 1,  # 전자기기
    2: 2,  # 가구
    3: 3,  # 악기
    4: 5   # 기타
}

# 교통수단 매핑
transportation_type_mapping = {
    1: 1,  # 시내/마을버스
    2: 2,  # 고속/시외버스
    3: 3,  # 철도
    4: 4,  # 택시
    5: 5,  # 전세버스
    6: 6,  # 화물 운반
    7: 7,  # 콜밴
    8: 8,  # 비행기
    9: 9,  # 선박
    10: 10 # 기타
}

def transform_funding(source_funding: SourceFunding, target_activity_id: int = None, funding_fixture: SourceFundingFixture = None) -> Dict:
    activity_d_id = 7 if source_funding.recent_edit < datetime.datetime(2024, 3, 1) else 2
    
    # 기본 데이터 변환
    transformed_data = {
        "club_id": source_funding.club_id,
        "activity_d_id": activity_d_id,
        "funding_status_enum": funding_status_mapping.get(source_funding.funding_feedback_type, 1),
        "purpose_activity_id": target_activity_id,
        "name": source_funding.name,
        "expenditure_date": source_funding.expenditure_date,
        "expenditure_amount": source_funding.expenditure_amount,
        "approved_amount": source_funding.approved_amount or 0,
        "trade_detail_explanation": source_funding.additional_explanation or "",
        "is_transportation": source_funding.is_transportation,
        "is_non_corporate_transaction": source_funding.is_non_corporate_transaction,
        "is_food_expense": source_funding.is_food_expense,
        "is_labor_contract": source_funding.is_labor_contract,
        "is_external_event_participation_fee": source_funding.is_external_event_participation_fee,
        "is_publication": source_funding.is_publication,
        "is_profit_making_activity": source_funding.is_profit_making_activity,
        "is_joint_expense": source_funding.is_joint_expense,
        "is_etc_expense": False,
        "number_of_club_supplies": 0,
        "price_of_club_supplies": 0,
        "number_of_fixture": 0,
        "price_of_fixture": 0,
        "created_at": source_funding.recent_edit,
        "edited_at": source_funding.recent_edit,
        "commented_at": source_funding.recent_feedback,
    }
    
    # 비품/물품 데이터 처리
    if funding_fixture and funding_fixture.funding_fixture_type_id in [1, 2]:  # 비품 구매 또는 비품 관리
        # 비품인 경우 - 물품과 비품 모두에 데이터 설정
        if funding_fixture.is_software == 1:
            transformed_data.update({
                "club_supplies_name": funding_fixture.fixture_name,
                "club_supplies_evidence_enum": funding_fixture.funding_fixture_type_id,
                "club_supplies_class_enum": 4,
                "club_supplies_software_evidence": funding_fixture.software_proof_text,
                "is_fixture": True,
                "fixture_name": funding_fixture.fixture_name,
                "fixture_evidence_enum": funding_fixture.funding_fixture_type_id,
                "fixture_class_enum": 4,
                "fixture_software_evidence": funding_fixture.software_proof_text,
            })
        else:
            transformed_data.update({
                # 물품 정보
                "club_supplies_name": funding_fixture.fixture_name,
                "club_supplies_evidence_enum": funding_fixture.funding_fixture_type_id,
                "club_supplies_class_enum": fixture_class_mapping.get(funding_fixture.fixture_type_id, 5),
                "club_supplies_purpose": funding_fixture.usage_purpose,
                # 비품 정보
                "is_fixture": True,
                "fixture_name": funding_fixture.fixture_name,
                "fixture_evidence_enum": funding_fixture.funding_fixture_type_id,
                "fixture_class_enum": fixture_class_mapping.get(funding_fixture.fixture_type_id, 5),
                "fixture_purpose": funding_fixture.usage_purpose
            })
    elif funding_fixture and funding_fixture.funding_fixture_type_id in [3, 4]:  # 동아리 물품 구매 또는 관리
        if funding_fixture.is_software == 1:
            transformed_data.update({
                "club_supplies_name": funding_fixture.fixture_name,
                "club_supplies_evidence_enum": funding_fixture.funding_fixture_type_id - 2,
                "club_supplies_class_enum": fixture_class_mapping.get(funding_fixture.fixture_type_id, 5),
                "club_supplies_software_evidence": funding_fixture.software_proof_text,
                "is_fixture": False
            })
        else:
            transformed_data.update({
                "club_supplies_name": funding_fixture.fixture_name,
                "club_supplies_evidence_enum": funding_fixture.funding_fixture_type_id - 2,
                "club_supplies_class_enum": fixture_class_mapping.get(funding_fixture.fixture_type_id, 5),
                "club_supplies_purpose": funding_fixture.usage_purpose,
                "is_fixture": False
            })
    
    return transformed_data

async def transform_funding_evidence_files(
        source_funding: SourceFunding,
        target_funding: TargetFunding,
        source_evidences: List[SourceFundingEvidence],
        target_funding_id: int
    ) -> List[Dict]:
    """
    FundingEvidence 파일들을 새로운 시스템으로 변환
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
        file_infos = []  # 각 파일의 메타데이터와 테이블 정보를 함께 저장
        
        async with aiohttp.ClientSession() as session:
            for evidence in source_evidences:
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
                file_metadata = {
                    "name": file_name,
                    "type": f"image/{file_type}",
                    "size": file_size
                }

                # 테이블 결정 및 메타데이터와 함께 저장
                if evidence.funding_evidence_type_id == 1:
                    file_infos.append({"metadata": file_metadata, "table_name": "funding_trade_evidence_file", "path": tmp_path})
                elif evidence.funding_evidence_type_id == 2:
                    file_infos.append({"metadata": file_metadata, "table_name": "funding_trade_detail_file", "path": tmp_path})
                elif evidence.funding_evidence_type_id == 3:
                    file_infos.append({"metadata": file_metadata, "table_name": "funding_etc_expense_file", "path": tmp_path})
                elif evidence.funding_evidence_type_id == 4:
                    if target_funding.is_fixture:
                        # 비품인 경우 두 테이블에 모두 추가
                        file_infos.append({"metadata": file_metadata, "table_name": "funding_fixture_image_file", "path": tmp_path})
                        file_infos.append({"metadata": file_metadata, "table_name": "funding_club_supplies_image_file", "path": tmp_path})
                    else:
                        file_infos.append({"metadata": file_metadata, "table_name": "funding_club_supplies_image_file", "path": tmp_path})
                elif evidence.funding_evidence_type_id == 5:
                    if target_funding.is_fixture:
                        # 비품인 경우 두 테이블에 모두 추가
                        file_infos.append({"metadata": file_metadata, "table_name": "funding_fixture_software_evidence_file", "path": tmp_path})
                        file_infos.append({"metadata": file_metadata, "table_name": "funding_club_supplies_software_evidence_file", "path": tmp_path})
                    else:
                        file_infos.append({"metadata": file_metadata, "table_name": "funding_club_supplies_software_evidence_file", "path": tmp_path})

        # API를 통해 업로드 URL 획득
        headers = {"Authorization": f"Bearer {API_ACCESS_TOKEN}"}
        max_retries = 3
        
        # 메타데이터 리스트 생성
        file_metadatas = [info["metadata"] for info in file_infos]
        
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
            file_path = file_infos[idx]["path"]
            
            async with aiohttp.ClientSession() as session:
                async with aiofiles.open(file_path, 'rb') as f:
                    file_content = await f.read()
                    
                async with session.put(url_info["uploadUrl"], data=file_content) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to upload file: {url_info['name']}")
            
            results.append({
                "funding_id": target_funding_id,
                "file_id": url_info["fileId"],
                "created_at": source_funding.recent_edit,
                "table_name": file_infos[idx]["table_name"]
            })

        return results

    finally:
        # 임시 파일 정리
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)

def transform_funding_transportation_passengers(
        source_funding: SourceFunding,
        target_students: List[TargetStudent],
        target_funding_id: int
    ) -> List[Dict]:
    return [
        {
            "funding_id": target_funding_id,
            "student_id": target_student.id,
            "created_at": source_funding.recent_edit,
        }
        for target_student in target_students
    ]

def transform_funding_feedbacks(
        source_funding: SourceFunding,
        source_funding_feedbacks: List[SourceFundingFeedback],
        target_executives: List[TargetExecutive],
        target_funding_id: int
    ) -> List[Dict]:
    target_executive_map = {target_executive.student.number: target_executive.id for target_executive in target_executives}

    # created_at으로 중복 제거를 위한 임시 딕셔너리
    unique_feedbacks = {}
    
    for feedback in source_funding_feedbacks:
        if feedback.student_id not in target_executive_map:
            continue
            
        created_at = feedback.added_time
        # 동일한 시간에 대해 가장 마지막 피드백만 유지
        unique_feedbacks[created_at] = {
            "funding_id": target_funding_id,
            "executive_id": target_executive_map[feedback.student_id],
            "funding_status_enum": funding_status_mapping.get(source_funding.funding_feedback_type, 1),
            "approved_amount": source_funding.approved_amount,
            "feedback": feedback.feedback,
            "created_at": created_at,
        }
    
    return list(unique_feedbacks.values())
