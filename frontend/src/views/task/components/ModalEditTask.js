import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Modal, CloseButton } from 'react-bootstrap';
import { putTask } from '../../../api/services/tasks';
import FormCreateTask from './FormCreateTask';
import { useTranslation, Trans } from 'react-i18next';

const ModalEditTask = (props) => { //show, task, onHide, ifEdit, setShowAlert

    const [url, setUrl] = useState(props.task.url); //required
    const [name, setName] = useState(props.task.name); //required
    const [priority, setPriority] = useState(props.task.priority); //required
    const [description, setDescription] = useState(props.task.description);
    const [playbook, setPlaybook] = useState(props.task.playbook); //required
    const { t } = useTranslation();

    useEffect(() => {

    }, [])

    const editTask = () => {

        putTask(url, name, description, priority, playbook)
            .then((response) => {
                console.log(response)
                console.log('se edito una tarea')
                props.ifEdit(response)
                props.onHide()
            })
            .catch((error) => {
                console.log(error)
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
                                <Card.Header>
                                    <Row>
                                        <Col>
                                            <Card.Title as="h5">{t('ngen.tasks')}</Card.Title>
                                            <span className="d-block m-t-5">{t('w.edit')} {t('ngen.task')}</span>
                                        </Col>
                                        <Col sm={12} lg={2}>
                                            <CloseButton aria-label={t('w.close')} onClick={props.onHide} />
                                        </Col>
                                    </Row>
                                </Card.Header>
                                <Card.Body>
                                    <FormCreateTask
                                        name={name} setName={setName}
                                        priority={priority} setPriority={setPriority}
                                        description={description} setDescription={setDescription}
                                        playbook={playbook}
                                        ifConfirm={editTask} ifCancel={props.onHide} />
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </Modal.Body>
            </Modal>
        </React.Fragment>
    )
}

export default ModalEditTask;