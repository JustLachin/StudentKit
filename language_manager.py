"""
Language Manager for Student Study Kit
Supports JSON language files and custom user translations
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any


class LanguageManager:
    """
    Professional Language Manager with JSON support
    Allows users to add custom language files
    """
    
    def __init__(self, languages_dir: str = "languages"):
        self.languages_dir = Path(languages_dir)
        self.languages_dir.mkdir(exist_ok=True)
        
        self.current_language = "tr"  # Default language
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.available_languages: Dict[str, str] = {}  # code: name
        
        self.load_all_languages()
        
        # Create default language files if they don't exist
        self._create_default_languages()
    
    def _create_default_languages(self):
        """Create default Turkish and English language files if not exist"""
        
        # Turkish language file
        tr_data = {
            "metadata": {
                "code": "tr",
                "name": "Türkçe",
                "native_name": "Türkçe",
                "author": "Student Study Kit",
                "version": "1.0"
            },
            "app": {
                "title": "Öğrenci Ders Kiti",
                "subtitle": "Kapsamlı çalışma arkadaşınız",
                "loading": "Yükleniyor...",
                "saving": "Kaydediliyor...",
                "error": "Hata",
                "success": "Başarılı",
                "warning": "Uyarı",
                "info": "Bilgi",
                "cancel": "İptal",
                "save": "Kaydet",
                "delete": "Sil",
                "edit": "Düzenle",
                "add": "Ekle",
                "close": "Kapat",
                "back": "Geri",
                "next": "İleri",
                "finish": "Bitir",
                "search": "Ara",
                "filter": "Filtrele",
                "sort": "Sırala",
                "refresh": "Yenile",
                "settings": "Ayarlar",
                "language": "Dil",
                "theme": "Tema",
                "volume": "Ses",
                "notifications": "Bildirimler"
            },
            "navigation": {
                "dashboard": "Ana Sayfa",
                "pomodoro": "Pomodoro",
                "notes": "Notlar",
                "lessons": "Dersler",
                "exams": "Sınavlar",
                "settings": "Ayarlar"
            },
            "dashboard": {
                "title": "Ana Sayfa",
                "welcome": "Hoş Geldiniz",
                "subtitle": "Kapsamlı çalışma arkadaşınız",
                "stats": {
                    "focus_sessions_7d": "Odak Seansları (7g)",
                    "total_focus_time": "Toplam Odak Süresi",
                    "notes_created": "Oluşturulan Notlar",
                    "upcoming_exams": "Yaklaşan Sınavlar"
                },
                "quick_actions": "Hızlı İşlemler",
                "actions": {
                    "start_pomodoro": "Pomodoro Başlat",
                    "new_note": "Yeni Not",
                    "view_schedule": "Programı Gör",
                    "check_exams": "Sınavları Kontrol Et"
                },
                "recent_activity": "Son Aktiviteler",
                "no_activity": "Henüz aktivite yok"
            },
            "pomodoro": {
                "title": "Pomodoro Zamanlayıcı",
                "timer": {
                    "focus_time": "ODAK ZAMANI",
                    "break_time": "MOLA ZAMANI",
                    "ready": "HAZIR"
                },
                "stats": {
                    "todays_sessions": "Bugünkü Seanslar",
                    "focus_duration": "Odak Süresi",
                    "completed": "Tamamlanan"
                },
                "controls": {
                    "start": "BAŞLAT",
                    "pause": "DURAKLAT",
                    "reset": "SIFIRLA",
                    "resume": "DEVAM ET",
                    "skip_break": "Molayı Atla"
                },
                "duration": "Süre",
                "durations": {
                    "15m": "15 dk",
                    "25m": "25 dk",
                    "45m": "45 dk",
                    "60m": "60 dk",
                    "custom": "Özel"
                },
                "subject": "Ders",
                "subjects": [
                    "Genel",
                    "Matematik",
                    "Fizik",
                    "Kimya",
                    "Biyoloji",
                    "Tarih",
                    "Coğrafya",
                    "Edebiyat",
                    "Programlama",
                    "İngilizce",
                    "Almanca",
                    "Diğer"
                ],
                "break": {
                    "short_break": "Kısa Mola (5 dk)",
                    "long_break": "Uzun Mola (15 dk)",
                    "break_started": "Mola başladı!",
                    "break_finished": "Mola bitti!"
                },
                "notifications": {
                    "session_complete": "Odak seansı tamamlandı!",
                    "break_complete": "Mola tamamlandı!",
                    "time_remaining": "Kalan süre: {minutes}:{seconds}"
                }
            },
            "notes": {
                "title": "Notlarım",
                "search_placeholder": "Not ara...",
                "new_note": "Yeni Not",
                "edit_note": "Notu Düzenle",
                "delete_note": "Notu Sil",
                "no_notes": "Henüz not yok",
                "created": "Oluşturuldu",
                "updated": "Güncellendi",
                "form": {
                    "title": "Not Başlığı",
                    "title_placeholder": "Not başlığı girin...",
                    "subject": "Ders",
                    "content": "İçerik",
                    "content_placeholder": "Notlarınızı buraya yazın..."
                },
                "actions": {
                    "record_voice": "Ses Kaydet",
                    "stop_recording": "Kaydı Durdur",
                    "attach_pdf": "PDF Ekle",
                    "view_pdf": "PDF Görüntüle",
                    "delete_pdf": "PDF Kaldır",
                    "recording": "Kaydediliyor...",
                    "audio_attached": "Ses dosyası eklendi",
                    "pdf_attached": "PDF dosyası eklendi"
                },
                "confirm_delete": "Bu notu silmek istediğinize emin misiniz?",
                "save_success": "Not başarıyla kaydedildi!",
                "delete_success": "Not başarıyla silindi!"
            },
            "lessons": {
                "title": "Haftalık Ders Programı",
                "add_lesson": "Ders Ekle",
                "edit_lesson": "Dersi Düzenle",
                "delete_lesson": "Dersi Sil",
                "no_lessons": "Bugün ders yok",
                "todays_lessons": "Bugünün Dersleri:",
                "days": [
                    "Pazartesi",
                    "Salı",
                    "Çarşamba",
                    "Perşembe",
                    "Cuma",
                    "Cumartesi",
                    "Pazar"
                ],
                "form": {
                    "subject": "Ders",
                    "subject_placeholder": "Ders adı",
                    "day": "Gün",
                    "start_time": "Başlangıç Saati",
                    "end_time": "Bitiş Saati",
                    "room": "Sınıf",
                    "room_placeholder": "Sınıf/Oda",
                    "teacher": "Öğretmen",
                    "teacher_placeholder": "Öğretmen adı",
                    "color": "Renk"
                },
                "lesson_card": {
                    "room": "Sınıf",
                    "teacher": "Öğretmen"
                },
                "confirm_delete": "Bu dersi silmek istediğinize emin misiniz?",
                "save_success": "Ders başarıyla eklendi!",
                "delete_success": "Ders başarıyla silindi!"
            },
            "exams": {
                "title": "Sınav Takvimi",
                "add_exam": "Sınav Ekle",
                "edit_exam": "Sınavı Düzenle",
                "delete_exam": "Sınavı Sil",
                "no_exams": "Yaklaşan sınav yok",
                "next_exam_countdown": "Sonraki Sınav Geri Sayımı",
                "countdown": {
                    "days": "g",
                    "hours": "s",
                    "minutes": "d",
                    "seconds": "sn",
                    "exam_now": "SINAV ZAMANI!",
                    "exam_started": "SINAV BAŞLADI!"
                },
                "status": {
                    "today": "BUGÜN!",
                    "tomorrow": "Yarın",
                    "days_left": "{days} gün",
                    "past": "Geçmiş"
                },
                "form": {
                    "title": "Başlık",
                    "title_placeholder": "Sınav adı",
                    "subject": "Ders",
                    "subject_placeholder": "Ders adı",
                    "date_time": "Tarih & Saat",
                    "duration": "Süre",
                    "duration_suffix": "dk",
                    "location": "Yer",
                    "location_placeholder": "Sınav yeri",
                    "priority": "Öncelik",
                    "notes": "Notlar"
                },
                "priorities": [
                    "Düşük",
                    "Orta",
                    "Yüksek"
                ],
                "details": {
                    "subject": "Ders",
                    "date": "Tarih",
                    "time": "Saat",
                    "location": "Yer",
                    "duration": "Süre",
                    "priority": "Öncelik"
                },
                "confirm_delete": "Bu sınavı silmek istediğinize emin misiniz?",
                "save_success": "Sınav başarıyla eklendi!",
                "delete_success": "Sınav başarıyla silindi!",
                "alert": {
                    "title": "Sınav Yaklaşıyor!",
                    "message": "{exam_name} sınavına 5 dakika kaldı!"
                }
            },
            "settings": {
                "title": "Ayarlar",
                "language": {
                    "title": "Dil Ayarları",
                    "current": "Mevcut Dil",
                    "select": "Dil Seçin",
                    "add_custom": "Özel Dil Ekle",
                    "custom_info": "Kendi JSON dil dosyanızı yükleyin",
                    "language_changed": "Dil değiştirildi!"
                },
                "appearance": {
                    "title": "Görünüm",
                    "theme": "Tema",
                    "dark_mode": "Koyu Mod",
                    "light_mode": "Açık Mod",
                    "accent_color": "Vurgu Rengi"
                },
                "sound": {
                    "title": "Ses Ayarları",
                    "volume": "Ses Seviyesi",
                    "mute": "Sesi Kapat",
                    "sound_effects": "Ses Efektleri",
                    "notifications": "Bildirim Sesleri"
                },
                "data": {
                    "title": "Veri Yönetimi",
                    "export": "Verileri Dışa Aktar",
                    "import": "Verileri İçe Aktar",
                    "backup": "Yedekle",
                    "restore": "Geri Yükle",
                    "clear_all": "Tüm Verileri Temizle",
                    "confirm_clear": "Tüm verileri silmek istediğinize emin misiniz? Bu işlem geri alınamaz!"
                },
                "about": {
                    "title": "Hakkında",
                    "version": "Versiyon",
                    "author": "Geliştirici",
                    "license": "Lisans",
                    "github": "GitHub"
                }
            },
            "time": {
                "minute": "dakika",
                "minutes": "dakika",
                "hour": "saat",
                "hours": "saat",
                "day": "gün",
                "days": "gün",
                "today": "Bugün",
                "tomorrow": "Yarın",
                "yesterday": "Dün"
            },
            "confirmations": {
                "delete_title": "Silme Onayı",
                "delete_message": "Bu öğeyi silmek istediğinize emin misiniz?",
                "unsaved_changes": "Kaydedilmemiş değişiklikler var. Çıkmak istediğinize emin misiniz?",
                "overwrite": "Bu dosya zaten var. Üzerine yazmak istiyor musunuz?"
            }
        }
        
        # Save Turkish file
        tr_file = self.languages_dir / "tr.json"
        if not tr_file.exists():
            with open(tr_file, 'w', encoding='utf-8') as f:
                json.dump(tr_data, f, ensure_ascii=False, indent=2)
    
    def load_all_languages(self):
        """Load all available language files from languages directory"""
        if not self.languages_dir.exists():
            return
        
        for json_file in self.languages_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                lang_code = json_file.stem
                self.translations[lang_code] = data
                
                # Get language name from metadata
                metadata = data.get("metadata", {})
                lang_name = metadata.get("native_name", metadata.get("name", lang_code))
                self.available_languages[lang_code] = lang_name
                
            except Exception as e:
                print(f"Error loading language file {json_file}: {e}")
    
    def set_language(self, lang_code: str) -> bool:
        """Set current language"""
        if lang_code in self.translations:
            self.current_language = lang_code
            return True
        return False
    
    def get(self, key_path: str, default: Optional[str] = None, **kwargs) -> str:
        """
        Get translation by key path (e.g., 'app.title', 'pomodoro.timer.focus_time')
        Supports nested keys with dot notation
        """
        try:
            # Get current language translation
            translation = self.translations.get(self.current_language, {})
            
            # Navigate through nested keys
            keys = key_path.split('.')
            value = translation
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key, default or key_path)
                else:
                    return default or key_path
            
            # If value is still a dict, return default
            if isinstance(value, dict):
                return default or key_path
            
            # Format with kwargs if provided
            if kwargs and isinstance(value, str):
                try:
                    value = value.format(**kwargs)
                except KeyError:
                    pass
            
            return value if value is not None else (default or key_path)
            
        except Exception as e:
            return default or key_path
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get dictionary of available languages {code: name}"""
        return self.available_languages.copy()
    
    def add_custom_language(self, file_path: str) -> bool:
        """Add a custom language file"""
        try:
            source = Path(file_path)
            if not source.exists():
                return False
            
            # Copy to languages directory
            dest = self.languages_dir / source.name
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate basic structure
            if "metadata" not in data or "app" not in data:
                return False
            
            with open(dest, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Reload languages
            self.load_all_languages()
            return True
            
        except Exception as e:
            print(f"Error adding custom language: {e}")
            return False
    
    def get_current_language_info(self) -> Dict[str, Any]:
        """Get information about current language"""
        translation = self.translations.get(self.current_language, {})
        return translation.get("metadata", {
            "code": self.current_language,
            "name": self.current_language,
            "native_name": self.current_language
        })
    
    def reload_languages(self):
        """Reload all language files"""
        self.translations.clear()
        self.available_languages.clear()
        self.load_all_languages()


# Global language manager instance
_lang_manager: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    """Get or create global language manager instance"""
    global _lang_manager
    if _lang_manager is None:
        _lang_manager = LanguageManager()
    return _lang_manager


def _(key_path: str, default: Optional[str] = None, **kwargs) -> str:
    """Shortcut function for getting translations"""
    return get_language_manager().get(key_path, default, **kwargs)
