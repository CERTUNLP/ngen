import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Modal, CloseButton } from 'react-bootstrap';
import { putEdge } from "../../../api/services/edges";
import FormCreateEdge from './FormCreateEdge';
import Alert from '../../../components/Alert/Alert';
import { useTranslation, Trans } from 'react-i18next';

const ModalEditEdge = (props) => {
    const [body, setBody] = useState(props.edge);
    const [selectChild, setSelectChild] = useState({});
    const [showAlert, setShowAlert] = useState(false)
    const { t } = useTranslation();


    useEffect(() => {
        setSelectChild({ value: props.edge.child, label: props.nameState })

    }, [props.nameState])

    const editEdge = () => {

        putEdge(body.url, body.discr, body.parent, body.child)
            .then((response) => {
                props.ifEdit(response)
                props.onHide()
            })
            .catch((error) => {
                console.log(error)
                setShowAlert(true)
            })
            .finally(() => {
                props.setShowAlert(true)
            })
    };

    return (
        <React.Fragment>
            <Modal size='lg' show={props.show} onHide={props.onHide} aria-labelledby="contained-modal-title-vcenter" centered>
                <Modal.Body>
                    <Row>
                        <Col>
                            <Card>
                                <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="edge" />
                                <Card.Header>
                                    <Row>
                                        <Col>
                                            <Card.Title as="h5">{t('transition')}</Card.Title>
                                            <span className="d-block m-t-5">{t('editTransition')}</span>
                                        </Col>
                                        <Col sm={12} lg={2}>
                                            <CloseButton aria-label='Cerrar' onClick={props.onHide} />
                                        </Col>
                                    </Row>
                                </Card.Header>
                                <Card.Body>
                                    <FormCreateEdge
                                        body={body} setBody={setBody}
                                        selectChild={selectChild} setSelectChild={setSelectChild}
                                        childernes={props.childrens}
                                        ifConfirm={editEdge}
                                        ifCancel={props.onHide} />
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </Modal.Body>
            </Modal>
        </React.Fragment>
    )
}

export default ModalEditEdge