import React from "react";
import { Card, CloseButton, Col, Form, Modal, Row, Table } from "react-bootstrap";
import CrudButton from "components/Button/CrudButton";
import { Link } from "react-router-dom";
import FormNetworkLabelCidr from "./FormNetworkLabelCidr";
import BadgeNetworkLabelContact from "./BadgeNetworkLabelContact";
import ActiveButton from "components/Button/ActiveButton";
import DateShowField from "components/Field/DateShowField";
import { useTranslation } from "react-i18next";

const ModalDetailNetwork = (props) => {
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
                      <Card.Title as="h5">{t("ngen.network_other")}</Card.Title>
                      <span className="d-block m-t-5">{t("ngen.network.detail")}</span>
                    </Col>
                    <Col sm={12} lg={2}>
                      <CrudButton type="edit" to={`/networks/edit/${props.id}`} checkPermRoute />
                      <CloseButton aria-label={t("button.close")} onClick={props.onHide} />
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <tbody>
                      {props.network.cidr ? (
                        <tr>
                          <td>{t("ngen.cidr")}</td>
                          <td>
                            <Form.Control plaintext readOnly defaultValue={props.network.cidr} />
                          </td>
                        </tr>
                      ) : (
                        <></>
                      )}
                      <tr>
                        <td>{t("w.active")}</td>
                        <td>
                          <ActiveButton active={props.network.active} />
                        </td>
                      </tr>
                      {props.network.domain ? (
                        <tr>
                          <td>{t("ngen.domain")}</td>
                          <td>
                            <Form.Control plaintext readOnly defaultValue={props.network.domain} />
                          </td>
                        </tr>
                      ) : (
                        <></>
                      )}
                      {props.network.parent ? (
                        <tr>
                          <td>{t("ngen.network.main")}</td>
                          <td>
                            <FormNetworkLabelCidr url={props.network.parent} />
                          </td>
                        </tr>
                      ) : (
                        <></>
                      )}
                      {props.network.children && props.network.children.length > 0 ? (
                        <tr>
                          <td>{t("ngen.network.subnets")}</td>
                          <td>
                            {Object.values(props.network.children).map((net, index) => {
                              return <FormNetworkLabelCidr url={net} key={index} />;
                            })}
                          </td>
                        </tr>
                      ) : (
                        <></>
                      )}
                      {props.network.contacts && props.network.contacts.length > 0 ? (
                        <tr>
                          <td>
                            {t("ngen.related")} {t("ngen.contact_other")}&nbsp;
                          </td>
                          <td>
                            {Object.values(props.network.contacts).map((contactItem, index) => {
                              return <BadgeNetworkLabelContact url={contactItem} key={index} />;
                            })}
                          </td>
                        </tr>
                      ) : (
                        <></>
                      )}
                      <tr>
                        <td>{t("ngen.date.created")}</td>
                        <td>
                          <DateShowField value={props?.network?.created} asFormControl />
                        </td>
                      </tr>
                      <tr>
                        <td>{t("ngen.date.modified")}</td>
                        <td>
                          <DateShowField value={props?.network?.modified} asFormControl />
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

export default ModalDetailNetwork;
