"""
Unit tests for EmailClient inbound mapping (ngen.mailer.email_client).

These exercise the defensive ingestion path: a single malformed inbound message
(missing Message-ID / Subject / Date header, HTML-only body, or otherwise
unparseable) must never abort the batch, and no content must be silently lost.
"""

import io
import os
import time
from datetime import datetime, timezone as dt_timezone
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from ngen.mailer.email_client import EmailClient
from ngen.models import EmailMessage


class FakeImboxMessage:
    """
    Mimics imbox's ``Struct``: only the attributes explicitly provided exist, so
    a missing header is a missing attribute (exactly like real imbox output).
    """

    def __init__(self, **attrs):
        self.__dict__.update(attrs)


def _client():
    # Build the client without __init__ so it does not connect to a server.
    return EmailClient.__new__(EmailClient)


RAW_FULL = (
    "Message-ID: <abc@ext.org>\r\n"
    "References: <root@ngen> <parent@ngen>\r\n"
    "In-Reply-To: <parent@ngen>\r\n"
    "Subject: Re: Case\r\n"
    "From: admin@fac.unlp.edu.ar\r\n"
    "\r\n"
    "hello"
)


class MapEmailTest(SimpleTestCase):
    def setUp(self):
        self.client = _client()

    def test_full_message_maps_all_fields(self):
        msg = FakeImboxMessage(
            message_id="<abc@ext.org>",
            subject="Re: Case",
            parsed_date=None,
            sent_from=[{"name": "Admin", "email": "admin@fac.unlp.edu.ar"}],
            sent_to=[{"name": "ngen", "email": "incidentes@cert.unlp.edu.ar"}],
            body={"plain": ["hello"], "html": ["<p>hello</p>"]},
            attachments=[],
            raw_email=RAW_FULL,
        )
        em = self.client.map_email(msg)
        self.assertEqual(em.message_id, "<abc@ext.org>")
        self.assertEqual(em.root_message_id, "<root@ngen>")      # References[0]
        self.assertEqual(em.parent_message_id, "<parent@ngen>")  # In-Reply-To
        self.assertEqual(em.references, ["<root@ngen>", "<parent@ngen>"])
        self.assertEqual(em.body, "hello")
        self.assertEqual(em.body_html, "<p>hello</p>")
        self.assertEqual(em.subject, "Re: Case")
        self.assertEqual(em.senders[0]["email"], "admin@fac.unlp.edu.ar")
        self.assertEqual(em.status, EmailMessage.Status.SENT)

    def test_html_only_body_does_not_crash(self):
        # Previously `body["plain"][0]` raised IndexError and killed the batch.
        msg = FakeImboxMessage(
            message_id="<html@ext.org>",
            subject="HTML only",
            parsed_date=None,
            sent_from=[],
            sent_to=[],
            body={"plain": [], "html": ["<p>only html</p>"]},
            attachments=[],
            raw_email="Message-ID: <html@ext.org>\r\n\r\n",
        )
        em = self.client.map_email(msg)
        self.assertEqual(em.body, "")
        self.assertEqual(em.body_html, "<p>only html</p>")

    def test_missing_message_id_is_derived_deterministically(self):
        # Previously a missing Message-ID raised
        # `AttributeError: 'Struct' object has no attribute 'message_id'`.
        attrs = dict(
            subject="No id",
            parsed_date=None,
            sent_from=[],
            sent_to=[],
            body={"plain": ["x"], "html": []},
            attachments=[],
            raw_email="Subject: No id\r\n\r\nx",
        )
        em1 = self.client.map_email(FakeImboxMessage(**attrs))
        em2 = self.client.map_email(FakeImboxMessage(**attrs))
        self.assertTrue(em1.message_id)
        self.assertTrue(em1.message_id.endswith("@no-message-id.ngen>"))
        self.assertEqual(em1.message_id, em2.message_id)  # deterministic -> dedup-safe

    def test_missing_subject_and_date_do_not_crash(self):
        msg = FakeImboxMessage(
            message_id="<nosub@ext.org>",
            sent_from=[],
            sent_to=[],
            body={"plain": ["body"], "html": []},
            attachments=[],
            raw_email="Message-ID: <nosub@ext.org>\r\n\r\nbody",
        )
        em = self.client.map_email(msg)
        self.assertEqual(em.subject, "")
        self.assertIsNone(em.date)
        self.assertEqual(em.body, "body")

    def test_bytes_body_part_is_decoded(self):
        msg = FakeImboxMessage(
            message_id="<bytes@ext.org>",
            subject="b",
            parsed_date=None,
            sent_from=[],
            sent_to=[],
            body={"plain": [b"ol\xc3\xa1"], "html": []},
            attachments=[],
            raw_email="Message-ID: <bytes@ext.org>\r\n\r\n",
        )
        em = self.client.map_email(msg)
        self.assertEqual(em.body, "olá")

    def test_multiple_body_parts_are_joined(self):
        # A multipart message may carry several parts of the same type; keep all.
        msg = FakeImboxMessage(
            message_id="<multi@ext.org>",
            subject="multi",
            parsed_date=None,
            sent_from=[],
            sent_to=[],
            body={"plain": ["part one", "part two"], "html": ["<p>a</p>", "<p>b</p>"]},
            attachments=[],
            raw_email="Message-ID: <multi@ext.org>\r\n\r\n",
        )
        em = self.client.map_email(msg)
        self.assertEqual(em.body, "part one\npart two")
        self.assertEqual(em.body_html, "<p>a</p>\n<p>b</p>")

    def test_long_message_id_is_not_truncated(self):
        long_id = "<" + "a" * 400 + "@ext.org>"
        msg = FakeImboxMessage(
            message_id=long_id,
            subject="long",
            parsed_date=None,
            sent_from=[],
            sent_to=[],
            body={"plain": ["x"], "html": []},
            attachments=[],
            raw_email="\r\n",
        )
        em = self.client.map_email(msg)
        self.assertEqual(em.message_id, long_id)  # full id preserved (field widened to 998)


