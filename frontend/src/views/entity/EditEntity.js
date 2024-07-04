import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Row, Col, Card } from 'react-bootstrap';
import { putEntity } from '../../api/services/entities';
import FormEntity from './components/FormEntity';
import Navigation from '../../components/Navigation/Navigation';
import Alert from '../../components/Alert/Alert';
import { getEntity } from '../../api/services/entities';
import { useTranslation, Trans } from 'react-i18next';

const EditEntity = () => {
    const location = useLocation();
    const fromState = location.state;
    const [entity, setEntity] = useState(fromState);
    const [name, setName] = useState('');
    const [active, setActive] = useState('');
    const { t } = useTranslation();

    //Alert
    const [showAlert, setShowAlert] = useState(false);

    useEffect(() => {

        if (entity) {
            setName(entity.name);
            setActive(entity.active);
        } else {
            const entityUrl = localStorage.getItem('entity');
            console.log("STORAGE")
            getEntity(entityUrl)
                .then((response) => {
                    setEntity(response.data)
                }).catch(error => console.log(error));

        }
    }, [entity]);

    //Update
    const editEntity = () => {
        putEntity(entity.url, name, active)
            .then((response) => {
                localStorage.removeItem('entity');
                window.location.href = "/entities"
            })
            .catch(() => {
                setShowAlert(true)
            });
    };

    return (
        <React.Fragment>
            <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="entity" />
            <Row>
                <Navigation actualPosition={t('ngen.entity_edit')} path="/entities" index={t('ngen.entity_other')} />
            </Row>
            <Row>
                <Col sm={12}>
                    <Card>
                        <Card.Header>
                            <Card.Title as="h5">{t('ngen.entity_other')}</Card.Title>
                            <span className="d-block m-t-5">{t('ngen.entity_edit')}</span>
                        </Card.Header>
                        <Card.Body>
                            <Row>
                                <Col sm={12} >
                                    <FormEntity
                                        name={name} setName={setName}
                                        active={active} setActive={setActive}
                                        ifConfirm={editEntity} edit={true} />
                                </Col>
                            </Row>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default EditEntity;
