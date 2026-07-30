import {
  createIcon,
  sortPotentialNumeric,
  enableRelationToggleButton,
  initPeriodContainer,
  createVariableContainer,
  addConceptVariables,
} from "../variable_relations_concepts";

import { faker } from "@faker-js/faker";

function get_period(): string {
  return faker.helpers.arrayElement([
    faker.number.int({ min: 1980, max: 2050 }).toString(),
    faker.word.verb(),
  ]);
}

function get_unique_periods(size: number): Array<string> {
  const periods: Set<string> = new Set();
  while (periods.size < size) {
    const period = get_period();
    if (periods.has(period)) {
      continue;
    }
    periods.add(period);
  }
  return Array.from(periods);
}

describe("Test basic functions", () => {
  test("Test sortPotentialNumeric", () => {
    const numbers = Array.from({ length: 5 }, () =>
      faker.number.int({ min: 1, max: 1000 }).toString(),
    );
    const words = Array.from({ length: 5 }, () => faker.word.verb());

    for (const numStr of numbers) {
      for (const word of words) {
        expect(sortPotentialNumeric(numStr, word)).toBe(-1);
        expect(sortPotentialNumeric(word, parseInt(numStr))).toBe(1);
      }
    }

    for (let i = 0; i < numbers.length - 1; i++) {
      const a = numbers[i];
      const b = numbers[i + 1];
      const expected =
        parseInt(a) < parseInt(b) ? -1 : parseInt(a) > parseInt(b) ? 1 : 0;
      expect(sortPotentialNumeric(a, b)).toBe(expected);
    }
  });

  test("Test Icon creation", () => {
    const labels = new Map();
    const deLabel = faker.word.words(2);
    const enLabel = faker.word.words(2);
    labels.set("de", deLabel);
    labels.set("en", enLabel);
    const cssClasses = [faker.word.adjective(), faker.word.adjective()];
    const icon = createIcon(cssClasses, labels);
    expect(icon.title).toBe(enLabel);
    expect(icon.classList.contains(cssClasses[0])).toBe(true);
    expect(icon.classList.contains(cssClasses[1])).toBe(true);
  });

  test("Test relation disabling function", () => {
    const button = document.getElementById("concept-relation-toggle");
    button.setAttribute("disabled", "true");
    expect(button.hasAttribute("disabled")).toBe(true);
    enableRelationToggleButton("concept");
    expect(button.hasAttribute("disabled")).toBe(false);
  });

  test("Test creating a period container", () => {
    const period = get_period();
    const container = initPeriodContainer(period);
    expect(container.tagName).toBe("DIV");
    expect(container.classList.contains("period-container")).toBe(true);
    expect(container.getAttribute("data-period-name")).toBe(period);
    const header = container.querySelector(".related-period-header");
    expect(header.textContent).toBe(`${period}:`);
  });

  test("Test variable container creation", () => {
    const id = faker.string.uuid();
    const name = faker.word.verb();
    const dataset_name = faker.word.verb();
    const period = get_period();
    const variable = {
      id: id,
      name: name,
      dataset_name: dataset_name,
      period_name: period,
    };
    const container = createVariableContainer(variable);
    expect(container.classList.contains("related-variable-container")).toBe(
      true,
    );
    expect(container.getAttribute("data-variable-name")).toBe(name);
    expect(container.getAttribute("data-variable-dataset-name")).toBe(
      dataset_name,
    );
    expect(container.getAttribute("title")).toBe(`${dataset_name}/${name}`);
    const link = container.querySelector("a");
    expect(link).not.toBeNull();
    expect(link.href).toBe(`http://localhost/variable/${id}`);
    expect(link.innerText).toBe(name);
  });

  test("Test fetch of variable data and construction of relations container", async () => {
    const size = faker.number.int({ min: 3, max: 6 });
    const generatedPeriods = get_unique_periods(size);
    const conceptVariables = Array.from({ length: size }, (_, i) => ({
      id: faker.string.uuid(),
      name: faker.lorem.slug(),
      dataset_name: faker.lorem.slug(),
      period_name: generatedPeriods[i],
    }));

    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve(conceptVariables),
      }),
    ) as jest.Mock;

    await addConceptVariables();
    await new Promise((resolve) => setTimeout(resolve, 0));

    const periods = document.querySelectorAll(".period-container");
    expect(periods.length).toBe(size);

    for (const variable of conceptVariables) {
      const container = document.querySelector(
        `div[data-period-name="${variable.period_name}"] > div[data-variable-name="${variable.name}"]`,
      );
      expect(container).not.toBeNull();
      expect(container.classList.contains("concept-relation-toggle")).toBe(
        true,
      );
    }

    const conceptButton = document.getElementById("concept-relation-toggle");
    expect(conceptButton.hasAttribute("disabled")).toBe(false);
  });
});
