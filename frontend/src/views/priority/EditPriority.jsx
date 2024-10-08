import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import FormPriority from "./components/FormPriority";

import { putPriority } from "../../api/services/priorities";
import { useLocation } from "react-router-dom";
import Alert from "../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const EditPriority = () => {
  const location = useLocation();
  const fromState = location.state;

  const [body, setBody] = useState(fromState);
  const [showAlert, setShowAlert] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    let attend_time_days = "";
    let attend_time_hours = "";
    let attend_time_minutes = "";
    let solve_time_days = "";
    let solve_time_hours = "";
    let solve_time_minutes = "";
    if (body.attend_time !== "") {
      attend_time_days = body.attend_time.split(" ")[1] ? body.attend_time.split(" ")[0] : "";
      attend_time_hours = body.attend_time.split(" ")[1] ? body.attend_time.split(":")[1] : body.attend_time.split(":")[0];
      attend_time_minutes = body.attend_time.split(" ")[1] ? body.attend_time.split(":")[2] : body.attend_time.split(":")[1];
    }
    if (body.solve_time !== "") {
      solve_time_days = body.solve_time.split(" ")[1] ? body.solve_time.split(" ")[0] : "";
      solve_time_hours = body.solve_time.split(" ")[1] ? body.solve_time.split(":")[1] : body.solve_time.split(":")[0];
      solve_time_minutes = body.solve_time.split(" ")[1] ? body.solve_time.split(":")[2] : body.solve_time.split(":")[1];
    }
    const form = {
      url: body.url,
      name: body.name,
      color: body.color,
      severity: body.severity,
      notification_amount: body.notification_amount,
      attend_time_days: attend_time_days,
      attend_time_hours: attend_time_hours,
      attend_time_minutes: attend_time_minutes,
      solve_time_days: solve_time_days,
      solve_time_hours: solve_time_hours,
      solve_time_minutes: solve_time_minutes
    };
    setBody(form);
  }, []);

  const editPriority = () => {
    "severity es primary key";
    "nombre se puede repetir pero es requerido";
    "color es requerido , ¿se puede repetir?";
    body.attend_time_days = body.attend_time_days === "" ? "0" : body.attend_time_days;
    body.attend_time_hours =
      body.attend_time_hours === "" ? "00" : body.attend_time_hours.length === 1 ? "0" + body.attend_time_hours : body.attend_time_hours;
    body.attend_time_minutes =
      body.attend_time_minutes === ""
        ? "00"
        : body.attend_time_minutes.length === 1
          ? "0" + body.attend_time_minutes
          : body.attend_time_minutes;

    body.solve_time_days = body.solve_time_days === "" ? "0" : body.solve_time_days;
    body.solve_time_hours =
      body.solve_time_hours === "" ? "00" : body.solve_time_hours.length === 1 ? "0" + body.solve_time_hours : body.solve_time_hours;
    body.solve_time_minutes =
      body.solve_time_minutes === ""
        ? "00"
        : body.solve_time_minutes.length === 1
          ? "0" + body.solve_time_minutes
          : body.solve_time_minutes;
    let attend_time = body.attend_time_days + " " + body.attend_time_hours + ":" + body.attend_time_minutes + ":00";
    let solve_time = body.solve_time_days + " " + body.solve_time_hours + ":" + body.solve_time_minutes + ":00";

    putPriority(body.url, body.name, body.color, body.severity, attend_time, solve_time)
      .then(() => {
        window.location.href = "/priorities";
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      });
  };
  const resetShowAlert = () => {
    setShowAlert(false);
  };
  return (
    <>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.priority.edit")}</Card.Title>
            </Card.Header>
            <FormPriority body={body} setBody={setBody} createPriority={editPriority} />
          </Card>
        </Col>
      </Row>
    </>
  );
};

export default EditPriority;
