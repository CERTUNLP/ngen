import React, { useEffect, useState } from 'react';
import { Modal } from 'react-bootstrap';
import { getMinifiedArtifact } from '../../api/services/artifact';
import { postEvent } from '../../api/services/events';
import { getMinifiedFeed } from '../../api/services/feeds';
import { getMinifiedPriority } from '../../api/services/priorities';
import { getMinifiedTaxonomy } from '../../api/services/taxonomies';
import { getMinifiedTlp } from '../../api/services/tlp';
import { getMinifiedUser } from '../../api/services/users';
import FormEvent from './components/FormEvent';

const ModalCreateEvent = ({ showModalEvent, setShowModalEvent, setEventList, eventList, setCurrentPage,  selectedEvent, setSelectedEvent, setEvents}) => {
  const formEmpty = {
    children: [],
    todos: [],
    artifacts: [],
    comments: null, // verificar aca si escribo y borro todo, se envia "" lo mismo para notes
    address_value: "", //requerido
    date: "",       //requerido
    notes: "",
    parent: [],
    priority: "",  //requerido
    tlp: "",        //requerido 
    taxonomy: "",   //requerido
    feed: "",       //requerido
    reporter: [],
    case: "",
    tasks: [],
    evidence: []
  }
  const [body, setBody] = useState(formEmpty)
  const [evidence, setEvidence] = useState([])
  const [TLP, setTLP] = useState([])
  const [feeds, setFeeds] = useState([])
  const [taxonomy, setTaxonomy] = useState([])
  const [priorities, setPriorities] = useState([])

  const [listArtifact, setListArtifact] = useState([])
  const [contactCreated, setContactsCreated] = useState(null);

  const [tlpNames, setTlpNames] = useState({});
  const [priorityNames, setPriorityNames] = useState({});
  const [userNames, setUserNames] = useState({});
  const [showAlert, setShowAlert] = useState(false)

  useEffect(() => {

    getMinifiedTlp().then((response) => {
      let listTlp = []
      let dicTlp = {}
      response.map((tlp) => {
        listTlp.push({ value: tlp.url, label: tlp.name })
        dicTlp[tlp.url] = { name: tlp.name, color: tlp.color }
      })
      setTLP(listTlp)
      setTlpNames(dicTlp)
    })
      .catch((error) => {
        setShowAlert(true) //hace falta?
        console.log(error)

      })

    getMinifiedTaxonomy().then((response) => {
      let listTaxonomies = []
      response.map((taxonomy) => {
        listTaxonomies.push({ value: taxonomy.url, label: taxonomy.name })
      })
      setTaxonomy(listTaxonomies)
    })
      .catch((error) => {
        console.log(error)

      })

    getMinifiedFeed().then((response) => { //se hardcodea las paginas
      let listFeed = []
      response.map((feed) => {
        listFeed.push({ value: feed.url, label: feed.name })
      })
      setFeeds(listFeed)
    })
      .catch((error) => {
        console.log(error)

      })

    getMinifiedPriority().then((response) => { //se hardcodea las paginas
      let priorityOp = []
      let dicPriority = {}
      response.map((priority) => {
        priorityOp.push({ value: priority.url, label: priority.name })
        dicPriority[priority.url] = priority.name
      })
      setPriorityNames(dicPriority)
      setPriorities(priorityOp)
    })
      .catch((error) => {
        console.log(error)

      })

    getMinifiedUser().then((response) => { //se hardcodea las paginas
      let dicUser = {}
      response.map((user) => {
        dicUser[user.url] = user.username
      })
      setUserNames(dicUser)
    })
      .catch((error) => {
        console.log(error)

      })

    getMinifiedArtifact()
      .then((response) => {
        var list = []
        response.map((artifact) => {
          list.push({ value: artifact.url, label: artifact.value })
        })
        setListArtifact(list)
      })
      .catch((error) => {
        console.log(error)
      })

  }, [contactCreated]);

  const createEvent = () => {

    const formDataEvent = new FormData();


    formDataEvent.append("date", body.date)// tengo que hacer esto porque solo me acepta este formato, ver a futuro
    formDataEvent.append("priority", body.priority)
    formDataEvent.append("tlp", body.tlp)
    formDataEvent.append("taxonomy", body.taxonomy)
    formDataEvent.append("feed", body.feed)
    formDataEvent.append("todos", body.todos)
    formDataEvent.append("comments", body.comments)
    formDataEvent.append("notes", body.notes)
    formDataEvent.append("parent", body.parent)
    formDataEvent.append("reporter", body.reporter)
    formDataEvent.append("case", body.case)
    formDataEvent.append("tasks", body.tasks)
    formDataEvent.append("address_value", body.address_value)
    if (evidence !== null) {
      for (let index = 0; index < evidence.length; index++) {
        formDataEvent.append("evidence", evidence[index])
        console.log(evidence[index])
      }
    } else {
      formDataEvent.append("evidence", evidence)
    }
    //no se estan enviando los artefactos revisar backend
    body.artifacts.forEach((item) => {
      formDataEvent.append('artifacts', item);
    });

    postEvent(formDataEvent)
      .then((response) => {
        //window.location.href = '/events';
        console.log(response.data)
        setShowModalEvent(false)
        setEventList([... eventList, response.data])
        setSelectedEvent([... eventList, response.data])
        
        setEvents([... eventList.map(event => event.url), response.data.url])
        setCurrentPage(1);
      })
      .catch((error) => {
        setShowAlert(true)
        console.log(error)
      })
  }
  return (
    <Modal show={showModalEvent} size="lg" onHide={() => setShowModalEvent(false)} aria-labelledby="contained-modal-title-vcenter" centered>
      <Modal.Header closeButton>
        <Modal.Title>Crear Evento</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div id="example-collapse-text">
          <FormEvent createEvent={createEvent} setBody={setBody} body={body}
            feeds={feeds} taxonomy={taxonomy} tlp={TLP} priorities={priorities}
            listArtifact={listArtifact} setContactsCreated={setContactsCreated}
            evidence={evidence} setEvidence={setEvidence}
            tlpNames={tlpNames}
            priorityNames={priorityNames} setPriorityNames={setPriorityNames}
            userNames={userNames} disableCardCase={true} disableCardEvidence={true} disableCardArtifacts={true} />
        </div>
      </Modal.Body>
    </Modal>
  );
};

export default ModalCreateEvent;