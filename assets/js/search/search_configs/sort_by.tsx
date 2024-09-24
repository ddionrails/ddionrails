import {Sorting} from "@elastic/react-search-ui";


/**
 *
 * @return {Element}
 */
function sortByEN() {
  return (
    <Sorting
      label={"Sort by"}
      sortOptions={[
        {
          name: "Relevance",
          value: [],
        },
        {
          name: "Period (ascending)",
          value: [
            {
              field: "period.label",
              direction: {order: "asc"},
            },
          ],
        },
        {
          name: "Period (descending)",
          value: [
            {
              field: "period.label",
              direction: {order: "desc"},
            },
          ],
        },
      ]}
    />
  );
}

// eslint-disable-next-line require-jsdoc
function sortByDE() {
  return (
    <Sorting
      label={"Sortiere nach"}
      sortOptions={[
        {
          name: "Relevanz",
          value: [],
          default: true,
        },
        {
          name: "Zeitraum (aufsteigend)",
          value: [
            {
              field: "period.label_de",
              direction: {order: "asc"},
            },
          ],
        },
        {
          name: "Zeitraum (absteigend)",
          value: [
            {
              field: "period.label_de",
              direction: {order: "desc"},
            },
          ],
        },
      ]}
    />
  );
}

const sortBy = new Map();
sortBy.set("en", sortByEN);
sortBy.set("de", sortByDE);

export {sortBy}
