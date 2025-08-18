import React, { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import { Button, FormControl, FormCheck, FormGroup, Alert, Card, Row, Col } from "react-bootstrap";
import apiInstance from "api/api";
import { validateUUID } from "utils/validators";
import { useTranslation } from "react-i18next";

const ContactCheckForm = () => {
  const { t } = useTranslation();
  const { uuid } = useParams();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const autoConfirm = queryParams.get("confirm") === "true";
  const [contactCheck, setContactCheck] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isValid, setIsValid] = useState(autoConfirm);
  const [notes, setNotes] = useState("");
  const [error, setError] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (!validateUUID(uuid)) {
      setError("El UUID proporcionado no es válido.");
      return;
    }
    apiInstance
      .get(`/contactcheck/validate/${uuid}/`, {
        withCredentials: false
      })
      .then((res) => {
        if (res.status === 404) {
          setError("El formulario no existe.");
        } else if (res.status === 400) {
          setError("El formulario ya ha sido validado o no está disponible.");
        } else {
          setContactCheck(res.data);
        }
      })
      .catch((err) => {
        setError(`No se pudo cargar el formulario. Error: ${err.response?.data?.detail || err.response?.data?.__all__ || "Error desconocido"}`);
      });
  }, [uuid]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    apiInstance
      .post(
        `/contactcheck/validate/${uuid}/`,
        {
          confirmed: isValid,
          notes: notes
        },
        {
          withCredentials: false,
          headers: {
            "Content-Type": "application/json"
          }
        }
      )
      .then(() => {
        setSubmitted(true);
      })
      .catch((error) => {
        setError("Hubo un error al enviar el formulario. Error: " + (error.response?.data?.detail || error.response?.data?.__all__ || "Error desconocido"));
      })
      .finally(() => {
        setIsSubmitting(false);
      });
  };

  return (
    <React.Fragment>
      {error && <Alert variant="danger">{error}</Alert>}
      {submitted && <Alert variant="success">{t("ngen.contactcheck.public.sent")}</Alert>}

      {!error && !submitted && (
        <Row>
          <Col sm={12}>
            <Card>
              <Card.Header>
                <Card.Title as="h5">{t("ngen.contactcheck.public.title")}</Card.Title>
                <span className="d-block m-t-5">
                  {t("ngen.contactcheck.public.description")}
                </span>
              </Card.Header>
              <Card.Body>
                {!contactCheck ? (
                  <p>{t("w.loading")}</p>
                ) : (
                  <form onSubmit={handleSubmit}>
                    <div className="mb-3 d-flex align-items-center">
                      <label className="form-label mb-0 me-2">{t("ngen.name_one")}</label>
                      <p className="text-muted mb-0">{contactCheck.contact?.name || t("w.not_available")}</p>
                    </div>

                    <div className="mb-3 d-flex align-items-center">
                      <label className="form-label mb-0 me-2">{t("w.email")}</label>
                      <p className="text-muted mb-0">{contactCheck.contact?.username || t("w.not_available")}</p>
                    </div>

                    <FormGroup className="mb-3">
                      <FormCheck
                        type="checkbox"
                        label={t("ngen.contactcheck.public.confirm")}
                        checked={isValid}
                        onChange={(e) => setIsValid(e.target.checked)}
                      />
                    </FormGroup>

                    {!isValid && (
                      <div className="mb-3">
                        <label className="form-label">{t("ngen.contactcheck.public.information")}: </label>
                        <small className="text-muted d-block mb-2">
                          {t("ngen.contactcheck.public.information.description")}
                        </small>
                        <FormControl
                          as="textarea"
                          rows={4}
                          placeholder={t("ngen.contactcheck.public.information.placeholder")}
                          value={notes}
                          onChange={(e) => setNotes(e.target.value)}
                          required={!isValid}
                        />
                      </div>
                    )}

                    <Button type="submit" disabled={isSubmitting || (!isValid && notes.trim() === "")}>
                      {isSubmitting ? `${t('w.sending')}...` : t("ngen.contactcheck.public.send")}
                    </Button>
                  </form>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </React.Fragment>
  );
};

export default ContactCheckForm;
