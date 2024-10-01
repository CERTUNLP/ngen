import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { getCase } from "../../api/services/cases";
import FormCase from "./components/FormCase";
import { getState } from "../../api/services/states";
import { useTranslation } from "react-i18next";

const EditCase = ({asNetworkAdmin}) => {
  const { t } = useTranslation();
  const location = useLocation();
  const fromState = location.state;
  const [url] = useState(fromState);

  const [caseItem, setCaseItem] = useState(null);

  //multiselect
  const [allStates, setSupportedStates] = useState([]);
  const [updateCase, setUpdateCase] = useState([]);

  useEffect(() => {
    getCase(url)
      .then((response) => {
        setCaseItem(response.data);
      })
      .catch((error) => {});
  }, [updateCase]);

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
  }, [caseItem]);

  return (
    caseItem && (
      <React.Fragment>
        <FormCase
          caseItem={caseItem}
          allStates={allStates}
          edit={true}
          save={t("button.save_changes")}
          evidenceColum={true}
          buttonsModalColum={true}
          setUpdateCase={setUpdateCase}
          updateCase={updateCase}
          asNetworkAdmin={true}
        />
      </React.Fragment>
    )
  );
};

export default EditCase;
