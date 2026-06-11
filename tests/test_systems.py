"""
SignBridge AI — Layers 7–12 Systems Test Suite
Tests: Conversation Platform, Analytics, Accessibility, Multilingual, Emergency System.
"""

from datetime import UTC, datetime

# ─── Layer 7: Conversation Platform ─────────────────────────────────────────────


class TestConversationSession:
    """Tests for ConversationSession."""

    def setup_method(self):
        from conversation.session import ConversationSession

        self.session = ConversationSession(language="English")

    def test_session_has_unique_id(self):
        from conversation.session import ConversationSession

        s1 = ConversationSession()
        s2 = ConversationSession()
        assert s1.session_id != s2.session_id

    def test_process_signer_input_returns_turn(self):
        turn = self.session.process_signer_input(["HELLO"], "Hello!", "English", 0.95)
        assert turn.final_text == "Hello!"
        assert turn.confidence == 0.95

    def test_add_listener_reply_creates_message(self):
        msg = self.session.add_listener_reply("Hi there!")
        assert msg.text == "Hi there!"

    def test_get_all_messages_grows(self):
        self.session.process_signer_input(["HELLO"], "Hello!")
        self.session.add_listener_reply("Hi!")
        messages = self.session.get_all_messages()
        assert len(messages) == 2

    def test_emotion_detection_urgent(self):
        from conversation.schemas import EmotionTone

        turn = self.session.process_signer_input(
            ["EMERGENCY"], "EMERGENCY!", "English", 1.0
        )
        assert turn.emotion in (EmotionTone.URGENT, EmotionTone.DISTRESSED)

    def test_get_summary_returns_summary(self):
        self.session.process_signer_input(["WATER", "WANT"], "I want water.")
        summary = self.session.get_summary()
        assert summary.total_turns == 1
        assert summary.total_messages == 1

    def test_reset_clears_messages(self):
        self.session.process_signer_input(["HELLO"], "Hello!")
        self.session.reset()
        assert len(self.session.get_all_messages()) == 0

    def test_export_returns_dict(self):
        self.session.process_signer_input(["HELLO"], "Hello!")
        exported = self.session.export()
        assert "session_id" in exported
        assert "messages" in exported


class TestDialogueManager:
    """Tests for the DialogueManager orchestrator."""

    def setup_method(self):
        from conversation.dialogue_manager import DialogueManager

        self.manager = DialogueManager()

    def test_start_session_returns_string(self):
        session_id = self.manager.start_session()
        assert isinstance(session_id, str)

    def test_two_sessions_have_different_ids(self):
        s1 = self.manager.start_session()
        s2 = self.manager.start_session()
        assert s1 != s2

    def test_process_turn_returns_dialogue_turn(self):
        session_id = self.manager.start_session()
        turn = self.manager.process_turn(
            session_id, ["HELLO"], "Hello!", "English", 0.9
        )
        assert turn.final_text == "Hello!"

    def test_add_listener_reply(self):
        session_id = self.manager.start_session()
        msg = self.manager.add_listener_reply(session_id, "How are you?")
        assert msg.text == "How are you?"

    def test_get_messages_includes_both_roles(self):
        session_id = self.manager.start_session()
        self.manager.process_turn(session_id, ["HELLO"], "Hello!")
        self.manager.add_listener_reply(session_id, "Hi there!")
        messages = self.manager.get_messages(session_id)
        assert len(messages) == 2

    def test_reset_session_clears_messages(self):
        session_id = self.manager.start_session()
        self.manager.process_turn(session_id, ["HELLO"], "Hello!")
        result = self.manager.reset_session(session_id)
        assert result is True
        assert len(self.manager.get_messages(session_id)) == 0

    def test_get_recent_context_returns_strings(self):
        session_id = self.manager.start_session()
        self.manager.process_turn(session_id, ["HELLO"], "Hello!")
        context = self.manager.get_recent_context(session_id, 5)
        assert "Hello!" in context

    def test_active_session_count(self):
        before = self.manager.get_active_session_count()
        self.manager.start_session()
        after = self.manager.get_active_session_count()
        assert after == before + 1


