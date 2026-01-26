delete global.window.location;
global.window = Object.create(window);

document.head.innerHTML = `
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1.0">
    <meta name="language" content="de">

  <meta name="study" content="soep-core">
  <meta name="modified" content="Jan. 26, 2026, 8:19 a.m.">


  <meta name="concept" content="pgesunt">
  <meta name="period" content="0">
  <meta name="dataset" content="pl">
  <meta name="variable" content="plb0049_v6">




    <title>
    pl/plb0049_h
    </title>
    <link rel="shortcut icon" type="image/png" href="/static/dist/favicon.ico">
    <!-- Webpack bundle: "index" CSS -->
    <link href="/static/dist/index.2d69f8e6bd017d1fafd6.css" rel="stylesheet">

  <!-- Webpack bundle: "visualization" CSS -->
  <link href="/static/dist/visualization.d92bb1b91414d6ebc070.css" rel="stylesheet">
  <link href="/static/dist/variables.c2991edd31a648673d04.css" rel="stylesheet">
  <link href="/static/dist/description_modal.2fd819550f76303759c9.css" rel="stylesheet">

</head>
`;

document.body.innerHTML =
  `
<button id="language-switch" aria-label="Sprachwechsel zu Deutsch" data-current-language="en" type="button" class="btn btn-outline-dark"></button>
` +
  "<p title='Concept' data-concept-name='concept_name'>" +
  "<i class='fa fa-cog'></i>" +
  "<a href='/concept/concept-id'>" +
  "Concept Label</a>" +
  "<a id='variable-name' href=''>variable_name</a>" +
  "</p>" +
  "<div id='table-container' data-bs-type='label-table'>" +
  "</div>" +
  `
<div id="variable-relations" class="card">
   <div class="card-header" id="variable-relations-header">
      Variable Relations
      <div class="btn-group" id="relations-buttons-container" role="group" aria-label="Variable relations toggle buttons">
         <button type="button" id="concept-relation-toggle" class="btn btn-secondary active">
         <i class="fa fa-cog fa-sm"></i>
         </button>
         <button type="button" id="sibling-relation-toggle" class="btn btn-secondary  active">
         <i class="fa-solid fa-handshake fa-sm"></i>
         </button>
         <button type="button" id="output-relation-toggle" class="btn btn-secondary active">
         <i class="fa-solid fa-circle-left fa-sm"></i>
         </button>
         <button type="button" id="input-relation-toggle" class="btn btn-secondary active">
         <i class="fa-solid fa-circle-right fa-sm"></i>
         </button>
      </div>
   </div>
   <div class="card-body">
   </div>
</div>
`;

(global.window as any).location = {
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