class SaveAttachmentsTest(SimpleTestCase):
    def setUp(self):
        self.client = _client()

    def _msg_with_attachment(self):
        return FakeImboxMessage(
            message_id="<att@ext.org>",
            subject="with attachment",
            parsed_date=None,
            sent_from=[],
            sent_to=[],
            body={"plain": ["real body"], "html": []},
            attachments=[{"filename": "x.pdf", "content": io.BytesIO(b"data")}],
            raw_email="Message-ID: <att@ext.org>\r\n\r\n",
        )

    def test_map_email_defers_attachment_writes(self):
        # map_email must not touch the filesystem (writes are deferred to
        # persist_attachments, after de-duplication).
        with patch("ngen.mailer.email_client.makedirs") as mk, patch(
            "ngen.mailer.email_client.open"
        ) as op:
            em = self.client.map_email(self._msg_with_attachment())
        mk.assert_not_called()
        op.assert_not_called()
        self.assertEqual(em.attachments, [])
        self.assertEqual(em._pending_attachments[0]["filename"], "x.pdf")

    @patch("ngen.mailer.email_client.makedirs", side_effect=OSError("disk full"))
    def test_storage_failure_keeps_message_and_records_error(self, _mk):
        em = self.client.map_email(self._msg_with_attachment())
        with patch.object(EmailMessage, "attachment_path", return_value="p/x.pdf"):
            self.client.persist_attachments(em)
        # A storage hiccup drops only the attachment, never the parsed message,
        # but the loss is recorded (never silent) so it can be recovered later.
        self.assertEqual(em.body, "real body")
        self.assertEqual(em.attachments, [])
        self.assertIn("attachment storage failed", em.last_error)
        self.assertIn("x.pdf", em.last_error)

    def test_persist_attachments_writes_and_fills_metadata(self):
        em = self.client.map_email(self._msg_with_attachment())
        written = {}

        class _Sink:
            def __enter__(self_):
                return self_

            def __exit__(self_, *a):
                return False

            def write(self_, data):
                written["data"] = data

        with patch("ngen.mailer.email_client.makedirs"), patch(
            "ngen.mailer.email_client.open", return_value=_Sink()
        ), patch.object(EmailMessage, "attachment_path", return_value="p/x.pdf"):
            self.client.persist_attachments(em)

        self.assertEqual(written["data"], b"data")
        self.assertEqual(em.attachments, [{"name": "x.pdf", "file": "p/x.pdf"}])
        self.assertIsNone(em.last_error)


