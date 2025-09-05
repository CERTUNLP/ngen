import React, { useState } from "react";
import { Button, FormControl, Alert, Card } from "react-bootstrap";
import apiInstance from "api/api";
import { validateEmail } from "utils/validators";
import { useTranslation } from "react-i18next";

const ExportEventsForm = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    apiInstance
      .post(
        "export_events/",
        { email },
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: false
        }
      )
      .then((res) => {
        setSuccess(res.data.message);
      })
      .catch((err) => {
        setError("Error al iniciar la exportación: " + (err.response?.data?.detail || err.message || t("w.error.unexpected")));
      })
      .finally(() => {
        setIsSubmitting(false);
      });
  };

  return (
    <Card>
      <Card.Header>
        <Card.Title as="h5">{t("ngen.export_events")}</Card.Title>
        <span className="d-block m-t-5">{t("ngen.export_events.description")}</span>
      </Card.Header>
      <Card.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        {success ? (
          <Alert variant="success">{success}</Alert>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label">{t("ngen.export_events.email")}</label>
              <FormControl
                type="email"
                placeholder={t("w.email.placeholder")}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                isInvalid={!validateEmail(email)}
                required
              />
            </div>

            <Button type="submit" disabled={isSubmitting || !validateEmail(email)}>
              {isSubmitting ? t("w.sending") : t("button.send")}
            </Button>
          </form>
        )}
      </Card.Body>
    </Card>
  );
};

export default ExportEventsForm;
