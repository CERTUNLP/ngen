
import React, { useState, useEffect } from 'react'
import { Card, Form, Button, Row, Col } from 'react-bootstrap'
import makeAnimated from 'react-select/animated';
import { validateName, validateDescription, validateUnrequiredInput } from '../../../utils/validators/state';
import SelectComponent from '../../../components/Select/SelectComponent';
import { useTranslation, Trans } from 'react-i18next';

const animatedComponents = makeAnimated();
const FormState = ({ body, setBody, createState, type }) => {
    const [selectAttended, setSelecAttended] = useState()
    const [selectSolved, setSelectSolved] = useState()
    const { t } = useTranslation();
    let solvedOptions = [
        {
            value: true,
            label: t('ngen.true')
        },
        {
            value: false,
            label: t('ngen.false')
        }
    ]
    let attendedOptions = [
        {
            value: true,
            label: t('ngen.true')
        },
        {
            value: false,
            label: t('ngen.false')
        }
    ]
    useEffect(() => {

        if (solvedOptions !== []) {
            solvedOptions.forEach(item => {
                if (item.value === body.solved) {
                    setSelectSolved({ label: item.label, value: item.value })
                }
            });
        }
        if (attendedOptions !== []) {
            attendedOptions.forEach(item => {
                if (item.value === body.attended) {
                    setSelecAttended({ label: item.label, value: item.value })
                }
            });
        }


    }, [])

    const completeField = (event) => {
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
        <div>
            <Card>
                <Card.Header>
                    <Card.Title as="h5">{type} {t('ngen.state_one')}</Card.Title>
                </Card.Header>
                <Card.Body>
                    <Form>
                        <Row>
                            <Col>
                                <Form.Group controlId="formGridAddress1">
                                    <Form.Label>{t('ngen.name_one')} <b style={{ color: "red" }}>*</b></Form.Label>
                                    <Form.Control
                                        placeholder={t('ngen.name.placeholder')}
                                        maxlength="100"
                                        value={body.name}
                                        name="name"
                                        isInvalid={!validateName(body.name)}
                                        onChange={(e) => completeField(e)}
                                    />
                                    {validateName(body.name) ? '' : <div className="invalid-feedback">{t('w.validateName')} </div>}
                                </Form.Group>
                            </Col>
                            <Col>
                                <SelectComponent controlId="exampleForm.ControlSelect1" label={t('w.attended')} options={attendedOptions} value={selectAttended} nameField="attended"
                                    onChange={completeField1} placeholder={t('selectOption')} setOption={setSelecAttended} required={true} />
                            </Col>
                            <Col>
                                <SelectComponent controlId="exampleForm.ControlSelect1" label={t('w.solved')} options={attendedOptions} value={selectSolved} nameField="solved"
                                    onChange={completeField1} placeholder={t('selectOption')} setOption={setSelectSolved} required={true} />
                            </Col>
                        </Row>

                        <Form.Group controlId="formGridAddress1">
                            <Form.Label>{t('ngen.description')}</Form.Label>
                            <Form.Control
                                placeholder={t('ngen.description.placeholder')}
                                maxlength="150"
                                value={body.description}
                                name="description"
                                isInvalid={(validateUnrequiredInput(body.description)) ? !validateDescription(body.description) : false}
                                onChange={(e) => completeField(e)}
                            />
                            {validateDescription(body.description) ? '' : <div className="invalid-feedback">{t('ngen.descrption.invalid')}</div>}
                        </Form.Group>


                        {body.name !== "" && validateName(body.name) && body.attended !== "" && body.solved !== "" ?
                            <Button variant="primary" onClick={createState} >{t('button.save')}</Button>
                            :
                            <Button variant="primary" disabled>{t('button.save')}</Button>
                        }

                        <Button variant="primary" href="/states">{t('button.cancel')}</Button>

                    </Form>
                </Card.Body>
            </Card>

        </div>
    )
}

export default FormState