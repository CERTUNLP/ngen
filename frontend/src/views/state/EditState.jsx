import React, { useEffect, useState } from 'react'
import { Row } from 'react-bootstrap'
import { useLocation, useParams } from 'react-router-dom';
import Alert from '../../components/Alert/Alert'
import FormState from './components/FormState'
import Navigation from '../../components/Navigation/Navigation'
import { putState, getState, getMinifiedState } from "../../api/services/states";
import ListEdge from '../edge/ListEdge'
import { useTranslation } from 'react-i18next'
import { COMPONENT_URL } from '../../config/constant';

const EditState = () => {
  const location = useLocation();
  const fromState = location.state;
  const [body, setBody] = useState({});

  const [states, setStates] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAlert, setShowAlert] = useState(false)
  const [edge, setEdge] = useState()
  const [id, setId] = useState(useParams());
  const { t } = useTranslation();

  const [sectionAddEdge, setSectionAddEdge] = useState(false);

  useEffect(() => {
    if (body.children !== []) {
      setSectionAddEdge(true)
    }

  }, [body]);

  useEffect(() => {
    if (body.url) {
      getMinifiedState().then((response) => {

        var listChildren = []
        response.map((state) => {
          console.log(body.url)
          if (state.url !== body.url) {
            listChildren.push({ value: state.url, label: state.name })
          }
        })
        setStates(listChildren)
      })
        .catch((error) => {
          console.log(error)
        })

    }
  }, [body]);

  useEffect(() => {
    if (id) {
      getState(COMPONENT_URL.state + id.id + "/").then((response) => {
        setBody(response.data)
      }).catch((error) => {
        console.log(error)

      }).finally(() => {
        setLoading(false)
      })
    }
  }, [id]);

  const editState = () => {
    putState(body.url, body.name, body.attended, body.solved, body.active,
      body.description, body.children).then(() => {
        window.location.href = '/states'
      }).catch((error) => {
        setShowAlert(true)
        console.log(error)
      })
  }
  return (
    <div>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)}
        component="state" />
      <Row>
        <Navigation actualPosition={t('ngen.state.edit')} path="/states"
          index={t('ngen.state_other')} />
      </Row>
      <FormState body={body} setBody={setBody} createState={editState}
        childernes={states}
        type={t('w.edit')} loading={loading} />
      {body ?
        <ListEdge url={body.url} sectionAddEdge={sectionAddEdge} setShowAlert={setShowAlert} loading={loading} />
        : ""
      }
    </div>
  )
}
export default EditState
