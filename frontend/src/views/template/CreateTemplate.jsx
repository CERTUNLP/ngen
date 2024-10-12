import React, { useEffect, useState } from "react";
import { Row, Spinner } from "react-bootstrap";
import { useLocation } from "react-router-dom";
import FormTemplate from "./components/FormTemplate";
import { postTemplate } from "../../api/services/templates";
import { getMinifiedTlp } from "../../api/services/tlp";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import { getMinifiedFeed } from "../../api/services/feeds";
import { getMinifiedPriority } from "../../api/services/priorities";
import { getMinifiedState } from "../../api/services/states";
import Alert from "../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const CreateTemplate = () => {
  const location = useLocation();
  const formEvent = location.state ? location.state : "";
  const formEmpty = {
    cidr: "",
    domain: "",
    address_value: formEvent.address_value ? formEvent.address_value : "",
    active: true,
    priority: "-1",
    event_taxonomy: formEvent.taxonomy ? formEvent.taxonomy : "",
    event_feed: formEvent.feed ? formEvent.feed : "",
    case_lifecycle: "auto",
    case_tlp: "-1",
    case_state: "-1"
  };
  const [body, setBody] = useState(formEmpty);
  const [TLP, setTLP] = useState([]);
  const [feeds, setFeeds] = useState([]);
  const [taxonomy, setTaxonomy] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [states, setStates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAlert, setShowAlert] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    const fetchPosts = async () => {
      setLoading(true);

      getMinifiedTlp()
        .then((response) => {
          let listTlp = response.map((tlp) => {
            return { value: tlp.url, label: tlp.name };
          });
          setTLP(listTlp);
        })
        .catch((error) => {
          console.log(error);
        })
        .finally(() => {
          setLoading(false);
        });

      getMinifiedTaxonomy()
        .then((response) => {
          let listTaxonomies = response.map((taxonomy) => {
            return { value: taxonomy.url, label: taxonomy.name };
          });
          setTaxonomy(listTaxonomies);
        })
        .catch((error) => {
          console.log(error);
        })
        .finally(() => {
          setLoading(false);
        });

      getMinifiedFeed()
        .then((response) => {
          //se hardcodea las paginas
          let listFeed = response.map((feed) => {
            return { value: feed.url, label: feed.name };
          });
          setFeeds(listFeed);
        })
        .catch((error) => {
          console.log(error);
        })
        .finally(() => {
          setLoading(false);
        });

      getMinifiedPriority()
        .then((response) => {
          //se hardcodea las paginas
          let listPriority = response.map((priority) => {
            return { value: priority.url, label: priority.name };
          });
          setPriorities(listPriority);
        })
        .catch((error) => {
          console.log(error);
        })
        .finally(() => {
          setLoading(false);
        });

      getMinifiedState()
        .then((response) => {
          let listStates = response.map((stateItem) => {
            return { value: stateItem.url, label: stateItem.name };
          });
          setStates(listStates);
        })
        .catch((error) => {})
        .finally(() => {
          setLoading(false);
        });
    };
    fetchPosts();
  }, []);
  const resetShowAlert = () => {
    setShowAlert(false);
  };

  const createTemplate = () => {
    postTemplate(
      body.address_value,
      body.active,
      body.priority,
      body.event_taxonomy,
      body.event_feed,
      body.case_lifecycle,
      body.case_tlp,
      body.case_state
    )
      .then(() => {
        window.location.href = "/templates";
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      });
  };
  return (
    <React.Fragment>
      {loading ? (
        <Spinner animation="border" />
      ) : (
        <FormTemplate
          body={body}
          setBody={setBody}
          createTemplate={createTemplate}
          tlp={TLP}
          feeds={feeds}
          taxonomy={taxonomy}
          priorities={priorities}
          states={states}
        />
      )}
    </React.Fragment>
  );
};

export default CreateTemplate;
