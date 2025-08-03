import hashlib
import httpx
import xmltodict
from urllib.parse import urlencode
from app.core.config import settings
from app.models.meeting import MeetingRequest, MeetingResponse, MeetingInfoResponse
from urllib.parse import quote_plus

BASE_URL = settings.BBB_URL.rstrip("/")
SECRET = settings.BBB_SECRET

async def create_meeting(data: MeetingRequest) -> MeetingResponse:
    params = {
        "name": data.name,
        "meetingID": data.meetingID,
        "moderatorPW": data.moderatorPW,
        "attendeePW": data.attendeePW,
    }
    if data.welcome:
        params["welcome"] = data.welcome
    if data.duration:
        params["duration"] = str(data.duration)

    sorted_items = sorted(params.items())
    encoded_str = urlencode(sorted_items, quote_via=quote_plus)
    checksum = hashlib.sha1(f"create{encoded_str}{SECRET}".encode("utf-8")).hexdigest()
    create_url = f"{BASE_URL}/create?{encoded_str}&checksum={checksum}"

    async with httpx.AsyncClient() as client:
        response = await client.get(create_url)

        if "<returncode>SUCCESS</returncode>" not in response.text:
            return MeetingResponse(join_url="", meetingID=data.meetingID, status="error")

    
    join_params_mod = {
        "meetingID": data.meetingID,
        "fullName": "Coordinador",
        "password": data.moderatorPW,
    }
    sorted_join_mod = sorted(join_params_mod.items())
    encoded_join_mod = urlencode(sorted_join_mod, quote_via=quote_plus)
    join_checksum_mod = hashlib.sha1(f"join{encoded_join_mod}{SECRET}".encode("utf-8")).hexdigest()
    join_url_mod = f"{BASE_URL}/join?{encoded_join_mod}&checksum={join_checksum_mod}"

    # 🔗 URL para participante
    join_params_att = {
        "meetingID": data.meetingID,
        "fullName": "Colaborador",
        "password": data.attendeePW,
    }
    sorted_join_att = sorted(join_params_att.items())
    encoded_join_att = urlencode(sorted_join_att, quote_via=quote_plus)
    join_checksum_att = hashlib.sha1(f"join{encoded_join_att}{SECRET}".encode("utf-8")).hexdigest()
    join_url_att = f"{BASE_URL}/join?{encoded_join_att}&checksum={join_checksum_att}"


    # join_params = {
    #     "meetingID": data.meetingID,
    #     "fullName": "Coordinador",
    #     "password": data.moderatorPW,
    # }
    # sorted_join = sorted(join_params.items())
    # encoded_join = urlencode(sorted_join, quote_via=quote_plus)
    # join_checksum = hashlib.sha1(f"join{encoded_join}{SECRET}".encode("utf-8")).hexdigest()
    # join_url = f"{BASE_URL}/join?{encoded_join}&checksum={join_checksum}"

    return MeetingResponse(moderator_url=join_url_mod, attendee_url=join_url_att, meetingID=data.meetingID, status="created")

async def get_join_url(meeting_id: str, full_name: str, password: str):
    join_params = {
        "meetingID": meeting_id,
        "fullName": full_name,
        "password": password,
    }
    join_str = urlencode(join_params)
    checksum = hashlib.sha1(f"join{join_str}{SECRET}".encode()).hexdigest()
    return f"{BASE_URL}/join?{join_str}&checksum={checksum}"

async def get_active_meetings():
    action = "getMeetings"
    checksum = hashlib.sha1(f"{action}{SECRET}".encode()).hexdigest()
    url = f"{BASE_URL}/{action}?checksum={checksum}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code != 200:
            raise Exception("No se pudo obtener las reuniones activas")

        data = xmltodict.parse(response.text)
        
        meetings_data = data.get("response", {}).get("meetings")

        if not meetings_data or not isinstance(meetings_data, dict):
            meetings = []
        else:
            meeting = meetings_data.get("meeting")
            if meeting is None:
                meetings = []
            elif isinstance(meeting, dict):
                meetings = [meeting]
            else:
                meetings = meeting

        return meetings
    
async def get_meeting_info(meeting_id: str) -> MeetingInfoResponse:
    action = "getMeetingInfo"
    params = {
        "meetingID": meeting_id,
    }
    query_str = urlencode(params)
    checksum = hashlib.sha1(f"{action}{query_str}{SECRET}".encode()).hexdigest()
    url = f"{BASE_URL}/{action}?{query_str}&checksum={checksum}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code != 200:
            raise Exception("No se pudo obtener la información de la reunión")

        data = xmltodict.parse(response.text)
        response_data = data.get("response", {})

        if response_data.get("returncode") != "SUCCESS":
            raise Exception(response_data.get("message", "Reunión no encontrada"))

        return MeetingInfoResponse(
            meetingID=response_data.get("meetingID"),
            running=response_data.get("running") == "true",
            participantCount=int(response_data.get("participantCount", 0)),
            moderatorCount=int(response_data.get("moderatorCount", 0)),
            startTime=response_data.get("startTime"),
            endTime=response_data.get("endTime"),
        )