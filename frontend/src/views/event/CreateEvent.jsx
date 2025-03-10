import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import FormEvent from "./components/FormEvent";
import { postEvent } from "../../api/services/events";
import { getMinifiedTlp } from "../../api/services/tlp";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import { getMinifiedFeed } from "../../api/services/feeds";
import { getMinifiedPriority } from "../../api/services/priorities";
import { getMinifiedUser } from "../../api/services/users";
import { getMinifiedArtifact } from "../../api/services/artifact";
import { getMinifiedTag } from "../../api/services/tags";
import { useTranslation } from "react-i18next";

const CreateEvent = ({ routeParams }) => {
  const formEmpty = {
    children: [],
    todos: [],
    artifacts: [],
    comments: null, // verificar aca si escribo y borro todo, se envia "" lo mismo para notes
    address_value: "", //requerido
    date: "", //requerido
    notes: "",
    parent: [],
    priority: "", //requerido
    tlp: "", //requerido
    taxonomy: "", //requerido
    feed: "", //requerido
    reporter: [],
    case: "",
    tasks: [],
    evidence: [],
    tags: []
  };
  const [body, setBody] = useState(formEmpty);
  const [evidence, setEvidence] = useState([]);
  const [TLP, setTLP] = useState([]);
  const [feeds, setFeeds] = useState([]);
  const [taxonomy, setTaxonomy] = useState([]);
  const [priorities, setPriorities] = useState([]);

  const [listArtifact, setListArtifact] = useState([]);
  const [listTag, setListTag] = useState([]);
  const [contactCreated, setContactsCreated] = useState(null);

  const [tlpNames, setTlpNames] = useState({});
  const [priorityNames, setPriorityNames] = useState({});
  const [userNames, setUserNames] = useState({});
  const [showAlert, setShowAlert] = useState(false);

  const { t } = useTranslation();
  const navigate = useNavigate();

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  const updateTags = () => {
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
  };

  useEffect(() => {
    getMinifiedTlp()
      .then((response) => {
        let listTlp = [];
        let dicTlp = {};
        response.forEach((tlp) => {
          listTlp.push({ value: tlp.url, label: tlp.name });
          dicTlp[tlp.url] = { name: tlp.name, color: tlp.color };
        });
        setTLP(listTlp);
        setTlpNames(dicTlp);
      })
      .catch((error) => {
        setShowAlert(true); //hace falta?
        console.log(error);
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
      });

    getMinifiedPriority()
      .then((response) => {
        //se hardcodea las paginas
        let priorityOp = [];
        let dicPriority = {};
        response.forEach((priority) => {
          priorityOp.push({ value: priority.url, label: priority.name });
          dicPriority[priority.url] = priority.name;
        });
        setPriorityNames(dicPriority);
        setPriorities(priorityOp);
      })
      .catch((error) => {
        console.log(error);
      });

    getMinifiedUser()
      .then((response) => {
        //se hardcodea las paginas
        let dicUser = {};
        response.forEach((user) => {
          dicUser[user.url] = user.username;
        });
        setUserNames(dicUser);
      })
      .catch((error) => {
        console.log(error);
      });

    getMinifiedArtifact()
      .then((response) => {
        var list = response.map((artifact) => {
          return { value: artifact.url, label: artifact.value };
        });
        setListArtifact(list);
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

    updateTags();
  }, [contactCreated]);

  const createEvent = () => {
    const formDataEvent = new FormData();

    formDataEvent.append("date", body.date); // tengo que hacer esto porque solo me acepta este formato, ver a futuro
    formDataEvent.append("priority", body.priority);
    formDataEvent.append("tlp", body.tlp);
    formDataEvent.append("taxonomy", body.taxonomy);
    formDataEvent.append("feed", body.feed);
    formDataEvent.append("todos", body.todos);
    formDataEvent.append("comments", body.comments);
    formDataEvent.append("notes", body.notes);
    formDataEvent.append("parent", body.parent);
    formDataEvent.append("reporter", body.reporter);
    formDataEvent.append("case", body.case);
    formDataEvent.append("tasks", body.tasks);
    formDataEvent.append("address_value", body.address_value);
    formDataEvent.append("tags", body.tags);
    if (evidence !== null) {
      for (let index = 0; index < evidence.length; index++) {
        formDataEvent.append("evidence", evidence[index]);
      }
    } else {
      formDataEvent.append("evidence", evidence);
    }
    //no se estan enviando los artefactos revisar backend
    body.artifacts.forEach((item) => {
      formDataEvent.append("artifacts", item);
    });

    postEvent(formDataEvent)
      .then((response) => {
        if (response.data.parent !== null) {
          localStorage.setItem("event", response.data.parent);
          localStorage.setItem("return", "List events");
          localStorage.setItem("button return", "");
          localStorage.setItem("navigation", "");
          navigate("/events/view");
        } else {
          navigate("/events");
        }
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      });
  };

  return (
    body && (
      <div>
        <FormEvent
          createEvent={createEvent}
          setBody={setBody}
          body={body}
          feeds={feeds}
          taxonomy={taxonomy}
          tlp={TLP}
          priorities={priorities}
          listArtifact={listArtifact}
          listTag={listTag}
          updateTags={updateTags}
          setContactsCreated={setContactsCreated}
          evidence={evidence}
          setEvidence={setEvidence}
          tlpNames={tlpNames}
          priorityNames={priorityNames}
          setPriorityNames={setPriorityNames}
          userNames={userNames}
          asNetworkAdmin={routeParams.asNetworkAdmin}
        />
      </div>
    )
  );
};

export default CreateEvent;
