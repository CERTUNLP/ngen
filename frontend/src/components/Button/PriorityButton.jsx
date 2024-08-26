import React, { useEffect, useState } from 'react';
import { Badge } from 'react-bootstrap';
import { getPriority } from '../../api/services/priorities';

const PriorityButton = (props) => {
  const [priority, setPriority] = useState('');
  // const [colorText, setColorText] = useState('');

  useEffect(() => {
    showPriority(props.url);
  }, []);

  const showPriority = (url) => {
    getPriority(url)
      .then((response) => {
        setPriority(response.data);
      })
      .catch();
  };

  return (
    priority && (
      <React.Fragment>
        <Badge
          className="badge mr-1"
          ref={(element) => {
            if (element) {
              element.style.setProperty('color', '#333', 'important');
              element.style.setProperty('background', priority.color, 'important');
            }
          }}
        >
          {priority.name}
        </Badge>
      </React.Fragment>
    )
  );
};

export default PriorityButton;
