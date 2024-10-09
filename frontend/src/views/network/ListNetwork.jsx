import React, { useEffect, useState } from "react";
import { Card, Col, Collapse, Row } from "react-bootstrap";
import CrudButton from "../../components/Button/CrudButton";
import { getNetworks } from "../../api/services/networks";
import { getMinifiedEntity } from "../../api/services/entities";
import TableNetwork from "./components/TableNetwork";
import Search from "../../components/Search/Search";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import Alert from "../../components/Alert/Alert";
import ButtonFilter from "../../components/Button/ButtonFilter";
import FilterSelectUrl from "../../components/Filter/FilterSelectUrl";
import FilterSelect from "../../components/Filter/FilterSelect";
import { useTranslation } from "react-i18next";

const ListNetwork = ({ routeParams }) => {
  const { t } = useTranslation();

  const [network, setNetwork] = useState([]);
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
  const [open, setOpen] = useState(false);
  const [typeFilter, setTypeFilter] = useState("");
  const [entitiesFilter, setEntitiesFilter] = useState("");
  const [order, setOrder] = useState("network_entity__name");

  const [entityNames, setEntityNames] = useState({});

  const types = [
    { value: "internal", label: t("ngen.network.type.internal") },
    { value: "external", label: t("ngen.network.type.external") }
  ];

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  //Hay que ver si mejora el redimiento
  useEffect(() => {
    getMinifiedEntity()
      .then((response) => {
        let listEntities = [];
        let dicEntities = {};
        response.forEach((entitiesItem) => {
          listEntities.push({ value: entitiesItem.url, label: entitiesItem.name });
          dicEntities[entitiesItem.url] = entitiesItem.name;
        });
        setEntities(listEntities);
        setEntityNames(dicEntities);
      })
      .catch((error) => {
        // Manejo de errores si es necesario
      });
  }, []);

  useEffect(() => {
    getNetworks(currentPage, entitiesFilter + typeFilter + wordToSearch, order, routeParams.asNetworkAdmin)
      .then((response) => {
        setNetwork(response.data.results);
        // Paginación
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
  }, [currentPage, isModify, wordToSearch, entitiesFilter, typeFilter, order]);

  return (
    <React.Fragment>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm={1} lg={1}>
                  <ButtonFilter open={open} setOpen={setOpen} />
                </Col>
                <Col sm={12} lg={8}>
                  <Search
                    type={t("filter.cidr_domain")}
                    setWordToSearch={setWordToSearch}
                    wordToSearch={wordToSearch}
                    setLoading={setLoading}
                    setCurrentPage={setCurrentPage}
                  />
                </Col>
                <Col sm={12} lg={3}>
                  <CrudButton type="create" name={t("ngen.network_one")} to="/networks/create" checkPermRoute />
                </Col>
              </Row>
              <br />
              <Collapse in={open}>
                <div id="example-collapse-text">
                  <Row>
                    <Col sm={4} lg={4}>
                      <FilterSelectUrl
                        options={entities}
                        itemName={t("ngen.entity_other")}
                        partOfTheUrl="network_entity"
                        itemFilter={entitiesFilter}
                        itemFilterSetter={setEntitiesFilter}
                        setLoading={setLoading}
                        setCurrentPage={setCurrentPage}
                      />
                    </Col>
                    <Col sm={4} lg={4}>
                      <FilterSelect
                        options={types}
                        partOfTheUrl="type"
                        setFilter={setTypeFilter}
                        currentFilter={typeFilter}
                        setLoading={setLoading}
                        placeholder={t("ngen.filter_by") + " " + t("ngen.type")}
                      />
                    </Col>
                  </Row>
                  <br />
                </div>
              </Collapse>
            </Card.Header>
            <Card.Body>
              <TableNetwork
                setIsModify={setIsModify}
                list={network}
                loading={loading}
                currentPage={currentPage}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                entityNames={entityNames}
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
export default ListNetwork;
