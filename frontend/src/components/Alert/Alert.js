import React, { useState, useEffect } from 'react';
import Toast from 'react-bootstrap/Toast';

import { store } from '../../store';
import { CLEAR_MESSAGE } from '../../store/actions';


const Alert = ({ showAlert , resetShowAlert, component}) => {
    const [show, setShow] = useState(false);
    const [text, setText] = useState('');
    const [type, setType] = useState('');
 
    const textMessage = store.getState().message.text;
    const typeAlert = store.getState().message.typeMessage;
    const typeComponent = store.getState().message.typeComponent;

    useEffect(() => {
        if (showAlert === true && textMessage  !== '' && typeComponent === component) {
            setText(textMessage);
            setType(typeAlert);
            setShow(true); 
        } else if (showAlert === true && textMessage  !== '' && typeComponent !== component) {
            resetAlert(); 
        } 
    });

    const resetAlert = () => {
                
        const { dispatch } = store;

        dispatch({
            type: CLEAR_MESSAGE
        });
        setShow(false);
        resetShowAlert();

    }
    
    return( 
        <div id="toastAlert">
            <Toast id={type==='success' ? 'alertStyleGreen' : 'alertStyleRed'} onClose={() => resetAlert()} show={show} autohide >
                    <i id="alertStyle__icon" className={type==='success' ? 'feather icon-check-circle mx-1' : 'feather icon-alert-triangle mx-1'} />
                    <tr id="alertStyle__text" plaintext readOnly>{text}</tr>                    
                    <i id="alertStyle__close" className="material-icons" title="Cerrar" onClick={() => resetAlert()}>close</i>
            </Toast>
        </div>
    );
 }

export default Alert;
