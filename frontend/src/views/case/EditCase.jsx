import React, { useEffect, useState } from "react";
import { Col, Row } from "react-bootstrap";
import { useParams } from "react-router-dom";
import CrudButton from "components/Button/CrudButton";
import { getCase } from "api/services/cases";
import FormCase from "./components/FormCase";
import { getState } from "api/services/states";
import { getMinifiedTag } from "api/services/tags";
import { useTranslation } from "react-i18next";
import { COMPONENT_URL } from "config/constant";

const EditCase = ({ routeParams }) => {
  const basePath = routeParams?.basePath || "";
  const { t } = useTranslation();

  const [caseItem, setCaseItem] = useState(null);

  //multiselect
  const [allStates, setSupportedStates] = useState([]);
  const [updateCase, setUpdateCase] = useState([]);
  const [id] = useState(useParams().id);
  const [listTag, setListTag] = useState([]);

  useEffect(() => {
    if (id) {
      getCase(COMPONENT_URL.case + id + "/")
        .then((response) => {
          setCaseItem(response.data);
        })
        .catch((error) => console.log(error));
    }
  }, [id]);

  useEffect(() => {
    let listStates = [];
    if (caseItem) {
      getState(caseItem.state)
        .then((response) => {
          listStates.push({ value: response.data.url, label: response.data.name });
          let children = response.data.children;
          children.forEach((child) => {
            getState(child)
              .then((responseChild) => {
                listStates.push({ value: responseChild.data.url, label: responseChild.data.name });
              })
              .catch((error) => {
                console.log(error);
              });
          });
          setSupportedStates(listStates);
        })
        .catch((error) => {
          console.log(error);
        });
    }
    
    getMinifiedTag()
      .then((response) => {
        var list = response.map((tag) => {
          return { url: tag.url, name: tag.name, color: tag.color, slug: tag.slug, value: tag.name, label: tag.name };
        });
        setListTag(list);
      })
      .catch((error) => {
        console.log(error);
      });
  }, [caseItem]);

  return (
    caseItem && (
      <React.Fragment>
        <Row>
          <Col>
            <h1 className="h3 mb-4 text-gray-800">{t("ngen.case_one")} {caseItem.uuid}</h1>
          </Col>
          <Col className="text-right" style={{ textAlign: 'right' }}>
            <CrudButton type="read" to={`${basePath}/cases/view/${id}`} checkPermRoute />
          </Col>
        </Row>
        <FormCase
          caseItem={caseItem}
          allStates={allStates}
          listTag={listTag}
          edit={true}
          save={t("button.save_changes")}
          evidenceColum={true}
          buttonsModalColum={true}
          setUpdateCase={setUpdateCase}
          updateCase={updateCase}
          asNetworkAdmin={routeParams.asNetworkAdmin}
        />
      </React.Fragment>
    )
  );
};

export default EditCase;
