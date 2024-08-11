import React, { useEffect, useState } from 'react';
import { Badge } from 'react-bootstrap';
import { getPriority } from '../../api/services/priorities';

const PriorityButton = (props) => {
  const [priority, setPriority] = useState('');
  // const [colorText, setColorText] = useState('');

  useEffect(() => {
    showPriority(props.url)
  }, []);

  const showPriority = (url) => {
    getPriority(url).then((response) => {
      setPriority(response.data)
    }).catch();
  }

  return (
    priority &&
    <React.Fragment>
      <Badge className="badge mr-1"
             style={{ background: `${priority.color}`, color: '#111111' }}>{priority.name}</Badge>
    </React.Fragment>
  );
};

export default PriorityButton;
