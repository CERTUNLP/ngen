import React, { useEffect, useState } from 'react'
import { useLocation, useParams } from 'react-router-dom';
import { Card, Col, Row } from 'react-bootstrap'
import { getEntity, putEntity } from '../../api/services/entities'
import FormEntity from './components/FormEntity'
import Navigation from '../../components/Navigation/Navigation'
import Alert from '../../components/Alert/Alert'
import { useTranslation } from 'react-i18next'
import { COMPONENT_URL } from 'config/constant';

const EditEntity = () => {
  const location = useLocation()
  const fromState = location.state
  const [entity, setEntity] = useState(fromState)
  const [name, setName] = useState('')
  const [active, setActive] = useState('')
  const { t } = useTranslation()
  const [id] = useState(useParams());

  //Alert
  const [showAlert, setShowAlert] = useState(false)

  useEffect(() => {

    if (id.id) {
      getEntity(COMPONENT_URL.entity + id.id + "/")
        .then((response) => {
          setEntity(response.data)
        }).catch(error => console.log(error));

    }
  }, [id]);

  useEffect(() => {

    if (entity) {
      setName(entity.name);
      setActive(entity.active);

    }
  }, [entity]);

  //Update
  const editEntity = () => {
    putEntity(entity.url, name, active).then((response) => {
      localStorage.removeItem('entity')
      window.location.href = '/entities'
    }).catch(() => {
      setShowAlert(true)
    })
  }

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)}
        component="entity" />
      <Row>
        <Navigation actualPosition={t('ngen.entity_edit')} path="/entities"
          index={t('ngen.entity_other')} />
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
                <Col sm={12}>
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
  )
}

export default EditEntity
