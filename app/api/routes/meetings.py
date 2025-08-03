from fastapi import APIRouter, HTTPException, Query
from app.services.bbb_service import create_meeting, get_join_url, get_active_meetings, get_meeting_info
from app.models.meeting import MeetingRequest, MeetingResponse, MeetingInfoResponse

router = APIRouter()

@router.post("/create", response_model=MeetingResponse)
async def create_meeting_endpoint(data: MeetingRequest):
    try:
        return await create_meeting(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@router.get("/join", tags=["Meetings"])
async def join_meeting_endpoint(
    meeting_id: str = Query(..., alias="meetingID"),
    full_name: str = Query(..., alias="fullName"),
    password: str = Query(...)
):
    try:
        join_url = await get_join_url(meeting_id, full_name, password)
        return {"join_url": join_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/active")
async def list_active_meetings():
    try:
        meetings = await get_active_meetings()
        return {"active_meetings": meetings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@router.get("/info/{meeting_id}", response_model=MeetingInfoResponse)
async def meeting_info(meeting_id: str):
    try:
        return await get_meeting_info(meeting_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
