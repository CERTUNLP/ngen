import React from "react";
import { Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import ButtonFilter from "./ButtonFilter";

const FilterToolbar = ({ open, setOpen, onReload, onClearFilters }) => {
  const { t } = useTranslation();

  return (
    <div className="d-flex gap-1">
      {setOpen && <ButtonFilter open={open} setOpen={setOpen} />}
      {onClearFilters && (
        <Button size="lm" variant="outline-secondary" onClick={onClearFilters}>
          {t("button.clear_filters")}
        </Button>
      )}
      {onReload && (
        <Button size="lm" variant="outline-primary" onClick={onReload} aria-label={t("ngen.retest.refresh")}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            fill="currentColor"
            className="bi bi-arrow-clockwise"
            viewBox="0 0 16 16"
            aria-hidden="true"
            focusable="false"
          >
            <path fillRule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z" />
            <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466" />
          </svg>
        </Button>
      )}
    </div>
  );
};

export default FilterToolbar;