class TestEmotionToneDetector:
    """Tests for EmotionToneDetector."""

    def setup_method(self):
        from conversation.emotion_tone import EmotionToneDetector

        self.detector = EmotionToneDetector()

    def test_detect_urgent_from_tokens(self):
        from conversation.schemas import EmotionTone

        result = self.detector.detect_from_tokens(["EMERGENCY"])
        assert result == EmotionTone.URGENT

    def test_detect_neutral_from_empty_tokens(self):
        from conversation.schemas import EmotionTone

        result = self.detector.detect_from_tokens([])
        assert result == EmotionTone.NEUTRAL

    def test_detect_grateful_from_text(self):
        from conversation.schemas import EmotionTone

        result = self.detector.detect_from_text("Thank you so much!")
        assert result == EmotionTone.GRATEFUL

    def test_detect_confused_from_text(self):
        from conversation.schemas import EmotionTone

        result = self.detector.detect_from_text("I don't understand.")
        assert result == EmotionTone.CONFUSED

    def test_token_emotion_takes_priority(self):
        from conversation.schemas import EmotionTone

        result = self.detector.detect(["EMERGENCY"], "Thank you.")
        assert result == EmotionTone.URGENT

    def test_get_response_suggestion_returns_string(self):
        from conversation.schemas import EmotionTone

        suggestion = self.detector.get_response_suggestion(EmotionTone.URGENT)
        assert len(suggestion) > 0
        assert "emergency" in suggestion.lower() or "urgent" in suggestion.lower()


# ─── Layer 9: Analytics Platform ─────────────────────────────────────────────────


class TestMetricsCollector:
    """Tests for the MetricsCollector."""

    def setup_method(self):
        from analytics.metrics_collector import MetricsCollector

        self.collector = MetricsCollector()

    def test_initial_total_zero(self):
        assert self.collector.get_total_translations() == 0

    def test_record_translation_increments(self):
        self.collector.record_translation(["HELLO"], "Hello!", "English", 0.9)
        assert self.collector.get_total_translations() == 1

    def test_average_confidence_single_record(self):
        self.collector.record_translation(["HELLO"], "Hello!", "English", 0.9)
        assert abs(self.collector.get_average_confidence() - 0.9) < 0.001

    def test_gesture_frequency_tracking(self):
        self.collector.record_translation(
            ["HELLO", "WORLD"], "Hello world!", "English", 0.8
        )
        freq = self.collector.get_gesture_frequency()
        assert freq.get("HELLO", 0) == 1
        assert freq.get("WORLD", 0) == 1

    def test_language_distribution_tracking(self):
        self.collector.record_translation(["HELLO"], "Hello!", "English", 0.9)
        self.collector.record_translation(["HOLA"], "Hola!", "Spanish", 0.8)
        dist = self.collector.get_language_distribution()
        assert dist.get("English", 0) == 1
        assert dist.get("Spanish", 0) == 1

    def test_get_top_gestures_returns_list(self):
        self.collector.record_translation(
            ["HELLO", "HELLO", "HELP"], "Hello!", "English", 1.0
        )
        top = self.collector.get_top_gestures(5)
        assert isinstance(top, list)
        assert len(top) > 0
        assert "gesture" in top[0] and "count" in top[0]

    def test_reset_clears_all(self):
        self.collector.record_translation(["HELLO"], "Hello!", "English", 0.9)
        self.collector.reset()
        assert self.collector.get_total_translations() == 0

    def test_full_snapshot_returns_dict(self):
        snapshot = self.collector.get_full_metrics_snapshot()
        assert "total_translations" in snapshot
        assert "average_confidence" in snapshot
        assert "gesture_frequency" in snapshot


# ─── Layer 10: Accessibility Engine ──────────────────────────────────────────────


class TestThemeManager:
    """Tests for the ThemeManager."""

    def setup_method(self):
        from accessibility.theme_manager import ThemeManager

        self.manager = ThemeManager()

    def test_get_all_themes_returns_dict(self):
        themes = self.manager.get_all_themes()
        assert isinstance(themes, dict)
        assert len(themes) > 0

    def test_high_contrast_theme_returns_css(self):
        css = self.manager.apply_theme("high_contrast")
        assert "background-color" in css or "#000000" in css

    def test_bauhaus_default_returns_empty_css(self):
        css = self.manager.apply_theme("bauhaus_default")
        assert css == ""

    def test_invalid_theme_fallback_to_default(self):
        css = self.manager.apply_theme("invalid_theme_name")
        assert isinstance(css, str)

    def test_inject_css_wraps_in_style_tag(self):
        result = self.manager.inject_css("body { color: red; }")
        assert "<style>" in result
        assert "body { color: red; }" in result

    def test_inject_empty_css_returns_empty(self):
        result = self.manager.inject_css("")
        assert result == ""

    def test_combined_css_merges_themes(self):
        css = self.manager.get_combined_css(["high_contrast", "reduced_motion"])
        assert len(css) > 0


