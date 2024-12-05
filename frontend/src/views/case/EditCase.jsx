import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getCase } from "../../api/services/cases";
import FormCase from "./components/FormCase";
import { getState } from "../../api/services/states";
import { getMinifiedTag } from "../../api/services/tags";
import { useTranslation } from "react-i18next";
import { COMPONENT_URL } from "config/constant";

const EditCase = ({asNetworkAdmin}) => {
  const { t } = useTranslation();

  const [caseItem, setCaseItem] = useState(null);

  //multiselect
  const [allStates, setSupportedStates] = useState([]);
  const [updateCase, setUpdateCase] = useState([]);
  const [id] = useState(useParams());
  const [listTag, setListTag] = useState([]);

  useEffect(() => {
    if (id.id) {
      getCase(COMPONENT_URL.case + id.id + "/")
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
          asNetworkAdmin={asNetworkAdmin}
        />
      </React.Fragment>
    )
  );
};

export default EditCase;
