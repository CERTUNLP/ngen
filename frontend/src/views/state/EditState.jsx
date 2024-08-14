import React, { useEffect, useState } from 'react'
import { Row } from 'react-bootstrap'
import { useLocation } from 'react-router-dom'
import Alert from '../../components/Alert/Alert'
import FormState from './components/FormState'
import Navigation from '../../components/Navigation/Navigation'
import { getAllStates, putState } from '../../api/services/states'
import ListEdge from '../edge/ListEdge'
import { useTranslation } from 'react-i18next'

const EditState = () => {
  const location = useLocation()
  const fromState = location.state
  const [body, setBody] = useState(fromState)

  const [states, setStates] = useState([])
  // const [loading, setLoading] = useState(true)
  const [showAlert, setShowAlert] = useState(false)
  const { t } = useTranslation()

  const [sectionAddEdge, setSectionAddEdge] = useState(false)

  useEffect(() => {
    if (body.children.length > 0) {
      setSectionAddEdge(true)
    }
    const fetchPosts = async () => {
      getAllStates().then((response) => {

        var listChildren = []
        response.forEach((state) => {
          if (state.url !== body.url) {
            listChildren.push({ value: state.url, label: state.name })
          }
        })
        setStates(listChildren)
      }).catch((error) => {
        console.log(error)
      })
    }
    fetchPosts()
  }, [])
  // const resetShowAlert = () => {
  //   setShowAlert(false);
  // }

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
             component="state"/>
      <Row>
        <Navigation actualPosition={t('ngen.state.edit')} path="/states"
                    index={t('ngen.state_other')}/>
      </Row>
      <FormState body={body} setBody={setBody} createState={editState}
                 childernes={states}
                 type={t('w.edit')}/>
      <ListEdge url={body.url} sectionAddEdge={sectionAddEdge}
                setShowAlert={setShowAlert}/>
    </div>
  )
}
export default EditState
