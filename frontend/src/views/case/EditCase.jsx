import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Row } from 'react-bootstrap'
import { getCase } from '../../api/services/cases'
import FormCase from './components/FormCase'
import Navigation from '../../components/Navigation/Navigation'
import { getState } from '../../api/services/states'
import { useTranslation } from 'react-i18next'

const EditCase = () => {
  const { t } = useTranslation()
  const location = useLocation()
  const fromState = location.state
  const [url] = useState(fromState)

  const [caseItem, setCaseItem] = useState(null)

  //multiselect
  const [allStates, setSupportedStates] = useState([])
  const [updateCase, setUpdateCase] = useState([])

  useEffect(() => {
    getCase(url).then(response => {
      setCaseItem(response.data)
    }).catch(error => {
    })

  }, [updateCase])

  useEffect(() => {
    let listStates = []
    if (caseItem) {

      getState(caseItem.state).then((response) => {
        listStates.push({ value: response.data.url, label: response.data.name })
        let children = response.data.children
        children.forEach((child) => {
          getState(child).then((responseChild) => {
            listStates.push(
              { value: responseChild.data.url, label: responseChild.data.name })
          }).catch((error) => {
            console.log(error)
          })
        })
        setSupportedStates(listStates)
      }).catch((error) => {
        console.log(error)
      })
    }

  }, [caseItem])

  return (caseItem &&
    <React.Fragment>
      <Row>
        <Navigation actualPosition={t('ngen.case_edit')} path="/cases"
                    index={t('ngen.case_other')}/>
      </Row>
      <FormCase caseItem={caseItem} allStates={allStates} edit={true}
                save={t('button.save_changes')}
                evidenceColum={true}
                buttonsModalColum={true} setUpdateCase={setUpdateCase}
                updateCase={updateCase}/>
    </React.Fragment>
  )
}

export default EditCase
