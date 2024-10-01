import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { getFeeds } from "../../api/services/feeds";
import CrudButton from "../../components/Button/CrudButton";
import Alert from "../../components/Alert/Alert";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import TableFeed from "./components/TableFeed";
import Search from "../../components/Search/Search";
import { useTranslation } from "react-i18next";

const ListFeed = () => {
  const [feeds, setFeeds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAlert, setShowAlert] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);

  const [order, setOrder] = useState("name");
  const [wordToSearch, setWordToSearch] = useState("");

  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const { t } = useTranslation();

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  //ORDER

  useEffect(() => {
    getFeeds(currentPage, wordToSearch, order)
      .then((response) => {
        setFeeds(response.data.results);
        setLoading(false);
        //PAGINATION
        setCountItems(response.data.count);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {
        console.log(error);
        setShowAlert(true);
      })
      .finally(() => {
        setLoading(false);
        setShowAlert(true);
      });
  }, [currentPage, wordToSearch, order]);

  return (
    <React.Fragment>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm={12} lg={9}>
                  <Search
                    type={t("search.by.name.description")}
                    setWordToSearch={setWordToSearch}
                    wordToSearch={wordToSearch}
                    setLoading={setLoading}
                  />
                </Col>
                <Col sm={12} lg={3}>
                  <CrudButton type="create" name={t("ngen.feed")} to="/feeds/create" checkPermRoute />
                </Col>
              </Row>
            </Card.Header>
            <TableFeed
              feeds={feeds}
              loading={loading}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              currentPage={currentPage}
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

export default ListFeed;
