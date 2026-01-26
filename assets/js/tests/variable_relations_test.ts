import { createIcon, sortPotentialNumeric } from "../variable_relations_concepts";

describe("Test basic functions", () => {

  test("Test sortPotentialNumeric", () => {
    let result = sortPotentialNumeric("1", "b");
    expect(result).toBe(-1);
    result = sortPotentialNumeric("b", 1);
    expect(result).toBe(1);
    result = sortPotentialNumeric("1", 2);
    expect(result).toBe(-1);
    result = sortPotentialNumeric("2", "1000");
    expect(result).toBe(-1);
  });

  test("Test Icon creation", ()=> {
    const labels = new Map()
    labels.set("de", "de")
    labels.set("en", "en")
    const icon = createIcon(["dummy"], labels)
    expect(icon.title).toBe("en")
  })



});
