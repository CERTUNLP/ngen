import React, { useState, useEffect } from 'react'
import { Button, Row, Form, Spinner, Col } from 'react-bootstrap';
import { validateSpaces } from '../../../utils/validators';
import { validateUserName, validateName, validateSelect, validateUserMail, validatePassword, validateUnrequiredInput } from '../../../utils/validators/user';
import SelectComponent from '../../../components/Select/SelectComponent';
import { useTranslation, Trans } from 'react-i18next';

const FormUser = ({ body, setBody, priorities, createUser, loading }) => {

    const [selectPriority, setSelectPriority] = useState()
    const { t } = useTranslation();

    useEffect(() => {

        if (priorities !== []) {
            priorities.forEach(item => {
                if (item.value === body.priority) {
                    setSelectPriority({ label: item.label, value: item.value })
                }
            });
        }

    }, [priorities, body.priority])

    if (loading) {
        return (
            <Row className='justify-content-md-center'>
                <Spinner animation='border' variant='primary' size='sm' />
            </Row>
        );
    }

    const FieldUsername = (event) => {
        if (validateSpaces(event.target.value)) {
            setBody({
                ...body,
                [event.target.name]: event.target.value
            }
            )
        }
    }

    const completeField = (event) => {
        setBody({
            ...body,
            [event.target.name]: event.target.value
        }
        )
    }

    const fieldPassword = (event) => {
        setBody({
            ...body,
            [event.target.name]: event.target.value
        }
        )
    }
    const completeField1 = (nameField, event, setOption) => {
        if (event) {
            setBody({
                ...body,
                [nameField]: event.value
            }
            )
        } else {
            setBody({
                ...body,
                [nameField]: ""
            }
            )

        }
        setOption(event)

    };
    return (
        <Form>
            <Row>
                <Col sm={12} lg={4}>
                    <Form.Group controlId="formGridAddress1">
                        <Form.Label>{t('ngen.user.username')} <b style={{ color: "red" }}>*</b></Form.Label>
                        <Form.Control
                            placeholder={t('ngen.user.placeholder')}
                            maxlength="150"
                            value={body.username}
                            name="username"
                            isInvalid={!validateUserName(body.username)}
                            onChange={(e) => FieldUsername(e)} />
                        {validateUserName(body.username) ? "" : <div className="invalid-feedback"> {t('validate.username')}</div>}
                    </Form.Group>
                </Col>
                <Col sm={12} lg={3}>
                    <SelectComponent controlId="exampleForm.ControlSelect1" label="Prioridades" options={priorities} value={selectPriority} nameField="priority"
                        onChange={completeField1} placeholder={t('ngen.priority.select')} setOption={setSelectPriority} required={true} />
                </Col>
                <Col sm={12} lg={5}>
                    <Form.Group controlId="formGridEmail">
                        <Form.Label>{t('w.email')}</Form.Label>
                        <Form.Control
                            placeholder={t('w.email.placeholder')}
                            maxlength="100"
                            value={body.email}
                            name="email"
                            onChange={(e) => completeField(e)}
                            isInvalid={(validateUnrequiredInput(body.email)) ? !validateUserMail(body.email) : false}
                        />
                        {validateUserMail(body.email) ? "" : <div className="invalid-feedback"> {t('w.email.validate')}</div>}
                    </Form.Group>
                </Col>
            </Row>
            <Row>
                <Col sm={12} lg={6}>
                    <Form.Group className="mb-3" controlId="formBasicPassword">
                        <Form.Label>{t('ngen.password')} <b style={{ color: "red" }}>*</b></Form.Label>
                        <Form.Control
                            type="password"
                            placeholder={t('ngen.password.placeholder')}
                            name="password"
                            onChange={(e) => fieldPassword(e)} />
                    </Form.Group>
                </Col>

                <Col sm={12} lg={6}>
                    <Form.Group className="mb-3" controlId="formBasicPassword">
                        <Form.Label>{t('ngen.password.confirm')} <b style={{ color: "red" }}>*</b></Form.Label>
                        <Form.Control
                            type="password"
                            placeholder={t('ngen.password.placeholder')}
                            name="passwordConfirmation"
                            isInvalid={(validateUnrequiredInput(body.password)) ? !validatePassword(body.password, body.passwordConfirmation) : false}
                            onChange={(e) => fieldPassword(e)} />
                        {!validatePassword(body.password, body.passwordConfirmation) ? "" : <div className="invalid-feedback"> {t('ngen.password.validation')}</div>}
                    </Form.Group>
                </Col>
            </Row>
            <Row>
                <Col sm={12} lg={6}>
                    <Form.Group controlId="formGridAddress1">
                        <Form.Label>{t('ngen.name_one')}</Form.Label>
                        <Form.Control
                            placeholder={t('ngen.name.placeholder')}
                            maxlength="150"
                            name="first_name"
                            value={body.first_name}
                            onChange={(e) => completeField(e)}
                            isInvalid={(validateUnrequiredInput(body.first_name)) ? !validateName(body.first_name) : false}
                        />
                        {validateName(body.first_name) ? "" : <div className="invalid-feedback"> {t('ngen.name.invalid')} </div>}
                    </Form.Group>
                </Col>

                <Col sm={12} lg={6}>
                    <Form.Group controlId="formGridAddress1">
                        <Form.Label>{t('ngen.last.name')}</Form.Label>
                        <Form.Control
                            placeholder={t('ngen.last.name.placeholder')}
                            maxlength="150"
                            value={body.last_name}
                            name="last_name"
                            onChange={(e) => completeField(e)}
                            isInvalid={(validateUnrequiredInput(body.last_name)) ? !validateName(body.last_name) : false}
                        />
                        {validateName(body.last_name) ? "" : <div className="invalid-feedback"> {t('ngen.name.invalid')} </div>}
                    </Form.Group>
                </Col>
            </Row>

            {body.password !== "" && validatePassword(body.password, body.passwordConfirmation)
                && body.username !== "" && validateUserName(body.username)
                && validateSelect(body.priority) ?
                <><Button variant="primary" onClick={createUser} >{t('button.save')}</Button></>
                :
                <><Button variant="primary" disabled>{t('button.save')}</Button></>}
            <Button variant="primary" href="/users">{t('button.cancel')}</Button>


        </Form>
    )
}
export default FormUser
