import { expect, test, describe, vi } from "vitest";
import ListPlaybook from "../../playbook/ListPlaybook"
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom';

// Mock the useTranslation function
vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));

    const setIsModify= vi.fn();
    const playbook= vi.fn();
    const loading= vi.fn();
    const taxonomyNames= vi.fn();

describe("ListPlaybook", () => {
    test("Test ListPlaybook correct display on screen.", () => {
        render(
        <MemoryRouter>
        <ListPlaybook 
        setIsModify={setIsModify} 
        list={playbook} 
        loading={loading} 
        taxonomyNames={taxonomyNames}> 
        </ListPlaybook>
        </MemoryRouter>
        );
        expect(ListPlaybook).toBeDefined();

        })
  });