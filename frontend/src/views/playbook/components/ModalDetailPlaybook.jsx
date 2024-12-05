import React, { useEffect, useState } from "react";
import { Card, CloseButton, Col, Form, Modal, Row, Table } from "react-bootstrap";
import CrudButton from "../../../components/Button/CrudButton";
import { Link } from "react-router-dom";
import FormGetName from "../../../components/Form/FormGetName";
import { getTask } from "../../../api/services/tasks";
import { getTaxonomy } from "../../../api/services/taxonomies";
import { useTranslation } from "react-i18next";
import DateShowField from "components/Field/DateShowField";

const ModalDetailPlaybook = (props) => {
  const { t } = useTranslation();

  return (
    <React.Fragment>
      <Modal size="lg" show={props.show} onHide={props.onHide} aria-labelledby="contained-modal-title-vcenter" centered>
        <Modal.Body>
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  <Row>
                    <Col>
                      <Card.Title as="h5">{t("ngen.playbook")}</Card.Title>
                      <span className="d-block m-t-5">{t("ngen.playbook.detail")}</span>
                    </Col>
                    <Col sm={12} lg={2}>
                      <Link to={`/playbooks/edit/${props.id}`}>
                        <CrudButton type="edit" />
                      </Link>
                      <CloseButton aria-label={t("button.close")} onClick={props.onHide} />
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <tbody>
                      {props.playbook.name ? (
                        <tr>
                          <td>{t("ngen.name_one")}</td>
                          <td>
                            <Form.Control plaintext readOnly defaultValue={props.playbook.name} />
                          </td>
                        </tr>
                      ) : (
                        <></>
                      )}
                      {props.playbook.taxonomy && props.playbook.taxonomy.length > 0 ? (
                        <tr>
                          <td>{t("ngen.taxonomy_other")}</td>
                          <td>
                            {Object.values(props.playbook.taxonomy).map((taxonomyItem, index) => {
                              return <FormGetName form={true} get={getTaxonomy} url={taxonomyItem} key={index} />;
                            })}
                          </td>
                        </tr>
                      ) : (
                        <></>
                      )}
                      {props.playbook.tasks && props.playbook.tasks.length > 0 ? (
                        <tr>
                          <td>{t("ngen.tasks")}</td>
                          <td>
                            {Object.values(props.playbook.tasks).map((taskItem, index) => {
                              return <FormGetName form={true} get={getTask} url={taskItem} key={index} />;
                            })}
                          </td>
                        </tr>
                      ) : (
                        <></>
                      )}
                      <tr>
                        <td>{t("ngen.date.created")}</td>
                        <td>
                          <DateShowField value={props?.playbook?.created} asFormControl />
                        </td>
                      </tr>
                      <tr>
                        <td>{t("ngen.date.modified")}</td>
                        <td>
                          <DateShowField value={props?.playbook?.modified} asFormControl />
                        </td>
                      </tr>
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>
    </React.Fragment>
  );
};

export default ModalDetailPlaybook;
