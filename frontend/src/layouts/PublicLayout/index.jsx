import React from "react";
import PropTypes from "prop-types";
import { Container, Row, Col, Card } from "react-bootstrap";

const PublicLayout = ({ children }) => {
  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col xs={12} sm={10} md={8} lg={6}>
          <Card>
            <Card.Body>{children}</Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

PublicLayout.propTypes = {
  children: PropTypes.node.isRequired
};

export default PublicLayout;
