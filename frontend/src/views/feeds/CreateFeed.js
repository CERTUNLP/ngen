import React, { useState } from 'react';
import { Card, Col, Row } from 'react-bootstrap';
import { postFeed } from '../../api/services/feeds';
import Alert from '../../components/Alert/Alert';
import Navigation from '../../components/Navigation/Navigation'
import FormFeed from './components/FormFeed'
import { useTranslation } from 'react-i18next';

const CreateFeed = () => {
  const [name, setName] = useState("");
  const [active, setActive] = useState(true);
  const [description, setDescription] = useState("");
  const [showAlert, setShowAlert] = useState(false)
  const { t } = useTranslation();
  const createFeed = () => {
    postFeed(name, description, active).then(() => {
      window.location.href = '/feeds';
    }).catch((error) => {
      console.log(error)
      setShowAlert(true)
    })
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  }

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} component="feed"/>
      <Row>
        <Navigation actualPosition={t('ngen.feed.information.add')} path="/feeds" index={t('ngen.feed.information')}/>
      </Row>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t('ngen.feed.information')}</Card.Title>
            </Card.Header>
            <Card.Body>
              <FormFeed name={name} setName={setName} active={active} setActive={setActive} description={description}
                        setDescription={setDescription} createFeed={createFeed}/>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default CreateFeed;
