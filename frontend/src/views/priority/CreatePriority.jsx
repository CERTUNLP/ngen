import React, { useState } from 'react';
import { Card, Col, Row } from 'react-bootstrap';
import FormPriority from './components/FormPriority';
import Navigation from '../../components/Navigation/Navigation';
import { postPriority } from '../../api/services/priorities';
import Alert from '../../components/Alert/Alert';
import { useTranslation } from 'react-i18next';

const AddPriority = () => {
  const formEmpty = {
    name: '',
    color: '',
    severity: '',
    notification_amount: '',
    attend_time_days: '',
    attend_time_hours: '',
    attend_time_minutes: '',
    solve_time_days: '',
    solve_time_hours: '',
    solve_time_minutes: ''
  };
  const [body, setBody] = useState(formEmpty);
  const [showAlert, setShowAlert] = useState(false);
  const { t } = useTranslation();

  const createPriority = () => {
    body.attend_time_days = body.attend_time_days === '' ? '0' : body.attend_time_days;
    body.attend_time_hours =
      body.attend_time_hours === '' ? '00' : body.attend_time_hours.length === 1 ? '0' + body.attend_time_hours : body.attend_time_hours;
    body.attend_time_minutes =
      body.attend_time_minutes === ''
        ? '00'
        : body.attend_time_minutes.length === 1
          ? '0' + body.attend_time_minutes
          : body.attend_time_minutes;

    body.solve_time_days = body.solve_time_days === '' ? '0' : body.solve_time_days;
    body.solve_time_hours =
      body.solve_time_hours === '' ? '00' : body.solve_time_hours.length === 1 ? '0' + body.solve_time_hours : body.solve_time_hours;
    body.solve_time_minutes =
      body.solve_time_minutes === ''
        ? '00'
        : body.solve_time_minutes.length === 1
          ? '0' + body.solve_time_minutes
          : body.solve_time_minutes;
    let attend_time = body.attend_time_days + ' ' + body.attend_time_hours + ':' + body.attend_time_minutes + ':00';
    let solve_time = body.solve_time_days + ' ' + body.solve_time_hours + ':' + body.solve_time_minutes + ':00';

    postPriority(body.name, body.color, body.severity, attend_time, solve_time)
      .then(() => {
        window.location.href = '/priorities';
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
        <Navigation actualPosition={t('ngen.priority.add')} path="/priorities" index={t('ngen.priority_other')} />
      </Row>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t('ngen.priority.add')}</Card.Title>
            </Card.Header>
            <FormPriority body={body} setBody={setBody} createPriority={createPriority} />
          </Card>
        </Col>
      </Row>
    </>
  );
};

export default AddPriority;
