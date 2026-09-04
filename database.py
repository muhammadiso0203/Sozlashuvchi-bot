import json
import random
import re
import logging
from pathlib import Path
from typing import Optional, List, Dict, Set
from config import RESPONSES_FILE

logger = logging.getLogger(__name__)

def normalize_uzbek(text: str) -> str:
    """O'zbekcha tutuq belgilarini va harflarni standartlashtiradi."""
    if not text:
        return ""
    for char in ["’", "‘", "ʻ", "ʼ", "`", "´"]:
        text = text.replace(char, "'")
    return text.lower().strip()

def clean_text(text: str) -> str:
    """Matndan tinish belgilarini olib tashlaydi, emojilarni va so'zlarni saqlab qoladi."""
    if not text:
        return ""
    text = normalize_uzbek(text)
    cleaned = re.sub(r'[\.,!?;:"\(\)\[\]\{\}\-_~/\\]', ' ', text)
    return " ".join(cleaned.split())

class DatabaseManager:
    def __init__(self, file_path: Path = RESPONSES_FILE):
        self.file_path = file_path
        self._data: Dict = {}
        self.load_data()

    def load_data(self):
        """JSON faylidan so'zlar va statistikani yuklaydi."""
        if not self.file_path.exists():
            self._data = {
                "exact_matches": {},
                "contains_matches": {},
                "mention_responses": [
                    "Labbay, qanday yordam bera olaman?",
                    "Salom! Men shu yerdaman 😊"
                ],
                "users": [],
                "groups": []
            }
            self.save_data()
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            
            # Agar users, groups yoki random_responses bo'lmasa, qo'shib qo'yamiz
            if "users" not in self._data:
                self._data["users"] = []
            if "groups" not in self._data:
                self._data["groups"] = []
            if "random_responses" not in self._data:
                self._data["random_responses"] = []
        except Exception as e:
            logger.error(f"Ma'lumotlar bazasini yuklashda xatolik: {e}")
            self._data = {
                "exact_matches": {},
                "contains_matches": {},
                "mention_responses": [],
                "random_responses": [],
                "users": [],
                "groups": []
            }

    def save_data(self):
        """Ma'lumotlarni JSON fayliga saqlaydi."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ma'lumotlar bazasini saqlashda xatolik: {e}")

    def add_user(self, user_id: int):
        """Yangi foydalanuvchini ro'yxatga qo'shadi."""
        users = self._data.setdefault("users", [])
        if user_id not in users:
            users.append(user_id)
            self.save_data()

    def add_group(self, chat_id: int):
        """Yangi guruhni ro'yxatga qo'shadi."""
        groups = self._data.setdefault("groups", [])
        if chat_id not in groups:
            groups.append(chat_id)
            self.save_data()

    def remove_group(self, chat_id: int):
        """Guruhni ro'yxatdan o'chiradi (bot chiqarib yuborilganda)."""
        groups = self._data.get("groups", [])
        if chat_id in groups:
            groups.remove(chat_id)
            self.save_data()

    def get_users(self) -> List[int]:
        """Barcha saqlangan foydalanuvchi ID lari ro'yxatini qaytaradi."""
        return list(self._data.get("users", []))

    def remove_user(self, user_id: int):
        """Foydalanuvchini ro'yxatdan o'chiradi (botni bloklaganda)."""
        users = self._data.get("users", [])
        if user_id in users:
            users.remove(user_id)
            self.save_data()

    def get_groups(self) -> List[int]:
        """Barcha saqlangan guruh ID lari ro'yxatini qaytaradi."""
        return list(self._data.get("groups", []))

    def find_response(self, text: str, is_mentioned_or_reply: bool = False) -> Optional[str]:
        """
        Kelgan xabarga mos javobni topadi.
        1-bosqich: Aniq moslik (Exact match)
        2-bosqich: Matn ichida uchrashi (Contains match)
        3-bosqich: Agar botga to'g'ridan-to'g'ri murojaat qilingan bo'lsa (Mention/Reply)
        """
        cleaned = clean_text(text)
        if not cleaned and not is_mentioned_or_reply:
            return None

        # 1. Aniq moslik
        exact_matches = self._data.get("exact_matches", {})
        if cleaned:
            for keyword, replies in exact_matches.items():
                if clean_text(keyword) == cleaned:
                    return random.choice(replies) if isinstance(replies, list) else replies

            # 2. Qisman moslik (xabar ichida kalit so'z yoki ibora uchrashi)
            contains_matches = self._data.get("contains_matches", {})
            for keyword, replies in contains_matches.items():
                cleaned_kw = clean_text(keyword)
                if cleaned_kw and cleaned_kw in cleaned:
                    return random.choice(replies) if isinstance(replies, list) else replies

        # 3. Agar botga reply yoki tag qilingan bo'lsa va kalit so'z topilmagan bo'lsa
        if is_mentioned_or_reply:
            mentions = self._data.get("mention_responses", [])
            randoms = self._data.get("random_responses", [])
            all_mentions = (mentions if mentions else []) + (randoms if randoms else [])
            if all_mentions:
                return random.choice(all_mentions)

        return None

    def get_random_response(self) -> Optional[str]:
        """Guruhdagi suhbatga tasodifiy qo'shilish uchun javoblardan birini tanlaydi."""
        random_list = self._data.get("random_responses", [])
        if random_list:
            return random.choice(random_list)
        return None

    def add_keyword_response(self, match_type: str, keyword: str, response: str) -> bool:
        """
        Yangi kalit so'z va unga javob qo'shadi.
        match_type: 'exact' yoki 'contains'
        """
        key_type = "exact_matches" if match_type == "exact" else "contains_matches"
        kw = keyword.strip().lower()
        if not kw:
            return False

        if key_type not in self._data:
            self._data[key_type] = {}

        if kw in self._data[key_type]:
            if isinstance(self._data[key_type][kw], list):
                if response not in self._data[key_type][kw]:
                    self._data[key_type][kw].append(response)
            else:
                self._data[key_type][kw] = [self._data[key_type][kw], response]
        else:
            self._data[key_type][kw] = [response]

        self.save_data()
        return True

    def remove_keyword(self, keyword: str) -> bool:
        """Kalit so'zni bazadan o'chiradi."""
        kw = keyword.strip().lower()
        found = False
        for category in ["exact_matches", "contains_matches"]:
            if kw in self._data.get(category, {}):
                del self._data[category][kw]
                found = True

        if found:
            self.save_data()
        return found

    def get_all_keywords(self) -> dict:
        """Barcha mavjud kalit so'zlarni qaytaradi."""
        return {
            "exact": list(self._data.get("exact_matches", {}).keys()),
            "contains": list(self._data.get("contains_matches", {}).keys())
        }

    def get_stats(self) -> dict:
        """Baza va bot statistikasini qaytaradi."""
        exact_count = len(self._data.get("exact_matches", {}))
        contains_count = len(self._data.get("contains_matches", {}))
        mention_count = len(self._data.get("mention_responses", []))
        users_count = len(self._data.get("users", []))
        groups_count = len(self._data.get("groups", []))

        return {
            "users_count": users_count,
            "groups_count": groups_count,
            "exact_keywords": exact_count,
            "contains_keywords": contains_count,
            "mention_replies": mention_count,
            "total_keywords": exact_count + contains_count
        }

db = DatabaseManager()
