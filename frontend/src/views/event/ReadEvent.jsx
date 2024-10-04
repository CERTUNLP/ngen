import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Button, Card, Col, Form, Row, Table } from "react-bootstrap";
import CallBackendByName from "../../components/CallBackendByName";
import CallBackendByType from "../../components/CallBackendByType";
import { getTaxonomy } from "../../api/services/taxonomies";
import { getPriority } from "../../api/services/priorities";
import { getUser } from "../../api/services/users";
import { getTLPSpecific } from "../../api/services/tlp";
import { getFeed } from "../../api/services/feeds";
import { getEvent } from "../../api/services/events";
import SmallEventTable from "./components/SmallEventTable";
import { getArtefact } from "../../api/services/artifact";
import SmallCaseTable from "../case/components/SmallCaseTable";
import { getEvidence } from "../../api/services/evidences";
import EvidenceCard from "../../components/UploadFiles/EvidenceCard";
import { useTranslation } from "react-i18next";
import PermissionCheck from "components/Auth/PermissionCheck";

const ReadEvent = ({ routeParams }) => {
  const location = useLocation();
  const [body, setBody] = useState({});
  const [eventItem, setEventItem] = useState(location?.state?.item || null);
  const [navigationRow] = useState(localStorage.getItem("navigation"));
  const [buttonReturn] = useState(localStorage.getItem("button return"));

  const [evidences, setEvidences] = useState([]);
  const [children, setChildren] = useState([]);
  const [childrenEvidences, setChildrenEvidences] = useState([]);
  const { t } = useTranslation();

  // const storageEventUrl = (url) => {
  //   localStorage.setItem('event', url);
  // };

  useEffect(() => {
    if (!eventItem) {
      const event = localStorage.getItem("event");
      getEvent(event)
        .then((responsive) => {
          setBody(responsive.data);
          setEventItem(responsive.data);
        })
        .catch((error) => console.log(error));
    }
  }, [eventItem]);

  useEffect(() => {
    const fetchAllEvidences = async () => {
      if (eventItem) {
        try {
          // Esperar a que todas las promesas de getEvidence se resuelvan
          const responses = await Promise.all(eventItem.evidence.map((url) => getEvidence(url)));
          // Extraer los datos de las respuestas
          const data = responses.map((response) => response.data);
          // Actualizar el estado con los datos de todas las evidencias
          setEvidences(data);
        } catch (error) {
          console.error("Error fetching evidence data:", error);
        }
      }
    };

    // Llamar a la función para obtener los datos de las evidencias
    fetchAllEvidences();

    const fetchAllChildren = async () => {
      if (eventItem) {
        try {
          // Esperar a que todas las promesas de getEvent se resuelvan
          const responses = await Promise.all(eventItem.children.map((url) => getEvent(url)));
          // Extraer los datos de las respuestas
          const data = responses.map((response) => response.data);
          // Actualizar el estado con los datos de todos los eventos hijos
          setChildren(data);
        } catch (error) {
          console.error("Error fetching children data:", error);
        }
      }
    }

    // Llamar a la función para obtener los datos de los eventos hijos
    fetchAllChildren();
  }, [eventItem]);

  useEffect(() => {
    const fetchAllChildrenEvidences = async () => {
      if (children.length > 0) {
        try {
          // Esperar a que todas las promesas de getEvidence se resuelvan para cada evento hijo, cada evidencia
          const responses = await Promise.all(
            children.map((child) => Promise.all(child.evidence.map((url) => getEvidence(url)))
            ));
          // Extraer los datos de las respuestas y filtrar los elementos vacíos
          const data = responses.map((response) => response[0]?.data).filter((evidence) => evidence !== undefined);
          // Actualizar el estado con los datos de todas las evidencias de los eventos hijos
          setChildrenEvidences(data);
        } catch (error) {
          console.error("Error fetching children evidences data:", error);
        }
      }
    };

    // Llamar a la función para obtener los datos de las evidencias de los eventos hijos
    fetchAllChildrenEvidences();
  }, [children]);

  const callbackTaxonomy = (url, setPriority) => {
    getTaxonomy(url)
      .then((response) => {
        setPriority(response.data);
      })
      .catch();
  };
  const callbackTlp = (url, setPriority) => {
    getTLPSpecific(url)
      .then((response) => {
        setPriority(response.data);
      })
      .catch();
  };
  const callbackFeed = (url, setPriority) => {
    getFeed(url)
      .then((response) => {
        setPriority(response.data);
      })
      .catch();
  };
  const callbackPriority = (url, set) => {
    getPriority(url)
      .then((response) => {
        set(response.data);
      })
      .catch();
  };
  const callbackEvent = (url, set) => {
    getEvent(url)
      .then((response) => {
        set(response.data);
      })
      .catch();
  };
  const callbackReporter = (url, set) => {
    getUser(url)
      .then((response) => {
        set(response.data);
      })
      .catch();
  };
  const callbackArtefact = (url, set) => {
    getArtefact(url)
      .then((response) => {
        set(response.data);
      })
      .catch();
  };
  const returnBack = () => {
    if (localStorage.getItem("return") === "List events") {
      window.location.href = "/events";
    } else {
      window.history.back();
    }
  };

  return (
    <React.Fragment>
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("menu.principal")}</Card.Title>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("date.one")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              <div>{body.date ? body.date.slice(0, 10) + " " + body.date.slice(11, 19) : "--"}</div>
            </Col>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("ngen.uuid")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              <div>{body.uuid}</div>
            </Col>
          </Row>
          <p />
          <Row>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("ngen.tlp")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              {body.tlp !== undefined ? <CallBackendByName url={body.tlp} callback={callbackTlp} /> : "-"}
            </Col>
            <PermissionCheck permissions={["view_feed"]}>
              <Col sm={12} lg={2} className={"align-self-center"}>
                {t("ngen.feed.information")}
              </Col>
              <Col sm={12} lg={4} className={"align-self-center"}>
                {body.feed !== undefined ? <CallBackendByName url={body.feed} callback={callbackFeed} /> : "-"}
              </Col>
            </PermissionCheck>
          </Row>
          <p />
          <Row>
            <PermissionCheck permissions={["view_taxonomy"]}>
              <Col sm={12} lg={2} className={"align-self-center"}>
                {t("ngen.taxonomy_one")}
              </Col>
              <Col sm={12} lg={4} className={"align-self-center"}>
                {body.taxonomy !== undefined ? <CallBackendByName url={body.taxonomy} callback={callbackTaxonomy} /> : "-"}
              </Col>
            </PermissionCheck>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("ngen.event.initial_taxonomy_slug")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              {body.initial_taxonomy_slug !== undefined ? (body.initial_taxonomy_slug ? body.initial_taxonomy_slug : "-") : "-"}
            </Col>
          </Row>
          <p />
          <Row>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("ngen.priority_one")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              {body.priority !== undefined ? <CallBackendByName url={body.priority} callback={callbackPriority} /> : "-"}
            </Col>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("reporter")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              {body.reporter !== undefined ? <CallBackendByName url={body.reporter} callback={callbackReporter} attr={"username"} /> : "-"}
            </Col>
          </Row>
          <p />
          <Row>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("ngen.event.parent")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              {body.parent !== undefined ? (
                body.parent ? (
                  // Esto no funciona por el routing, al acceder al elemento parent y tener la misma URL el componente no recarga
                  // Y aunque recargue, luego no funciona el history back
                  // <Link to="/events/view" state={ body.parent }} >
                  //     <Button className="fa fa-eye mx-auto font-weight-light" variant="outline-primary"
                  //             onClick={() =>
                  //                 storageEventUrl(body.parent)
                  //             }>
                  //             {' ' + t('ngen.event.parent')}
                  //     </Button>
                  // </Link>
                  <CallBackendByName url={body.parent} callback={callbackEvent} attr={"uuid"} />
                ) : (
                  "-"
                )
              ) : (
                "-"
              )}
            </Col>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("ngen.children")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              {body.children !== undefined ? body.children.length : "0"}
            </Col>
          </Row>
          <p />
          <Row>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("ngen.event.merged")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              {body.merged !== undefined ? (body.merged ? t("w.yes") : t("w.no")) : "-"}
            </Col>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("w.blocked")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              {body.blocked !== undefined ? (body.merged ? t("w.yes") : t("w.no")) : "-"}
            </Col>
          </Row>
          <p />
          <Row>
            <Col sm={12} lg={2} className={"align-self-center"}>
              {t("notes")}
            </Col>
            <Col sm={12} lg={4} className={"align-self-center"}>
              {body.notes}
            </Col>
          </Row>
          {/*</Table>*/}
        </Card.Body>
      </Card>
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("ngen.affectedResources")}</Card.Title>
        </Card.Header>
        {body.domain !== null ? (
          <Card.Body>
            <Row>
              <Col sm={12} lg={2} className={"align-self-center"}>
                {t("ngen.domain")}
              </Col>
              <Col sm={12} lg={4} className={"align-self-center"}>
                &nbsp;
                <Form.Control plaintext readOnly defaultValue={body.domain} />
              </Col>
            </Row>
          </Card.Body>
        ) : (
          <Card.Body>
            <Row>
              <Col sm={12} lg={2} className={"align-self-center"}>
                {t("ngen.cidr")}
              </Col>
              <Col sm={12} lg={4} className={"align-self-center"}>
                &nbsp;
                <Form.Control plaintext readOnly defaultValue={body.cidr} />
              </Col>
            </Row>
          </Card.Body>
        )}
      </Card>

      <SmallCaseTable readCase={body.case} disableColumOption={true} />

      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("ngen.artifact_other")}</Card.Title>
        </Card.Header>
        <Card.Body>
          <Row>
            {body.artifacts !== undefined
              ? body.artifacts.map((url) => {
                return <CallBackendByType key={url} url={url} callback={callbackArtefact} useBadge={true} />;
              })
              : ""}
          </Row>
        </Card.Body>
      </Card>

      <EvidenceCard evidences={evidences} disableDelete={true} disableDragAndDrop={true} />

      <EvidenceCard evidences={childrenEvidences} disableDelete={true} disableDragAndDrop={true} title={t("ngen.evidences.children")} />

      {/* deshabilitamos la columna opciones para view y delete hasta que se corrija el uso de localstorage para la navegacion ya que no puede ir de un evento a otro sin usar href.location */}
      <SmallEventTable list={children} disableLink={true} disableColumOption={true} disableUuid={false} disableColumnDelete={false} disableMerged={true} title={t("ngen.children")} />

      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("ngen.event.additional")}</Card.Title>
        </Card.Header>
        <Card.Body>
          <Table responsive>
            <tbody>
              <tr>
                <td>{t("ngen.comments")}</td>
                <td>
                  <Form.Control plaintext readOnly defaultValue="" />
                </td>
              </tr>

              <tr>
                <td>{t("ngen.date.created")}</td>
                <td>
                  <Form.Control
                    plaintext
                    readOnly
                    defaultValue={body.created !== undefined ? body.created.slice(0, 10) + " " + body.date.slice(11, 19) : ""}
                  />
                </td>
              </tr>
              <tr>
                <td>{t("ngen.date.modified")}</td>
                <td>
                  <Form.Control
                    plaintext
                    readOnly
                    defaultValue={body.modified !== undefined ? body.modified.slice(0, 10) + " " + body.date.slice(11, 19) : ""}
                  />
                </td>
              </tr>
            </tbody>
          </Table>
        </Card.Body>
      </Card>
      {buttonReturn !== "false" ? (
        <Button variant="primary" onClick={() => returnBack()}>
          {t("button.return")}
        </Button>
      ) : (
        ""
      )}
    </React.Fragment>
  );
};

export default ReadEvent;
