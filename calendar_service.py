"""تكامل Google Calendar: عرض، إضافة، حذف، والبحث عن المواعيد."""

import json
import os
from datetime import datetime, timedelta
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarService:
    def __init__(self, settings):
        self.settings = settings
        self.service = self._build_service()

    def _build_service(self):
        creds = None
        if self.settings.google_token_json:
            creds = Credentials.from_authorized_user_info(
                json.loads(self.settings.google_token_json), SCOPES
            )
        elif os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        if not creds or not creds.valid:
            if self.settings.google_credentials_json:
                client_config = json.loads(self.settings.google_credentials_json)
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=0)
            elif os.path.exists("credentials.json"):
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                raise RuntimeError(
                    "لم يتم العثور على GOOGLE_TOKEN_JSON أو credentials.json. "
                    "شغّل scripts/authorize_calendar.py أولاً."
                )
            # يُستخدم محلياً فقط؛ في Railway ضَع محتواه في GOOGLE_TOKEN_JSON.
            with open("token.json", "w", encoding="utf-8") as file:
                file.write(creds.to_json())

        return build("calendar", "v3", credentials=creds, cache_discovery=False)

    @staticmethod
    def _event_datetime(event: dict[str, Any]) -> datetime:
        raw = event["start"].get("dateTime") or event["start"].get("date")
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))

    def upcoming(self, hours: int = 168, limit: int = 20):
        now = datetime.now().astimezone()
        result = self.service.events().list(
            calendarId=self.settings.calendar_id,
            timeMin=now.isoformat(),
            timeMax=(now + timedelta(hours=hours)).isoformat(),
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        return result.get("items", [])

    def create_event(self, summary: str, start: datetime, end: datetime, description: str = ""):
        body = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start.isoformat(), "timeZone": self.settings.timezone},
            "end": {"dateTime": end.isoformat(), "timeZone": self.settings.timezone},
        }
        return self.service.events().insert(calendarId=self.settings.calendar_id, body=body).execute()

    def delete_event(self, event_id: str):
        self.service.events().delete(calendarId=self.settings.calendar_id, eventId=event_id).execute()

    def find_event(self, event_id: str):
        return self.service.events().get(calendarId=self.settings.calendar_id, eventId=event_id).execute()

    def events_starting_between(self, start: datetime, end: datetime):
        result = self.service.events().list(
            calendarId=self.settings.calendar_id,
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            maxResults=50,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        return result.get("items", [])
