import Pagination from "react-bootstrap/Pagination";
import React, { useEffect, useState } from "react";
import { settingPageSize } from "../../api/services/setting";

const AdvancedPagination = ({
  countItems,
  updatePage,
  updatePagination,
  setUpdatePagination,
  setLoading,
  disabledPagination,
  setDisabledPagination,
  parentCurrentPage = -1,
  ifModify = true
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [initPage, setInitPage] = useState(1);

  // lastPage represents the last page or the total of pages, 10 represents the number of items per page
  const [lastPage, setLastPage] = useState(1);

  // arrayPages represents the array of pages to display in view
  const [arrayPages, setArrayPages] = useState([]);
  const [pageSize, setPageSize] = useState(null);

  useEffect(() => {
    settingPageSize()
      .then((value) => {
        setPageSize(value);
      })
      .catch((error) => {
        console.log(error);
      });
  }, [updatePagination]);

  useEffect(() => {
    if (pageSize !== null) {
      if (updatePagination) {
        setCurrentPage(1);
      }
      // First time to set lastPage
      if (updatePagination && currentPage === 1) {
        // no se actualiza por lastpage
        setLastPage(Math.ceil(countItems / pageSize));
        setUpdatePagination(false);
        setInitPage(1);
        //setLoading(true)
      }

      if (parentCurrentPage === -1) {
        let list = [];
        let index = currentPage - 2 > 0 ? currentPage - 2 : 1;

        // Array of pages only display 3 numbers
        while (index <= lastPage && index <= currentPage + 2) {
          list.push(index);
          ++index;
        }
        setArrayPages(list);
      } else {
        if (!arrayPages.includes(parentCurrentPage)) {
          console.log("No existe la pagina en el array");
        }
      }
    }
  }, [currentPage, countItems, lastPage, updatePagination]);
  //}, [countItems, lastPage, updatePagination]);

  const updateCurrentPage = (chosenPage) => {
    setCurrentPage(chosenPage);
    updatePage(chosenPage);
    if (currentPage !== chosenPage) {
      setDisabledPagination(true);
      setLoading(true);
    }
  };

  const arrayPagesPrev = () => {
    let prev = currentPage - 1;
    if (!arrayPages.includes(prev)) {
      let newArrayPages = arrayPages.map((num) => num - 1);
      setArrayPages(newArrayPages);
    }
    setCurrentPage(prev);
    updatePage(prev);
    setDisabledPagination(true);
    setLoading(true);
  };

  const arrayPagesNext = () => {
    let next = currentPage + 1;
    if (!arrayPages.includes(next)) {
      let newArrayPages = arrayPages.map((num) => num + 1);
      setArrayPages(newArrayPages);
    }
    setCurrentPage(next);
    updatePage(next);
    setDisabledPagination(true);
    setLoading(true);
  };

  return (
    <Pagination>
      {currentPage === 1 ? (
        <Pagination.Prev disabled />
      ) : (
        <Pagination.Prev disabled={disabledPagination} onClick={() => arrayPagesPrev()} />
      )}
      {currentPage >= 4 && (
        <Pagination.Item disabled={disabledPagination} onClick={() => updateCurrentPage(1)}>
          1
        </Pagination.Item>
      )}
      {currentPage >= 5 && (
        currentPage === 5 ? (
          <Pagination.Item disabled={disabledPagination} onClick={() => updateCurrentPage(2)}>
            2
          </Pagination.Item>
        ) : (
            <Pagination.Ellipsis disabled={disabledPagination} />
          )
      )}
      {arrayPages.map((page) =>
        page === currentPage ? (
          <Pagination.Item key={page} disabled={disabledPagination} onClick={() => updateCurrentPage(page)} active>
            {page}
          </Pagination.Item>
        ) : (
          <Pagination.Item key={page} disabled={disabledPagination} onClick={() => updateCurrentPage(page)}>
            {page}
          </Pagination.Item>
        )
      )}
      {currentPage <= lastPage - 4 && (
        currentPage === lastPage - 4 ? (
          <Pagination.Item disabled={disabledPagination} onClick={() => updateCurrentPage(lastPage - 1)}>
            {lastPage - 1}
          </Pagination.Item>
        ) : (
            <Pagination.Ellipsis disabled={disabledPagination} />
          )
      )}
      {currentPage <= lastPage - 3 && (
        <Pagination.Item disabled={disabledPagination} onClick={() => updateCurrentPage(lastPage)}>
          {lastPage}
        </Pagination.Item>
      )}
      {currentPage === lastPage ? (
        <Pagination.Next disabled />
      ) : (
        <Pagination.Next disabled={disabledPagination} onClick={() => arrayPagesNext()} />
      )}
    </Pagination>
  );
};

export default AdvancedPagination;
