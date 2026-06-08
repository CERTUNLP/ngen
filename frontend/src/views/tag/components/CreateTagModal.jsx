import React from "react";
import { Card, Col, Modal, Row } from "react-bootstrap";
import FormTag from "./FormTag";
import { useTranslation } from "react-i18next";

const CreateTagModal = ({ show, onHide, value, setValue, colorTag, setColorTag, createTag, isUpdate = false, url }) => {
  const { t } = useTranslation();
  return (
    <Modal size="lg" show={show} onHide={onHide} aria-labelledby="contained-modal-title-vcenter" centered>
      <Modal.Header closeButton>
        <Modal.Title id="contained-modal-title-vcenter">
          {isUpdate ? t("crud.edit") + " " + t("ngen.tag_one") : t("crud.add") + " " + t("ngen.tag_one")}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Row>
          <Col>
            <Card>
              <Card.Body>
                <FormTag
                  value={value}
                  setValue={setValue}
                  color={colorTag}
                  setColor={setColorTag}
                  ifConfirm={createTag}
                  ifCancel={onHide}
                  isUpdate={isUpdate}
                  url={url}
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
