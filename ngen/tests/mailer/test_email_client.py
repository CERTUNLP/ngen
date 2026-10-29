"""
Unit tests for EmailClient inbound mapping (ngen.mailer.email_client).

These exercise the defensive ingestion path: a single malformed inbound message
(missing Message-ID / Subject / Date header, HTML-only body, or otherwise
unparseable) must never abort the batch, and no content must be silently lost.
"""

from django.test import SimpleTestCase

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
