import React, { useState, useEffect } from 'react'
import FormState from './components/FormState'
import Navigation from '../../components/Navigation/Navigation'
import Alert from '../../components/Alert/Alert';
import { postState, putState } from "../../api/services/states";
import ListEdge from '../edge/ListEdge';
import { useTranslation, Trans } from 'react-i18next';

const AddState = () => {


    const formEmpty = {
        name: "",//requerido
        attended: "",//requerido
        solved: "",//requerido
        active: null,
        description: "",
        children: []
    }
    const [state, setState] = useState({});
    const [url, setUrl] = useState('');
    const [body, setBody] = useState(formEmpty)
    const [childernes, setChildernes] = useState([])
    const [showAlert, setShowAlert] = useState(false)
    const { t } = useTranslation();

    //Collapse
    const [sectionAddEdge, setSectionAddEdge] = useState(false);

    const resetShowAlert = () => {
        setShowAlert(false);
    }

    const createState = () => {
        postState(body.name, body.attended, body.solved, 1, body.description, body.children)
            .then((response) => {
                setState(response.data) // y la url
                setUrl(response.data.url)
                setSectionAddEdge(true)
            })
            .catch((error) => {
                setShowAlert(true)
                console.log(error)
            }).finally(() => {
                setShowAlert(true)
            })
    }

    const editState = () => {
        putState(url, body.name, body.attended, body.solved, 1, body.description, body.children)
            .then((response) => {
                setState(response.data) // y la url
                setUrl(response.data.url)
                setSectionAddEdge(true)
            })
            .catch((error) => {
                setShowAlert(true)
                console.log(error)
            }).finally(() => {
                setShowAlert(true)
            })
    }


    return (
        <div>
            <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="state" />
            <Navigation actualPosition={t('ngen.state.add')} path="/states" index={t('ngen.state_other')} />
            <FormState body={body} setBody={setBody} createState={!sectionAddEdge ? createState : editState} childernes={childernes} type={t('w.add')} />
            <ListEdge url={url} sectionAddEdge={sectionAddEdge} setShowAlert={setShowAlert} />

        </div>
    )
}
export default AddState