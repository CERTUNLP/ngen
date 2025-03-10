import React, { useEffect, useState } from "react";
import { getStates } from "../../api/services/states";
import { Card, Col, Row } from "react-bootstrap";
import Search from "../../components/Search/Search";
import CrudButton from "../../components/Button/CrudButton";
import TableStates from "./components/TableStates";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import Alert from "../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const ListState = () => {
  const [loading, setLoading] = useState(true);
  const [states, setStates] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const [isModify, setIsModify] = useState(null);
  const { t } = useTranslation();

  const [wordToSearch, setWordToSearch] = useState("");
  const [order] = useState("");

  const [showAlert, setShowAlert] = useState(false);

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    getStates(currentPage, wordToSearch, order)
      .then((response) => {
        setStates(response.data.results);
        setCountItems(response.data.count);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setShowAlert(true);
        setLoading(false);
      });
  }, [currentPage, wordToSearch, order, isModify]);

  return (
    <div>
      <Card>
        <Card.Header>
          <Row>
            <Col sm={12} lg={9}>
              <Search
                type={t("ngen.state_one")}
                setWordToSearch={setWordToSearch}
                wordToSearch={wordToSearch}
                setLoading={setLoading}
                setCurrentPage={setCurrentPage}
              />
            </Col>
            <Col sm={12} lg={3}>
              <CrudButton type="create" name={t("ngen.state_one")} to="/states/create" state={states} checkPermRoute />
            </Col>
          </Row>
        </Card.Header>
        <Card.Body>
          <TableStates states={states} loading={loading} currentPage={currentPage} setIsModify={setIsModify} />
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
    </div>
  );
};

export default ListState;
