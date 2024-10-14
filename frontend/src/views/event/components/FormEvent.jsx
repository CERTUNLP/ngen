import React, { useEffect, useState } from "react";
import { Button, Card, Col, Form, Row } from "react-bootstrap";
import Select from "react-select";
import makeAnimated from "react-select/animated";
import CrudButton from "components/Button/CrudButton";
import SelectComponent from "../../../components/Select/SelectComponent";
import { postArtifact } from "../../../api/services/artifact";
import { postStringIdentifier } from "../../../api/services/stringIdentifier";
import Alert from "../../../components/Alert/Alert";
import { getMinifiedState } from "../../../api/services/states";
import ModalCreateCase from "../../case/ModalCreateCase";
import ModalReadCase from "../../case/ModalReadCase";
import ModalListCase from "../../case/ModalListCase";
import CreateArtifactModal from "../../artifact/CreateArtifactModal";
import { getCase } from "../../../api/services/cases";
import SmallCaseTable from "../../case/components/SmallCaseTable";
import EvidenceCard from "../../../components/UploadFiles/EvidenceCard";
import { getEvidence } from "../../../api/services/evidences";
import { useTranslation } from "react-i18next";

const animatedComponents = makeAnimated();
const FormEvent = (props) => {
  const [date, setDate] = useState(props.body.date ? props.body.date.substring(0, 16) : getCurrentDateTime());
  const [artifactsValueLabel, setArtifactsValueLabel] = useState([]);
  const [modalCreate, setModalCreate] = useState(false);
  const [typeArtifact, setTypeArtifact] = useState("0");
  const [value, setValue] = useState("");
  const [showAlert, setShowAlert] = useState(false);
  const [showErrorMessage, setShowErrorMessage] = useState(false);

  //modal create case
  const [showModalCase, setShowModalCase] = useState(false);
  const [showModalListCase, setShowModalListCase] = useState(false);

  const [priorityFilter, setPriorityFilter] = useState("");
  const [tlpFilter, setTlpFilter] = useState("");
  const [stateFilter, setStateFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [wordToSearch, setWordToSearch] = useState("");
  const [updatePagination, setUpdatePagination] = useState(false);

  const [selectedCases, setSelectedCases] = useState([]);

  const caseItem = {
    lifecycle: "", //required
    priority: "", //required
    tlp: "", //required
    state: "", //required
    date: null, //required
    name: "",
    parent: null,
    assigned: null,
    attend_date: null, //imprime la hora actual +3horas
    solve_date: null,
    comments: [], //?
    evidence: []
  };
  const [selectPriority, setSelectPriority] = useState();
  const [selectTlp, setSelectTlp] = useState();
  const [selectTaxonomy, setSelectTaxonomy] = useState();
  const [selectFeed, setSelectFeed] = useState();
  const [selectCase, setSelectCase] = useState("");
  const [states, setStates] = useState([]); //multiselect
  const [allStates, setAllStates] = useState({}); //multiselect

  const [modalShowCase, setModalShowCase] = useState(false);
  const [caseToLink, setCaseToLink] = useState({});
  const [caseSelectedFromTheList, setCaseSelectedFromTheList] = useState({});
  const [tableDetail, setTableDetail] = useState(false);

  const { t } = useTranslation();

  useEffect(() => {
    // Función para obtener los datos de todas las evidencias
    const fetchAllEvidences = async () => {
      try {
        // Esperar a que todas las promesas de getEvidence se resuelvan
        const responses = await Promise.all(props.body.evidence.map((url) => getEvidence(url)));
        // Extraer los datos de las respuestas
        const data = responses.map((response) => response.data);
        // Actualizar el estado con los datos de todas las evidencias
        props.evidence.forEach((evidence) => {
          if (evidence.url === undefined) {
            data.push(evidence);
          }
        });

        props.setEvidence(data);
      } catch (error) {
        console.error("Error fetching evidence data:", error);
      }
    };

    // Llamar a la función para obtener los datos de las evidencias
    fetchAllEvidences();
  }, [props.body.evidence]);

  useEffect(() => {
    getMinifiedState()
      .then((response) => {
        let list = [];
        let dicState = {};
        response.forEach((stateItem) => {
          list.push({ value: stateItem.url, label: stateItem.name });
          dicState[stateItem.url] = stateItem.name;
        });
        setAllStates(dicState);
        setStates(list);
      })
      .catch((error) => {
        console.log(error);
      });
  }, []);

  useEffect(() => {
    if (
      Object.keys(props.priorityNames).length !== 0 &&
      Object.keys(props.tlpNames).length !== 0 &&
      Object.keys(allStates).length !== 0 &&
      Object.keys(props.userNames).length !== 0 &&
      props.body.case !== null
    ) {
      getCase(props.body.case)
        .then((response) => {
          setCaseToLink({
            value: response.data.url,
            name: response.data.name,
            date: response.data.date,
            priority: props.priorityNames[response.data.priority],
            tlp: response.data.tlp ? props.tlpNames[response.data.tlp].name : "",
            state: allStates[response.data.state],
            user: props.userNames[response.data.user_creator]
          });
        })
        .catch((error) => {
          console.log(error);
        });
    }

    if (props.tlp.length > 0) {
      props.tlp.forEach((item) => {
        if (item.value === props.body.tlp) {
          setSelectTlp({ label: item.label, value: item.value });
        }
      });
    }
    if (props.taxonomy.length > 0) {
      props.taxonomy.forEach((item) => {
        if (item.value === props.body.taxonomy) {
          setSelectTaxonomy({ label: item.label, value: item.value });
        }
      });
    }
    if (props.feeds.length > 0) {
      props.feeds.forEach((item) => {
        if (item.value === props.body.feed) {
          setSelectFeed({ label: item.label, value: item.value });
        }
      });
    }
    if (props.priorities.length > 0) {
      props.priorities.forEach((item) => {
        if (item.value === props.body.priority) {
          setSelectPriority({ label: item.label, value: item.value });
        }
      });
    }
  }, [props.priorityNames, props.tlpNames, props.userNames, allStates]);

  useEffect(() => {
    let listDefaultArtifact = props.listArtifact
      .filter((elemento) => props.body.artifacts.includes(elemento.value))
      .map((elemento) => ({
        value: elemento.value,
        label: elemento.label
      }));

    setArtifactsValueLabel(listDefaultArtifact);
  }, [props.body.artifacts, props.listArtifact]);

  const completeFieldStringIdentifier = (event) => {
    if (event.target.value !== "") {
      postStringIdentifier(event.target.value)
        .then((response) => {
          setShowErrorMessage(response.data.artifact_type === "OTHER" || response.data.artifact_type === "EMAIL");
        })
        .catch((error) => {
          console.log(error);
        })
        .finally(() => { });
    }

    if (event.target.value === "") {
      setShowErrorMessage(false); //para que no aparesca en rojo si esta esta el input vacio en el formulario
    }
    props.setBody({ ...props.body, [event.target.name]: event.target.value });
  };

  const completeField = (event) => {
    props.setBody({
      ...props.body,
      [event.target.name]: event.target.value
    });
  };

  const selectArtefact = (event) => {
    props.setBody({
      ...props.body,
      ["artifacts"]: event.map((e) => {
        return e.value;
      })
    });
  };

  const modalCaseDetail = (url, name, date, priority, tlp, state, user) => {
    localStorage.setItem("case", url);
    setModalShowCase(true);
    setShowModalListCase(false);
    localStorage.setItem("navigation", false);
    localStorage.setItem("button return", false);
    setCaseSelectedFromTheList({
      value: url,
      name: name,
      date: date,
      priority: priority,
      tlp: tlp,
      state: state,
      user: user
    });
  };

  const handleClickRadio = (event, url, name, date, priority, tlp, state, user) => {
    const selectedId = event.target.id;
    if (selectedCases) {
      // Si es radio button, solo debe haber uno seleccionado
      setSelectedCases([selectedId]);
    } else {
      // Si es checkbox, permitir selección múltiple
      setSelectedCases((prevSelected) =>
        prevSelected.includes(selectedId) ? prevSelected.filter((id) => id !== selectedId) : [...prevSelected, selectedId]
      );
    }
    setCaseSelectedFromTheList({
      value: url,
      name: name,
      date: date,
      priority: priority,
      tlp: tlp,
      state: state,
      user: user
    });
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  const createArtifact = () => {
    console.log(value);
    //postArtifact(typeArtifact, Math.floor(value)) por que use un Math.floor(value) no me acuerdo
    postArtifact(typeArtifact, value)
      .then((response) => {
        props.setContactsCreated(response); //
        setModalCreate(false); //
        setTypeArtifact("-1");
        setValue("");
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setModalCreate(false);
      });
  };

  const modalCase = () => {
    //setId
    setShowModalCase(true);
  };

  const modalListCase = () => {
    setUpdatePagination(true);
    setShowModalListCase(true);
  };

  const completeField1 = (nameField, event, setOption) => {
    if (event) {
      props.setBody({
        ...props.body,
        [nameField]: event.value
      });
    } else {
      props.setBody({
        ...props.body,
        [nameField]: ""
      });
    }
    setOption(event);
  };

  const returnToListOfCases = () => {
    setShowModalListCase(true);
    setModalShowCase(false);
    setUpdatePagination(true);
  };

  const linkCaseToEvent = () => {
    completeField1("case", caseSelectedFromTheList, setSelectCase);
    setCaseToLink(caseSelectedFromTheList);
    setShowModalListCase(false);
    setModalShowCase(false);
    setCurrentPage(1);
    setTlpFilter("");
    setPriorityFilter("");
    setStateFilter("");
    setWordToSearch("");
    setUpdatePagination(true);
  };

  function getCurrentDateTime() {
    const now = new Date();
    const year = now.getUTCFullYear();
    const month = (now.getUTCMonth() + 1).toString().padStart(2, "0");
    const day = now.getUTCDate().toString().padStart(2, "0");
    const hours = now.getUTCHours().toString().padStart(2, "0");
    const minutes = now.getUTCMinutes().toString().padStart(2, "0");
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  function closeModal() {
    setShowModalListCase(false);
    setCurrentPage(1);
    setTlpFilter("");
    setPriorityFilter("");
    setStateFilter("");
    setWordToSearch("");
  }

  const tableCaseDetail = (url, name, date, priority, tlp, state, user) => {
    localStorage.setItem("case", url);
    setModalShowCase(true);
    setTableDetail(true);
    localStorage.setItem("navigation", false);
    localStorage.setItem("button return", false);
    setCaseToLink({
      value: url,
      name: name,
      date: date,
      priority: priority,
      tlp: tlp,
      state: state,
      user: user
    });
  };

  const closeModalDetail = () => {
    setModalShowCase(false);
    setTableDetail(false);
  };
  const deleteCaseFromForm = () => {
    setCaseToLink({});
    setSelectedCases([]);
  };

  return (
    <div>
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("menu.principal")}</Card.Title>
        </Card.Header>
        <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />
        <Card.Body>
          <Form>
            <Row>
              <Col sm={12} lg={4}>
                <Form.Group controlId="formGridAddress1">
                  <Form.Label>
                    {t("date.one")}
                    <b style={{ color: "red" }}>*</b>
                  </Form.Label>
                  <Form.Control
                    type="datetime-local"
                    maxLength="150"
                    max={getCurrentDateTime()}
                    value={date}
                    isInvalid={new Date(date) > new Date(getCurrentDateTime())}
                    onChange={(e) => {
                      completeField(e);
                      setDate(e.target.value);
                    }}
                    name="date"
                  />
                  {new Date(date) > new Date(getCurrentDateTime()) ? <div className="invalid-feedback">{t("date.invalid")}</div> : ""}
                </Form.Group>
              </Col>
              <Col sm={12} lg={4}>
                <SelectComponent
                  controlId="exampleForm.ControlSelect1"
                  label={t("ngen.tlp")}
                  options={props.tlp}
                  value={selectTlp}
                  nameField="tlp"
                  onChange={completeField1}
                  placeholder={t("ngen.tlp.select")}
                  setOption={setSelectTlp}
                  required={true}
                />
              </Col>
              <Col sm={12} lg={4}>
                <SelectComponent
                  controlId="exampleForm.ControlSelect1"
                  label={t("ngen.taxonomy_one")}
                  options={props.taxonomy}
                  value={selectTaxonomy}
                  nameField="taxonomy"
                  onChange={completeField1}
                  placeholder={t("ngen.taxonomy.one.select")}
                  setOption={setSelectTaxonomy}
                  required={true}
                />
              </Col>
            </Row>
            <Row>
              <Col sm={12} lg={4}>
                <SelectComponent
                  controlId="exampleForm.ControlSelect1"
                  label={t("ngen.feed.information")}
                  options={props.feeds}
                  value={selectFeed}
                  nameField="feed"
                  onChange={completeField1}
                  placeholder={t("ngen.feed.information.select")}
                  setOption={setSelectFeed}
                  required={true}
                  disabled={props.body.children.length > 0 && props.body.children.length > 0 ? true : false}
                />
              </Col>
              <Col sm={12} lg={4}>
                <SelectComponent
                  controlId="exampleForm.ControlSelect1"
                  label={t("ngen.priority_other")}
                  options={props.priorities}
                  value={selectPriority}
                  nameField="priority"
                  onChange={completeField1}
                  placeholder={t("ngen.priority.select")}
                  setOption={setSelectPriority}
                  required={true}
                />
              </Col>
            </Row>
            <Form.Group controlId="formGridAddress1">
              <Form.Label>{t("notes")}</Form.Label>
              <Form.Control
                placeholder={t("ngen.notes.placeholder")}
                maxLength="150"
                value={props.body.notes}
                onChange={(e) => completeField(e)}
                name="notes"
              />
            </Form.Group>
            <p />
          </Form>
        </Card.Body>
      </Card>
      {props.disableCardArtifacts ? (
        ""
      ) : (
        <Card>
          <Card.Header>
            <Card.Title as="h5">{t("ngen.affectedResources")}</Card.Title>
          </Card.Header>
          <Card.Body>
            <Form.Label>
              {t("cidr.domain.email")}
              <b style={{ color: "red" }}>*</b>
            </Form.Label>
            <Row>
              <Col sm={12} lg={6}>
                <Form.Group controlId="formGridAddress1">
                  <Form.Control
                    placeholder={t("ngen.enter.ipv4.ipv6.domain.email")}
                    maxLength="150"
                    value={props.body.address_value}
                    disabled={props.body.children.length > 0 && props.body.children.length > 0 ? true : false}
                    onChange={(e) => completeFieldStringIdentifier(e)}
                    isInvalid={showErrorMessage}
                    name="address_value"
                  />
                  {showErrorMessage ? <div className="invalid-feedback"> {t("error.ipv4.ipv6.domain.email")}</div> : ""}
                </Form.Group>
              </Col>
            </Row>
          </Card.Body>
        </Card>
      )}
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("ngen.artifact_other")}</Card.Title>
        </Card.Header>
        <Card.Body>
          <Form>
            <Form.Group controlId="formGridAddress1">
              <Row>
                <Col sm={12} lg={9}>
                  <Select
                    placeholder={t("ngen.artifact_other_select")}
                    closeMenuOnSelect={false}
                    components={animatedComponents}
                    isMulti
                    value={artifactsValueLabel}
                    onChange={selectArtefact}
                    options={props.listArtifact}
                  />
                </Col>
                <Col sm={12} lg={3}>
                  <CrudButton type="create" name={t("ngen.artifact_one")} onClick={() => setModalCreate(true)} />
                </Col>
              </Row>
            </Form.Group>
          </Form>
        </Card.Body>
      </Card>
      {props.disableCardCase ? (
        ""
      ) : (
        <SmallCaseTable
          readCase={caseToLink.value}
          modalCaseDetail={tableCaseDetail}
          disableLink={true}
          modalCase={modalCase}
          modalListCase={modalListCase}
          deleteCaseFromForm={deleteCaseFromForm}
        />
      )}

      <ModalCreateCase
        showModalCase={showModalCase}
        setShowModalCase={setShowModalCase}
        caseItem={caseItem}
        states={states}
        setCaseToLink={setCaseToLink}
        setSelectCase={setSelectCase}
        selectCase={selectCase}
        completeField1={completeField1}
        stateNames={allStates}
      />

      <ModalListCase
        stateNames={allStates}
        showModalListCase={showModalListCase}
        modalCaseDetail={modalCaseDetail}
        closeModal={closeModal}
        selectedCases={selectedCases}
        priorityNames={props.priorityNames}
        tlpNames={props.tlpNames}
        userNames={props.userNames}
        handleClickRadio={handleClickRadio}
        linkCaseToEvent={linkCaseToEvent}
        completeField1={completeField1}
        caseToLink={caseToLink}
        setSelectCase={setSelectCase}
        selectCase={selectCase}
        setShowModalListCase={setShowModalListCase}
        priorities={props.priorities}
        tlp={props.tlp}
        allStates={states}
        priorityFilter={priorityFilter}
        setPriorityFilter={setPriorityFilter}
        tlpFilter={tlpFilter}
        setTlpFilter={setTlpFilter}
        stateFilter={stateFilter}
        setStateFilter={setStateFilter}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        wordToSearch={wordToSearch}
        setWordToSearch={setWordToSearch}
        updatePagination={updatePagination}
        setUpdatePagination={setUpdatePagination}
        asNetworkAdmin={props.asNetworkAdmin}
      />

      <ModalReadCase
        modalShowCase={modalShowCase}
        tableDetail={tableDetail}
        closeModalDetail={closeModalDetail}
        returnToListOfCases={returnToListOfCases}
        linkCaseToEvent={linkCaseToEvent}
      />

      {props.disableCardEvidence ? (
        ""
      ) : (
        <EvidenceCard
          evidences={props.evidence}
          setEvidences={props.setEvidence}
          setUpdateCase={props.setUpdateEvidence}
          updateCase={props.updateEvidence}
        />
      )}

      <CreateArtifactModal
        show={modalCreate}
        onHide={() => setModalCreate(false)}
        value={value}
        setValue={setValue}
        typeArtifact={typeArtifact}
        setTypeArtifact={setTypeArtifact}
        createArtifact={createArtifact}
      />

      {props.body.tlp !== "" &&
        props.body.taxonomy !== "" &&
        props.body.feed !== "" &&
        props.body.priority !== "" &&
        props.body.address_value !== "" &&
        !showErrorMessage ? (
        <Button variant="primary" onClick={props.createEvent}>
          {t("button.save")}
        </Button>
      ) : (
        <Button variant="primary" disabled>
          {t("button.save")}
        </Button>
      )}
      <CrudButton type="cancel" />
    </div>
  );
};

export default FormEvent;
