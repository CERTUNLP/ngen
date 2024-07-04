import React from 'react'
import { Button, Row, Form, Spinner, Col} from 'react-bootstrap';

const FormSetting = ({body, setBody}) => {

    const completeField=(event)=>{ 
        setBody({...body,
            [event.target.name] : event.target.value}
        )       
    };
    
  return (
    <div>
        
        
       
    </div>
  )
}

export default FormSetting