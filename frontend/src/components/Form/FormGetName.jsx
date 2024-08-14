import React, { useEffect, useState } from 'react'
import { Form } from 'react-bootstrap'

const FormGetName = (props) => { // url, get, key, Form: true o false
  const [item, setItem] = useState('')

  useEffect(() => {

    showName(props.url)

  }, [])

  const showName = (url) => {
    props.get(url).then((response) => {
      setItem(response.data)
    }).catch()
  }

  return (
    item &&
    <React.Fragment>
      {props.form ? <Form.Control plaintext readOnly defaultValue={item.name}
                                  key={props.url}/>
        :
        <>{item.name}</>
      }
    </React.Fragment>
  )
}

export default FormGetName
