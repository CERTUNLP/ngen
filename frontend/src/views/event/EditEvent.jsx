import React, { useEffect, useState } from "react";
import { Row } from "react-bootstrap";
import FormEvent from "./components/FormEvent";
import Navigation from "../../components/Navigation/Navigation";
import { getEvent, patchEvent, putEvent } from "../../api/services/events";
import { useLocation } from "react-router-dom";
import Alert from "../../components/Alert/Alert";
import { getMinifiedTlp } from "../../api/services/tlp";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import { getMinifiedFeed } from "../../api/services/feeds";
import { getMinifiedPriority } from "../../api/services/priorities";
import { deleteEvidence } from "../../api/services/evidences";
import { getMinifiedUser } from "../../api/services/users";
import { getMinifiedArtifact } from "../../api/services/artifact";
import { useTranslation } from "react-i18next";

const EditEvent = () => {
  //const [date, setDate] = useState(caseItem.date  != null ? caseItem.date.substring(0,16) : '') //required
  const { t } = useTranslation();
  const location = useLocation();
  const fromState = location.state;
  // const [event] = useState(fromState)
  const [body, setBody] = useState(fromState);
  const [evidence, setEvidence] = useState([]);
  const [TLP, setTLP] = useState([]);
  const [feeds, setFeeds] = useState([]);
  const [taxonomy, setTaxonomy] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [users, setUsers] = useState([]);
  const [listArtifact, setListArtifact] = useState([]);
  const [contactCreated, setContactsCreated] = useState(null);
  const [showAlert, setShowAlert] = useState(false);

  const [tlpNames, setTlpNames] = useState({});
  const [priorityNames, setPriorityNames] = useState({});
  const [userNames, setUserNames] = useState({});
  const [updateEvidence, setUpdateEvidence] = useState([]);

  useEffect(() => {
    getEvent(body.url)
      .then((response) => {
        response.data.case = response.data.case ? response.data.case : "";
        response.data.date = response.data.date.substring(0, 16);
        setBody(response.data);
      })
      .catch((error) => {
        console.log(error);
      });
  }, [updateEvidence]);

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
        let listUser = [];
        let dicUser = {};
        response.forEach((user) => {
          listUser.push({ value: user.url, label: user.username });
          dicUser[user.url] = user.username;
        });
        setUsers(listUser);
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
  }, [contactCreated]);

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  const editEvent = () => {
    const formDataEvent = new FormData();

    if (body.children.length === 0) {
      //se eliminan las evidencias
      if (evidence instanceof FileList) {
        body.evidence.forEach((url) => {
          deleteEvidence(url).then((response) => {
            console.log(response);
          });
        });
      }
      //console.log(fecha.toISOString())//YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]

      formDataEvent.append("date", body.date); // tengo que hacer esto porque solo me acepta este formato, ver a futuro
      //f.append("date", fecha.toISOString())
      formDataEvent.append("priority", body.priority);
      formDataEvent.append("tlp", body.tlp);
      formDataEvent.append("taxonomy", body.taxonomy);
      body.artifacts.forEach((item) => {
        formDataEvent.append("artifacts", item);
      });
      formDataEvent.append("feed", body.feed);
      formDataEvent.append("address_value", body.address_value);

      formDataEvent.append("case", body.case);

      formDataEvent.append("todos", body.todos);
      formDataEvent.append("comments", body.comments);
      //f.append("cidr", body.cidr)// 'null' does not appear to be an IPv4 or IPv6 network"
      formDataEvent.append("notes", body.notes);
      //f.append("parent", body.parent) //"Invalid hyperlink - No URL match."]
      formDataEvent.append("reporter", body.reporter);
      //f.append("case", body.case) //"Invalid hyperlink - No URL match.
      formDataEvent.append("tasks", body.tasks);

      if (evidence !== null) {
        for (let index = 0; index < evidence.length; index++) {
          formDataEvent.append("evidence", evidence[index]);
        }
      } else {
        formDataEvent.append("evidence", evidence);
      }
      //formDataEvent.append('artifacts',body.artifacts);

      putEvent(body.url, formDataEvent)
        .then(() => { })
        .catch((error) => {
          setShowAlert(true); //hace falta?
          console.log(error);
        });
    } else {
      if (evidence instanceof FileList) {
        body.evidence.forEach((url) => {
          deleteEvidence(url).then((response) => {
            console.log(response);
          });
        });
      }
      //console.log(fecha.toISOString())//YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]

      console.log("body", body);
      formDataEvent.append("date", body.date); // tengo que hacer esto porque solo me acepta este formato, ver a futuro
      //f.append("date", fecha.toISOString())
      formDataEvent.append("priority", body.priority);
      formDataEvent.append("tlp", body.tlp);
      //formDataEvent.append("taxonomy", body.taxonomy)
      if (body.artifacts.length > 0) {
        body.artifacts.forEach((item) => {
          formDataEvent.append("artifacts", item);
        });
      }
      //formDataEvent.append("feed", body.feed)
      //formDataEvent.append("address_value", body.address_value)
      formDataEvent.append("case", body.case);
      formDataEvent.append("todos", body.todos);
      formDataEvent.append("comments", body.comments);
      //f.append("cidr", body.cidr)// 'null' does not appear to be an IPv4 or IPv6 network"
      formDataEvent.append("notes", body.notes);
      //f.append("parent", body.parent) //"Invalid hyperlink - No URL match."]
      formDataEvent.append("reporter", body.reporter);
      //f.append("case", body.case) //"Invalid hyperlink - No URL match.
      formDataEvent.append("tasks", body.tasks);

      if (evidence !== null) {
        for (let index = 0; index < evidence.length; index++) {
          formDataEvent.append("evidence", evidence[index]);
        }
      } else {
        formDataEvent.append("evidence", evidence);
      }
      //formDataEvent.append('artifacts',body.artifacts);

      patchEvent(body.url, formDataEvent)
        .then(() => { })
        .catch((error) => {
          // setShowAlert(true); //hace falta?
          console.log(error);
        });
    }
  };

  return (
    body && (
      <div>
        <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} component="event" />
        <Row>
          <Navigation actualPosition={t("ngen.event.edit")} path="/events" index={t("ngen.event_one")} />
        </Row>
        <FormEvent
          createEvent={editEvent}
          setBody={setBody}
          body={body}
          feeds={feeds}
          taxonomy={taxonomy}
          tlp={TLP}
          priorities={priorities}
          users={users}
          listArtifact={listArtifact}
          setContactsCreated={setContactsCreated}
          evidence={evidence}
          setEvidence={setEvidence}
          updateEvidence={updateEvidence}
          setUpdateEvidence={setUpdateEvidence}
          tlpNames={tlpNames}
          priorityNames={priorityNames}
          setPriorityNames={setPriorityNames}
          userNames={userNames}
        />
      </div>
    )
  );
};

export default EditEvent;
