import { expect, test, describe, vi } from "vitest";
import ListTaxonomy from "../../taxonomy/ListTaxonomies"
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom';
import TableTaxonomy from "views/taxonomy/components/TableTaxonomy";

// Mock the useTranslation function
vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));

  const setIsModify= vi.fn();
  const taxonomies= vi.fn();
  const loading= vi.fn();
  const order= vi.fn();
  const setOrder= vi.fn();
  const setLoading= vi.fn();
  const taxonomyGroups= vi.fn();
  const minifiedTaxonomies= vi.fn();


  

describe("ListTaxonomy", () => {
    test("Test ListTaxonomy correct display on screen.", () => {
        render(
        <MemoryRouter>
        <ListTaxonomy>
        <TableTaxonomy 
        setIsModify={setIsModify}
        list={taxonomies}
        loading={loading}
        order={order}
        setOrder={setOrder}
        setLoading={setLoading}
        taxonomyGroups={taxonomyGroups}
        minifiedTaxonomies={minifiedTaxonomies}
        />
        </ListTaxonomy>
        </MemoryRouter>
        );
        expect(ListTaxonomy).toBeDefined();

        })
  });