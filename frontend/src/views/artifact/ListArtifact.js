import React from 'react';
import { Card, Col, Row } from 'react-bootstrap';

const ListArtifact = ({ artifact }) => {


  return (
    <React.Fragment>


      <Card>
        <Card.Header>
          <Row>
            <Col sm={12} lg={3}>

            </Col>
          </Row>
        </Card.Header>
        <Card.Body>
          {/*<TableArtifact artifact={artifact}/>*/}
        </Card.Body>
      </Card>

    </React.Fragment>
  )
}

export default ListArtifact
