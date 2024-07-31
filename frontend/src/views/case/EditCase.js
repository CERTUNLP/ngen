import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Row } from 'react-bootstrap';
import { getCase } from '../../api/services/cases';
import FormCase from './components/FormCase';
import Navigation from '../../components/Navigation/Navigation';
import { getState } from '../../api/services/states';
import { useTranslation, Trans } from 'react-i18next';


const EditCase = () => {

    const location = useLocation();
    const fromState = location.state;
    const [url, setUrl] = useState(null);
    const [caseItem, setCaseItem] = useState(location?.state?.item || null);

    //multiselect
    const [allStates, setSupportedStates] = useState([])
    const [updateCase, setUpdateCase] = useState([])

    console.log(fromState)

    useEffect(() => {
        const { caseUrl, navigation, buttonReturn } = location.state || {};
        console.log(caseUrl)
        setUrl(caseUrl)
        
      }, [location.state]);

    useEffect(() => {
        if (url !== null){
            getCase(url)
            .then(response => {
                setCaseItem(response.data)
            })
            .catch(error => {
            })
        }
        
    }, [updateCase, url])


    useEffect(() => {
        let listStates = []
        if (caseItem) {

            getState(caseItem.state)
                .then((response) => {
                    console.log(response)

                    listStates.push({ value: response.data.url, label: response.data.name })
                    let children = response.data.children;
                    children.forEach((child) => {
                        getState(child)
                            .then((responseChild) => {
                                console.log(responseChild)
                                listStates.push({ value: responseChild.data.url, label: responseChild.data.name })
                            })
                            .catch((error) => {
                                console.log(error)
                            })
                    })
                    console.log(listStates);
                    setSupportedStates(listStates);
                })
                .catch((error) => {
                    console.log(error)
                })
        }

    }, [caseItem])

const { t } = useTranslation();


return (caseItem &&
    <React.Fragment>
        <Row>
            <Navigation actualPosition={t('ngen.case_edit')} path="/cases" index={t('ngen.case_other')} />
        </Row>
        <FormCase caseItem={caseItem} allStates={allStates} edit={true} save={t('button.savechanges')} evidenceColum={true}
            buttonsModalColum={true} setUpdateCase={setUpdateCase} updateCase={updateCase}  />
    </React.Fragment>
);
};

export default EditCase;
