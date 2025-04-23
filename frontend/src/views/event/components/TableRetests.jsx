import React from "react";
import Table from "react-bootstrap/Table";
import { useTranslation } from "react-i18next";

const TableRetests = ({ retests }) => {
  const { t } = useTranslation();

  return (
    <Table responsive hover className="text-center">
      <thead>
        <tr>
          <th>{t("ngen.retest.target")}</th>
          <th>{t("ngen.retest.result")}</th>
          <th>{t("ngen.retest.vulnerable")}</th>
          <th>{t("ngen.retest.analyzerType")}</th>
          <th>{t("ngen.retest.date")}</th>
          <th>{t("ngen.retest.details")}</th>
        </tr>
      </thead>
      <tbody>
        {retests.map((retest, index) => (
          <tr key={index}>
            <td>{retest.target}</td>
            <td>
              <span
                className="text-truncate"
                title={retest.result}
                style={{
                  display: "inline-block",
                  maxWidth: `${70}ch`,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {retest.result}
              </span>
            </td>
            <td>{retest.vulnerable ? t("w.yes") : t("w.no")}</td>
            <td>{retest.analyzer_type}</td>
            <td>{new Date(retest.date).toLocaleString()}</td>
            <td>
              <a
                href={retest.analyzer_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline-primary btn-sm rounded-circle"
                title={t("ngen.retest.details")}
              >
                <i className="fa fa-link"></i>
              </a>
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default TableRetests;