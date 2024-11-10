from datetime import datetime
import pytz

class TimeUtils:

    @classmethod
    def vn_current_time(cls) -> datetime:
        now = datetime.now(tz=pytz.utc)
        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        if now.tzinfo is None:
            now = pytz.utc.localize(now)
        now_vn = now.astimezone(vietnam_tz).replace(tzinfo=None)
        return now_vn
