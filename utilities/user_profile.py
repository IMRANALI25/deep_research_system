from dataclasses import dataclass


@dataclass
class UserContext:
    user_id: str = "ia-2025"
    user_name: str = "Imran Ali"
    user_email: str = "ee_imranali@yahoo.com"
    user_city: str = "Karachi"
    user_preferences: str = "Technology, Science, AI, Programming"
