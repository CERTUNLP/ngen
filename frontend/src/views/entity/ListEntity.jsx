import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import CrudButton from "../../components/Button/CrudButton";
import TableEntity from "./components/TableEntity";
import { getEntities } from "../../api/services/entities";
import Search from "../../components/Search/Search";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import Alert from "../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const ListEntity = ({ routeParams }) => {
  const [entities, setEntities] = useState([]);
  const [isModify, setIsModify] = useState(null);

  const [loading, setLoading] = useState(true);

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  //AdvancedPagination
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);

  const [wordToSearch, setWordToSearch] = useState("");
  const [order, setOrder] = useState("name");
  const { t } = useTranslation();

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    getEntities(currentPage, wordToSearch, order, routeParams.asNetworkAdmin)
      .then((response) => {
        setEntities(response.data.results);
        // Pagination
        setCountItems(response.data.count);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {
        // Show alert
      })
      .finally(() => {
        setShowAlert(true);
        setLoading(false);
      });
  }, [currentPage, isModify, wordToSearch, order]);

  return (
    <React.Fragment>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm={12} lg={9}>
                  <Search
                    type={t("w.entityByName")}
                    setWordToSearch={setWordToSearch}
                    wordToSearch={wordToSearch}
                    setLoading={setLoading}
                    setCurrentPage={setCurrentPage}
                  />
                </Col>
                <Col sm={12} lg={3}>
                  <CrudButton type="create" name={t("ngen.entity")} to="/entities/create" checkPermRoute />
                </Col>
              </Row>
            </Card.Header>
            <Card.Body>
              <TableEntity
                setIsModify={setIsModify}
                list={entities}
                loading={loading}
                setLoading={setLoading}
                currentPage={currentPage}
                order={order}
                setOrder={setOrder}
                asNetworkAdmin={routeParams.asNetworkAdmin}
                basePath={routeParams.basePath}
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
    </React.Fragment>
  );
};

export default ListEntity;
