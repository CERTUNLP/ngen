import React from 'react';
import { Button, Card, Col, Form, Row } from 'react-bootstrap';
import { validateFieldText, validateHours, validateMinutes, validateNumber } from '../../../utils/validators';
import { useTranslation } from 'react-i18next';

const FormPriority = ({ body, setBody, createPriority }) => {
  const completeField = (event) => {
    setBody({
      ...body,
      [event.target.name]: event.target.value
    });
  };
  const { t } = useTranslation();

  const activateBooton = (body) => {
    if (!validateFieldText(body.name)) {
      return false;
    }
    if (!validateNumber(body.severity)) {
      return false;
    }
    if (body.name === '') {
      return false;
    }
    if (body.severity === '') {
      return false;
    }
    if (body.color === '') {
      return false;
    }
    if (body.attend_time_days !== '') {
      if (!validateNumber(body.attend_time_days)) {
        return false;
      }
    }
    if (body.attend_time_hours !== '') {
      if (!validateHours(body.attend_time_hours)) {
        return false;
      }
    }
    if (body.attend_time_minutes !== '') {
      if (!validateMinutes(body.attend_time_minutes)) {
        return false;
      }
    }
    if (body.solve_time_days !== '') {
      if (!validateNumber(body.solve_time_days)) {
        return false;
      }
    }
    if (body.solve_time_hours !== '') {
      if (!validateHours(body.solve_time_hours)) {
        return false;
      }
    }
    if (body.solve_time_minutes !== '') {
      if (!validateMinutes(body.solve_time_minutes)) {
        return false;
      }
    }
    return true;
  };

  return (
    <Card.Body>
      <Form>
        <Row>
          <Col sm={12} lg={4}>
            <Form.Group controlId="formGridAddress1">
              <Form.Label>
                {t('ngen.name_one')}
                <b style={{ color: 'red' }}>*</b>
              </Form.Label>
              <Form.Control
                placeholder={t('ngen.name.placeholder')}
                maxLength="150"
                value={body.name}
                name="name"
                isInvalid={!validateFieldText(body.name)}
                onChange={(e) => completeField(e)}
              />
              {validateFieldText(body.name) ? '' : <div className="invalid-feedback"> {t('w.validate.character')}</div>}
            </Form.Group>
          </Col>
          <Col sm={12} lg={4}>
            <Form.Group controlId="formGridAddress1">
              <Form.Label>
                {t('ngen.priority.severity')} <b style={{ color: 'red' }}>*</b>
              </Form.Label>
              <Form.Control
                placeholder={t('ngen.priority.severity.placeholder')}
                maxLength="150"
                value={body.severity}
                name="severity"
                isInvalid={!validateNumber(body.severity)}
                onChange={(e) => completeField(e)}
              />
              {validateNumber(body.severity) ? '' : <div className="invalid-feedback"> {t('w.validate.numbers')} </div>}
            </Form.Group>
          </Col>
          <Col sm={12} lg={4}>
            <Form.Group controlId="formGridAddress1">
              <Form.Label>
                {t('ngen.color')} <b style={{ color: 'red' }}>*</b>
              </Form.Label>
              <Form.Control
                placeholder={t('ngen.priority.color.placeholder')}
                maxLength="150"
                value={body.color}
                name="color"
                onChange={(e) => completeField(e)}
              />
              {body.color !== '' ? '' : <div className="invalid-feedback">{t('ngen.color.validate')}</div>}
              {
                //tengo ver un validador para color
              }
            </Form.Group>
          </Col>
        </Row>
        <Row>
          <Col sm={12} lg={4}>
            <Form.Group controlId="formGridAddress1">
              <Form.Label>
                {t('ngen.priority.notification_amount')} <b style={{ color: 'red' }}>*</b>
              </Form.Label>
              <Form.Control
                placeholder={t('ngen.priority.notification_amount.placeholder')}
                maxLength="150"
                value={body.notification_amount}
                name="notification_amount"
                isInvalid={!validateNumber(body.notification_amount)}
                onChange={(e) => completeField(e)}
              />
              {validateNumber(body.notification_amount) ? '' : <div className="invalid-feedback"> {t('w.validate.numbers')} </div>}
            </Form.Group>
          </Col>
        </Row>

        <Row>
          <Form.Label>{t('time.to.attend')}</Form.Label>
          <Col>
            <Form.Group controlId="formGridAddress1">
              {t('date.days')}{' '}
              <Form.Control
                placeholder={t('placeholder.date')}
                maxLength="150"
                value={body.attend_time_days}
                name="attend_time_days"
                isInvalid={body.attend_time_days !== '' && !validateNumber(body.attend_time_days)}
                onChange={(e) => completeField(e)}
              />
            </Form.Group>
          </Col>
          <Col>
            <Form.Group controlId="formGridAddress1">
              {t('date.hours')}{' '}
              <Form.Control
                placeholder={t('placeholder.hours')}
                maxLength="2"
                value={body.attend_time_hours}
                name="attend_time_hours"
                isInvalid={body.attend_time_hours !== '' && !validateHours(body.attend_time_hours)}
                onChange={(e) => completeField(e)}
              />
            </Form.Group>
          </Col>
          <Col>
            <Form.Group controlId="formGridAddress1">
              {t('date.minutes')}{' '}
              <Form.Control
                placeholder={t('placeholder.minutes')}
                maxLength="2"
                value={body.attend_time_minutes}
                name="attend_time_minutes"
                isInvalid={body.attend_time_minutes !== '' && !validateMinutes(body.attend_time_minutes)}
                onChange={(e) => completeField(e)}
              />
            </Form.Group>
          </Col>
        </Row>
        <Row>
          <Form.Label>{t('time.to.solve')} </Form.Label>
          <Col>
            <Form.Group controlId="formGridAddress1">
              {t('date.days')}{' '}
              <Form.Control
                placeholder={t('placeholder.date')}
                maxLength="150"
                value={body.solve_time_days}
                name="solve_time_days"
                isInvalid={body.solve_time_days !== '' && !validateNumber(body.solve_time_days)}
                onChange={(e) => completeField(e)}
              />
            </Form.Group>
          </Col>
          <Col>
            <Form.Group controlId="formGridAddress1">
              {t('date.hours')}{' '}
              <Form.Control
                placeholder={t('placeholder.hours')}
                value={body.solve_time_hours}
                isInvalid={body.solve_time_hours !== '' && !validateHours(body.solve_time_hours)}
                name="solve_time_hours"
                onChange={(e) => completeField(e)}
              />
            </Form.Group>
          </Col>
          <Col>
            <Form.Group controlId="formGridAddress1">
              {t('date.minutes')}{' '}
              <Form.Control
                placeholder={t('placeholder.minutes')}
                maxLength="2"
                value={body.solve_time_minutes}
                isInvalid={body.solve_time_minutes !== '' && !validateMinutes(body.solve_time_minutes)}
                name="solve_time_minutes"
                onChange={(e) => completeField(e)}
              />
            </Form.Group>
          </Col>
        </Row>
        {activateBooton(body) ? (
          <>
            <Button variant="primary" onClick={createPriority}>
              {t('button.save')}
            </Button>
          </>
        ) : (
          <>
            <Button variant="primary" disabled>
              {t('button.save')}
            </Button>
          </>
        )}

        <Button variant="primary" href="/priorities">
          {t('button.cancel')}
        </Button>
      </Form>
    </Card.Body>
  );
};

export default FormPriority;
