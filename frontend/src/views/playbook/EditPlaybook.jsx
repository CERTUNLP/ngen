import React, { useEffect, useState } from 'react'
import { useLocation, useParams } from 'react-router-dom'
import { Button, Card, Col, Row } from 'react-bootstrap'
import { putPlaybook, getPlaybook } from '../../api/services/playbooks'
import FormCreatePlaybook from '../playbook/components/FormCreatePlaybook'
import { getMinifiedTaxonomy } from '../../api/services/taxonomies'
import ListTask from '../task/ListTask'
import Navigation from '../../components/Navigation/Navigation'
import Alert from '../../components/Alert/Alert'
import { useTranslation } from 'react-i18next'
import { COMPONENT_URL } from 'config/constant'

const EditPlaybook = () => {
  const [playbook, setPlaybook] = useState({})
  const [id] = useState(useParams());
  const { t } = useTranslation()

  const [url, setUrl] = useState()
  const [name, setName] = useState()
  const [taxonomy, setTaxonomy] = useState()

  //Dropdown
  const [allTaxonomies, setAllTaxonomies] = useState([]);

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {

    if (id.id) {
      getPlaybook(COMPONENT_URL.playbook + id.id + "/")
        .then((response) => {
          setPlaybook(response.data)
        }).catch(error => console.log(error));

    }
  }, [id]);

  useEffect(() => {

    if (playbook) {
      setUrl(playbook.url)
      setName(playbook.name)
      setTaxonomy(playbook.taxonomy)
    }
  }, [playbook]);

  useEffect(() => {
    getMinifiedTaxonomy().then((response) => {
      //allTaxonomies
      let listAllTaxonomies = response.map((taxonomyItem) => {
        return {
          value: taxonomyItem.url,
          label: taxonomyItem.name + ' (' + labelTaxonomy[taxonomyItem.type] +
            ')',
        }
      })
      setAllTaxonomies(listAllTaxonomies)
    }).catch((error) => {
      console.log(error)
    })
  }, []);

  const labelTaxonomy = {
    vulnerability: "Vulnerabilidad",
    incident: "Incidente"
  };

  const editPlaybook = () => {
    putPlaybook(url, name, taxonomy)
      .then()
      .catch()
      .finally(() => {
        setShowAlert(true);
      });
  };

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="playbook" />
      <Row>
        <Navigation actualPosition={t("ngen.playbook.edit")} path="/playbooks" index="Playbook" />
      </Row>

      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.playbook")}</Card.Title>
              <span className="d-block m-t-5">{t("ngen.playbook.edit")}</span>
            </Card.Header>
            <Card.Body>
              <FormCreatePlaybook
                name={name}
                setName={setName}
                taxonomy={taxonomy}
                setTaxonomy={setTaxonomy}
                ifConfirm={editPlaybook}
                allTaxonomies={allTaxonomies}
                save={t("button.save_changes")}
              />
            </Card.Body>
          </Card>

          <ListTask urlPlaybook={url} sectionAddTask={true} setShowAlert={setShowAlert} />

          <Button variant="primary" href="/playbooks">
            {t("button.return")}
          </Button>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default EditPlaybook;
