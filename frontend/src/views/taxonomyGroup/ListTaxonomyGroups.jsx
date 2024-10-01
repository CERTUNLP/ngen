import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { Link } from "react-router-dom";
import CrudButton from "../../components/Button/CrudButton";
import Alert from "../../components/Alert/Alert";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import Search from "../../components/Search/Search";
import TableTaxonomyGroup from "./components/TableTaxonomyGroup";
import { useTranslation } from "react-i18next";
import { getMinifiedTaxonomyGroups, getTaxonomyGroups } from "../../api/services/taxonomyGroups";

const listTaxonomyGroups = () => {
  const [taxonomyGroups, setTaxonomyGroups] = useState([]);
  const [isModify, setIsModify] = useState(null);
  const [loading, setLoading] = useState(true);
  const { t } = useTranslation();

  const [showAlert, setShowAlert] = useState(false);

  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const [wordToSearch, setWordToSearch] = useState("");

  const [order, setOrder] = useState("name");

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    getTaxonomyGroups(currentPage, wordToSearch, order)
      .then((response) => {
        setCountItems(response.data.count);
        setTaxonomyGroups(response.data.results);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {
        //alert
        console.log(error);
      })
      .finally(() => {
        setShowAlert(true);
        setLoading(false);
      });

  }, [currentPage, isModify, order, wordToSearch]);

  return (
    <React.Fragment>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm={12} lg={9}>
                  <Search
                    type={t("search.by.name")}
                    setWordToSearch={setWordToSearch}
                    wordToSearch={wordToSearch}
                    setLoading={setLoading}
                  />
                </Col>

                <Col sm={12} lg={3}>
                  <CrudButton type="create" name={t("ngen.taxonomyGroup_one")} to="/taxonomyGroups/create" checkPermRoute />
                </Col>
              </Row>
            </Card.Header>
            <Card.Body>
              <TableTaxonomyGroup
                setIsModify={setIsModify}
                list={taxonomyGroups}
                loading={loading}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
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

export default listTaxonomyGroups;
