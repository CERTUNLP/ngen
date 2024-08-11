import React, { useEffect, useState } from 'react';
import { Button, Col, Form, Row } from 'react-bootstrap';
import { getAllPriorities } from '../../../api/services/priorities';
import { validateAlphanumeric, validateSpace } from '../../../utils/validators';
import { validateTaskDescription, validateTaskName, validateUnrequiredInput } from '../../../utils/validators/tasks';
import { useTranslation } from 'react-i18next';

// props: name, setName, priority, setPriority, playbook, setPlaybook,
// description, setDescription, ifConfirm, ifCancel 

const FormCreateTask = (props) => {

  //Dropdown
  const [priorityOption, setPriorityOption] = useState([])
  const { t } = useTranslation();

  useEffect(() => {

    getAllPriorities().then((response) => {
      setPriorityOption(response)
      console.log(response.data.results)
    }).catch((error) => {
      console.log(error)
    })

  }, [])

  return (
    <React.Fragment>
      <Form>
        <Row>
          <Col sm={12} lg={12}>
            <Form.Group controlId="Form.Task.Name">
              <Form.Label>{t('ngen.name_one')} <b style={{ color: "red" }}>*</b></Form.Label>
              <Form.Control
                placeholder={t('ngen.name_one')}
                maxLength="100"
                value={props.name}
                onChange={(e) => props.setName(e.target.value)}
                isInvalid={(validateUnrequiredInput(props.name)) ? !validateAlphanumeric(props.name) : false}
              />
              {!validateTaskName(props.name) ?
                <div className="invalid-feedback">{t('w.validate.character')}</div> : ''}
            </Form.Group>
          </Col>
        </Row>
        <Row>
          <Col sm={12} lg={12}>
            <Form.Group controlId="Form.Task.Priority">
              <Form.Label>{t('ngen.priority_one')} <b style={{ color: "red" }}>*</b></Form.Label>
              <Form.Control
                name="priority"
                type="choice"
                as="select"
                value={props.priority}
                onChange={(e) => props.setPriority(e.target.value)}>
                <option value='0'>{t('w.select')}</option>
                {priorityOption.map((priorityItem, index) => {
                  return (
                    <option key={index} value={priorityItem.url}>{priorityItem.name}</option>
                  );
                })}
              </Form.Control>
              {props.priority ? '' : <div className="invalid-feedback">{t('ngen.priority.select')}</div>}
            </Form.Group>
          </Col>
        </Row>
        <Row>
          <Col sm={12} lg={12}>
            <Form.Group controlId="Form.Task.Description">
              <Form.Label>{t('ngen.description')}<b style={{ color: "red" }}>*</b></Form.Label>
              <Form.Control
                as="textarea"
                placeholder={t('ngen.description')}
                maxLength="250"
                rows={4}
                value={props.description}
                onChange={(e) => props.setDescription(e.target.value)}
                isInvalid={(validateUnrequiredInput(props.description)) ? !validateAlphanumeric(props.description) : false}
              />
              {!validateTaskDescription(props.description) ?
                <div className="invalid-feedback">{t('ngen.description.invalid')}</div> : ''}
              <p>{props.description.length}/200</p>
            </Form.Group>
          </Col>
        </Row>
        <Row>
          <Form.Group>
            {(!validateSpace(props.name) || !validateAlphanumeric(props.name)
              || (props.priority === '0') || !validateSpace(props.description)) ?
              <><Button variant="primary" disabled>{t('button.save')}</Button></>
              :
              <><Button variant="primary" onClick={props.ifConfirm}>{t('button.save')}</Button></>
            }
            <Button variant="primary" onClick={props.ifCancel}>{t('button.cancel')}</Button>
          </Form.Group>
        </Row>
      </Form>
    </React.Fragment>
  );
};

export default FormCreateTask;
