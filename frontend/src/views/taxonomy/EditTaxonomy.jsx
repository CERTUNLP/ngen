import React, { useEffect, useState } from "react";
import { Button, Card, Col, Form, Row, Spinner } from "react-bootstrap";
import DropdownState from "../../components/Dropdown/DropdownState";
import { useLocation, useParams } from "react-router-dom";
import { validateDescription, validateName, validateType, validateUnrequiredInput } from "../../utils/validators/taxonomy";
import { getMinifiedTaxonomy, putTaxonomy, getTaxonomy } from "../../api/services/taxonomies";
import SelectLabel from "../../components/Select/SelectLabel";
import { useTranslation } from "react-i18next";
import { getMinifiedTaxonomyGroups } from "../../api/services/taxonomyGroups";
import { COMPONENT_URL } from "config/constant";
import CrudButton from "components/Button/CrudButton";

const EditTaxonomy = () => {
  const location = useLocation();
  const fromState = location.state;
  const [taxonomy, seTaxonomy] = useState({});
  const { t } = useTranslation();

  const [type, setType] = useState(taxonomy.type);
  const [name, setName] = useState(taxonomy.name);
  const [description, setDescription] = useState(taxonomy.description);
  const [parent, setParent] = useState(taxonomy.parent);
  const [group, setGroup] = useState(taxonomy.group);
  const [alias_of, setAlias_of] = useState(taxonomy.alias_of);
  const [active, setActive] = useState(+taxonomy.active);
  const [needs_review, setNeeds_review] = useState(+taxonomy.needs_review);
  // const [currentParent, setSelectParent] = useState("")
  // const [currentTaxonomyGroup, setSelectTaxonomyGroup] = useState("")
  // const [currentAlias_of, setSelectAlias_of] = useState("")
  const [showAlert, setShowAlert] = useState(false);

  const [taxonomies, setTaxonomies] = useState([]);
  const [groups, setGroups] = useState([]);

  const [selectParent, setSelectParent] = useState();
  const [selectGroup, setSelectGroup] = useState();
  const [selectAlias_of, setSelectAlias_of] = useState();
  const [selectedType, setSelectedType] = useState();
  const [isGroupDisabled, setIsGroupDisabled] = useState(false);
  const [loading, setLoading] = useState(true);
  const [id] = useState(useParams());

  let typeOption = [
    // Como se usa en un useEffect, esta variable debe estar antes de que se ejecute el useEffect si no tiene un problema de ejecucion
    {
      value: "vulnerability",
      label: t("ngen.vulnerability")
    },
    {
      value: "incident",
      label: t("ngen.incident")
    },
    {
      value: "other",
      label: t("ngen.other")
    }
  ];

  useEffect(() => {
    if (id.id) {
      getTaxonomy(COMPONENT_URL.taxonomy + id.id + "/")
        .then((response) => {
          seTaxonomy(response.data);

          setType(response.data.type);
          setName(response.data.name);
          setDescription(response.data.description);
          setParent(response.data.parent);
          setGroup(response.data.group);
          setAlias_of(response.data.alias_of);
          setActive(+response.data.active);
          setNeeds_review(+response.data.needs_review);
        })
        .catch((error) => console.log(error))
        .finally(() => {
          setShowAlert(true);
          setLoading(false);
        });
    }
  }, [id]);

  useEffect(() => {
    getMinifiedTaxonomy().then((response) => {
      let listTaxonomies = [];
      listTaxonomies.push({ value: "", label: "" });
      response.forEach((taxonomy) => {
        listTaxonomies.push({ value: taxonomy.url, label: taxonomy.name });
      });
      setTaxonomies(listTaxonomies);
    });

    getMinifiedTaxonomyGroups().then((response) => {
      let listTaxonomyGroups = [];
      response.forEach((taxonomyGroup) => {
        listTaxonomyGroups.push({ value: taxonomyGroup.url, label: taxonomyGroup.name });
      });
      setGroups(listTaxonomyGroups);
    });
  }, []);

  useEffect(() => {
    if (taxonomies.length > 0) {
      taxonomies.forEach((item) => {
        if (item.value === parent) {
          setSelectParent({ label: item.label, value: item.value });
        }
        if (item.value === alias_of) {
          setSelectAlias_of({ label: item.label, value: item.value });
        }
      });
    }
    if (groups.length > 0) {
      groups.forEach((item) => {
        if (item.value === group) {
          setSelectGroup({ label: item.label, value: item.value });
        }
      });
    }
    if (typeOption.length > 0) {
      typeOption.forEach((item) => {
        if (item.value === type) {
          setSelectedType({ label: item.label, value: item.value });
        }
      });
    }
  }, [taxonomies, parent, group, alias_of, groups, type]);

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  const handleParentChange = (value) => {
    setParent(value);
    setGroup(null);
    setSelectGroup(null);
    if (value) {
      setIsGroupDisabled(true);
    } else {
      setIsGroupDisabled(false);
    }
  };

  const editTaxonomy = () => {
    putTaxonomy(taxonomy.url, type, name, description, active, parent, alias_of, needs_review, group)
      .then(() => {
        window.location.href = "/taxonomies";
      })
      .catch((error) => {
        console.log(error);
        setShowAlert(true);
      });
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  return (
    <React.Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.taxonomy_one")}</Card.Title>
            </Card.Header>
            <Card.Body>
              <Form>
                <Row>
                  <Col sm={12} lg={6}>
                    <Form.Group>
                      <Form.Label>
                        {t("ngen.name_one")}
                        <b style={{ color: "red" }}>*</b>
                      </Form.Label>
                      <Form.Control
                        type="text"
                        defaultValue={taxonomy.name}
                        onChange={(e) => setName(e.target.value)}
                        isInvalid={!validateName(name)}
                      />
                      {validateName(name) ? "" : <div className="invalid-feedback">{t("ngen.name.invalid")}</div>}
                    </Form.Group>
                  </Col>
                  <Col sm={12} lg={4}>
                    <SelectLabel
                      set={setType}
                      setSelect={setSelectedType}
                      options={typeOption}
                      value={selectedType}
                      placeholder={t("ngen.type")}
                      required={true}
                    />
                  </Col>
                  <Col sm={12} lg={1}>
                    <Form.Group>
                      <Form.Label>{t("ngen.state_one")}</Form.Label>
                      <DropdownState state={taxonomy.active} setActive={setActive}></DropdownState>
                    </Form.Group>
                  </Col>
                  <Col sm={12} lg={1}>
                    <Form.Group>
                      <Form.Label>{t("ngen.taxonomy.needs_review")}</Form.Label>
                      <DropdownState state={taxonomy.needs_review} setActive={setNeeds_review} str_true="w.yes" str_false="w.no" />
                    </Form.Group>
                  </Col>
                </Row>
                <Row>
                  <Col sm={12} lg={4}>
                    <SelectLabel
                      set={handleParentChange}
                      setSelect={setSelectParent}
                      options={taxonomies}
                      value={selectParent}
                      placeholder={t("ngen.taxonomy.parent")}
                      required={false}
                      legend={t("ngen.taxonomy.parent.legend.edit")}
                    />
                  </Col>
                  <Col sm={12} lg={4}>
                    <SelectLabel
                      set={setGroup}
                      setSelect={setSelectGroup}
                      options={groups}
                      disabled={isGroupDisabled}
                      value={selectGroup}
                      placeholder={t("ngen.taxonomy.group")}
                      required={false}
                      legend={t("ngen.taxonomy.group.legend.edit")}
                    />
                  </Col>
                  <Col sm={12} lg={4}>
                    <SelectLabel
                      set={setAlias_of}
                      setSelect={setSelectAlias_of}
                      options={taxonomies}
                      value={selectAlias_of}
                      placeholder={t("ngen.taxonomy.alias_of")}
                      required={false}
                    />
                  </Col>
                </Row>
                <Row>
                  <Col sm={12} lg={12}>
                    <Form.Group>
                      <Form.Label>{t("ngen.description")}</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        defaultValue={taxonomy.description}
                        onChange={(e) => setDescription(e.target.value)}
                        isInvalid={validateUnrequiredInput(description) ? !validateDescription(description) : false}
                      />
                      {validateDescription(description) ? "" : <div className="invalid-feedback">{t("ngen.description.invalid")}</div>}
                    </Form.Group>
                  </Col>
                </Row>
                <Form.Group as={Col}>
                  {validateType(type) && validateName(name) && name !== "" ? (
                    <Button variant="primary" onClick={editTaxonomy}>
                      {t("button.save")}
                    </Button>
                  ) : (
                    <Button variant="primary" disabled>
                      {t("button.save")}
                    </Button>
                  )}
                  <CrudButton type="cancel" />
                </Form.Group>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default EditTaxonomy;
