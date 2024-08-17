import React, { useEffect, useState } from 'react';
import { Form } from 'react-bootstrap';
import { getNetwork } from '../../../api/services/networks';

const FormNetworkLabelCidr = (props) => {
  //TODO refactorizar los Form
  const [network, setNetwork] = useState('');

  useEffect(() => {
    showParentCidr(props.url);
  }, [props.url]);

  const showParentCidr = (url) => {
    getNetwork(url)
      .then((response) => {
        setNetwork(response.data);
      })
      .catch();
  };
  return (
    network && (
      <React.Fragment>
        <Form.Control plaintext readOnly defaultValue={network.cidr} />
      </React.Fragment>
    )
  );
};

export default FormNetworkLabelCidr;
