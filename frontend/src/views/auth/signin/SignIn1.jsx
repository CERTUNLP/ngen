import React, { useState, useEffect, useContext, useRef } from "react";
import { Button, Card } from "react-bootstrap";
import { NavLink } from "react-router-dom";

import Alert from "./../../../components/Alert/Alert";
import setAlert from "../../../utils/setAlert";
import Breadcrumb from "../../../layouts/AdminLayout/Breadcrumb";

import RestLogin from "./RestLogin";

import { useTranslation } from "react-i18next";
import { COMPONENT_URL } from "../../../config/constant";
import { ThemeContext } from "../../../contexts/ThemeContext";
import useBackendHealth from "../../../hooks/useBackendHealth";

const Signin1 = () => {
  const { t } = useTranslation();
  const [showAlert, setShowAlert] = useState(false);
  const [signup, setSignup] = useState(false);
  const [oidcEnabled, setOidcEnabled] = useState(false);
  const connected = useBackendHealth();
  const [logoVersion, setLogoVersion] = useState(0);
  const prevConnected = useRef(connected);

  const { isDark } = useContext(ThemeContext);

  useEffect(() => {
    if (connected && !prevConnected.current) {
      setLogoVersion((version) => version + 1);
    }
    prevConnected.current = connected;
  }, [connected]);

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  useEffect(() => {
    const external = localStorage.getItem("API_SERVER");
    setSignup(localStorage.getItem("ALLOW_SIGNUP") === "True" || localStorage.getItem("ALLOW_SIGNUP") === "true");

    const cached = localStorage.getItem("OIDC_ENABLED");
    if (cached === "True" || cached === "true") {
      setOidcEnabled(true);
    }

    if (external) {
      fetch(external + COMPONENT_URL.configPublic)
        .then((res) => res.json())
        .then((data) => {
          data.forEach((item) => {
            if (item.key === "OIDC_ENABLED" || item.key === "NGEN_LANG" || item.key === "ALLOW_SIGNUP") {
              localStorage.setItem(item.key, item.value);
            }
          });
          const signupItem = data.find((item) => item.key === "ALLOW_SIGNUP");
          if (signupItem) {
            setSignup(signupItem.value === true || signupItem.value === "True" || signupItem.value === "true");
          }
          const oidcItem = data.find((item) => item.key === "OIDC_ENABLED");
          if (oidcItem) {
            const enabled = oidcItem.value === true || oidcItem.value === "True" || oidcItem.value === "true";
            setOidcEnabled(enabled);
          }
        })
        .catch((error) => {
          console.error("Error connecting to backend:", error);
          setAlert("Error connecting to backend: " + error.message, "error", "login");
          setShowAlert(true);
        });
    } else {
      console.error(`Backend url cannot be reached: ${external}`);
      setAlert(`Backend url cannot be reached: ${external}`, "error", "login");
      setShowAlert(true);
    }
  }, []);

  const handleSsoLogin = () => {
    window.location.href = localStorage.getItem("API_SERVER") + COMPONENT_URL.ssoLogin;
  };

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} component="login" />
      <Breadcrumb />
      <div className="auth-wrapper">
        <div className="auth-content">
          <div className="auth-bg">
            <span className="r" />
            <span className="r s" />
            <span className="r s" />
            <span className="r" />
          </div>
          <Card className="borderless text-center">
            <Card.Body>
              <div className="mb-4">
                <img
                  src={localStorage.getItem("API_SERVER") + "static/img/ngenlogo_inv" + (isDark ? "_light" : "") + ".png?t=" + logoVersion}
                  alt="NGEN"
                  className="logo"
                  id="teamlogo_login"
                />
              </div>

              <div className="mb-4 d-flex align-items-center justify-content-center gap-2">
                <i className="feather icon-unlock auth-icon" />
              </div>

              {oidcEnabled && (
                <div className="mb-3">
                  <Button
                    className="btn-block"
                    variant="outline-primary"
                    onClick={handleSsoLogin}
                  >
                    {t("login.sso")}
                  </Button>
                  <div className="d-flex align-items-center my-3">
                    <hr className="flex-grow-1" />
                    <span className="mx-2 text-muted">{t("login.or")}</span>
                    <hr className="flex-grow-1" />
                  </div>
                </div>
              )}

              <RestLogin connected={connected} />

              {signup && (
                <>
                  <hr />
                  <p className="mb-0 text-muted">
                    {t("login.do_not_have_an_account")}&nbsp;
                    <NavLink to="/auth/signup" className="f-w-400">
                      {t("button.signup")}
                    </NavLink>
                  </p>
                  <br />
                </>
              )}

            </Card.Body>
          </Card>
        </div>
      </div>
    </React.Fragment>
  );
};

export default Signin1;