class AttachmentDirKeyTest(SimpleTestCase):
    """A long/unsafe Message-ID must not blow the filesystem path-component limit."""

    def test_long_message_id_is_bounded_and_safe(self):
        long_id = "<" + "a" * 400 + "@ext.org>"
        comp = EmailMessage(message_id=long_id).attachment_path("x.pdf").split("/")[-2]
        self.assertLessEqual(len(comp.encode("utf-8")), 255)
        # unsafe/over-long id -> stable hash, deterministic across instances
        self.assertRegex(comp, r"^sha256-[0-9a-f]{64}$")
        again = EmailMessage(message_id=long_id).attachment_path("y.pdf").split("/")[-2]
        self.assertEqual(comp, again)

    def test_short_safe_message_id_is_used_verbatim(self):
        em = EmailMessage(message_id="<abc@ext.org>")
        comp = em.attachment_path("x.pdf").split("/")[-2]
        self.assertEqual(comp, "<abc@ext.org>")

    def test_hash_shaped_message_id_cannot_collide_with_a_hashed_key(self):
        # Another mail whose Message-ID *is* a hashed key must not land in the
        # long id's directory (it would overwrite its attachments).
        long_id = "<" + "a" * 400 + "@ext.org>"
        hashed = EmailMessage(message_id=long_id).attachment_path("x").split("/")[-2]
        lookalike = EmailMessage(message_id=hashed).attachment_path("x").split("/")[-2]
        self.assertNotEqual(hashed, lookalike)


class NulAndBoundsTest(SimpleTestCase):
    """PostgreSQL cannot store NUL in text/jsonb, nor ids over the column size."""

    def setUp(self):
        self.client = _client()

    def test_nul_characters_are_replaced_everywhere(self):
        msg = FakeImboxMessage(
            message_id="<nul@ext.org>",
            subject="a\x00b",
            parsed_date=None,
            sent_from=[{"name": "Ad\x00min", "email": "a@b.c"}],
            sent_to=[],
            body={"plain": ["p\x00"], "html": [b"<p>h\x00</p>"]},
            attachments=[],
            raw_email="Message-ID: <nul@ext.org>\r\n\r\n",
        )
        em = self.client.map_email(msg)
        for value in (em.subject, em.body, em.body_html, em.senders[0]["name"]):
            self.assertNotIn("\x00", value)
        self.assertEqual(em.body_html, "<p>h�</p>")

    def test_message_id_over_column_size_is_bounded_deterministically(self):
        huge = "<" + "b" * 1200 + "@ext.org>"
        a = self.client.get_message_id(FakeImboxMessage(message_id=huge))
        b = self.client.get_message_id(FakeImboxMessage(message_id=huge))
        self.assertLessEqual(len(a), 998)
        self.assertTrue(a.endswith("@long-message-id.ngen>"))
        self.assertEqual(a, b)


