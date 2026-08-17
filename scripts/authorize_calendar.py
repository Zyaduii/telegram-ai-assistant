"""شغّل هذا السكربت محلياً مرة واحدة لتفويض Google Calendar."""

import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
    credentials_path = Path("credentials.json")
    if not credentials_path.exists():
        raise SystemExit("ضع ملف credentials.json بجانب هذا السكربت ثم أعد التشغيل.")
    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    credentials = flow.run_local_server(port=0)
    Path("token.json").write_text(credentials.to_json(), encoding="utf-8")
    print("تم إنشاء token.json. انسخ محتواه إلى GOOGLE_TOKEN_JSON في Railway.")
    print(json.dumps(json.loads(credentials.to_json()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
