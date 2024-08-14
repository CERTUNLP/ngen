import React from 'react'
import { Card, CloseButton, Col, Modal, Row } from 'react-bootstrap'
import FormArtifact from './components/FormArtifact'
import { useTranslation } from 'react-i18next'

const CreateArtifactModal = ({
  show,
  onHide,
  value,
  setValue,
  typeArtifact,
  setTypeArtifact,
  createArtifact,
}) => {
  const { t } = useTranslation()
  return (
    <Modal size="lg" show={show} onHide={onHide}
           aria-labelledby="contained-modal-title-vcenter" centered>
      <Modal.Body>
        <Row>
          <Col>
            <Card>
              <Card.Header>
                <Row>
                  <Col>
                    <Card.Title as="h5">{t('ngen.artifact_one')}</Card.Title>
                    <span className="d-block m-t-5">{t(
                      'ngen.artifact_create')}</span>
                  </Col>
                  <Col sm={12} lg={2}>
                    <CloseButton aria-label={t('w.close')} onClick={onHide}/>
                  </Col>
                </Row>
              </Card.Header>
              <Card.Body>
                <FormArtifact
                  value={value} setValue={setValue}
                  type={typeArtifact} setType={setTypeArtifact}
                  ifConfirm={createArtifact} ifCancel={onHide}
                />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Modal.Body>
    </Modal>
  )
}

export default CreateArtifactModal
