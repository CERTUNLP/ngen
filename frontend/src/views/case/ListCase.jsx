import React, { useEffect, useState } from "react";
import { Badge, Button, Card, Col, Collapse, Row } from "react-bootstrap";
import CrudButton from "../../components/Button/CrudButton";
import TableCase from "./components/TableCase";
import { getCases, mergeCase } from "../../api/services/cases";
import { getMinifiedPriority } from "../../api/services/priorities";
import { getMinifiedTlp } from "../../api/services/tlp";
import { getMinifiedUser } from "../../api/services/users";
import { getMinifiedState } from "../../api/services/states";
import Search from "../../components/Search/Search";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import ModalConfirm from "../../components/Modal/ModalConfirm";
import Alert from "../../components/Alert/Alert";
import FilterToolbar from "../../components/Button/FilterToolbar";
import FilterSelectUrl from "../../components/Filter/FilterSelectUrl";
import FilterSelect from "../../components/Filter/FilterSelect";
import { useTranslation } from "react-i18next";
import PermissionCheck from "../../components/Auth/PermissionCheck";

const ListCase = ({ routeParams }) => {
  const basePath = routeParams.basePath ? routeParams.basePath : "";

  const [cases, setCases] = useState([]); //lista de casos
  const [ifModify, setIfModify] = useState(null);
  const [loading, setLoading] = useState(true);

  //merge
  const [selectedCases, setSelectedCases] = useState([]);
  const [showModal, setShowModal] = useState(false);

  //Alert
  const [showAlert, setShowAlert] = useState(false);
  //Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  //filters
  const [order, setOrder] = useState("-modified");
  const [wordToSearch, setWordToSearch] = useState("");
  const [open, setOpen] = useState(false);

  const [priorities, setPriorities] = useState([]);
  const [priorityFilter, setPriorityFilter] = useState("");
  const [valuePriorityFilter, setValuePriorityFilter] = useState(null);

  const [tlpFilter, setTlpFilter] = useState("");
  const [tlps, setTlps] = useState([]);
  const [valueTlpFilter, setValueTlpFilter] = useState(null);

  const [states, setStates] = useState([]);
  const [stateFilter, setStateFilter] = useState("");

  //url by name
  const [priorityNames, setPriorityNames] = useState({});
  const [tlpNames, setTlpNames] = useState({});
  const [stateNames, setStateNames] = useState({});
  const [userNames, setUserNames] = useState({});

  const [refresh, setRefresh] = useState(true);

  const { t } = useTranslation();

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  //ORDER
  useEffect(() => {
    getMinifiedUser()
      .then((response) => {
        let dicUser = {};
        response.forEach((user) => {
          dicUser[user.url] = user.username;
        });
        setUserNames(dicUser);
      })
      .catch((error) => {
        console.log(error);
      });

    getMinifiedState()
      .then((response) => {
        let stateOp = [];
        let dicState = {};
        response.forEach((state) => {
          stateOp.push({ value: state.url, label: state.name });
          dicState[state.url] = state.name;
        });
        setStateNames(dicState);
        setStates(stateOp);
      })
      .catch((error) => {
        console.log(error);
      });

    getMinifiedPriority()
      .then((response) => {
        let priorityOp = [];
        let dicPriority = {};
        response.forEach((priority) => {
          priorityOp.push({ value: priority.url, label: priority.name });
          dicPriority[priority.url] = priority.name;
        });
        setPriorityNames(dicPriority);
        setPriorities(priorityOp);
      })
      .catch((error) => {
        console.log(error);
      });

    getMinifiedTlp()
      .then((response) => {
        let list = [];
        let dicTlp = {};
        response.forEach((tlp) => {
          list.push({ value: tlp.url, label: tlp.name });
          dicTlp[tlp.url] = { name: tlp.name, color: tlp.color };
        });
        setTlpNames(dicTlp);
        setTlps(list);
      })
      .catch((error) => {
        console.log(error);
      });
    //getCases(currentPage,priorityFilter+tlpFilter+stateFilter+wordToSearch, order)
    getCases(currentPage, priorityFilter + tlpFilter + stateFilter + wordToSearch, order, routeParams.asNetworkAdmin)
      .then((response) => {
        setCases(response.data.results);
        setCountItems(response.data.count);
        // Pagination
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {})
      .finally(() => {
        setShowAlert(true);
        setLoading(false);
      });
  }, [currentPage, ifModify, order, wordToSearch, priorityFilter, tlpFilter, stateFilter, refresh]);

  const mergeConfirm = () => {
    setShowModal(true);
  };

  const merge = () => {
    const parent = selectedCases.shift();
    selectedCases.forEach((child) => {
      mergeCase(parent, child)
        .then((response) => setIfModify(response))
        .catch((error) => console.log(error))
        .finally(() => {
          setSelectedCases([]);
          setShowModal(false);
        });
    });
  };

  const reloadPage = () => {
    setLoading(true);
    setRefresh((prev) => !prev);
  };

  const clearFilters = () => {
    setLoading(true);
    setWordToSearch("");
    setPriorityFilter("");
    setValuePriorityFilter(null);
    setTlpFilter("");
    setValueTlpFilter(null);
    setStateFilter("");
    setValueStateFilter(null);
    setCurrentPage(1);
    setRefresh((prev) => !prev);
  };

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="case" />
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm="auto">
                  <FilterToolbar open={open} setOpen={setOpen} onReload={reloadPage} onClearFilters={clearFilters} />
                </Col>
                <Col sm={1} lg={6}>
                  <Search type={t("ngen.case_one")} setWordToSearch={setWordToSearch} wordToSearch={wordToSearch} setLoading={setLoading} setCurrentPage={setCurrentPage} />
                </Col>
                <Col>
                  <CrudButton type="create" name={t("ngen.case_one")} to={basePath + "/cases/create"} checkPermRoute />

                  <PermissionCheck optionalPermissions={["change_case", "change_case_network_admin"]}>
                    <Button
                      disabled={selectedCases.length <= 1}
                      size="lm"
                      className="text-capitalize"
                      variant={selectedCases.length > 0 ? "outline-dark" : "outline-secondary"}
                      title="Merge"
                      onClick={() => mergeConfirm()}
                    >
                      <i className="fa fa-code-branch" />
                      { t("ngen.merge") }&nbsp;
                      <Badge className="badge mr-1" bg={selectedCases.length > 0 ? "primary" : "secondary"}>{selectedCases.length}</Badge>
                    </Button>
                  </PermissionCheck>
                </Col>
              </Row>
              <Row></Row>
              <br />
              <Collapse in={open}>
                <div id="example-collapse-text">
                  <Row>
                    <Col sm={4} lg={4}>
                      <FilterSelectUrl
                        options={priorities}
                        itemName={t("ngen.priority_one")}
                        partOfTheUrl="priority"
                        itemFilter={priorityFilter}
                        itemFilterSetter={setPriorityFilter}
                        value={valuePriorityFilter}
                        setValue={setValuePriorityFilter}
                        setLoading={setLoading}
                        setCurrentPage={setCurrentPage}
                      />
                    </Col>
                    <Col sm={4} lg={4}>
                      <FilterSelectUrl
                        options={tlps}
                        itemName={t("ngen.tlp")}
                        partOfTheUrl="tlp"
                        itemFilter={tlpFilter}
                        itemFilterSetter={setTlpFilter}
                        value={valueTlpFilter}
                        setValue={setValueTlpFilter}
                        setLoading={setLoading}
                        setCurrentPage={setCurrentPage}
                      />
                    </Col>
                    <Col sm={4} lg={4}>
                      <FilterSelectUrl
                        options={states}
                        itemName={t("ngen.state_one")}
                        partOfTheUrl="state"
                        itemFilter={stateFilter}
                        itemFilterSetter={setStateFilter}
                        setLoading={setLoading}
                        setCurrentPage={setCurrentPage}
                      />
                    </Col>
                  </Row>
                  <br />
                </div>
              </Collapse>
            </Card.Header>
            <Card.Body>
              <TableCase
                cases={cases}
                loading={loading}
                selectedCases={selectedCases}
                setSelectedCases={setSelectedCases}
                order={order}
                setOrder={setOrder}
                setIfModify={setIfModify}
                setLoading={setLoading}
                priorityNames={priorityNames}
                stateNames={stateNames}
                tlpNames={tlpNames}
                userNames={userNames}
                editColum={true}
                deleteColum={true}
                navigationRow={true}
                buttonReturn={false}
                disableNubersOfEvents={true}
                disableDateModified={false}
                basePath={basePath}
              />
            </Card.Body>
            <Card.Footer>
              <Row className="justify-content-md-center">
                <Col md="auto">
                  <AdvancedPagination
                    countItems={countItems}
                    updatePage={updatePage}
                    updatePagination={updatePagination}
                    setUpdatePagination={setUpdatePagination}
                    setLoading={setLoading}
                    setDisabledPagination={setDisabledPagination}
                    disabledPagination={disabledPagination}
                  />
                </Col>
              </Row>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
      <ModalConfirm
        type="merge"
        component={t("ngen.case_other")}
        name={selectedCases}
        showModal={showModal}
        onHide={() => setShowModal(false)}
        ifConfirm={() => merge()}
      />
    </React.Fragment>
  );
};

export default ListCase;
