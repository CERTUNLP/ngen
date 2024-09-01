import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Col, Row } from "react-bootstrap";

import * as Yup from "yup";
import { Formik } from "formik";
import { register } from "../../../api/services/auth";
import Alert from "./../../../components/Alert/Alert";

import { useTranslation } from "react-i18next";

const RestRegister = ({ className, ...rest }) => {
  const [showAlert, setShowAlert] = useState(false);
  const [delayAlert, setDelayAlert] = useState(5000);
  const [registered, setRegistered] = useState(false);
  const { t } = useTranslation();
  let history = useNavigate();

  const resetShowAlert = () => {
    if (registered === true) {
      history.push("/auth/signin", { from: "/auth/signup" });
    } else {
      setShowAlert(false);
      setDelayAlert(5000);
    }
  };

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} delay={delayAlert} />
      <Formik
        initialValues={{
          username: "",
          email: "",
          password: "",
          submit: null
        }}
        validationSchema={Yup.object().shape({
          email: Yup.string().email(t("signup.error.email.invalid")).max(255).required(t("signup.error.email.required")),
          username: Yup.string().required(t("signup.error.username.required")),
          password: Yup.string().max(255).required(t("signup.error.password.required"))
        })}
        onSubmit={async (values, { setErrors, setStatus, setSubmitting }) => {
          register(values.username, values.password, values.email)
            .then((response) => {
              setShowAlert(true);
              setDelayAlert(2000);
              setRegistered(true);
            })
            .catch((error) => {
              setShowAlert(true);
            });
        }}
      >
        {({ errors, handleBlur, handleChange, handleSubmit, isSubmitting, touched, values }) => (
          <form noValidate onSubmit={handleSubmit} className={className} {...rest}>
            <div className="form-group mb-3">
              <input
                className="form-control"
                error={touched.username && errors.username}
                label="Username"
                placeholder={t("ngen.user.username")}
                name="username"
                onBlur={handleBlur}
                onChange={handleChange}
                type="email"
                value={values.username}
              />
              {touched.username && errors.username && <small className="text-danger form-text">{errors.username}</small>}
            </div>
            <div className="form-group mb-3">
              <input
                className="form-control"
                error={touched.email && errors.email}
                label="Email Address"
                placeholder={t("w.email")}
                name="email"
                onBlur={handleBlur}
                onChange={handleChange}
                type="email"
                value={values.email}
              />
              {touched.email && errors.email && <small className="text-danger form-text">{errors.email}</small>}
            </div>
            <div className="form-group mb-4">
              <input
                className="form-control"
                error={touched.password && errors.password}
                label="Password"
                placeholder={t("ngen.password")}
                name="password"
                onBlur={handleBlur}
                onChange={handleChange}
                type="password"
                value={values.password}
              />
              {touched.password && errors.password && <small className="text-danger form-text">{errors.password}</small>}
            </div>

            <Row>
              <Col mt={2}>
                <Button className="btn-block" color="primary" disabled={isSubmitting} size="large" type="submit" variant="primary">
                  {t("button.signup")}
                </Button>
              </Col>
            </Row>
          </form>
        )}
      </Formik>
      <hr />
    </React.Fragment>
  );
};

export default RestRegister;
