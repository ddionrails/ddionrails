delete global.window.location;
global.window = Object.create(window);

document.body.innerHTML =
  "<html><p title='Concept' data-concept-name='concept_name'>" +
  "<i class='fa fa-cog'></i>" +
  "<a href='/concept/concept-id'>" +
  "Concept Label</a>" +
  "<a id='variable-name' href=''>variable_name</a>" +
  "</p>" +
  "<div id='table-container' data-bs-type='label-table'>" +
  "</div>" +
  "</html>";

global.window.location = {
  ancestorOrigins: null,
  hash: null,
  host: "localhost",
  port: "80",
  protocol: "http:",
  hostname: "localhost",
  href: "http://localhost/study-name/datasets/dataset-name/variable-name",
  origin: "http://localhost",
  pathname: null,
  search: null,
  assign: null,
  reload: null,
  replace: null,
};
