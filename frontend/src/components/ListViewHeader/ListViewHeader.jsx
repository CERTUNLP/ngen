import React from "react";
import { Col, Row } from "react-bootstrap";
import Search from "../Search/Search";
import FilterToolbar from "../Button/FilterToolbar";

const ListViewHeader = ({
  open,
  setOpen,
  onReload,
  onClearFilters,
  searchType,
  wordToSearch,
  setWordToSearch,
  setLoading,
  setCurrentPage,
  children
}) => {
  return (
    <Row>
      <Col sm="auto">
        <FilterToolbar open={open} setOpen={setOpen} onReload={onReload} onClearFilters={onClearFilters} />
      </Col>
      <Col>
        <Search
          type={searchType}
          setWordToSearch={setWordToSearch}
          wordToSearch={wordToSearch}
          setLoading={setLoading}
          setCurrentPage={setCurrentPage}
        />
      </Col>
      <Col sm="auto" className="d-flex gap-1">
        {children}
      </Col>
    </Row>
  );
};

export default ListViewHeader;