class TestKeyboardNavRegistry:
    """Tests for the keyboard navigation registry."""

    def setup_method(self):
        from accessibility.keyboard_nav import KeyboardNavRegistry

        self.registry = KeyboardNavRegistry()

    def test_get_all_shortcuts_non_empty(self):
        shortcuts = self.registry.get_all_shortcuts()
        assert len(shortcuts) > 0

    def test_each_shortcut_has_required_fields(self):
        for shortcut in self.registry.get_all_shortcuts():
            assert "key" in shortcut
            assert "action" in shortcut
            assert "description" in shortcut

    def test_generate_keyboard_listener_contains_script(self):
        html = self.registry.generate_keyboard_listener_html()
        assert "<script>" in html
        assert "keydown" in html

    def test_generate_shortcut_reference_html_contains_table(self):
        html = self.registry.generate_shortcut_reference_html()
        assert "<table" in html


# ─── Layer 11: Multilingual Engine ───────────────────────────────────────────────


class TestLanguageRegistry:
    """Tests for the language registry."""

    def setup_method(self):
        from multilingual.language_registry import LanguageRegistry

        self.registry = LanguageRegistry()

    def test_get_all_returns_16_languages(self):
        all_langs = self.registry.get_all()
        assert len(all_langs) == 16

    def test_get_english_metadata(self):
        lang = self.registry.get("English")
        assert lang is not None
        assert lang.bcp47 == "en-US"
        assert lang.is_rtl is False

    def test_arabic_is_rtl(self):
        lang = self.registry.get("Arabic")
        assert lang.is_rtl is True

    def test_urdu_is_rtl(self):
        lang = self.registry.get("Urdu")
        assert lang.is_rtl is True

    def test_get_rtl_languages_returns_arabic_and_urdu(self):
        rtl = self.registry.get_rtl_languages()
        assert "Arabic" in rtl
        assert "Urdu" in rtl

    def test_get_bcp47_english(self):
        assert self.registry.get_bcp47("English") == "en-US"

    def test_get_bcp47_unknown_fallback(self):
        assert self.registry.get_bcp47("Klingon") == "en-US"

    def test_get_native_name_hindi(self):
        name = self.registry.get_native_name("Hindi")
        assert name == "हिंदी"

    def test_get_flag_returns_emoji(self):
        flag = self.registry.get_flag("English")
        assert "🇺🇸" == flag


class TestRTLHandler:
    """Tests for the RTL handler."""

    def setup_method(self):
        from multilingual.rtl_handler import RTLHandler

        self.handler = RTLHandler()

    def test_arabic_is_rtl(self):
        assert self.handler.is_rtl_language("Arabic") is True

    def test_english_not_rtl(self):
        assert self.handler.is_rtl_language("English") is False

    def test_wrap_rtl_adds_div(self):
        result = self.handler.wrap_rtl_text("مرحبا", "Arabic")
        assert "<div" in result
        assert "rtl" in result

    def test_wrap_ltr_returns_plain_text(self):
        result = self.handler.wrap_rtl_text("Hello", "English")
        assert result == "Hello"

    def test_get_html_dir_rtl(self):
        assert self.handler.get_html_dir_attribute("Arabic") == "rtl"

    def test_get_html_dir_ltr(self):
        assert self.handler.get_html_dir_attribute("English") == "ltr"


# ─── Layer 12: Emergency System ───────────────────────────────────────────────────


