import React, { useEffect, useState } from "react";
import { Button, Card, CloseButton, Col, Form, Modal, Row, Table } from "react-bootstrap";
import { useLocation } from "react-router-dom";
import Navigation from "../../components/Navigation/Navigation";
import SmallEventTable from "../event/components/SmallEventTable";
import { getCase } from "../../api/services/cases";
import apiInstance from "../../api/api";
import { getEvent } from "../../api/services/events";
import { getEvidence } from "../../api/services/evidences";
import EvidenceCard from "../../components/UploadFiles/EvidenceCard";
import { useTranslation } from "react-i18next";

const ReadCase = () => {
  const location = useLocation();
  const [caseItem, setCaseItem] = useState(location?.state?.item || null);
  const [navigationRow] = useState(localStorage.getItem("navigation"));
  const [buttonReturn] = useState(localStorage.getItem("button return"));

  const [id, setId] = useState("");
  const [date, setDate] = useState("");
  const [attend_date, setAttend_Date] = useState("");
  const [solve_date, setSolve_Date] = useState("");
  const [created, setCreated] = useState("");
  const [modified, setModified] = useState("");

  const [assigned, setAssigned] = useState("");
  const [priority, setPriority] = useState("");
  const [tlp, setTlp] = useState("");
  const [state, setState] = useState("");

  const [modalShowEvent, setModalShowEvent] = useState(false);

  const [list, setList] = useState([]);

  const [evidences, setEvidences] = useState([]);
  const [eventEvidences, setEventEvidences] = useState([]);

  const { t } = useTranslation();

  useEffect(() => {
    if (caseItem !== null) {
      const eventPromises = caseItem.events.map((url) => getEvent(url));

      Promise.all(eventPromises)
        .then((responses) => {
          // Todas las llamadas se han completado exitosamente
          const eventsData = responses.map((response) => response.data);
          setList(eventsData);
        })
        .catch((error) => {
          // Maneja cualquier error que ocurra durante las llamadas
          const errorMessage = t("error.event");
          console.error(errorMessage, error);
        });
    }
    if (!caseItem) {
      const caseUrl = localStorage.getItem("case");
      getCase(caseUrl)
        .then((response) => {
          setCaseItem(response.data);
        })
        .catch((error) => console.log(error));
    }

    const getEvidenceFile = (url) => {
      return apiInstance
        .get(url)
        .then((response) => {
          return response.data.file;
        })
        .catch((error) => {
          console.log(error);
        });
    };

    const getName = (url, set) => {
      return apiInstance
        .get(url)
        .then((response) => {
          set(response.data.name);
        })
        .catch((error) => {
          console.log(error);
        });
    };

    // const getUuid = (url, set) => {
    //   return apiInstance.get(url).then(response => {
    //     set(response.data.uuid);
    //   }).catch(error => {
    //     console.log(error)
    //   })
    // }

    const getAssignedUser = (url) => {
      return apiInstance
        .get(url)
        .then((response) => {
          setAssigned(response.data.username);
        })
        .catch((error) => {
          console.log(error);
        });
    };
    const formatDate = (dateTime, set) => {
      //2023-09-11T17:14:20.292538Z
      let date = dateTime.split("T");
      set(date[0] + " " + date[1].slice(0, 8));
    };

    if (caseItem) {
      if (caseItem.evidence.length > 0) {
        getEvidenceFile(caseItem.evidence);
      }
      if (caseItem.evidence_events.length > 0) {
        getEvidenceFile(caseItem.evidence_events);
      }
      getName(caseItem.priority, setPriority);
      getName(caseItem.tlp, setTlp);
      if (caseItem.user_creator) {
        getAssignedUser(caseItem.user_creator);
      } else {
        setAssigned(t("ngen.status.not_assigned"));
      }
      getName(caseItem.state, setState);

      let idItem = caseItem.url.split("/")[caseItem.url.split("/").length - 2];
      setId(idItem);

      let datetime = caseItem.created.split("T");
      setCreated(datetime[0] + " " + datetime[1].slice(0, 8));
      datetime = caseItem.modified.split("T");
      setModified(datetime[0] + " " + datetime[1].slice(0, 8));

      if (caseItem.date) {
        formatDate(caseItem.date, setDate);
      }
      if (caseItem.attend_date) {
        formatDate(caseItem.attend_date, setAttend_Date);
      }
      if (caseItem.solve_date) {
        formatDate(caseItem.solve_date, setSolve_Date);
      }
    }
  }, [caseItem]);

  useEffect(() => {
    if (caseItem) {
      const fetchAllEvidences = async () => {
        try {
          // Esperar a que todas las promesas de getEvidence se resuelvan
          const responses = await Promise.all(caseItem.evidence.map((url) => getEvidence(url)));
          // Extraer los datos de las respuestas
          const data = responses.map((response) => response.data);
          // Actualizar el estado con los datos de todas las evidencias
          setEvidences(data);
        } catch (error) {
          console.error("Error fetching evidence data:", error);
        }
      };

      // Llamar a la función para obtener los datos de las evidencias
      fetchAllEvidences();


      const fetchAllEventEvidences = async () => {
        try {
          // Esperar a que todas las promesas de getEvidence se resuelvan
          const responses = await Promise.all(caseItem.evidence_events.map((url) => getEvidence(url)));
          // Extraer los datos de las respuestas
          const data = responses.map((response) => response.data);
          // Actualizar el estado con los datos de todas las evidencias
          setEventEvidences(data);
        } catch (error) {
          console.error("Error fetching event evidence data:", error);
        }
      };

      // Llamar a la función para obtener los datos de las evidencias
      fetchAllEventEvidences();
    }
  }, [caseItem]);

  return (
    caseItem && (
      <React.Fragment>
        {navigationRow !== "false" ? (
          <Row>
            <Navigation actualPosition={t("w.detail")} path="/cases" index={t("ngen.case_other")} />
          </Row>
        ) : (
          " "
        )}
        <Row>
          <Col sm={12}>
            <Card>
              <Card.Header>
                <Card.Title as="h5">{t("w.main")}</Card.Title>
              </Card.Header>
              <Card.Body>
                <Table responsive>
                  <tbody>
                    <tr>
                      <td>{t("ngen.uuid")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={caseItem.uuid} />
                      </td>
                      <td>{t("ngen.system.id")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={id} />
                      </td>
                    </tr>
                    <tr>
                      <td> {t("ngen.name_one")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={caseItem.name ? caseItem.name : "-"} />
                      </td>
                      <td>{t("ngen.priority_one")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={priority} />
                      </td>
                    </tr>
                    <tr>
                      <td>{t("ngen.tlp")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={tlp} />
                      </td>
                      <td>{t("ngen.lifecycle_one")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={caseItem.lifecycle} />
                      </td>
                    </tr>
                    <tr>
                      <td>{t("ngen.state_one")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={state} />
                      </td>
                      <td>{t("ngen.status.assigned")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={assigned} />
                      </td>
                    </tr>
                  </tbody>
                </Table>
              </Card.Body>
            </Card>

            <Card>
              <Card.Header>
                <Card.Title as="h5">{t("date.other")}</Card.Title>
              </Card.Header>
              <Card.Body>
                <Table responsive>
                  <tbody>
                    <tr>
                      <td>{t("ngen.case.management_start_date")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={date} />
                      </td>
                      <td>{t("w.attended")}</td>
                      {caseItem.attend_date ? (
                        <td>
                          <Form.Control plaintext readOnly defaultValue={attend_date} />
                        </td>
                      ) : (
                        <td>
                          <Form.Control plaintext readOnly defaultValue={t("w.attended.no")} />
                        </td>
                      )}

                      <td>{t("w.solved")}</td>
                      {caseItem.solve_date ? (
                        <td>
                          <Form.Control plaintext readOnly defaultValue={solve_date} />
                        </td>
                      ) : (
                        <td>
                          <Form.Control plaintext readOnly defaultValue={t("w.solved.no")} />
                        </td>
                      )}
                    </tr>
                    <tr>
                      <td>{t("ngen.date.created")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={created} />
                      </td>
                      <td>{t("ngen.date.modified")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={modified} />
                      </td>
                      <td></td>
                      <td></td>
                    </tr>
                  </tbody>
                </Table>
              </Card.Body>
            </Card>

            <EvidenceCard evidences={evidences} disableDelete={true} disableDragAndDrop={true} title={`${t("ngen.evidences.case")}`} />

            <EvidenceCard evidences={eventEvidences} disableDelete={true} disableDragAndDrop={true} title={`${t("ngen.evidences.event")}`} />

            <SmallEventTable list={list} disableLink={true} disableColumOption={false} disableUuid={false} disableColumnDelete={true} />

            <Card>
              <Card.Header>
                <Card.Title as="h5">{t("w.info")}</Card.Title>
              </Card.Header>
              <Card.Body>
                <Row>
                  <Col sm={6} lg={3}>
                    {t("ngen.comments")}
                  </Col>
                  <Col>
                    <Form.Control plaintext readOnly defaultValue={caseItem.comments} />
                  </Col>
                </Row>
              </Card.Body>
            </Card>
            {caseItem.children.length > 0 ? (
              <Card>
                <Card.Header>
                  <Card.Title as="h5">{t("ngen.children")}</Card.Title>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col sm={6} lg={3}>
                      {t("ngen.children")}
                    </Col>
                    <Col>
                      <Form.Control plaintext readOnly defaultValue={caseItem.children} />
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            ) : (
              <></>
            )}

            {buttonReturn !== "false" ? (
              <Button variant="primary" href="/cases">
                {t("button.return")}
              </Button>
            ) : (
              ""
            )}
          </Col>
        </Row>

        <Modal
          size="lg"
          show={modalShowEvent}
          onHide={() => setModalShowEvent(false)}
          aria-labelledby="contained-modal-title-vcenter"
          centered
        >
          <Modal.Body>
            <Row>
              <Col>
                <Card>
                  <Card.Header>
                    <Row>
                      <Col>
                        <Card.Title as="h5">{t("ngen.event_one")}</Card.Title>
                        <span className="d-block m-t-5">{t("ngen.event.detail")}</span>
                      </Col>
                      <Col sm={12} lg={4}>
                        <CloseButton aria-label={t("w.close")} onClick={() => setModalShowEvent(false)} />
                      </Col>
                    </Row>
                  </Card.Header>
                  <Card.Body>{t("ngen.event.information")}</Card.Body>
                </Card>
              </Col>
            </Row>
          </Modal.Body>
        </Modal>
      </React.Fragment>
    )
  );
};

export default ReadCase;