class AttachmentFilenameTest(SimpleTestCase):
    def setUp(self):
        self.client = _client()

    def _em(self, filename):
        return self.client.map_email(
            FakeImboxMessage(
                message_id="<fn@ext.org>",
                subject="s",
                parsed_date=None,
                sent_from=[],
                sent_to=[],
                body={"plain": ["real body"], "html": []},
                attachments=[{"filename": filename, "content": io.BytesIO(b"d")}],
                raw_email="Message-ID: <fn@ext.org>\r\n\r\n",
            )
        )

    def test_nul_in_filename_is_recorded_not_raised(self):
        em = self._em("bad\x00name.pdf")
        # Real open() raises ValueError("embedded null byte"); it must not escape.
        with patch("ngen.mailer.email_client.makedirs"):
            self.client.persist_attachments(em)
        self.assertEqual(em.attachments, [])
        self.assertIn("attachment storage failed", em.last_error)
        self.assertNotIn("\x00", em.last_error)

    @override_settings(MEDIA_ROOT="/media", EMAIL_ATTACHMENTS_FILE_ROOT="att")
    def test_filename_cannot_escape_the_attachment_directory(self):
        em = self._em("../../../etc/evil.sh")
        opened = []

        class _Sink:
            def __enter__(self_):
                return self_

            def __exit__(self_, *a):
                return False

            def write(self_, data):
                pass

        def _open(p, mode):
            opened.append(p)
            return _Sink()

        with patch("ngen.mailer.email_client.makedirs"), patch(
            "ngen.mailer.email_client.open", side_effect=_open
        ):
            self.client.persist_attachments(em)

        self.assertEqual(len(opened), 1)
        self.assertEqual(opened[0], os.path.join("/media", "att", "<fn@ext.org>", "evil.sh"))
        self.assertEqual(em.attachments[0]["name"], "../../../etc/evil.sh")

    @override_settings(MEDIA_ROOT="/media", EMAIL_ATTACHMENTS_FILE_ROOT="att")
    def test_same_sanitized_name_gets_distinct_files(self):
        em = self.client.map_email(
            FakeImboxMessage(
                message_id="<dup@ext.org>",
                subject="s",
                parsed_date=None,
                sent_from=[],
                sent_to=[],
                body={"plain": ["b"], "html": []},
                attachments=[
                    {"filename": "one/report.pdf", "content": io.BytesIO(b"1")},
                    {"filename": "two/report.pdf", "content": io.BytesIO(b"2")},
                    {"filename": "report.pdf", "content": io.BytesIO(b"3")},
                ],
                raw_email="Message-ID: <dup@ext.org>\r\n\r\n",
            )
        )
        writes = {}

        def _open(p, mode):
            class _Sink:
                def __enter__(self_):
                    return self_

                def __exit__(self_, *a):
                    return False

                def write(self_, data):
                    writes[p] = data

            return _Sink()

        with patch("ngen.mailer.email_client.makedirs"), patch(
            "ngen.mailer.email_client.open", side_effect=_open
        ):
            self.client.persist_attachments(em)

        files = [a["file"] for a in em.attachments]
        self.assertEqual(len(set(files)), 3)  # nothing overwritten
        self.assertEqual(
            [os.path.basename(f) for f in files],
            ["report.pdf", "report (2).pdf", "report (3).pdf"],
        )
        # original names kept for display, each paired with its own bytes
        self.assertEqual(
            [a["name"] for a in em.attachments],
            ["one/report.pdf", "two/report.pdf", "report.pdf"],
        )
        self.assertEqual(sorted(writes.values()), [b"1", b"2", b"3"])
        self.assertIsNone(em.last_error)


RECEIVED = (
    "Received: from relay.example (relay.example [192.0.2.1])\r\n"
    "\tby mail.cert.unlp.edu.ar (Postfix) with ESMTPS id 1CF449DEB\r\n"
    "\tfor <incidentes@cert.unlp.edu.ar>; Wed, 21 Oct 2026 12:37:09 -0300 (-03)\r\n"
)


def _utc(*args):
    return datetime(*args, tzinfo=dt_timezone.utc)


