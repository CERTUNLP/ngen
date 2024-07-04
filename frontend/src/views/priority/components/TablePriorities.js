import React, { useState } from 'react'
import {
    Card, Table, Modal, Row, Col, Form, CloseButton, Spinner
} from 'react-bootstrap';
import { Link } from 'react-router-dom'
import { deletePriority } from "../../../api/services/priorities";
import CrudButton from '../../../components/Button/CrudButton';
import ModalConfirm from '../../../components/Modal/ModalConfirm';
import Alert from '../../../components/Alert/Alert';
import Ordering from '../../../components/Ordering/Ordering'
import { useTranslation, Trans } from 'react-i18next';

const TablePriorities = ({ Priorities, loading, order, setOrder, setLoading, currentPage }) => {
    const [remove, setRemove] = useState(false);
    const [deleteName, setDeleteName] = useState("");
    const [deleteUrl, setDeleteUrl] = useState("");
    const [priority, setPriority] = useState({});
    const [modalShow, setModalShow] = useState(false);
    const [showAlert, setShowAlert] = useState(false)
    const { t } = useTranslation();

    const resetShowAlert = () => {
        setShowAlert(false);
    }

    if (loading) {
        return (
            <Row className='justify-content-md-center'>
                <Spinner animation='border' variant='primary' size='sm' />
            </Row>
        );
    }

    const handleShow = (name, url) => {

        setDeleteName(name)
        setDeleteUrl(url)
        setRemove(true)
    }

    const handleDelete = () => {
        deletePriority(deleteUrl).then(() => {
            window.location.href = '/priorities';
        })
            .catch((error) => {
                setRemove(false)
                setShowAlert(true)
                console.log(error)
            })
    }
    const showModalPriority = (priority) => {

        setPriority(priority)
        setModalShow(true)

    }

    const letterSize = { fontSize: '1.1em' }
    return (
        <div>
            <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />

            <ul className="list-group my-4">
                <Table responsive hover className="text-center">
                    <thead>
                        <tr>
                            <Ordering field="name" label={t('ngen.name_one')} order={order} setOrder={setOrder} setLoading={setLoading} letterSize={letterSize} />
                            <th style={letterSize}>{t('date.limit.response')}</th>
                            <th style={letterSize}>{t('date.limit.resolution')}</th>
                            <th style={letterSize}>{t('ngen.options')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Priorities.map((priority, index) => {
                            return (
                                <tr key={index}>
                                    <td>{priority.name}</td>
                                    <td>{priority.attend_time}</td>
                                    <td>{priority.solve_time}</td>

                                    <td>
                                        <CrudButton type='read' onClick={() => { showModalPriority(priority) }} />

                                        <Link to={{ pathname: "/priorities/edit", state: priority }} >
                                            <CrudButton type='edit' />
                                        </Link>
                                        <CrudButton type='delete' onClick={() => handleShow(priority.name, priority.url)} />
                                    </td>

                                </tr>
                            )
                        })}
                        <Modal size='lg' show={modalShow} onHide={() => setModalShow(false)} aria-labelledby="contained-modal-title-vcenter" centered>
                            <Modal.Body>
                                <Row>
                                    <Col>
                                        <Card>
                                            <Card.Header>
                                                <Row>
                                                    <Col>
                                                        <Card.Title as="h5">{t('ngen.priority_one')}</Card.Title>
                                                        <span className="d-block m-t-5">{t('ngen.priority.detail')}</span>
                                                    </Col>
                                                    <Col sm={12} lg={4}>
                                                        <Link to={{ pathname: "/priorities/edit", state: priority }} >
                                                            <CrudButton type='edit' />
                                                        </Link>
                                                        <CloseButton aria-label={t('w.close')} onClick={() => setModalShow(false)} />
                                                    </Col>
                                                </Row>
                                            </Card.Header>
                                            <Card.Body>
                                                <Table responsive >
                                                    <tr>
                                                        <td>{t('ngen.name_one')}</td>
                                                        <td>
                                                            <Form.Control plaintext readOnly defaultValue={priority.name} />
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>{t('date.limit.response')}</td>
                                                        <td>
                                                            <Form.Control plaintext readOnly defaultValue={priority.attend_time} />
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>{t('date.limit.resolution')}</td>
                                                        <td>
                                                            <Form.Control plaintext readOnly defaultValue={priority.solve_time} />
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>{t('ngen.severity')}</td>
                                                        <td>
                                                            <Form.Control plaintext readOnly defaultValue={priority.severity} />
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>{t('ngen.notifications.quantity')}</td>
                                                        <td>
                                                            <Form.Control plaintext readOnly defaultValue={priority.notification_amount} />
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>{t('w.creation')}</td>
                                                        <td>
                                                            <Form.Control plaintext readOnly defaultValue={priority.created ? priority.created.slice(0, 10) + " " + priority.created.slice(11, 19) : ""} />
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>{t('w.update')}</td>
                                                        <td>
                                                            <Form.Control plaintext readOnly defaultValue={priority.modified ? priority.modified.slice(0, 10) + " " + priority.modified.slice(11, 19) : ""} />
                                                        </td>
                                                    </tr>
                                                </Table>
                                            </Card.Body>
                                        </Card>
                                    </Col>
                                </Row>
                            </Modal.Body>
                        </Modal>
                        <ModalConfirm type='delete' component={t('ngen.priority_one')} name={deleteName} showModal={remove} onHide={() => setRemove(false)} ifConfirm={() => handleDelete(deleteUrl)} />
                    </tbody>
                </Table>
            </ul>

        </div>
    )
}

export default TablePriorities