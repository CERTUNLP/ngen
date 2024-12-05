import React, { useEffect, useState } from "react";
import FormCase from "./components/FormCase";
import { getAllStates } from "../../api/services/states";
import { getMinifiedTag } from "../../api/services/tags";
import { useTranslation } from "react-i18next";

const CreateCase = ({ routeParams }) => {
  const [allStates, setAllStates] = useState([]); //multiselect
  const [stateName, setStatesName] = useState([]);
  const [listTag, setListTag] = useState([]);

  const caseItem = {
    lifecycle: "", //required
    priority: "", //required
    tlp: "", //required
    state: "", //required
    date: null, //required
    name: "",
    parent: null,
    assigned: null,
    attend_date: null, //imprime la hora actual +3horas
    solve_date: null,
    comments: [], //?
    evidence: [],
    events: [],
    tags: []
  };

  useEffect(() => {
    getAllStates()
      .then((response) => {
        let listStates = [];
        let dicState = {};
        response.forEach((stateItem) => {
          listStates.push({
            value: stateItem.url,
            label: stateItem.name,
            childrenUrl: stateItem.children
          });
          dicState[stateItem.url] = stateItem.name;
        });
        setStatesName(dicState);
        setAllStates(listStates);
      })
      .catch((error) => {
        console.log(error);
      });
    
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
  }, []);

  const { t } = useTranslation();

  return (
    <React.Fragment>
      <FormCase
        caseItem={caseItem}
        allStates={allStates}
        edit={false}
        listTag={listTag}
        save={t("button.case_create")}
        evidenceColum={true}
        stateName={stateName}
        setStatesName={setStatesName}

        buttonsModalColum={true}
        asNetworkAdmin={routeParams.asNetworkAdmin}
      />
    </React.Fragment>
  );
};

export default CreateCase;
