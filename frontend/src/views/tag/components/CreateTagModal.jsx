import React from "react";
import { Card, CloseButton, Col, Modal, Row } from "react-bootstrap";
import FormTag from "./FormTag";
import { useTranslation } from "react-i18next";

const CreateTagModal = ({ show, onHide, value, setValue, colorTag, setColorTag, createTag }) => {
  const { t } = useTranslation();
  return (
    <Modal size="lg" show={show} onHide={onHide} aria-labelledby="contained-modal-title-vcenter" centered>
      <Modal.Body>
        <Row>
          <Col>
            <Card>
              <Card.Header>
                <Row>
                  <Col>
                    <Card.Title as="h5">{t("ngen.tag_one")}</Card.Title>
                    <span className="d-block m-t-5">{t("ngen.tag_other")}</span>
                  </Col>
                  <Col sm={12} lg={2}>
                    <CloseButton aria-label={t("w.close")} onClick={onHide} />
                  </Col>
                </Row>
              </Card.Header>
              <Card.Body>
                <FormTag
                  value={value}
                  setValue={setValue}
                  color={colorTag}
                  setColor={setColorTag}
                  ifConfirm={createTag}
                  ifCancel={onHide}
                />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Modal.Body>
    </Modal>
  );
};

export default CreateTagModal;
