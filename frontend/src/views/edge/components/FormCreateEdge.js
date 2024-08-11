import React from 'react';
import { Button, Col, Form, Row } from 'react-bootstrap';
import Select from 'react-select';
import { useTranslation } from 'react-i18next';


const FormCreateEdge = ({ body, setBody, selectChild, setSelectChild, childernes, ifConfirm, ifCancel }) => {
  const { t } = useTranslation();
  const messageToPlaceholder = t('selectOption')
  const messageWithoutOptions = t('noOption')

  const completeChildernes = (event) => {
    if (event) {
      setBody({
        ...body,
        ["child"]: event.value
      })
      setSelectChild(event)
    } else {
      setSelectChild("")
    }
  }

  const completeField = (event) => {
    setBody({
      ...body,
      [event.target.name]: event.target.value
    })
  }

  return (
    <React.Fragment>
      <Form>
        <Row>
          <Col>

            <Form.Group controlId="formGridAddress1">
              <Form.Label>{t('transitionName')}<b style={{ color: "red" }}>*</b></Form.Label>
              <Form.Control
                placeholder={t('enterDiscriminator')}
                maxLength="150"
                value={body.discr}
                name="discr"
                onChange={(e) => completeField(e)}
              />
              {/*validateDescription(body.description) ? '' : <div className="invalid-feedback">Ingrese una descripcion que contenga hasta 250 caracteres y que no sea vacía</div>*/}
            </Form.Group>
          </Col>
          <Col>
            <Form.Group controlId="formGridAddress1">
              <Form.Label>{t('w.nextState')}<b style={{ color: "red" }}>*</b></Form.Label>
              <Select
                value={selectChild}
                isClearable
                defaultValue={body.child}
                placeholder={messageToPlaceholder}
                noOptionsMessage={() => messageWithoutOptions}
                onChange={completeChildernes}
                options={childernes}
              />
            </Form.Group>
          </Col>
        </Row>
        <Row className="justify-content-center">
          <Form.Group>
            {body.discr.trim() !== "" && selectChild !== "" ?
              <><Button variant="primary" onClick={ifConfirm}>{t('button.save')}</Button></>
              :
              <><Button variant="primary" disabled>{t('button.save')}</Button></>}
            <Button variant="primary" onClick={ifCancel}>{t('button.cancel')}</Button>
          </Form.Group>
        </Row>
      </Form>

    </React.Fragment>
  );
}

export default FormCreateEdge
