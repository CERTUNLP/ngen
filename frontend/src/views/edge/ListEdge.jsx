import React, { useEffect, useState } from "react";
import { Card, CloseButton, Col, Collapse, Modal, Row, Table, Spinner } from "react-bootstrap";
import CrudButton from "../../components/Button/CrudButton";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import FormCreateEdge from "./components/FormCreateEdge";
import { getAllStates, getState } from "../../api/services/states";
import { getAllEdges, postEdge } from "../../api/services/edges";
import RowEdge from "./components/RowEdge";
import Alert from "../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const ListEdge = (props) => {
  const [states, setStates] = useState([]);
  const [edges, setEdges] = useState([]);
  // const [listChildren, setListChildren] = useState([])
  const [children, setChildren] = useState([]);
  const [urlByStateName, setUrlByStateName] = useState({});
  const [edge, setEdge] = useState({
    discr: "",
    parent: "",
    child: null
  });
  const [selectChild, setSelectChild] = useState("");

  const [showAlert, setShowAlert] = useState(false);

  //Create Edge
  const [modalCreate, setModalCreate] = useState(false);

  const [edgeCreated, setEdgeCreated] = useState(null);
  const [edgeDeleted, setEdgeDeleted] = useState(null);
  const [edgeUpdated, setEdgeUpdated] = useState(null);

  //AdvancedPagination
  // const [currentPage, setCurrentPage] = useState(1);
  const [countItems] = useState(0);
  const { t } = useTranslation();

  useEffect(() => {
    if (props.url !== undefined) {
      getState(props.url)
        .then((response) => {
          //este metodo es para las posibles opciones a hora de cargar un edge en el formulario
          setChildren(findElementsWithSameUrl(response.data.children, states));
        })
        .catch((error) => {
          console.log(error);
        });
    }

    if (props.url !== undefined) {
      getAllEdges()
        .then((response) => {
          //necito listar todos los edges que esten asociado a este estado padre
          setEdges(findElementsTheEdges(props.url, response));
        })
        .catch((error) => {
          console.log(error);
        });
    }

    getAllStates()
      .then((response) => {
        var listChildren = [];
        var listStates = [];
        var dicState = {};
        response.forEach((state) => {
          listChildren.push({ value: state.url, label: state.name });
          listStates.push(state);
          dicState[state.url] = state.name;
        });
        setChildren(listChildren);
        setStates(listStates);
        setUrlByStateName(dicState);
      })
      .catch((error) => {
        console.log(error);
      });
  }, [edgeCreated, edgeDeleted, edgeUpdated, props.url]);

  if (props.loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }
  /**/

  function updatePage(chosenPage) {
    // setCurrentPage(chosenPage);
  }

  function findElementsWithSameUrl(url, states) {
    if (url !== undefined) {
      const foundItems = [];

      states.forEach((elemento) => {
        if (url.includes(elemento.url)) {
          foundItems.push(elemento);
        }
      });

      return foundItems;
    }
  }

  function findElementsTheEdges(url, edges) {
    if (url !== undefined) {
      const foundItems = [];

      edges.forEach((edges) => {
        if (url === edges.parent) {
          foundItems.push(edges);
        }
      });

      return foundItems;
    }
  }

  const closeModal = () => {
    setEdge({
      discr: "",
      parent: null,
      child: null
    });
    setSelectChild("");
    setModalCreate(false);
  };

  const createEdge = () => {
    postEdge(edge.discr, props.url, edge.child)
      .then((response) => {
        setEdgeCreated(response);
        setEdge({
          discr: "",
          parent: null,
          child: null
        });
        setSelectChild("");
        setModalCreate(false);
      })
      .catch((error) => {
        console.log(error);
        setShowAlert(true);
      })
      .finally(() => {
        props.setShowAlert(true);
      });
  };

  return (
    <div>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="edge" />
              <Row>
                <Col sm={12} lg={9}>
                  <Card.Title as="h5">{t("transition_other")}</Card.Title>
                  <span className="d-block m-t-5">{t("transitionList")}</span>
                </Col>
                <Col sm={12} lg={3}>
                  <CrudButton
                    type="create"
                    name={t("transition")}
                    onClick={() => setModalCreate(true)}
                    permissions="add_edge"
                    disabled={!props.sectionAddEdge}
                  />
                </Col>
              </Row>
            </Card.Header>

            <Collapse in={props.sectionAddEdge}>
              <div id="basic-collapse">
                <Card.Body>
                  <Table responsive hover className="text-center">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>{t("transitionName")}</th>
                        <th>{t("w.posteriorState")}</th>
                        <th>{t("ngen.action_one")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {edges ? (
                        edges.map((edge, index) => {
                          return (
                            <RowEdge
                              key={edge.url}
                              url={edge.url}
                              edges={edges}
                              urlByStateName={urlByStateName}
                              states={states}
                              listChildren={children}
                              id={index + 1}
                              edgeDeleted={edgeDeleted}
                              setEdgeDeleted={setEdgeDeleted}
                              edgeUpdated={edgeUpdated}
                              setEdgeUpdated={setEdgeUpdated}
                              setShowAlert={setShowAlert}
                              setEdges={setEdges}
                              edge={edge}
                            />
                          );
                        })
                      ) : (
                        <></>
                      )}
                    </tbody>
                  </Table>
                </Card.Body>
                <Card.Footer>
                  <Row className="justify-content-md-center">
                    <Col md="auto">
                      <AdvancedPagination countItems={countItems} updatePage={updatePage}></AdvancedPagination>
                    </Col>
                  </Row>
                </Card.Footer>
              </div>
            </Collapse>
          </Card>
        </Col>
      </Row>

      <Modal size="lg" show={modalCreate} onHide={() => closeModal()} aria-labelledby="contained-modal-title-vcenter" centered>
        <Modal.Body>
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="edge" />
                  <Row>
                    <Col>
                      <Card.Title as="h5">{t("transition")}</Card.Title>
                      <span className="d-block m-t-5">{t("transitionAdd")}</span>
                    </Col>
                    <Col sm={12} lg={2}>
                      <CloseButton aria-label={t("w.close")} onClick={() => closeModal()} />
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <FormCreateEdge
                    body={edge}
                    setBody={setEdge}
                    selectChild={selectChild}
                    setSelectChild={setSelectChild}
                    childernes={children}
                    ifConfirm={createEdge}
                    ifCancel={() => setModalCreate(false)}
                  />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>
    </div>
  );
};

export default ListEdge;
