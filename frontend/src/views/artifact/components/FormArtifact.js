import React, { useState } from 'react';
import { Row, Card, Form, Button, Col } from 'react-bootstrap';
import { validateFieldText, validateNumber } from '../../../utils/validators';
import FormArtifactsSelect from './FormArtifactsSelect';
import { useTranslation, Trans } from 'react-i18next';


const FormArtifact = (props) => {

    const { t } = useTranslation();


    const typeOptions = [
        {
            value: '0',
            name: t('ngen.option_select')
        },
        {
            value: 'ip',
            name: 'Ip'
        },
        {
            value: 'domain',
            name: 'Domain'
        },
        {
            value: 'fqdn',
            name: 'Fqdn'
        },
        {
            value: 'url',
            name: 'Url'
        },
        {
            value: 'mail',
            name: 'Mail'
        },
        {
            value: 'hash',
            name: 'Hash'
        },
        {
            value: 'file',
            name: 'File'
        },
        {
            value: 'other',
            name: 'Other'
        },
        {
            value: 'user-agent',
            name: 'User-agent'
        },
        {
            value: 'autonomous-system',
            name: 'Autonomous-system'
        }
    ]
    const [validArtifact, setValidArtifact] = useState(false)

    return (
        <div>
            <Card.Body>
                <Form>
                    <Form.Group controlId="exampleForm.ControlSelect1">
                        <Form.Label>{t('ngen.type')}</Form.Label>
                        <Form.Control
                            name="type"
                            type="choice"
                            as="select"
                            value={props.type}
                            onChange={(e) => props.setType(e.target.value)}
                            isInvalid={props.type === "-1"}>

                            {typeOptions.map((t) => {
                                return (<option value={t.value}>{t.name}</option>);
                            })}

                        </Form.Control>
                    </Form.Group>

                    <FormArtifactsSelect
                        value={props.value}
                        setValue={props.setValue}
                        type={props.type}
                        setValidArtifact={setValidArtifact} />


                    {props.type !== "0" && props.value !== "" ?
                        <><Button variant="primary" onClick={props.ifConfirm} >{t('button.save')}</Button></>
                        :
                        <><Button variant="primary" disabled>{t('button.save')}</Button></>

                    }
                    <Button variant="primary" onClick={props.ifCancel}>{t('button.cancel')}</Button>
                </Form>
            </Card.Body>
        </div>
    )
}

export default FormArtifact;
