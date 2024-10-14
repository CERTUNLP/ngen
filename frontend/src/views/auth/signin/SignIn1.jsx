import React, { useState, useEffect } from "react";
import { Card } from "react-bootstrap";
import { NavLink } from "react-router-dom";

import Alert from "./../../../components/Alert/Alert";
import setAlert from "../../../utils/setAlert";
import Breadcrumb from "../../../layouts/AdminLayout/Breadcrumb";

import RestLogin from "./RestLogin";

import { useTranslation } from "react-i18next";

const Signin1 = () => {
  const { t } = useTranslation();
  const [showAlert, setShowAlert] = useState(false);
  const [signup, setSignup] = useState(false);

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  useEffect(() => {
    const external = localStorage.getItem("API_SERVER");
    setSignup(localStorage.getItem("enable_signup") === "true");

    if (external) {
      fetch(external, { mode: "cors" }) // Usar 'cors' en lugar de 'no-cors'
        .then((response) => {
          if (response.ok) {
            console.log("Connection to backend successful");
          } else {
            setAlert("Network response was not ok", "error", "login");
            throw new Error("Network response was not ok");
          }
        })
        .catch((error) => {
          console.error("Error connecting to backend:", error);
          setAlert("Error connecting to backend: " + error.message, "error", "login");
        })
        .finally(() => {
          setShowAlert(true);
        });
    } else {
      console.error("API_SERVER is not set in localStorage");
      setAlert("API_SERVER is not set in localStorage", "error", "login");
      setShowAlert(true);
    }
  }, []); // El array vacío asegura que useEffect solo se ejecute una vez al montar el componente

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
                  src={localStorage.getItem("API_SERVER") + "static/img/ngenlogo_inv.png"}
                  alt="NGEN"
                  className="logo"
                  id="teamlogo_login"
                />
              </div>

              <div className="mb-4">
                <i className="feather icon-unlock auth-icon" />
              </div>

              <RestLogin />

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
