import React, { useState } from "react";
import { Button, Col, OverlayTrigger, Row, Tooltip } from "react-bootstrap";

import * as Yup from "yup";
import { Formik } from "formik";
import { login } from "../../../api/services/auth";
import store from "./../../../store";
import Alert from "./../../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const RestLogin = ({ className, connected = true, ...rest }) => {
  const { t } = useTranslation();
  const [showAlert, setShowAlert] = useState(false);
  const { dispatch } = store;

  const validationMessages = {
    un: t("validation.username_or_email"),
    pw: t("validation.password")
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />
      <Formik
        initialValues={{
          username: "",
          password: "",
          submit: null
        }}
        validationSchema={Yup.object().shape({
          username: Yup.string().max(255).required(validationMessages.un),
          password: Yup.string().max(255).required(validationMessages.pw)
        })}
        onSubmit={async (values, { setErrors, setStatus, setSubmitting }) => {
          login(values.username, values.password);
        }}
      >
        {({ errors, handleBlur, handleChange, handleSubmit, isSubmitting, touched, values }) => {
          const validationMessages = [
            ...(touched.username && errors.username ? [errors.username] : []),
            ...(touched.password && errors.password ? [errors.password] : [])
          ];

          return (
          <form noValidate onSubmit={handleSubmit} className={className} {...rest}>
            <div className="form-group mb-3">
              <input
                className={"form-control" + (touched.username && errors.username ? " is-invalid" : "")}
                aria-invalid={!!(touched.username && errors.username)}
                aria-label={t("ngen.user.username_or_email")}
                placeholder={t("ngen.user.username_or_email")}
                name="username"
                onBlur={handleBlur}
                onChange={handleChange}
                type="text"
                value={values.username}
              />
            </div>
            <div className="form-group mb-4">
              <input
                className={"form-control" + (touched.password && errors.password ? " is-invalid" : "")}
                aria-invalid={!!(touched.password && errors.password)}
                aria-label={t("ngen.password")}
                placeholder={t("ngen.password")}
                name="password"
                onBlur={handleBlur}
                onChange={handleChange}
                type="password"
                value={values.password}
              />
            </div>

            <Row>
              <Col mt={2}>
                {!connected ? (
                  <OverlayTrigger
                    placement="top"
                    overlay={<Tooltip id="login-button-tooltip">{t("ngen.connection.disconnected")}</Tooltip>}
                  >
                    <span className="d-block w-100">
                      <Button className="btn-block" color="primary" disabled={isSubmitting || !connected} size="large" type="submit" variant="primary">
                        <i className="feather icon-zap text-danger me-2" aria-hidden="true" />
                        {t("button.login")}
                      </Button>
                    </span>
                  </OverlayTrigger>
                ) : validationMessages.length > 0 ? (
                  <OverlayTrigger
                    placement="top"
                    overlay={<Tooltip id="login-validation-tooltip">{validationMessages.join(" ")}</Tooltip>}
                  >
                    <span className="d-block w-100">
                      <Button className="btn-block" color="primary" disabled={isSubmitting} size="large" type="submit" variant="primary">
                        {t("button.login")}
                      </Button>
                    </span>
                  </OverlayTrigger>
                ) : (
                  <Button className="btn-block" color="primary" disabled={isSubmitting} size="large" type="submit" variant="primary">
                    {t("button.login")}
                  </Button>
                )}
              </Col>
            </Row>
          </form>
          );
        }}
      </Formik>
    </React.Fragment>
  );
};

export default RestLogin;
