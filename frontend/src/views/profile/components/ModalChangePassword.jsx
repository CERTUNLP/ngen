import React, { useState } from "react";
import { Form, Modal, Button, Row } from "react-bootstrap";
import { changePassword } from "api/services/profile";
import { useTranslation } from "react-i18next";
import setAlert from "utils/setAlert";
import { validatePassword } from "utils/validators/user";
import { getCurrentUser } from "utils/permissions";

const ModalChangePassword = ({ show, setShow }) => {
  const [passwordOld, setPasswordOld] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");
  const [formErrors, setFormErrors] = useState({});

  const { t } = useTranslation();

  const handleChangePassword = () => {
    changePassword(getCurrentUser().id, passwordOld, password1, password2)
      .then(() => {
        setAlert("La contraseña se ha cambiado correctamente", "success");
        setShow(false);
      })
      .catch((error) => {
        setFormErrors(error.response.data);
        console.log(error.response.data);
      });
  };

  return (
    <Modal show={show} onHide={() => setShow(false)}>
      <Modal.Header closeButton>
        <Modal.Title>{t("ngen.password.change")}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Row>
          <Form.Label>{t("ngen.user.ask_password")}</Form.Label>
          <Form.Control type="password" placeholder={t("ngen.password.actual")} onChange={(e) => setPasswordOld(e.target.value)} />
          <Form.Text className="text-muted">
            {formErrors.old_password ? (
              <div class="text-danger">
                <small> {formErrors.old_password}</small>
              </div>
            ) : (
              ""
            )}
          </Form.Text>
        </Row>
        <Row>
          <Form.Label>{t("ngen.password.new")}</Form.Label>
          <Form.Control type="password" placeholder={t("ngen.password")} onChange={(e) => setPassword1(e.target.value)} />
          {formErrors.new_password1 ? (
            <div class="text-danger">
              <small> {formErrors.new_password1}</small>
            </div>
          ) : (
            ""
          )}
        </Row>
        <Row>
          <Form.Label>{t("ngen.password.confirm")}</Form.Label>
          <Form.Control
            type="password"
            placeholder={t("ngen.password.confirm")}
            isInvalid={!validatePassword(password1, password2)}
            onChange={(e) => setPassword2(e.target.value)}
          />
          {formErrors.new_password2 ? (
            <div class="text-danger">
              <small> {formErrors.new_password2}</small>
            </div>
          ) : (
            ""
          )}
        </Row>
        <Row>
          <Form.Text className="text-muted">
            {t("ngen.password.legend1")}
            <br />
            {t("ngen.password.legend2")}
            <br />
            {t("ngen.password.legend3")}
            <br />
            {t("ngen.password.legend4")}
          </Form.Text>
        </Row>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => setShow(false)}>
          {t("w.close")}
        </Button>
        <Button variant="primary" onClick={handleChangePassword}>
          {t("ngen.accept")}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ModalChangePassword;
