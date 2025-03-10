import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { postPlaybook, putPlaybook } from "../../api/services/playbooks";
import FormCreatePlaybook from "../playbook/components/FormCreatePlaybook";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import ListTask from "../task/ListTask";
import { useTranslation } from "react-i18next";
import CrudButton from "components/Button/CrudButton";

const CreatePlaybook = () => {
  const [url, setUrl] = useState("");
  const [name, setName] = useState("");
  const [taxonomy, setTaxonomy] = useState([]);
  const { t } = useTranslation();

  //Renderizar
  const [allTaxonomies, setAllTaxonomies] = useState([]); //lista con formato para multiselect value, label

  //Collapse
  const [sectionAddTask, setSectionAddTask] = useState(false);

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    getMinifiedTaxonomy().then((response) => {
      let listTaxonomies = [];
      response.map((taxonomyItem) => {
        listTaxonomies.push({
          value: taxonomyItem.url,
          label: taxonomyItem.name + " (" + labelTaxonomy[taxonomyItem.type] + ")"
        });
      });
      setAllTaxonomies(listTaxonomies);
    });
  }, [sectionAddTask]);

  const createPlaybook = () => {
    postPlaybook(name, taxonomy)
      .then((response) => {
        setUrl(response.data.url); // y la url
        setSectionAddTask(true);
      })
      .catch()
      .finally(() => {
        setShowAlert(true);
      });
  };

  const editPlaybook = () => {
    putPlaybook(url, name, taxonomy)
      .then()
      .catch()
      .finally(() => {
        setShowAlert(true);
      });
  };

  const labelTaxonomy = {
    vulnerability: "Vulnerabilidad",
    incident: "Incidente"
  };

  return (
    <React.Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.playbook")}</Card.Title>
              <span className="d-block m-t-5">{t("ngen.playbook.add")}</span>
            </Card.Header>
            <Card.Body>
              <FormCreatePlaybook
                name={name}
                setName={setName}
                taxonomy={taxonomy}
                setTaxonomy={setTaxonomy}
                ifConfirm={!sectionAddTask ? createPlaybook : editPlaybook}
                allTaxonomies={allTaxonomies}
                save={!sectionAddTask ? t("button.create") : t("button.save_changes")}
              />
            </Card.Body>
          </Card>

          <ListTask urlPlaybook={url} sectionAddTask={sectionAddTask} setShowAlert={setShowAlert} />
          
          <CrudButton type="cancel" />
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default CreatePlaybook;
