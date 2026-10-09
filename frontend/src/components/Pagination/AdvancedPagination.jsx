import Pagination from "react-bootstrap/Pagination";
import Form from "react-bootstrap/Form";
import React, { useEffect, useId, useState } from "react";
import { useTranslation } from "react-i18next";
import { getSettingPageSize } from "../../api/services/setting";

// Number of pages shown on each side of the current page
const SIBLINGS = 2;

/**
 * Controlled pagination: the parent owns `currentPage` and is notified through `updatePage`.
 * The total of pages is derived from `countItems` and the page size setting.
 */
const AdvancedPagination = ({ countItems, currentPage = 1, updatePage, setLoading, disabledPagination = false, setDisabledPagination }) => {
  const { t } = useTranslation();
  const goToId = useId();
  const [pageSize, setPageSize] = useState(null);
  const [goToValue, setGoToValue] = useState(String(currentPage));

  useEffect(() => {
    getSettingPageSize()
      .then((value) => setPageSize(value))
      .catch((error) => console.log(error));
  }, []);

  useEffect(() => {
    setGoToValue(String(currentPage));
  }, [currentPage]);

  const lastPage = pageSize ? Math.max(1, Math.ceil(countItems / pageSize)) : 1;

  const changePage = (page) => {
    if (page < 1 || page > lastPage || page === currentPage) return;
    updatePage(page);
    setDisabledPagination?.(true);
    setLoading?.(true);
  };

  const commitGoTo = () => {
    const page = parseInt(goToValue, 10);
    if (Number.isNaN(page)) {
      setGoToValue(String(currentPage));
      return;
    }
    const clamped = Math.min(Math.max(page, 1), lastPage);
    setGoToValue(String(clamped));
    changePage(clamped);
  };

  const windowStart = Math.max(1, currentPage - SIBLINGS);
  const windowEnd = Math.min(lastPage, currentPage + SIBLINGS);
  const windowPages = [];
  for (let page = windowStart; page <= windowEnd; page++) {
    windowPages.push(page);
  }

  const pageItem = (page) => (
    <Pagination.Item key={page} active={page === currentPage} disabled={disabledPagination} onClick={() => changePage(page)}>
      {page}
    </Pagination.Item>
  );

  // Gaps of a single page show that page instead of an ellipsis
  const leading = [];
  if (windowStart > 1) leading.push(pageItem(1));
  if (windowStart === 3) leading.push(pageItem(2));
  if (windowStart > 3) leading.push(<Pagination.Ellipsis key="start-ellipsis" disabled />);

  const trailing = [];
  if (windowEnd < lastPage - 2) trailing.push(<Pagination.Ellipsis key="end-ellipsis" disabled />);
  if (windowEnd === lastPage - 2) trailing.push(pageItem(lastPage - 1));
  if (windowEnd < lastPage) trailing.push(pageItem(lastPage));

  return (
    <div className="d-flex flex-wrap align-items-center justify-content-center gap-3">
      <Pagination className="mb-0">
        <Pagination.Prev disabled={disabledPagination || currentPage <= 1} onClick={() => changePage(currentPage - 1)} />
        {leading}
        {windowPages.map(pageItem)}
        {trailing}
        <Pagination.Next disabled={disabledPagination || currentPage >= lastPage} onClick={() => changePage(currentPage + 1)} />
      </Pagination>
      {lastPage > 1 && (
        <div className="d-flex align-items-center gap-2 text-nowrap">
          <label htmlFor={goToId} className="mb-0">
            {t("ngen.pagination.go_to")}
          </label>
          <Form.Control
            id={goToId}
            type="number"
            size="sm"
            min={1}
            max={lastPage}
            value={goToValue}
            disabled={disabledPagination}
            style={{ width: "5rem" }}
            onChange={(e) => setGoToValue(e.target.value)}
            onBlur={commitGoTo}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                commitGoTo();
              }
            }}
          />
          <span>
            {t("ngen.pagination.of")} {lastPage}
          </span>
        </div>
      )}
    </div>
  );
};

export default AdvancedPagination;
