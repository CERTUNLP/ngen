import React from 'react'
import { Button, Col, Form, Row } from 'react-bootstrap'
import { validateName } from '../../../utils/validators/entity'
import { useTranslation } from 'react-i18next'

const FormEntity = (props) => { // props: name, setName, ifConfirm, {edit:false | true -> active, setActive}
  const { t } = useTranslation()

  const stateOptions = [
    {
      value: true,
      name: t('w.active'),
    },
    {
      value: false,
      name: t('w.inactive'),
    },
  ]

  return (
    <React.Fragment>
      <Form>
        <Row lg={12}>
          <Col sm={12} lg={8}>
            <Form.Group controlId="Form.Entity.Name">
              <Form.Label>{t('ngen.name_one')}<b style={{ color: 'red' }}>*</b></Form.Label>
              <Form.Control
                type="text"
                name="name"
                placeholder={t('ngen.name_one')}
                value={props.name}
                onChange={(e) => props.setName(e.target.value)}
                isInvalid={!validateName(props.name)}
              />
              {validateName(props.name) ? '' : <div
                className="invalid-feedback">{t('w.validateName')} </div>}

            </Form.Group>
          </Col>
          {props.edit ?
            <Col sm={12} lg={4}>
              <Form.Group controlId="Form.Contact.State.edit">
                <Form.Label>{t('ngen.state_one')} </Form.Label>
                <Form.Control
                  name="edit"
                  type="choice"
                  as="select"
                  value={props.active}
                  onChange={(e) => props.setActive(e.target.value)}>
                  {stateOptions.map((item, index) => {
                    return (
                      <option key={index}
                              value={item.value}>{item.name}</option>
                    )
                  })}
                </Form.Control>
              </Form.Group>
            </Col>
            :
            <></>

          }
        </Row>

        {props.name !== '' && validateName(props.name) ?
          <><Button variant="primary" onClick={props.ifConfirm}>{t(
            'button.save')}</Button></>
          :
          <><Button variant="primary" disabled>{t('button.save')}</Button></>
        }

        <Button variant="primary" href="/entities">{t('button.cancel')}</Button>
      </Form>
    </React.Fragment>
  )
}

export default FormEntity
