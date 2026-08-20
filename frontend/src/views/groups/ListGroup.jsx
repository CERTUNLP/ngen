import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { getGroups } from "../../api/services/groups";
import CrudButton from "../../components/Button/CrudButton";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import TableGroup from "./components/TableGroup";
import ListViewHeader from "../../components/ListViewHeader/ListViewHeader";
import { useTranslation } from "react-i18next";

const ListGroup = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [isModify, setIsModify] = useState(null);
  const [order, setOrder] = useState("name");
  const [wordToSearch, setWordToSearch] = useState("");
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const [refresh, setRefresh] = useState(true);
  const { t } = useTranslation();

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  const reloadPage = () => {
    setLoading(true);
    setRefresh((prev) => !prev);
  };

  const clearFilters = () => {
    setLoading(true);
    setWordToSearch("");
    setCurrentPage(1);
    setRefresh((prev) => !prev);
  };

  useEffect(() => {
    getGroups(currentPage, wordToSearch, order)
      .then((response) => {
        setGroups(response.data.results);
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
        setLoading(false);
      });
  }, [currentPage, wordToSearch, order, isModify, refresh]);

  return (
    <React.Fragment>
      <Row>
        <Col sm="auto">
          <Card>
            <Card.Header>
              <ListViewHeader
                searchType={t("search.by.name.description")}
                wordToSearch={wordToSearch}
                setWordToSearch={setWordToSearch}
                setLoading={setLoading}
                setCurrentPage={setCurrentPage}
                onReload={reloadPage}
                onClearFilters={clearFilters}
              >
                <CrudButton type="create" name={t("w.groups")} to="/groups/create" checkPermRoute />
              </ListViewHeader>
            </Card.Header>
            <TableGroup
              groups={groups}
              loading={loading}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              currentPage={currentPage}
              setIsModify={setIsModify}
            />
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

export default ListGroup;
