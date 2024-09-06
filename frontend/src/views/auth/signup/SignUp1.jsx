import React from "react";
import { Card, Col, Row } from "react-bootstrap";
import { NavLink } from "react-router-dom";

// import { API_SERVER } from "../../../config/constant";
import RestRegister from "./RestRegister";
import Breadcrumb from "../../../layouts/AdminLayout/Breadcrumb";

import { useTranslation } from "react-i18next";

const SignUp1 = () => {
  const { t } = useTranslation();

  return (
    <React.Fragment>
      <Breadcrumb />
      <div className="auth-wrapper">
        <div className="auth-content">
          <div className="auth-bg">
            <span className="r" />
            <span className="r s" />
            <span className="r s" />
            <span className="r" />
          </div>
          <Card className="borderless">
            <Row className="align-items-center">
              <Col>
                <Card.Body className="text-center">
                  <div className="mb-4">
                    <img src={localStorage.getItem("API_SERVER") + "static/img/ngenlogo_inv.png"} alt="NGEN" className="logo" id="teamlogo_login" />
                  </div>

                  <div className="mb-4">
                    <i className="feather icon-user-plus auth-icon" />
                  </div>

                  <RestRegister />

                  <p className="mb-2">
                    {t("signup.already_have_an_account")}{" "}
                    <NavLink to="/auth/signin" className="f-w-400">
                      {t("button.signin")}
                    </NavLink>
                  </p>

                  <br />
                </Card.Body>
              </Col>
            </Row>
          </Card>
        </div>
      </div>
    </React.Fragment>
  );
};

export default SignUp1;
