import React, { useEffect, useState } from "react";
import { Button, Card, Col, Form, Row } from "react-bootstrap";
import DropdownState from "../../components/Dropdown/DropdownState";
import { useLocation } from "react-router-dom";
import Alert from "../../components/Alert/Alert";
import { validateDescription, validateName, validateType, validateUnrequiredInput } from "../../utils/validators/taxonomy";
import { getMinifiedTaxonomy, putTaxonomy } from "../../api/services/taxonomies";
import SelectLabel from "../../components/Select/SelectLabel";
import { useTranslation } from "react-i18next";
import { getMinifiedTaxonomyGroups } from "../../api/services/taxonomyGroups";

const EditTaxonomy = () => {
  const location = useLocation();
  const fromState = location.state;
  const [taxonomy] = useState(fromState);
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
    //
    // {
    //     (parent != undefined) ?
    //         getTaxonomy(parent)
    //             .then((response) => {
    //                 setSelectParent(response.data.name)
    //             })
    //         : setSelectParent("Sin padre")
    // }

    // {
    //     (alias_of != undefined) ?
    //         getTaxonomy(alias_of)
    //             .then((response) => {
    //                 setSelectAlias_of(response.data.name)
    //             })
    //         : setSelectAlias_of("Sin alias")
    // }
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

  let typeOption = [
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
                  <Button variant="info" href="/taxonomies">
                    {t("button.close")}
                  </Button>
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
