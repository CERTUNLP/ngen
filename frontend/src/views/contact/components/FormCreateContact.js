import React, { useEffect, useState } from 'react';
import { Button, Col, Row, Form } from 'react-bootstrap';
import { validateName, validateContact, validateSelect } from '../../../utils/validators/contact';
import FormContactSelectUsername from './FormContactSelectUSername';
import { getMinifiedPriority } from '../../../api/services/priorities';
import SelectLabel from '../../../components/Select/SelectLabel';
import { useTranslation, Trans } from 'react-i18next';

const FormCreateContact = (props) => {
    // props: name, setName, role, setRole, priority, setPriority, type, setType, contact, setContact, keypgp, setKey, ifConfirm, ifCancel
    const [validContact, setValidContact] = useState(false)
    const [prioritiesOption, setPrioritiesOption] = useState([])
    const { t } = useTranslation();

    const [selectPriority, setSelectPriority] = useState()
    const [selectRole, setSelectRole] = useState()
    const [selectType, setSelectType] = useState()

    useEffect(() => {

        getMinifiedPriority()
            .then((response) => {
                let listPriority = []
                response.map((priority) => {
                    listPriority.push({ value: priority.url, label: priority.name })
                })
                setPrioritiesOption(listPriority)
            })
            .catch((error) => {
                console.log(error)
            })

    }, [])

    useEffect(() => {
        if (prioritiesOption !== []) {
            prioritiesOption.forEach(item => {
                if (item.value === props.priority) {
                    setSelectPriority({ label: item.label, value: item.value })
                }
            });
        }
        if (roleOptions !== []) {
            roleOptions.forEach(item => {
                if (item.value === props.role) {
                    setSelectRole({ label: item.label, value: item.value })
                }
            });
        }
        if (typeOptions !== []) {
            typeOptions.forEach(item => {
                if (item.value === props.type) {
                    setSelectType({ label: item.label, value: item.value })
                }
            });
        }


    }, [prioritiesOption])

    const roleOptions = [
        {
            value: 'technical',
            label: `${t('ngen.role.technical')}`,
        },
        {
            value: 'administrative',
            label: `${t('ngen.role.administrative')}`,
        },
        {
            value: 'abuse',
            label: `${t('ngen.role.abuse')}`,
        },
        {
            value: 'notifications',
            label: `${t('ngen.role.notifications')}`,
        },
        {
            value: 'noc',
            label: `${t('ngen.role.noc')}`,
        }
    ]

    const typeOptions = [
        {
            value: 'email',
            label: 'Correo Electronico'
        },
        {
            value: 'telegram',
            label: 'Telegram'
        },
        {
            value: 'phone',
            label: 'Telefono'
        },
        {
            value: 'uri',
            label: 'URI'
        },
    ]

    return (
        <React.Fragment>
            <Form>
                <Row>
                    <Col sm={12} lg={4}>
                        <Form.Group controlId="Form.Contact.Name">
                            <Form.Label>{t('ngen.name_one')} <b style={{ color: "red" }}>*</b></Form.Label>
                            <Form.Control
                                type="nombre"
                                placeholder={t('ngen.name_one')}
                                maxlength="100"
                                value={props.name}
                                onChange={(e) => props.setName(e.target.value)}
                                isInvalid={!validateName(props.name)}
                            />
                        </Form.Group>
                    </Col>
                    <Col sm={12} lg={4}>
                        <SelectLabel set={props.setRole} setSelect={setSelectRole} options={roleOptions}
                            value={selectRole} placeholder={t('ngen.role_one')} required={true} />
                    </Col>
                    <Col sm={12} lg={4}>
                        <SelectLabel set={props.setPriority} setSelect={setSelectPriority} options={prioritiesOption}
                            value={selectPriority} placeholder={t('ngen.priority_one')} required={true} />
                    </Col>
                </Row>
                <Row>
                    <Col lg={4}>
                        <SelectLabel set={props.setType} setSelect={setSelectType} options={typeOptions}
                            value={selectType} placeholder={t('ngen.type')} required={true} />
                    </Col>
                    <Col lg={8}>
                        <FormContactSelectUsername selectedType={props.type}
                            contact={props.contact} setContact={props.setContact}
                            setValidContact={setValidContact} />
                    </Col>
                </Row>
                <Form.Group controlId="Form.Contact.Key">
                    <Form.Label>{t('ngen.public.key')}</Form.Label>
                    <Form.Control
                        type="string"
                        placeholder={t('ngen.key.placeholder')}
                        value={props.keypgp}
                        maxlength="100"
                        onChange={(e) => { props.setKey(e.target.value) }} />
                </Form.Group>
                <Form.Group>
                    {props.name !== "" && (validateName(props.name) && validateSelect(props.role) && validateSelect(props.priority) && validateSelect(props.type) && validateContact(props.contact) && (validContact)) ?
                        <><Button variant="primary" onClick={props.ifConfirm} >{t('button.save')}</Button></>
                        :
                        <><Button variant="primary" disabled>{t('button.save')}</Button></>
                    }
                    <Button variant="primary" onClick={props.ifCancel}>{t('button.cancel')}</Button>
                </Form.Group>
            </Form>
        </React.Fragment>
    );
};

export default FormCreateContact;
