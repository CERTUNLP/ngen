import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import TableContact from "./components/TableContact";
import ListViewHeader from "../../components/ListViewHeader/ListViewHeader";
import CrudButton from "../../components/Button/CrudButton";
import { getContacts } from "../../api/services/contacts";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import Alert from "../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const ListContact = ({ routeParams }) => {
  const { t } = useTranslation();
  const [contacts, setContacts] = useState([]);
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
  const [refresh, setRefresh] = useState(true);

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
    setCurrentPage(currentPage); //?

    getContacts(currentPage, wordToSearch, order, routeParams.asNetworkAdmin)
      .then((response) => {
        setContacts(response.data.results);
        //Pagination
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
  }, [currentPage, isModify, wordToSearch, order, refresh]);

  // ------- SEARCH --------
  //filtro
  // let show = []
  // if (!search) {
  //   show = contacts
  // } else {
  //   show = contacts.filter((item) =>
  //     item.name.toLowerCase().includes(search.toLocaleLowerCase())
  //   )
  // }

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="contact" />
      <Row>
        <Col sm="auto">
          <Card>
            <Card.Header>
              <ListViewHeader
                searchType={t("w.entityByName")}
                wordToSearch={wordToSearch}
                setWordToSearch={setWordToSearch}
                setLoading={setLoading}
                setCurrentPage={setCurrentPage}
                onReload={reloadPage}
                onClearFilters={clearFilters}
              >
                <CrudButton type="create" name={t("ngen.contact_one")} to="/contacts/create" checkPermRoute />
              </ListViewHeader>
            </Card.Header>
            <Card.Body>
              <TableContact
                setIsModify={setIsModify}
                list={contacts}
                loading={loading}
                currentPage={currentPage}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
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
export default ListContact;