class GetDateTest(SimpleTestCase):
    """
    The stored date must be the real instant in UTC whatever the sender's zone,
    the container's zone or settings.TIME_ZONE (imbox's parsed_date dropped the
    offset: 12:37 -0300 was stored as 12:37 UTC).
    """

    def setUp(self):
        self.client = _client()

    def _date(self, headers):
        return self.client.get_date(FakeImboxMessage(raw_email=headers + "\r\nbody"))

    def test_offset_is_honoured(self):
        self.assertEqual(
            self._date("Date: Wed, 21 Oct 2026 12:37:05 -0300 (-03)\r\n"),
            _utc(2026, 10, 21, 15, 37, 5),
        )

    def test_any_sender_zone_gives_the_same_instant(self):
        for header in (
            "Wed, 21 Oct 2026 12:37:05 -0300",
            "Wed, 21 Oct 2026 21:07:05 +0530",
            "Wed, 21 Oct 2026 15:37:05 +0000",
            "Wed, 21 Oct 2026 15:37:05 GMT",
            "Wed, 21 Oct 2026 10:37:05 EST",
            "21 Oct 26 12:37:05 -0300",  # no weekday, 2-digit year
        ):
            with self.subTest(header=header):
                self.assertEqual(self._date("Date: %s\r\n" % header), _utc(2026, 10, 21, 15, 37, 5))

    def test_result_is_always_aware_utc(self):
        d = self._date("Date: Wed, 21 Oct 2026 12:37:05 -0300\r\n")
        self.assertEqual(d.utcoffset().total_seconds(), 0)

    def test_no_usable_offset_uses_our_receipt_time(self):
        # -0000 / unknown zone names / no zone: the sender's zone is unknown.
        for header in (
            "Wed, 21 Oct 2026 15:37:05 -0000",
            "Wed, 21 Oct 2026 17:37:05 CEST",
            "Wed, 21 Oct 2026 15:37:05",
        ):
            with self.subTest(header=header):
                self.assertEqual(
                    self._date(RECEIVED + "Date: %s\r\n" % header), _utc(2026, 10, 21, 15, 37, 9)
                )

    def test_no_usable_offset_and_no_receipt_assumes_utc(self):
        self.assertEqual(
            self._date("Date: Wed, 21 Oct 2026 15:37:05 -0000\r\n"), _utc(2026, 10, 21, 15, 37, 5)
        )

    def test_date_after_our_receipt_is_not_trusted(self):
        # Sender clock in UTC but labelled -0300: claims 18:37Z, we got it 15:37Z.
        self.assertEqual(
            self._date(RECEIVED + "Date: Wed, 21 Oct 2026 15:37:05 -0300\r\n"),
            _utc(2026, 10, 21, 15, 37, 9),
        )

    def test_small_clock_skew_keeps_the_sender_date(self):
        self.assertEqual(
            self._date(RECEIVED + "Date: Wed, 21 Oct 2026 12:42:00 -0300\r\n"),
            _utc(2026, 10, 21, 15, 42, 0),
        )

    def test_missing_or_invalid_date_falls_back_to_receipt(self):
        self.assertEqual(self._date(RECEIVED), _utc(2026, 10, 21, 15, 37, 9))
        self.assertEqual(
            self._date(RECEIVED + "Date: no es una fecha\r\n"), _utc(2026, 10, 21, 15, 37, 9)
        )

    def test_nothing_usable_gives_none(self):
        self.assertIsNone(self._date("Subject: x\r\n"))
        self.assertIsNone(self._date("Date: garbage\r\nReceived: garbage; garbage\r\n"))

    def test_topmost_received_is_ours(self):
        older = "Received: from a by b; Wed, 21 Oct 2026 12:37:05 -0300\r\n"
        self.assertEqual(
            self._date(RECEIVED + older + "Date: Wed, 21 Oct 2026 15:37:05 -0000\r\n"),
            _utc(2026, 10, 21, 15, 37, 9),
        )

    def test_out_of_range_dates_do_not_raise(self):
        self.assertIsNone(self._date("Date: Fri, 31 Dec 9999 23:59:59 -1200\r\n"))
        received_edge = "Received: from a by b; Fri, 31 Dec 9999 23:59:59 +0000\r\n"
        self.assertEqual(
            self._date(received_edge + "Date: Wed, 21 Oct 2026 12:37:05 -0300\r\n"),
            _utc(2026, 10, 21, 15, 37, 5),
        )

    @override_settings(TIME_ZONE="Asia/Tokyo")
    def test_independent_of_container_zone_and_time_zone_setting(self):
        old = os.environ.get("TZ")
        os.environ["TZ"] = "America/Argentina/Buenos_Aires"
        time.tzset()
        try:
            d = self._date("Date: Wed, 21 Oct 2026 12:37:05 -0300\r\n")
        finally:
            if old is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = old
            time.tzset()
        self.assertEqual(d, _utc(2026, 10, 21, 15, 37, 5))

    @override_settings(USE_TZ=False, TIME_ZONE="America/Argentina/Buenos_Aires")
    def test_naive_local_time_when_use_tz_is_off(self):
        d = self._date("Date: Wed, 21 Oct 2026 15:37:05 +0000\r\n")
        self.assertIsNone(d.tzinfo)
        self.assertEqual(d, datetime(2026, 10, 21, 12, 37, 5))

    def test_map_email_stores_the_corrected_date(self):
        em = self.client.map_email(
            FakeImboxMessage(
                message_id="<tz@ext.org>",
                subject="tz",
                parsed_date=datetime(2026, 10, 21, 12, 37, 5),  # imbox's wrong value
                sent_from=[],
                sent_to=[],
                body={"plain": ["x"], "html": []},
                attachments=[],
                raw_email="Message-ID: <tz@ext.org>\r\nDate: Wed, 21 Oct 2026 12:37:05 -0300\r\n\r\nx",
            )
        )
        self.assertEqual(em.date, _utc(2026, 10, 21, 15, 37, 5))


