import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import FormState from "./components/FormState";
import { putState, getState, getMinifiedState } from "../../api/services/states";
import ListEdge from "../edge/ListEdge";
import { useTranslation } from "react-i18next";
import { COMPONENT_URL } from "../../config/constant";

const EditState = () => {
  const [body, setBody] = useState({});

  const [states, setStates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAlert, setShowAlert] = useState(false);
  const [id, setId] = useState(useParams());
  const { t } = useTranslation();

  const [sectionAddEdge, setSectionAddEdge] = useState(false);

  useEffect(() => {
    if (body.children && body.children.length > 0) {
      setSectionAddEdge(true);
    }
  }, [body]);

  useEffect(() => {
    if (body.url) {
      getMinifiedState()
        .then((response) => {
          var listChildren = [];
          response.map((state) => {
            console.log(body.url);
            if (state.url !== body.url) {
              listChildren.push({ value: state.url, label: state.name });
            }
          });
          setStates(listChildren);
        })
        .catch((error) => {
          console.log(error);
        });
    }
  }, [body]);

  useEffect(() => {
    if (id) {
      getState(COMPONENT_URL.state + id.id + "/")
        .then((response) => {
          setBody(response.data);
        })
        .catch((error) => {
          console.log(error);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [id]);

  const editState = () => {
    putState(body.url, body.name, body.attended, body.solved, body.active, body.description, body.children)
      .then(() => {
        window.location.href = "/states";
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      });
  };
  return (
    <div>
      <FormState body={body} setBody={setBody} createState={editState} childernes={states} type={t("w.edit")} loading={loading} />
      <ListEdge url={body.url} sectionAddEdge={sectionAddEdge} setShowAlert={setShowAlert} loading={loading} />
    </div>
  );
};
export default EditState;
