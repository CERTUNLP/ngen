import React from 'react';
import { Button, Col, Form, Row } from 'react-bootstrap';
import { validateDescription, validateName, validateUnrequiredInput } from '../../../utils/validators/feed';
import DropdownState from '../../../components/Dropdown/DropdownState';
import { useTranslation } from 'react-i18next';

const FormFeed = (props) => {
  const { t } = useTranslation();
  return (
    <Form>
      <Row>
        <Col sm={12} lg={6}>
          <Form.Group>
            <Form.Label>
              {t('ngen.name_one')}
              <b style={{ color: 'red' }}>*</b>
            </Form.Label>
            <Form.Control
              type="text"
              placeholder={t('ngen.name_one')}
              value={props.name}
              onChange={(e) => props.setName(e.target.value)}
              isInvalid={!validateName(props.name)}
            />
            {validateName(props.name) ? '' : <div className="invalid-feedback">{t('w.validateName')}</div>}
          </Form.Group>
        </Col>
      </Row>
      <Row>
        <Col sm={12} lg={6}>
          <Form.Group>
            <Form.Label>{t('ngen.description')} </Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              placeholder={t('ngen.description.placeholder')}
              value={props.description}
              onChange={(e) => props.setDescription(e.target.value)}
              isInvalid={validateUnrequiredInput(props.description) ? !validateDescription(props.description) : false}
            />
            {validateDescription(props.description) ? '' : <div className="invalid-feedback">{t('w.validateDesc')} </div>}
          </Form.Group>
        </Col>
      </Row>
      <Row>
        <Col sm={12} lg={1}>
          <Form.Group>
            <Form.Label>{t('ngen.state_one')} </Form.Label>
            <DropdownState state={props.active} setActive={props.setActive} />
          </Form.Group>
        </Col>
      </Row>
      <Row>
        <Form.Group as={Col}>
          {props.name !== '' && validateName(props.name) ? (
            <Button variant="primary" onClick={props.createFeed}>
              {t('button.save')}
            </Button>
          ) : (
            <Button variant="primary" disabled>
              {t('button.save')}
            </Button>
          )}
          <Button variant="info" href="/feeds">
            {t('button.cancel')}
          </Button>
        </Form.Group>
      </Row>
    </Form>
  );
};

export default FormFeed;
