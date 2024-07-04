import React from 'react'
import { Row, Card, Form, Button, Col } from 'react-bootstrap'
import { validateFieldText, validateNumber, validateHours, validateMinutes } from '../../../utils/validators';
import { useTranslation, Trans } from 'react-i18next';

const FormPriority = ({ body, setBody, createPriority }) => {


        const completeField = (event) => {
                setBody({
                        ...body,
                        [event.target.name]: event.target.value
                }
                )
        }
        const { t } = useTranslation();

        const activateBooton = (body) => {
                if (!validateFieldText(body.name)) {
                        return false
                }
                if (!validateNumber(body.severity)) {
                        return false
                }
                if (body.name == "") {
                        return false
                }
                if (body.severity == "") {
                        return false
                }
                if (body.color === "") {
                        return false
                }
                if (body.attend_time_days !== "") {
                        if (!validateNumber(body.attend_time_days)) {
                                return false
                        }
                }
                if (body.attend_time_hours !== "") {
                        if (!validateHours(body.attend_time_hours)) {
                                return false
                        }
                }
                if (body.attend_time_minutes !== "") {
                        if (!validateMinutes(body.attend_time_minutes)) {
                                return false
                        }
                }
                if (body.solve_time_days !== "") {
                        if (!validateNumber(body.solve_time_days)) {
                                return false
                        }
                }
                if (body.solve_time_hours !== "") {
                        if (!validateHours(body.solve_time_hours)) {
                                return false
                        }
                }
                if (body.solve_time_minutes !== "") {
                        if (!validateMinutes(body.solve_time_minutes)) {
                                return false
                        }
                }
                return true
        }

        return (
                <Card.Body>
                        <Form>
                                <th></th>

                                <Row>
                                        <Col sm={12} lg={4}>
                                                <Form.Group controlId="formGridAddress1">
                                                        <Form.Label>{t('ngen.name_one')}<b style={{ color: "red" }}>*</b> </Form.Label>
                                                        <Form.Control
                                                                placeholder={t('ngen.name.placeholder')}
                                                                maxlength="150"
                                                                value={body.name}
                                                                name="name"
                                                                isInvalid={!validateFieldText(body.name)}
                                                                onChange={(e) => completeField(e)} />
                                                        {validateFieldText(body.name) ? "" : <div className="invalid-feedback"> {t('w.validate.character')}</div>}
                                                </Form.Group>
                                        </Col>
                                        <Col sm={12} lg={4}>
                                                <Form.Group controlId="formGridAddress1">
                                                        <Form.Label>{('ngen.severity')} <b style={{ color: "red" }}>*</b></Form.Label>
                                                        <Form.Control
                                                                placeholder={('ngen.severity.placeholder')}
                                                                maxlength="150"
                                                                value={body.severity}
                                                                name="severity"
                                                                isInvalid={!validateNumber(body.severity)}
                                                                onChange={(e) => completeField(e)} />
                                                        {validateNumber(body.severity) ? "" : <div className="invalid-feedback"> {t('w.validate.numbers')} </div>}
                                                </Form.Group>
                                        </Col>
                                        <Col sm={12} lg={4}>
                                                <Form.Group controlId="formGridAddress1">
                                                        <Form.Label>{t('ngen.color')} <b style={{ color: "red" }}>*</b> </Form.Label>
                                                        <Form.Control
                                                                placeholder={('ngen.color.placeholder')}
                                                                maxlength="150"
                                                                value={body.color}
                                                                name="color"
                                                                onChange={(e) => completeField(e)} />
                                                        {body.color !== "" ? "" : <div className="invalid-feedback">{t('ngen.color.validate')}</div>}
                                                        {
                                                                //tengo ver un validador para color
                                                        }
                                                </Form.Group>
                                        </Col>
                                </Row>

                                <Form.Label>{t('time.to.attend')}</Form.Label>
                                <Row>
                                        <Col>
                                                <Form.Group controlId="formGridAddress1">
                                                        {t('date.days')}  <Form.Control
                                                                placeholder={t('placeholder.date')}
                                                                maxlength="150"
                                                                value={body.attend_time_days}
                                                                name="attend_time_days"
                                                                isInvalid={body.attend_time_days !== "" && !validateNumber(body.attend_time_days)}

                                                                onChange={(e) => completeField(e)} />
                                                </Form.Group>
                                        </Col>
                                        <Col>
                                                <Form.Group controlId="formGridAddress1">
                                                        {t('date.hours')}  <Form.Control
                                                                placeholder={t('placeholder.hours')}
                                                                maxlength="2"
                                                                value={body.attend_time_hours}
                                                                name="attend_time_hours"
                                                                isInvalid={body.attend_time_hours !== "" && !validateHours(body.attend_time_hours)}
                                                                onChange={(e) => completeField(e)} />
                                                </Form.Group>
                                        </Col>
                                        <Col>
                                                <Form.Group controlId="formGridAddress1">
                                                        {t('date.minutes')} <Form.Control
                                                                placeholder={t('placeholder.minutes')}
                                                                maxlength="2"
                                                                value={body.attend_time_minutes}
                                                                name="attend_time_minutes"
                                                                isInvalid={body.attend_time_minutes !== "" && !validateMinutes(body.attend_time_minutes)}
                                                                onChange={(e) => completeField(e)} />
                                                </Form.Group>
                                        </Col>
                                </Row>
                                <Form.Label>{t('time.to.solve')} </Form.Label>
                                <Row>
                                        <Col>
                                                <Form.Group controlId="formGridAddress1">
                                                        {t('date.days')}  <Form.Control
                                                                placeholder={t('placeholder.date')}
                                                                maxlength="150"
                                                                value={body.solve_time_days}
                                                                name="solve_time_days"
                                                                isInvalid={body.solve_time_days !== "" && !validateNumber(body.solve_time_days)}
                                                                onChange={(e) => completeField(e)} />

                                                </Form.Group>
                                        </Col>
                                        <Col>
                                                <Form.Group controlId="formGridAddress1">
                                                        {t('date.hours')}  <Form.Control
                                                                placeholder={t('placeholder.hours')}
                                                                value={body.solve_time_hours}
                                                                isInvalid={body.solve_time_hours !== "" && !validateHours(body.solve_time_hours)}
                                                                name="solve_time_hours"
                                                                onChange={(e) => completeField(e)} />

                                                </Form.Group>
                                        </Col>
                                        <Col>
                                                <Form.Group controlId="formGridAddress1">
                                                        {t('date.minutes')}  <Form.Control
                                                                placeholder={t('placeholder.minutes')}
                                                                maxlength="2"
                                                                value={body.solve_time_minutes}
                                                                isInvalid={body.solve_time_minutes !== "" && !validateMinutes(body.solve_time_minutes)}
                                                                name="solve_time_minutes"
                                                                onChange={(e) => completeField(e)} />
                                                </Form.Group>
                                        </Col>
                                </Row>
                                {activateBooton(body) ?
                                        <><Button variant="primary" onClick={createPriority} >{t('button.save')}</Button></>
                                        : <><Button variant="primary" disabled>{t('button.save')}</Button></>}

                                <Button variant="primary" href="/priorities">{t('button.cancel')}</Button>
                        </Form>
                </Card.Body>)

}

export default FormPriority