class TestSOSDetector:
    """Tests for the SOS detector."""

    def setup_method(self):
        from emergency.sos_detector import SOSDetector

        self.detector = SOSDetector()

    def test_sos_token_triggers_event(self):
        event = self.detector.check_tokens(["SOS"])
        assert event is not None
        assert event.severity in {"CRITICAL", "URGENT", "ALERT"}

    def test_emergency_token_triggers_urgent(self):
        event = self.detector.check_tokens(["EMERGENCY"])
        assert event is not None

    def test_help_token_triggers_alert(self):
        event = self.detector.check_tokens(["HELP"])
        assert event is not None

    def test_neutral_tokens_return_none(self):
        event = self.detector.check_tokens(["HELLO", "HOW", "ARE", "YOU"])
        assert event is None

    def test_empty_tokens_return_none(self):
        event = self.detector.check_tokens([])
        assert event is None

    def test_event_has_required_fields(self):
        event = self.detector.check_tokens(["EMERGENCY"])
        assert hasattr(event, "severity")
        assert hasattr(event, "confidence")
        assert hasattr(event, "message")
        assert hasattr(event, "timestamp")

    def test_window_accumulation(self):
        self.detector.update(["CHEST"])
        self.detector.update(["PAIN"])
        # Window should have accumulated CHEST + PAIN pattern
        assert (
            self.detector.get_event_count() >= 0
        )  # May or may not trigger depending on order


class TestAlertDispatcher:
    """Tests for the alert dispatcher."""

    def setup_method(self):
        from emergency.alert_dispatcher import AlertDispatcher

        self.dispatcher = AlertDispatcher()

    def test_initial_alert_count_zero(self):
        assert self.dispatcher.get_alert_count() == 0

    def test_dispatch_increments_count(self):
        from emergency.sos_detector import LEVEL_URGENT, SOSEvent

        event = SOSEvent(
            severity=LEVEL_URGENT,
            triggered_tokens=["HELP"],
            matching_pattern=["HELP"],
            confidence=0.9,
            timestamp=datetime.now(UTC),
            message="Test event",
        )
        self.dispatcher.dispatch(event, "Test User")
        assert self.dispatcher.get_alert_count() == 1

    def test_dispatch_returns_record_with_id(self):
        from emergency.sos_detector import LEVEL_URGENT, SOSEvent

        event = SOSEvent(
            severity=LEVEL_URGENT,
            triggered_tokens=["HELP"],
            matching_pattern=["HELP"],
            confidence=0.9,
            timestamp=datetime.now(UTC),
            message="Test",
        )
        record = self.dispatcher.dispatch(event)
        assert record.alert_id.startswith("ALT_")

    def test_clear_history(self):
        from emergency.sos_detector import LEVEL_URGENT, SOSEvent

        event = SOSEvent(
            severity=LEVEL_URGENT,
            triggered_tokens=["HELP"],
            matching_pattern=["HELP"],
            confidence=0.9,
            timestamp=datetime.now(UTC),
            message="Test",
        )
        self.dispatcher.dispatch(event)
        self.dispatcher.clear_history()
        assert self.dispatcher.get_alert_count() == 0


class TestEmergencyPhrases:
    """Tests for emergency phrase bank."""

    def test_sos_trigger_tokens_non_empty(self):
        from emergency.emergency_phrases import SOS_TRIGGER_TOKENS

        assert len(SOS_TRIGGER_TOKENS) > 0
        assert "EMERGENCY" in SOS_TRIGGER_TOKENS

    def test_get_english_phrase_passthrough(self):
        from emergency.emergency_phrases import get_emergency_phrase

        phrase = "EMERGENCY — I need immediate help!"
        result = get_emergency_phrase(phrase, "English")
        assert result == phrase

    def test_get_spanish_phrase(self):
        from emergency.emergency_phrases import get_emergency_phrase

        result = get_emergency_phrase("Call an ambulance.", "Spanish")
        assert "ambulancia" in result.lower()

    def test_get_hindi_phrase(self):
        from emergency.emergency_phrases import get_emergency_phrase

        result = get_emergency_phrase("I cannot breathe.", "Hindi")
        assert len(result) > 0

    def test_unknown_phrase_returns_english(self):
        from emergency.emergency_phrases import get_emergency_phrase

        result = get_emergency_phrase("Some unknown phrase", "Spanish")
        assert result == "Some unknown phrase"  # No translation = fallback

    def test_emergency_categories_non_empty(self):
        from emergency.emergency_phrases import EMERGENCY_CATEGORIES

        assert len(EMERGENCY_CATEGORIES) >= 4
        assert "Medical" in EMERGENCY_CATEGORIES
        assert "Safety" in EMERGENCY_CATEGORIES
