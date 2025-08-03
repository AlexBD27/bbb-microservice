from pydantic import BaseModel

class MeetingRequest(BaseModel):
    meetingID: str
    moderatorPW: str
    attendeePW: str
    name: str
    welcome: str | None = None
    duration: int | None = None

class MeetingResponse(BaseModel):
    moderator_url: str
    attendee_url: str
    meetingID: str
    status: str

class MeetingInfoResponse(BaseModel):
    meetingID: str
    running: bool
    participantCount: int
    moderatorCount: int
    startTime: str | None = None
    endTime: str | None = None
