import React, { useState, useEffect } from 'react';
import { Button, Card, CloseButton, Col, Row, Form, Modal } from 'react-bootstrap';
import { getMinifiedEntity } from '../../../api/services/entities';
import { getAllNetworks } from '../../../api/services/networks';
import CrudButton from '../../../components/Button/CrudButton';
import FormCreateContact from '../../contact/components/FormCreateContact';
import { postContact } from '../../../api/services/contacts';
import { validateSelect } from '../../../utils/validators/network';
import Select from 'react-select';
import makeAnimated from 'react-select/animated';
import DropdownState from '../../../components/Dropdown/DropdownState';
import Alert from '../../../components/Alert/Alert';
import { postStringIdentifier } from "../../../api/services/stringIdentifier";
import SelectLabel from '../../../components/Select/SelectLabel';
import { useTranslation, Trans } from 'react-i18next';

const animatedComponents = makeAnimated();

const FormCreateNetwork = (props) => {
    // props: ifConfirm children setChildren cidr setCidr domain setDomain active setActive 
    // type setType parent setParent network_entity setNetwork_entity contacts setContactss 
    // {edit:false | true -> active, setActive} !!allContacts

    //Dropdown
    const [entitiesOption, setEntitiesOption] = useState([])
    const [networksOption, setNetworksOption] = useState([])

    //Multiselect
    const [contactsValueLabel, setContactsValueLabel] = useState([])

    //Create Contact
    const [modalCreate, setModalCreate] = useState(false)
    const [supportedName, setSupportedName] = useState('');
    const [selectRol, setSelectRol] = useState('');
    const [supportedPriority, setSupportedPriority] = useState('');
    const [supportedContact, setSupportedContact] = useState('');
    const [supportedKey, setSupportedKey] = useState(null);
    const [selectType, setSelectType] = useState('');
    const [showErrorMessage, setShowErrorMessage] = useState(false)

    const [selectEntity, setSelectEntity] = useState()
    const [selectedType, setSelectedType] = useState()

    //Alert
    const [showAlert, setShowAlert] = useState(false);
    const { t } = useTranslation();

    let typeOption = [
        {
            value: 'internal', label: t('ngen.network.type.internal')
        },
        {
            value: 'external', label: t('ngen.network.type.external')
        }
    ]

    useEffect(() => {

        getMinifiedEntity()
            .then((response) => {
                let listEntity = []
                response.map((entity) => {
                    listEntity.push({ value: entity.url, label: entity.name })
                })

                setEntitiesOption(listEntity)
                console.log(response)
            })
            .catch((error) => {
                console.log(error)
            })

        getAllNetworks()
            .then((response) => {
                setNetworksOption(response)
                console.log(response)
            })
            .catch((error) => {
                console.log(error)
            })

    }, [])

    useEffect(() => {
        if (entitiesOption !== []) {
            entitiesOption.forEach(item => {
                if (item.value === props.network_entity) {
                    setSelectEntity({ label: item.label, value: item.value })
                }
            });
        }
        if (typeOption !== []) {
            typeOption.forEach(item => {
                if (item.value === props.type) {
                    setSelectedType({ label: item.label, value: item.value })
                }
            });
        }

        //selected contacts 
        let listDefaultContact = props.allContacts.filter(elemento => props.contacts.includes(elemento.value))
            .map(elemento => ({ value: elemento.value, label: elemento.label }));
        setContactsValueLabel(listDefaultContact)

    }, [props.contacts, props.allContacts, props.network_entity])

    //Multiselect    
    const selectContacts = (event) => {
        props.setContacts(
            event.map((e) => {
                return e.value
            })
        )
    }

    console.log(contactsValueLabel);
    console.log(props.network_entity);

    const completeFieldStringIdentifier = (event) => {

        if (event.target.value !== "") {
            postStringIdentifier(event.target.value).then((response) => {
                setShowErrorMessage(response.data.artifact_type === "OTHER" || response.data.artifact_type === "EMAIL")
            })
                .catch((error) => {
                    console.log(error)
                }).finally(() => {
                    console.log("finalizo")
                })
        }

        if (event.target.value === "") {
            setShowErrorMessage(false)//para que no aparesca en rojo si esta esta el input vacio en el formulario
        }
        props.setAddress_value(event.target.value)
    }

    //Create Contact
    const createContact = () => { //refactorizar al FormContact

        postContact(supportedName, supportedContact, supportedKey, selectType, selectRol, supportedPriority)
            .then((response) => {
                console.log(response)
                props.setContactsCreated(response) //
                setModalCreate(false) //
            })
            .catch((error) => {
                console.log(error)
            })
            .finally(() => {
                setShowAlert(true);
            });
    };


    return (
        <React.Fragment>
            <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="contact" />
            <Form>
                <Row>
                    <Col sm={12} lg={4}>
                        <SelectLabel set={props.setType} setSelect={setSelectedType} options={typeOption}
                            value={selectedType} placeholder={t('ngen.type')} required={true} />
                    </Col>
                    <Col sm={12} lg={4}>
                        <SelectLabel set={props.setNetwork_entity} setSelect={setSelectEntity} options={entitiesOption}
                            value={selectEntity} placeholder={t('ngen.entity')} />
                    </Col>
                </Row>

                <Row>
                    <Col sm={12} lg={8}>
                        <Form.Label>{t('cidr.domain')}<b style={{ color: "red" }}>*</b></Form.Label>
                        <Form.Group controlId="formGridAddress1">
                            <Form.Control
                                placeholder={t('ngen.enter.ipv4.ipv6.domain.email')}
                                maxlength="150"
                                onChange={(e) => completeFieldStringIdentifier(e)}
                                value={props.address_value}
                                isInvalid={showErrorMessage}
                                name="address_value" />
                            {showErrorMessage ? <div className="invalid-feedback"> {t('error.ipv4.ipv6.domain')} </div> : ""}
                        </Form.Group>
                    </Col>
                </Row>
                <Row>
                    <Col sm={12} lg={8}>
                        <Form.Group controlId="Form.Network.Contacts.Multiselect">
                            <Form.Label>{t('ngen.contact_other')} <b style={{ color: "red" }}>*</b></Form.Label>
                            <Select
                                value={contactsValueLabel}
                                placeholder={t('ngen.contact.select')}
                                closeMenuOnSelect={false}
                                components={animatedComponents}
                                isMulti
                                onChange={selectContacts}
                                options={props.allContacts}
                            />
                        </Form.Group>
                    </Col>

                </Row>
                <Row>
                    <Col sm={12} lg={4}>
                        <CrudButton type='create' name={t('ngen.contact_one')} onClick={() => setModalCreate(true)} />
                    </Col>
                </Row>
                {props.edit ?
                    <Row>
                        <Col>
                            <Form.Group>
                                <Form.Label>{t('ngen.state_one')}</Form.Label>
                                <DropdownState state={props.active} setActive={props.setActive}></DropdownState>
                            </Form.Group>
                        </Col>
                    </Row>
                    :
                    <></>}

                <Row>
                    <Col>
                        <Form.Group>
                            {props.address_value !== "" && !showErrorMessage && validateSelect(props.type) && (props.contacts.length > 0) ?
                                <><Button variant="primary" onClick={props.ifConfirm} >{t('button.save')}</Button></>
                                :
                                <><Button variant="primary" disabled>{t('button.save')}</Button></> //disabled
                            }
                            <Button variant="primary" href="/networks">{t('button.cancel')}</Button>
                        </Form.Group>
                    </Col>
                </Row>
            </Form>

            <Modal size='lg' show={modalCreate} onHide={() => setModalCreate(false)} aria-labelledby="contained-modal-title-vcenter" centered>
                <Modal.Body>
                    <Row>
                        <Col>
                            <Card>
                                <Card.Header>
                                    <Row>
                                        <Col>
                                            <Card.Title as="h5">{t('ngen.contact_other')}</Card.Title>
                                            <span className="d-block m-t-5">{t('ngen.contact.create')}</span>
                                        </Col>
                                        <Col sm={12} lg={2}>
                                            <CloseButton aria-label={t('w.close')} onClick={() => setModalCreate(false)} />
                                        </Col>
                                    </Row>
                                </Card.Header>
                                <Card.Body>
                                    <FormCreateContact
                                        name={supportedName} setName={setSupportedName}
                                        role={selectRol} setRole={setSelectRol}
                                        priority={supportedPriority} setPriority={setSupportedPriority}
                                        type={selectType} setType={setSelectType}
                                        contact={supportedContact} setContact={setSupportedContact}
                                        keypgp={supportedKey} setKey={setSupportedKey}
                                        ifConfirm={createContact} ifCancel={() => setModalCreate(false)} />
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </Modal.Body>
            </Modal>
        </React.Fragment>
    );
};

export default FormCreateNetwork;
