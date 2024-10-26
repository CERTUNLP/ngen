import { expect, test, describe, vi } from "vitest";
import ListArtifact from "../../artifact/ListArtifact"
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom';

// Mock the useTranslation function
vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));

describe("ListArtifact", () => {
    test("Test ListArtifact correct display on screen.", () => {
        render(
          <MemoryRouter>

           <ListArtifact>

        </ListArtifact>
        </MemoryRouter>
        );
        expect(ListArtifact.toBeDefined)

        })
  });

 

