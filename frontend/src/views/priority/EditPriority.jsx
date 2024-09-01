import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import FormPriority from "./components/FormPriority";
import Navigation from '../../components/Navigation/Navigation'
import { putPriority, getPriority } from '../../api/services/priorities'
import { useLocation, useParams } from 'react-router-dom';
import Alert from '../../components/Alert/Alert'
import { useTranslation } from 'react-i18next'
import { COMPONENT_URL } from 'config/constant'

const EditPriority = () => {

  const [priority, setPriority] = useState({})
  const [body, setBody] = useState({})
  const [showAlert, setShowAlert] = useState(false)
  const { t } = useTranslation()
  const [id, setId] = useState(useParams());

  useEffect(() => {
    if (id.id) {
      getPriority(COMPONENT_URL.priority + id.id + "/")
        .then((response) => {
          setPriority(response.data)
        }).catch(error => console.log(error));
    }

  }, [id])
  console.log(body)

  useEffect(() => {
    if(Object.keys(priority).length > 0){
      let attend_time_days = ''
      let attend_time_hours = ''
      let attend_time_minutes = ''
      let solve_time_days = ''
      let solve_time_hours = ''
      let solve_time_minutes = ''
      if (priority.attend_time !== '') {
        attend_time_days = priority.attend_time.split(' ')[1]
          ? priority.attend_time.split(' ')[0]
          : ''
        attend_time_hours = priority.attend_time.split(' ')[1]
          ? priority.attend_time.split(':')[1]
          : priority.attend_time.split(':')[0]
        attend_time_minutes = priority.attend_time.split(' ')[1]
          ? priority.attend_time.split(':')[2]
          : priority.attend_time.split(':')[1]
      }
      if (priority.solve_time !== '') {
        solve_time_days = priority.solve_time.split(' ')[1] ? priority.solve_time.split(
          ' ')[0] : ''
        solve_time_hours = priority.solve_time.split(' ')[1] ? priority.solve_time.split(
          ':')[1] : priority.solve_time.split(':')[0]
        solve_time_minutes = priority.solve_time.split(' ')[1]
          ? priority.solve_time.split(':')[2]
          : priority.solve_time.split(':')[1]
      }
      const form = {
        url: priority.url,
        name: priority.name,
        color: priority.color,
        severity: priority.severity,
        notification_amount: priority.notification_amount,
        attend_time_days: attend_time_days,
        attend_time_hours: attend_time_hours,
        attend_time_minutes: attend_time_minutes,
        solve_time_days: solve_time_days,
        solve_time_hours: solve_time_hours,
        solve_time_minutes: solve_time_minutes,
      }
      setBody(form)
    }

  }, [priority])

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
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} component="priority" />
      <Row>
        <Navigation actualPosition={t("ngen.priority.edit")} path="/priorities" index={t("ngen.priority_other")} />
      </Row>
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