class GetMessageIdTest(SimpleTestCase):
    def setUp(self):
        self.client = _client()

    def test_returns_header_when_present(self):
        msg = FakeImboxMessage(message_id="<present@x>", raw_email="")
        self.assertEqual(self.client.get_message_id(msg), "<present@x>")

    def test_derives_and_is_stable_when_absent(self):
        msg_a = FakeImboxMessage(raw_email="same-bytes")
        msg_b = FakeImboxMessage(raw_email="same-bytes")
        msg_c = FakeImboxMessage(raw_email="other-bytes")
        self.assertEqual(
            self.client.get_message_id(msg_a), self.client.get_message_id(msg_b)
        )
        self.assertNotEqual(
            self.client.get_message_id(msg_a), self.client.get_message_id(msg_c)
        )

    def test_bytes_payloads_hashed_faithfully(self):
        # Two id-less messages differing only by an undecodable byte must not
        # collide (a lossy decode would map both 0xff and 0xfe to "").
        a = FakeImboxMessage(raw_email=b"\xff")
        b = FakeImboxMessage(raw_email=b"\xfe")
        self.assertNotEqual(
            self.client.get_message_id(a), self.client.get_message_id(b)
        )


class BuildErrorMessageTest(SimpleTestCase):
    def setUp(self):
        self.client = _client()

    def test_error_record_is_viewable(self):
        msg = FakeImboxMessage(
            message_id="<err@ext.org>",
            sent_from=[{"name": "x", "email": "x@y.com"}],
            sent_to=[],
        )
        em = self.client.build_error_message(msg, ValueError("boom"))
        self.assertEqual(em.message_id, "<err@ext.org>")
        self.assertEqual(em.status, EmailMessage.Status.SENT)
        self.assertIn("boom", em.last_error)
        self.assertIn("no se pudo procesar", em.body.lower())
        self.assertTrue(em.subject)  # placeholder subject when the message had none

    def test_recovers_threading_headers(self):
        # The placeholder must thread into the case conversation
        # (CommunicationChannel filters by root_message_id), so References /
        # In-Reply-To are recovered best-effort instead of orphaning it.
        raw = (
            "Message-ID: <err2@ext.org>\r\n"
            "References: <root@ngen> <parent@ngen>\r\n"
            "In-Reply-To: <parent@ngen>\r\n"
            "\r\nx"
        )
        msg = FakeImboxMessage(
            message_id="<err2@ext.org>", raw_email=raw, sent_from=[], sent_to=[]
        )
        em = self.client.build_error_message(msg, ValueError("boom"))
        self.assertEqual(em.root_message_id, "<root@ngen>")
        self.assertEqual(em.parent_message_id, "<parent@ngen>")
        self.assertEqual(em.references, ["<root@ngen>", "<parent@ngen>"])


class MapEmailsTest(SimpleTestCase):
    def setUp(self):
        self.client = _client()

    def test_one_bad_message_does_not_abort_batch(self):
        good = FakeImboxMessage(
            message_id="<good@ext.org>",
            subject="good",
            parsed_date=None,
            sent_from=[],
            sent_to=[],
            body={"plain": ["ok"], "html": []},
            attachments=[],
            raw_email="Message-ID: <good@ext.org>\r\n\r\nok",
        )
        # A non-string raw_email makes email.message_from_string() raise inside
        # map_email -> it must fall back to an error record, not propagate.
        bad = FakeImboxMessage(
            message_id="<bad@ext.org>",
            subject="bad",
            parsed_date=None,
            sent_from=[],
            sent_to=[],
            body={"plain": ["x"], "html": []},
            attachments=[],
            raw_email=12345,
        )
        mapped = self.client.map_emails([("1", good), ("2", bad)])

        self.assertEqual(len(mapped), 2)  # one output per input, order preserved
        self.assertEqual(mapped[0].message_id, "<good@ext.org>")
        self.assertEqual(mapped[0].body, "ok")
        # The bad one becomes a viewable placeholder, not a crash.
        self.assertEqual(mapped[1].message_id, "<bad@ext.org>")
        self.assertIsNotNone(mapped[1].last_error)
        self.assertEqual(mapped[1].status, EmailMessage.Status.SENT)
